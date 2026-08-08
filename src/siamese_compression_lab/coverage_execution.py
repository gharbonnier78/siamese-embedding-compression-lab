"""Deterministic execution layer for v0.2.2 coverage simulations.

This module changes execution only. It does not change the Study 0 estimands, bootstrap
weights, threshold rules, coverage criteria, historical evidence, or preregistered scenario
parameters. Independent scenario/dataset substreams are derived exclusively with
``numpy.random.SeedSequence.spawn``; arithmetic seed offsets are intentionally absent.
"""

from __future__ import annotations

import hashlib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import numpy as np

from .coverage_simulation import (
    CoverageResult,
    CoverageScenario,
    _coverage_result,
    _covered,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from .subject_bootstrap import DegenerateReplicateError
from .subject_bootstrap_vectorized import (
    subject_bootstrap_delta_fnmr_vectorized as subject_bootstrap_delta_fnmr,
    subject_bootstrap_fixed_threshold_vectorized as subject_bootstrap_fixed_threshold,
)


@dataclass(frozen=True)
class SeedSequenceDescriptor:
    """Serializable identity of a spawned SeedSequence node."""

    entropy: int | tuple[int, ...]
    spawn_key: tuple[int, ...]
    pool_size: int = 4

    @classmethod
    def from_seed_sequence(cls, value: np.random.SeedSequence) -> SeedSequenceDescriptor:
        entropy = value.entropy
        if isinstance(entropy, (list, tuple, np.ndarray)):
            normalized_entropy: int | tuple[int, ...] = tuple(int(item) for item in entropy)
        else:
            normalized_entropy = int(entropy)
        return cls(
            entropy=normalized_entropy,
            spawn_key=tuple(int(item) for item in value.spawn_key),
            pool_size=int(value.pool_size),
        )

    def materialize(self) -> np.random.SeedSequence:
        return np.random.SeedSequence(
            self.entropy,
            spawn_key=self.spawn_key,
            pool_size=self.pool_size,
        )


@dataclass(frozen=True)
class DatasetSeedLineage:
    """Seed lineage for one independently replayable simulated dataset."""

    dataset_index: int
    dataset: SeedSequenceDescriptor
    distances: SeedSequenceDescriptor
    bootstrap: SeedSequenceDescriptor


@dataclass(frozen=True)
class ScenarioExecutionPlan:
    """Immutable graph and dataset seed plan for one scenario."""

    scenario: SeedSequenceDescriptor
    graph: SeedSequenceDescriptor
    datasets: tuple[DatasetSeedLineage, ...]


@dataclass(frozen=True)
class DatasetCoverageOutcome:
    """One dataset result plus byte-level digests used for replay equivalence tests."""

    dataset_index: int
    representation_covered: bool
    operational_fnmr_covered: bool
    operational_fmr_covered: bool
    degenerate: bool
    representation_delta_sha256: str | None
    operational_fnmr_sha256: str | None
    operational_fmr_sha256: str | None
    dataset_spawn_key: tuple[int, ...]
    distances_spawn_key: tuple[int, ...]
    bootstrap_spawn_key: tuple[int, ...]


def spawn_scenario_seed_sequences(
    root_seed: int,
    scenario_count: int,
) -> tuple[SeedSequenceDescriptor, ...]:
    """Spawn independent scenario streams from the frozen root seed."""
    if scenario_count <= 0:
        raise ValueError("scenario_count must be positive")
    root = np.random.SeedSequence(int(root_seed))
    return tuple(
        SeedSequenceDescriptor.from_seed_sequence(child)
        for child in root.spawn(scenario_count)
    )


def build_scenario_execution_plan(
    scenario_seed: SeedSequenceDescriptor,
    simulated_datasets: int,
) -> ScenarioExecutionPlan:
    """Spawn graph and per-dataset children, then distance/bootstrap leaves per dataset."""
    if simulated_datasets <= 0:
        raise ValueError("simulated_datasets must be positive")
    scenario = scenario_seed.materialize()
    graph_child, *dataset_children = scenario.spawn(simulated_datasets + 1)
    lineages: list[DatasetSeedLineage] = []
    for dataset_index, dataset_child in enumerate(dataset_children):
        distance_child, bootstrap_child = dataset_child.spawn(2)
        lineages.append(
            DatasetSeedLineage(
                dataset_index=dataset_index,
                dataset=SeedSequenceDescriptor.from_seed_sequence(dataset_child),
                distances=SeedSequenceDescriptor.from_seed_sequence(distance_child),
                bootstrap=SeedSequenceDescriptor.from_seed_sequence(bootstrap_child),
            )
        )
    return ScenarioExecutionPlan(
        scenario=scenario_seed,
        graph=SeedSequenceDescriptor.from_seed_sequence(graph_child),
        datasets=tuple(lineages),
    )


def seed_descriptor_to_int(seed: SeedSequenceDescriptor) -> int:
    """Convert a spawned leaf into a deterministic 128-bit PCG64 seed token.

    The statistical substream identity is established *before this boundary* by the
    reviewed ``SeedSequence.spawn`` hierarchy. ``generate_state`` is used only to adapt
    that already-spawned leaf to existing estimator APIs that accept an integer seed.
    This deliberately avoids changing the reviewed estimator functions or passing mutable
    Generator state between processes; it is not an arithmetic re-derivation of the seed.
    """
    state = seed.materialize().generate_state(4, dtype=np.uint32)
    value = 0
    for offset, word in enumerate(state):
        value |= int(word) << (32 * offset)
    return value


def _float64_digest(values: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(values, dtype=np.float64)
    return hashlib.sha256(contiguous.tobytes(order="C")).hexdigest()


def run_coverage_dataset(
    scenario: CoverageScenario,
    graph,
    lineage: DatasetSeedLineage,
    bootstrap_replicates: int,
) -> DatasetCoverageOutcome:
    """Execute one dataset from its recorded lineage; safe for isolated replay."""
    truth = scenario_truth(scenario)
    candidate, reference = simulate_distances(
        scenario,
        graph,
        seed=seed_descriptor_to_int(lineage.distances),
    )
    bootstrap_seed = seed_descriptor_to_int(lineage.bootstrap)
    try:
        representation_replicates = subject_bootstrap_delta_fnmr(
            rows=graph,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=scenario.target_fmr,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        )
        representation_delta = np.asarray(
            [row.delta_fnmr for row in representation_replicates], dtype=np.float64
        )

        operational_replicates = subject_bootstrap_fixed_threshold(
            rows=graph,
            distances=candidate,
            validation_threshold=truth.candidate_threshold,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        )
        operational_fnmr = np.asarray(
            [row.fnmr for row in operational_replicates], dtype=np.float64
        )
        operational_fmr = np.asarray(
            [row.fmr for row in operational_replicates], dtype=np.float64
        )
        return DatasetCoverageOutcome(
            dataset_index=lineage.dataset_index,
            representation_covered=_covered(representation_delta, truth.delta_fnmr),
            operational_fnmr_covered=_covered(operational_fnmr, truth.candidate_fnmr),
            operational_fmr_covered=_covered(
                operational_fmr, truth.operational_candidate_fmr
            ),
            degenerate=False,
            representation_delta_sha256=_float64_digest(representation_delta),
            operational_fnmr_sha256=_float64_digest(operational_fnmr),
            operational_fmr_sha256=_float64_digest(operational_fmr),
            dataset_spawn_key=lineage.dataset.spawn_key,
            distances_spawn_key=lineage.distances.spawn_key,
            bootstrap_spawn_key=lineage.bootstrap.spawn_key,
        )
    except DegenerateReplicateError:
        return DatasetCoverageOutcome(
            dataset_index=lineage.dataset_index,
            representation_covered=False,
            operational_fnmr_covered=False,
            operational_fmr_covered=False,
            degenerate=True,
            representation_delta_sha256=None,
            operational_fnmr_sha256=None,
            operational_fmr_sha256=None,
            dataset_spawn_key=lineage.dataset.spawn_key,
            distances_spawn_key=lineage.distances.spawn_key,
            bootstrap_spawn_key=lineage.bootstrap.spawn_key,
        )


def _dataset_worker(args) -> DatasetCoverageOutcome:
    scenario, graph, lineage, bootstrap_replicates = args
    return run_coverage_dataset(scenario, graph, lineage, bootstrap_replicates)


def run_coverage_scenario_datasets(
    scenario: CoverageScenario,
    *,
    simulated_datasets: int,
    bootstrap_replicates: int,
    scenario_seed: SeedSequenceDescriptor,
    workers: int = 1,
) -> list[DatasetCoverageOutcome]:
    """Run a scenario serially or in processes without changing dataset RNG streams."""
    if bootstrap_replicates <= 0:
        raise ValueError("bootstrap_replicates must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")
    plan = build_scenario_execution_plan(scenario_seed, simulated_datasets)
    graph = make_sparse_graph(scenario, seed=seed_descriptor_to_int(plan.graph))
    tasks = [
        (scenario, graph, lineage, bootstrap_replicates)
        for lineage in plan.datasets
    ]
    if workers == 1:
        return [_dataset_worker(task) for task in tasks]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # executor.map preserves input order; scheduling/completion order cannot alter output order.
        return list(executor.map(_dataset_worker, tasks))


def aggregate_dataset_outcomes(
    scenario: CoverageScenario,
    outcomes: list[DatasetCoverageOutcome],
    *,
    bootstrap_replicates: int,
) -> list[CoverageResult]:
    if not outcomes:
        raise ValueError("coverage aggregation requires dataset outcomes")
    ordered = sorted(outcomes, key=lambda item: item.dataset_index)
    degenerate = sum(int(item.degenerate) for item in ordered)
    return [
        _coverage_result(
            scenario.name,
            "representation_delta_fnmr",
            [item.representation_covered for item in ordered],
            degenerate_datasets=degenerate,
            bootstrap_replicates=bootstrap_replicates,
        ),
        _coverage_result(
            scenario.name,
            "operational_fnmr",
            [item.operational_fnmr_covered for item in ordered],
            degenerate_datasets=degenerate,
            bootstrap_replicates=bootstrap_replicates,
        ),
        _coverage_result(
            scenario.name,
            "operational_fmr",
            [item.operational_fmr_covered for item in ordered],
            degenerate_datasets=degenerate,
            bootstrap_replicates=bootstrap_replicates,
        ),
    ]


def run_coverage_scenario_seedsequence(
    scenario: CoverageScenario,
    *,
    simulated_datasets: int,
    bootstrap_replicates: int,
    scenario_seed: SeedSequenceDescriptor,
    workers: int = 1,
) -> list[CoverageResult]:
    outcomes = run_coverage_scenario_datasets(
        scenario,
        simulated_datasets=simulated_datasets,
        bootstrap_replicates=bootstrap_replicates,
        scenario_seed=scenario_seed,
        workers=workers,
    )
    return aggregate_dataset_outcomes(
        scenario,
        outcomes,
        bootstrap_replicates=bootstrap_replicates,
    )
