"""Tests for public artifacts only; full-model tests are not released here."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.check_release import audit, read, validate_split
from scripts.summarize_paper_results import collect, summarize, METRICS


ROOT = Path(__file__).resolve().parents[1]


class PreviewTests(unittest.TestCase):
    def test_preview_integrity(self):
        result = audit(ROOT)
        self.assertFalse(result["model_training_or_inference_executed"])
        self.assertEqual(result["status"], "partial_pre_acceptance_preview")

    def test_no_neural_implementation_or_weights(self):
        for name in ("retrosnt", "main.py", "environment.yml", "processed"):
            self.assertFalse((ROOT / name).exists())
        for suffix in ("*.pt", "*.pth"):
            self.assertEqual(list(ROOT.rglob(suffix)), [])

    def test_frozen_split(self):
        sizes = validate_split(read(ROOT / "reproducibility/seed42/splits.json"))
        self.assertEqual(sizes, {"train": 28296, "validation": 3537, "test": 3537})

    def test_duplicate_or_overlapping_indices_are_rejected(self):
        parts = read(ROOT / "reproducibility/seed42/splits.json")
        parts["train"][0] = parts["validation"][0]
        with self.assertRaises(ValueError):
            validate_split(parts)

    def test_configs_keep_training_and_split_seeds_separate(self):
        for group, seed, given in (("with_class", 43, True), ("without_class", 44, False)):
            cfg = read(ROOT / f"configs/{group}.yaml")
            self.assertEqual(cfg["seed"], seed)
            self.assertEqual(cfg["data"]["split_seed"], 42)
            self.assertIs(cfg["model"]["use_reaction_class"], given)

    def test_original_selected_scores(self):
        results = collect(ROOT)
        expected = {"with_class": ["67.80", "87.31", "91.86"],
                    "without_class": ["60.56", "81.82", "87.96"]}
        for group, scores in expected.items():
            actual = results[group]["checkpoints"]["calibrated"]["topk"]
            self.assertEqual([actual[key]["display_percent"] for key in METRICS], scores)
            self.assertEqual(read(ROOT / "runs" / group / "selected_result.json"), results[group])

    def test_summary_rejects_invalid_scores_and_multiple_runs(self):
        record = {"seed": 43, "metrics": {key: 0.5 for key in METRICS}}
        with self.assertRaises(ValueError):
            summarize([record, record])
        record["metrics"][METRICS[0]] = float("nan")
        with self.assertRaises(ValueError):
            summarize([record])

    def test_tampered_result_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "preview"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = target / "runs/with_class/20261114_013808/evaluation_test.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                audit(target)

    def test_upstream_attribution_and_partial_release_notice(self):
        manifest = read(ROOT / "reproducibility/source_manifest.json")
        self.assertEqual(manifest["data_provenance"]["source_repository"],
                         "https://github.com/zpczaizheli/Retro-MTGR")
        self.assertIn("partial public release", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
