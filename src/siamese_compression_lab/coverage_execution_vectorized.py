"""Parallel coverage execution candidate using exact vectorized subject weights.

This module composes the reviewed SeedSequence/process orchestration with the full-bootstrap
vectorized candidate. It is still an engineering experiment: the authoritative coverage
execution path remains unchanged until equivalence and combined scaling evidence are reviewed.
No historical Study 0 scores are read here and no production coverage gate is executed here.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .coverage_execution import (
    DatasetCoverageOutcome,
    DatasetSeedLineage,
    SeedSequenceDescriptor,
    _float64_digest,
    build_scenario_execution_plan,
    seed_descriptor_to_int,
)
from .coverage_simulation import (
    CoverageScenario,
    _covered,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from .subject_bootstrap import DegenerateReplicateError
from .subject_bootstrap_vectorized import (
    subject_bootstrap_delta_fnmr_vectorized,
    subject_bootstrap_fixed_threshold_vectorized,
)


def run_coverage_dataset_vectorized(
    scenario: CoverageScenario,
    graph,
    lineage: DatasetSeedLineage,
    bootstrap_replicates: int,
) -> DatasetCoverageOutcome:
    """Execute one simulated dataset with vectorized bootstrap weights."""
    truth = scenario_truth(scenario)
    candidate, reference = simulate_distances(
        scenario,
        graph,
        seed=seed_descriptor_to_int(lineage.distances),
    )
    bootstrap_seed = seed_descriptor_to_int(lineage.bootstrap)
    try:
        representation_replicates = subject_bootstrap_delta_fnmr_vectorized(
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

        operational_replicates = subject_bootstrap_fixed_threshold_vectorized(
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


def _dataset_worker_vectorized(args) -> DatasetCoverageOutcome:
    scenario, graph, lineage, bootstrap_replicates = args
    return run_coverage_dataset_vectorized(
        scenario, graph, lineage, bootstrap_replicates
    )


def run_coverage_scenario_datasets_vectorized(
    scenario: CoverageScenario,
    *,
    simulated_datasets: int,
    bootstrap_replicates: int,
    scenario_seed: SeedSequenceDescriptor,
    workers: int = 1,
) -> list[DatasetCoverageOutcome]:
    """Run vectorized datasets serially or in processes with unchanged RNG lineage."""
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
        return [_dataset_worker_vectorized(task) for task in tasks]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_dataset_worker_vectorized, tasks))
