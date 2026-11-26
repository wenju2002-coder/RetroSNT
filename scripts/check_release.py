"""Audit the partial preview only; no neural model is loaded or evaluated."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_split(parts):
    expected = {"train": 28296, "validation": 3537, "test": 3537}
    if {key: len(value) for key, value in parts.items()} != expected:
        raise ValueError("Unexpected split sizes")
    for key, values in parts.items():
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in values):
            raise ValueError(f"Non-integer split index: {key}")
        if len(set(values)) != len(values):
            raise ValueError(f"Repeated split index: {key}")
    train, validation, test = (set(parts[key]) for key in ("train", "validation", "test"))
    if train & validation or train & test or validation & test:
        raise ValueError("Overlapping partitions")
    if train | validation != set(range(31833)):
        raise ValueError("Unexpected training/validation pool")
    if parts["test"] != list(range(31833, 35370)):
        raise ValueError("Unexpected fixed test indices")
    return expected


def audit(root=ROOT):
    root = Path(root).resolve()
    checksums = read(root / "reproducibility/release_checksums.json")
    for relative, expected in checksums.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Checksum path is outside the preview")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Preview checksum mismatch: {relative}")
    for name in ("retrosnt", "main.py", "processed"):
        if (root / name).exists():
            raise ValueError(f"Unexpected full-implementation artifact in preview: {name}")
    manifest = read(root / "reproducibility/source_manifest.json")
    scope = manifest["release_scope"]
    if scope["status"] != "partial_pre_acceptance_preview":
        raise ValueError("Release scope must identify this as a partial preview")
    for flag in ("model_implementation_included", "training_implementation_included",
                 "inference_implementation_included", "model_weights_included",
                 "raw_data_included", "full_reproduction_supported"):
        if scope[flag] is not False:
            raise ValueError(f"Incorrect partial-release flag: {flag}")
    sizes = validate_split(read(root / "reproducibility/seed42/splits.json"))
    for group, seed in (("with_class", 43), ("without_class", 44)):
        config = read(root / f"configs/{group}.yaml")  # Supplied YAML files also use valid JSON syntax.
        if config["data"]["split_seed"] != 42 or config["seed"] != seed:
            raise ValueError(f"Unexpected split/training seed: {group}")
        if config["model"]["use_reaction_class"] is not (group == "with_class"):
            raise ValueError(f"Incorrect class setting: {group}")
    return {"status": scope["status"], "files_verified": len(checksums),
            "split_sizes": sizes, "model_training_or_inference_executed": False}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
    print("PASS: preview artifacts verified; this is not a full-model reproduction.")
