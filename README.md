# RetroSNT

Reaction-center-aware spiking tokenized graph network for single-step retrosynthesis.

Companion project for the current five-seed manuscript:
**Evaluating single-step retrosynthesis with local environment counts and explicit ranking protocols**.

## Release status: pre-acceptance partial preview

This is a **partial public release**, not the complete RetroSNT implementation.
The model architecture implementation, training and loss code, inference/decoding
code, preprocessing algorithms, and model weights are **not included at this stage**.
Full source code and reproduction instructions are planned for release upon
manuscript acceptance.

The available scripts independently verify the supplied split metadata and
archived result files. They do not train or execute the neural model, regenerate
its predictions, or constitute a full reproduction of the manuscript experiments.

## Available now

```text
configs/                 # Example with_class and without_class configurations
reproducibility/seed42/   # Fixed split indices, vocabularies, counts, and input hashes
runs/with_class/          # Historical single-run example, not the five-seed paper mean
runs/without_class/       # Historical single-run example, not the five-seed paper mean
scripts/                 # Standalone split/result verification tools
tests/                   # Tests for this partial preview only
```

Configuration files document experiment settings; they are not executable model
implementations. There is intentionally no training or inference entry point in
this release. The withheld code is not embedded in the archive or Git history.

## Run the public checks

Python 3.10 or later is sufficient. No third-party Python packages, GPU, model
weights, or raw reactions are needed for these checks.

```bash
python scripts/check_release.py
python scripts/summarize_paper_results.py --check
python -m unittest discover -s tests -v
```

These commands check file integrity, split sizes and disjointness, example
configuration consistency, and the two historical archived runs. They do not
recompute the manuscript's five-seed statistics. Passing them does not certify
model training, inference, or full benchmark reproducibility.

## Data source and partition

Reaction data originate from [Retro-MTGR](https://github.com/zpczaizheli/Retro-MTGR).
The manuscript analyzes a fixed eight-class USPTO-derived instance, not an
independently verified official ten-class USPTO-50K test split.
The original reaction file and auxiliary inputs are not redistributed here. The
input hashes and file placement are documented in [data/README.md](data/README.md).

The supplied reference split contains 28,296 training, 3,537 validation, and 3,537
test reactions. Test positions are `[31833,35370)` (zero-based); training and
validation were stratified by reaction class within `[0,31833)` using split seed
42. Both class settings share this reference split. Training seeds are separate
from the split seed. Neural-run split identity is author-confirmed; the supplied
snapshot and its input identities are documented separately.

A shared data source does not by itself establish an identical training and
validation partition to Retro-MTGR.

## Results aligned with the five-seed manuscript

The following values match Tables 2 and 3 of the current CEJ v06 manuscript
(2026-11-23). Neural results are arithmetic means ± sample standard deviations
(%, `ddof=1`) over **all five training seeds: 40, 41, 42, 43, and 44**, separately
for each reaction-class setting and checkpoint type. Each test set has 3,537
reactions on the same fixed reference split. No highest-scoring seed is selected
for these reported means, and best/calibrated results are not mixed according to
which test score is higher.

| Reaction-class setting | Checkpoint | Top-1 (%) | Top-3 (%) | Top-5 (%) |
|---|---|---:|---:|---:|
| Class withheld (`without_class`) | `best.pt` — primary | 59.00 ± 0.95 | 80.28 ± 0.72 | 85.76 ± 1.32 |
| Class withheld (`without_class`) | `calibrated.pt` | 59.50 ± 0.95 | 81.65 ± 0.26 | 87.83 ± 0.50 |
| Class given (`with_class`) | `best.pt` — primary | 67.44 ± 0.38 | 86.39 ± 0.34 | 90.18 ± 0.70 |
| Class given (`with_class`) | `calibrated.pt` | 67.45 ± 0.34 | 86.98 ± 0.29 | 91.52 ± 0.49 |

The primary neural analysis uses validation-selected, uncalibrated `best.pt`
checkpoints. Calibration is fitted on validation data and reported separately as
a sensitivity analysis. Manuscript Table 2 includes both checkpoint types;
Table 3 uses the calibrated rows. The standard deviations describe between-run
variation on one fixed split; they are not confidence intervals over independent
test datasets.

This is a descriptive archival cohort, **not an identical-schedule** five-seed
replication. Early-stopping patience is 12 for seeds 40, 41, 43, and 44, but 1,000
for seed 42, within a 100-epoch budget. The class-withheld seed-42 run ended after
93 completed epochs. The current configuration examples do not replace the
individual historical configurations documented with the manuscript.

### Train-only EnvCount reference

The manuscript's validation-selected EnvCount reference is fitted only on the
28,296 training reactions, without refitting on validation records. Radius 3 and
smoothing parameter 2 are selected using validation data in both class settings.
Its mapped-label, global joint-ranking results are deterministic, not five-seed
means:

| Reaction-class setting | Top-1 (%) | Top-3 (%) | Top-5 (%) |
|---|---:|---:|---:|
| Class withheld | 50.24 | 75.01 | 83.29 |
| Class given | 59.66 | 82.98 | 90.13 |

These are descriptive local comparisons, not a matched-protocol ranking against
the published literature models. The manuscript's separate historical paired
audit uses its own stored checkpoints and a training-plus-validation count table;
it is not pooled into these five-seed neural means.

### What the public archive currently contains

The `runs/` directories retain **historical single-run examples** only: with-class
seed 43 and without-class seed 44. These examples were previously selected by
calibrated test Top-1 within seeds 41, 43, and 44. Their original JSON files and
selection metadata remain unchanged for provenance; they are not the current
five-seed paper results. See [the archive manifest](reproducibility/source_manifest.json).

The full five-seed statistics are documented in the manuscript's
`results_five_seeds.json` and its archived evaluations. Those complete artifacts
are not yet included in this partial public preview. Consequently,
`summarize_paper_results.py --check` currently verifies the two historical examples,
not the five-seed means displayed above. No neural results were generated by the
public preview scripts.

`retro_mtgr_top1/3/5` denotes exact matches of ordered `(center bond, left
leaving-group label, right leaving-group label)` triples under the local evaluator.
It is not reconstructed reactant-set accuracy. The full evaluator and neural
implementation are part of the planned complete release.

The reported local results use the original annotation-assisted candidate policy:
non-ring bonds plus the annotated centre when it is a ring bond. They should not
be described as unrestricted product-only or all-bond predictions. Sharing the
Retro-MTGR task decomposition does not establish identical data or ranking
conditions to its published model results.

## Planned complete release

The planned post-acceptance release will add the neural model, training objectives
and engine, full preprocessing and decoding implementations, matching dependency
instructions, and end-to-end reproduction commands. This notice describes a plan;
the complete implementation is not currently available in this repository.

The scope of this partial release should also be reflected in the manuscript's
code-availability statement. This repository does not assign an open-source
license; licensing and upstream redistribution permissions remain for the authors
to confirm before distributing additional materials.
