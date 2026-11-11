# Measuring building glazing with mobile RGB-D

**Working research draft: accuracy, availability and computational effort.**
Maintainer: Samuel Jung · [info@jettsterbuild.com](mailto:info@jettsterbuild.com).

This package reproduces statistics from anonymised derived native measurements.
It contains the 30-capture screened comparison pool and its fixed 27-capture
primary cohort, including unsuccessful attempts and physical reference dimensions.
Screening and the greater-than-40% availability selection were post hoc. The
30 captures are not the total originally collected series. Configurations share
frames; they are not independent samples. Front groups are visually assigned and
not an independently verified building/facade identity register.

## Reproduce

Python 3.10 was checked. From a fresh checkout:

```sh
python -m venv .venv
# Activate the environment using your platform's normal command.
python -m pip install -r requirements.lock
python analysis/reproduce_statistics.py
python analysis/reproduce_settings.py
python analysis/reproduce_figures.py
python analysis/verify.py
```

Paths resolve from the scripts, so these commands also work from another directory.
Outputs go to `results/`. The verification checks file hashes, completeness,
references, all failure denominators and numerical agreement with the frozen
source summaries. Dependencies are pinned to the tested environment.

## Original-model CPU operating points

Version `v0.2-validation` adds a separate segmentation interpretation analysis.
All nine original models use the same 149 validation images and the same
image-mean PQ-like selection rule. All thresholds were frozen before calculating
the new fixed-threshold metrics from the existing TEST147 prediction caches.

```sh
python analysis/verify_matching.py
python analysis/reproduce_confidence.py
python analysis/plot_confidence.py
```

The first command checks 300 synthetic cases against exhaustive matching. The
second independently reproduces all nine validation selections and reported
validation/test operating-point metrics from pseudonymised scores and pairwise
IoU matrices. Results and the comparison plot go to `results/validation/`.

| Family | 139 training images | 278 training images | 555 training images |
|---|---:|---:|---:|
| RF-DETR-Seg-Small | 0.43 | 0.34 | 0.45 |
| RTMDet-Ins-Tiny | 0.60 | 0.69 | 0.50 |
| Mask R-CNN ResNet50-FPN | 0.95 | 0.92 | 0.94 |

These are selected operating scores, not calibrated correctness probabilities.
Mask R-CNN with 139 training images reaches the prespecified upper grid boundary
0.95; it is only the best point within that grid. All outcomes are retained,
including small reductions in some RF-DETR test metrics. The validation data
already supported checkpoint selection. TEST147 was previously evaluated, and
earlier development use is documented for 77 of its images. This is a post-hoc
protocol revision, not an untouched independent test.

The CPU thresholds are not verified Core ML/iPhone operating points. They do not
change the original physical dataset or its timings. No reconstructed physical
measurements or replay code are included. See
[`data/confidence_schema.md`](data/confidence_schema.md) for labels, matching,
denominators, pseudonymisation and the limit that IoU matrices cannot reproduce
private mask generation or annotation geometry.

## Interpretation and availability

Availability includes every attempted target/configuration pair. Width/height
errors are conditional on numeric results. The main estimator gives each capture
equal weight; exploratory intervals resample visual front groups. These intervals
condition on the selected cohort and do not remove selection bias. Exploratory
S5/S10/S20 tolerances are reported as descriptive analyses, not established
construction acceptance limits. The best S20 configuration was selected on this
same cohort and is not an independently validated winner.

The physical results and timings are the original iPhone outputs. Additional
original-model CPU operating-point analysis concerns segmentation interpretation;
it does not reconstruct or replace any physical measurements. No physical replay
is part of this study package. Requested K is not necessarily the accepted frame count.
Cached work attribution is not new live latency. See `data/README.md`,
`data/schema.json` and `config/analysis.json` for exact boundaries.

Raw RGB-D data and trained weights are not public. They may be requested for
reasonable research purposes via the contact above, subject to privacy, rights,
third-party terms and an agreed transfer scope. The nine original checkpoints
and training/split provenance are preserved in a separate private repository.
The product/capture app remains private. This package reproduces analysis of
derived rows, not capture, model inference or the complete measurement pipeline.

No journal acceptance, independent validation, DOI or final author approval is
claimed. Repository maintenance is not a confirmed manuscript authorship list.
No reuse licence is granted by the existence of this public repository; see
`RIGHTS.md`. Reproduction requests are welcome.
