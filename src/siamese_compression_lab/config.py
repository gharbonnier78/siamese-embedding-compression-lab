"""Configuration loading and run-freezing utilities."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DataConfig:
    mode: str = "synthetic"
    data_root: str = "data"
    kaggle_dataset: str = "jessicali9530/lfw-dataset"
    backbone: str = "resnet18_imagenet"
    cache_dir: str = "cache"
    val_identity_fraction: float = 0.25
    split_seed: int = 20260806
    synthetic_input_dim: int = 512
    synthetic_latent_dim: int = 40
    synthetic_train_identities: int = 80
    synthetic_val_identities: int = 30
    synthetic_test_identities: int = 30
    synthetic_images_per_identity: int = 6
    synthetic_pairs_per_split: int = 600


@dataclass(frozen=True)
class TrainingConfig:
    output_dim: int = 128
    seeds: tuple[int, ...] = (11, 29, 47)
    epochs: int = 35
    batch_size: int = 128
    learning_rate: float = 0.002
    weight_decay: float = 0.0001
    contrastive_margin: float = 1.0
    patience: int = 6
    minimum_improvement: float = 0.0001


@dataclass(frozen=True)
class EvaluationConfig:
    target_fmrs: tuple[float, ...] = (0.01,)
    bootstrap_replicates: int = 400
    bootstrap_seed: int = 20260806
    noninferiority_delta_fnmr: float = 0.03
    minimum_validation_impostors: int = 200
    template_dtype_bytes: int = 4
    gallery_sizes: tuple[int, ...] = (1_000, 100_000, 1_000_000, 150_000_000)


@dataclass(frozen=True)
class ReplayConfig:
    contract_version: str = "mmals-replay-domain-pack/1.0"
    profile: str = "standard"
    objective_id: str = "edge_template_noninferiority"
    preserve_csv_compatibility: bool = True


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str = "siamese_embedding_compression"
    description: str = (
        "Compare raw, random, PCA and supervised Siamese projections under a fixed "
        "template-storage budget."
    )
    data: DataConfig = field(default_factory=DataConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    replay: ReplayConfig = field(default_factory=ReplayConfig)


def _construct(config_type: type, values: dict[str, Any]) -> Any:
    return config_type(**values)


def load_config(path: str | Path) -> ExperimentConfig:
    """Load YAML and reject unknown top-level sections through dataclass constructors."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return ExperimentConfig(
        experiment_id=raw.get("experiment_id", ExperimentConfig.experiment_id),
        description=raw.get("description", ExperimentConfig.description),
        data=_construct(DataConfig, raw.get("data", {})),
        training=_construct(TrainingConfig, _tuplify(raw.get("training", {}), {"seeds"})),
        evaluation=_construct(
            EvaluationConfig,
            _tuplify(raw.get("evaluation", {}), {"target_fmrs", "gallery_sizes"}),
        ),
        replay=_construct(ReplayConfig, raw.get("replay", {})),
    )


def _tuplify(values: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    result = dict(values)
    for name in fields:
        if name in result:
            result[name] = tuple(result[name])
    return result


def config_dict(config: ExperimentConfig) -> dict[str, Any]:
    return asdict(config)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def config_digest(config: ExperimentConfig) -> str:
    return hashlib.sha256(canonical_json(config_dict(config)).encode("utf-8")).hexdigest()


def validate_config(config: ExperimentConfig) -> None:
    if config.data.mode not in {"synthetic", "lfw"}:
        raise ValueError("data.mode must be 'synthetic' or 'lfw'")
    if config.training.output_dim <= 0:
        raise ValueError("training.output_dim must be positive")
    if not config.training.seeds:
        raise ValueError("at least one pre-specified seed is required")
    if len(set(config.training.seeds)) != len(config.training.seeds):
        raise ValueError("training seeds must be unique")
    if not 0 < config.data.val_identity_fraction < 1:
        raise ValueError("val_identity_fraction must be in (0, 1)")
    if any(not 0 < fmr < 1 for fmr in config.evaluation.target_fmrs):
        raise ValueError("target FMR values must be in (0, 1)")
    if config.evaluation.bootstrap_replicates < 20:
        raise ValueError("at least 20 bootstrap replicates are required")
    if config.evaluation.minimum_validation_impostors < 1:
        raise ValueError("minimum_validation_impostors must be positive")
