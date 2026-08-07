"""LFW ingestion with identity-disjoint TRAIN/VALIDATION and frozen image features."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .config import ExperimentConfig
from .data import DatasetBundle, PairSplit


@dataclass(frozen=True)
class PairRecord:
    identity1: str
    image1: int
    identity2: str
    image2: int
    same: int
    pair_id: str


def _first_match(root: Path, name: str) -> Path | None:
    matches = sorted(root.rglob(name), key=lambda path: (len(path.parts), str(path)))
    return matches[0] if matches else None


def _has_pair_files(root: Path) -> bool:
    return _first_match(root, "matchpairsDevTrain.csv") is not None


def resolve_lfw_root(config: ExperimentConfig) -> tuple[Path, str]:
    requested = Path(config.data.data_root).expanduser().resolve()
    if requested.exists() and _has_pair_files(requested):
        return requested, "local"
    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError(
            "LFW files were not found. Install the 'lfw' optional dependencies or place "
            "the public Kaggle LFW dataset under data_root."
        ) from exc
    downloaded = Path(kagglehub.dataset_download(config.data.kaggle_dataset)).resolve()
    if not _has_pair_files(downloaded):
        raise FileNotFoundError(
            f"Kaggle dataset downloaded to {downloaded}, but DevTrain CSV files were absent"
        )
    return downloaded, f"kagglehub:{config.data.kaggle_dataset}"


def _read_csv_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if rows and not rows[0][0].strip().replace("_", "").isalnum() or rows and rows[0][0].lower() in {"name", "name1", "person"}:
        rows = rows[1:]
    return [row for row in rows if row]


def _load_dev_pairs(root: Path, split: str) -> tuple[list[PairRecord], dict[str, str]]:
    suffix = "Train" if split == "train" else "Test"
    matched_path = _first_match(root, f"matchpairsDev{suffix}.csv")
    mismatched_path = _first_match(root, f"mismatchpairsDev{suffix}.csv")
    if matched_path is None or mismatched_path is None:
        raise FileNotFoundError(f"missing LFW Dev{suffix} pair CSV files under {root}")
    records: list[PairRecord] = []
    for index, row in enumerate(_read_csv_rows(matched_path)):
        if len(row) < 3:
            continue
        identity, first, second = row[0], int(row[1]), int(row[2])
        records.append(
            PairRecord(identity, first, identity, second, 1, f"{split}_genuine_{index:05d}")
        )
    for index, row in enumerate(_read_csv_rows(mismatched_path)):
        if len(row) < 4:
            continue
        records.append(
            PairRecord(
                row[0],
                int(row[1]),
                row[2],
                int(row[3]),
                0,
                f"{split}_impostor_{index:05d}",
            )
        )
    return records, {
        "matched_pairs_file": str(matched_path),
        "mismatched_pairs_file": str(mismatched_path),
        "matched_pairs_sha256": _sha256(matched_path),
        "mismatched_pairs_sha256": _sha256(mismatched_path),
    }


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _split_dev_train_by_identity(
    records: list[PairRecord], val_fraction: float, seed: int
) -> tuple[list[PairRecord], list[PairRecord], int, list[str], list[str]]:
    identities = sorted(
        {record.identity1 for record in records} | {record.identity2 for record in records}
    )
    rng = np.random.default_rng(seed)
    shuffled = np.asarray(identities, dtype=object)
    rng.shuffle(shuffled)
    n_validation = max(1, round(val_fraction * len(shuffled)))
    validation_identities = set(map(str, shuffled[:n_validation]))
    train_identities = set(map(str, shuffled[n_validation:]))
    train, validation = [], []
    dropped_cross_partition = 0
    for record in records:
        pair_identities = {record.identity1, record.identity2}
        if pair_identities <= train_identities:
            train.append(record)
        elif pair_identities <= validation_identities:
            validation.append(record)
        else:
            dropped_cross_partition += 1
    for name, subset in (("train", train), ("validation", validation)):
        labels = {record.same for record in subset}
        if labels != {0, 1}:
            raise ValueError(f"identity-disjoint {name} split lost a pair class: {labels}")
    return (
        train,
        validation,
        dropped_cross_partition,
        sorted(train_identities),
        sorted(validation_identities),
    )


def _find_images_root(root: Path) -> Path:
    candidates = sorted(
        [path for path in root.rglob("lfw-deepfunneled") if path.is_dir()],
        key=lambda path: (-len(path.parts), str(path)),
    )
    for candidate in candidates:
        # A valid root has identity directories immediately below it. Some mirrors
        # repeat the lfw-deepfunneled directory name, so a recursive JPG check would
        # incorrectly select the outer container.
        if next(candidate.glob("*/*.jpg"), None) is not None:
            return candidate
    raise FileNotFoundError("could not locate lfw-deepfunneled image directory")


def _record_path(images_root: Path, identity: str, number: int) -> Path:
    path = images_root / identity / f"{identity}_{number:04d}.jpg"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def _paths_and_digest(images_root: Path, records: list[PairRecord]) -> tuple[list[Path], str]:
    paths = sorted(
        {
            _record_path(images_root, identity, number)
            for record in records
            for identity, number in (
                (record.identity1, record.image1),
                (record.identity2, record.image2),
            )
        }
    )
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(str(path.relative_to(images_root)).encode("utf-8"))
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
    return paths, hasher.hexdigest()


def _state_digest(model: Any) -> str:
    hasher = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        hasher.update(name.encode("utf-8"))
        hasher.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return hasher.hexdigest()


def _extract_resnet18(
    paths: list[Path], cache_path: Path, seed: int
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, Dataset
        from torchvision import models, transforms
        from torchvision.models import ResNet18_Weights
    except ImportError as exc:
        raise RuntimeError("The LFW run requires torch and torchvision") from exc

    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        cached_paths = cached["paths"].astype(str)
        embeddings = cached["embeddings"].astype(np.float32)
        mapping = {path: embedding for path, embedding in zip(cached_paths, embeddings)}
        return mapping, {
            "feature_cache": str(cache_path),
            "feature_cache_hit": True,
            "backbone_state_sha256": str(cached["backbone_state_sha256"]),
        }

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    model.fc = nn.Identity()
    model.eval().to(device)
    for parameter in model.parameters():
        parameter.requires_grad = False
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),
        ]
    )

    class ImagePaths(Dataset):
        def __len__(self) -> int:
            return len(paths)

        def __getitem__(self, index: int) -> Any:
            with Image.open(paths[index]) as image:
                return transform(image.convert("RGB"))

    loader = DataLoader(
        ImagePaths(), batch_size=128, shuffle=False, num_workers=0, pin_memory=device.type == "cuda"
    )
    batches: list[np.ndarray] = []
    with torch.inference_mode():
        for batch in loader:
            batches.append(model(batch.to(device)).cpu().numpy().astype(np.float32))
    embeddings = np.concatenate(batches, axis=0)
    path_strings = np.asarray([str(path.resolve()) for path in paths])
    state_sha = _state_digest(model)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        cache_path,
        paths=path_strings,
        embeddings=embeddings,
        backbone_state_sha256=np.asarray(state_sha),
    )
    mapping = {path: embedding for path, embedding in zip(path_strings, embeddings)}
    return mapping, {
        "feature_cache": str(cache_path),
        "feature_cache_hit": False,
        "backbone_state_sha256": state_sha,
        "device": str(device),
        "preprocessing": "Resize(224,224)+ImageNetNormalize; Antonio replication",
    }


def _to_pair_split(
    name: str,
    records: list[PairRecord],
    images_root: Path,
    embeddings: dict[str, np.ndarray],
) -> PairSplit:
    path1 = [str(_record_path(images_root, record.identity1, record.image1).resolve()) for record in records]
    path2 = [str(_record_path(images_root, record.identity2, record.image2).resolve()) for record in records]
    return PairSplit(
        name=name,
        x1=np.stack([embeddings[path] for path in path1]).astype(np.float32),
        x2=np.stack([embeddings[path] for path in path2]).astype(np.float32),
        same=np.asarray([record.same for record in records], dtype=np.int8),
        identity1=np.asarray([record.identity1 for record in records]),
        identity2=np.asarray([record.identity2 for record in records]),
        pair_id=np.asarray([record.pair_id for record in records]),
        source="LFW DevTrain/DevTest pair protocol",
    )


def make_lfw_bundle(config: ExperimentConfig) -> DatasetBundle:
    if config.data.backbone != "resnet18_imagenet":
        raise ValueError("v0.1 implements the Antonio-compatible resnet18_imagenet backbone")
    root, acquisition = resolve_lfw_root(config)
    dev_train, dev_train_meta = _load_dev_pairs(root, "train")
    dev_test, dev_test_meta = _load_dev_pairs(root, "test")
    train, validation, dropped, train_ids, validation_ids = _split_dev_train_by_identity(
        dev_train, config.data.val_identity_fraction, config.data.split_seed
    )
    images_root = _find_images_root(root)
    # Cache the complete official DevTrain/DevTest image universe. The feature cache is
    # therefore independent of the chosen TRAIN/VALIDATION identity partition.
    all_records = dev_train + dev_test
    paths, image_digest = _paths_and_digest(images_root, all_records)
    cache_key = hashlib.sha256(
        f"resnet18_imagenet|antonio_resize224_v1|{image_digest}".encode()
    ).hexdigest()[:20]
    cache_path = Path(config.data.cache_dir).expanduser().resolve() / f"lfw_{cache_key}.npz"
    embeddings, feature_meta = _extract_resnet18(
        paths, cache_path, seed=config.training.seeds[0]
    )
    bundle = DatasetBundle(
        train=_to_pair_split("train", train, images_root, embeddings),
        validation=_to_pair_split("validation", validation, images_root, embeddings),
        test=_to_pair_split("test", dev_test, images_root, embeddings),
        metadata={
            "dataset": "Labeled Faces in the Wild (LFW)",
            "protocol": "DevTrain identity split + untouched DevTest",
            "acquisition": acquisition,
            "dataset_root": str(root),
            "images_sha256": image_digest,
            "backbone": config.data.backbone,
            "feature_extraction": feature_meta,
            "dev_train_files": dev_train_meta,
            "dev_test_files": dev_test_meta,
            "split_seed": config.data.split_seed,
            "dropped_cross_partition_impostor_pairs": dropped,
            "train_identity_count": len(train_ids),
            "validation_identity_count": len(validation_ids),
            "evidence_level": "lfw_exploratory_benchmark",
            "scientific_claim_allowed": True,
            "warning": (
                "Limited benchmark claim only: ImageNet ResNet-18 is not a biometric-grade "
                "face backbone and LFW DevTest is too small for low-FMR operational claims."
            ),
        },
    )
    bundle.validate_no_identity_leakage()
    return bundle
