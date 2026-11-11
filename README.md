# Measuring building glazing with mobile RGB-D

**Working research draft: accuracy, availability and computational effort.**
Maintainer: Samuel Jung · [info@jettsterbuild.com](mailto:info@jettsterbuild.com).

This package contains anonymised derived data and portable analysis for a screened
30-capture comparison pool and its fixed 27-capture primary cohort. All failed
attempts and reference dimensions are retained. Screening and the greater-than-40%
availability selection were post hoc; the 30 captures are not the full collection.
Repeated views and shared frames are accounted for in the documented analysis.

## Reproduce

Python 3.10 and the pinned dependencies were checked from a fresh checkout:

```sh
python -m venv .venv
# Activate the environment using your platform's normal command.
python -m pip install -r requirements.lock
python analysis/reproduce_statistics.py
python analysis/reproduce_settings.py
python analysis/reproduce_figures.py
python analysis/verify.py
python analysis/verify_matching.py
python analysis/reproduce_confidence.py
python analysis/plot_confidence.py
```

Outputs go to `results/`, with operating-point outputs in `results/validation/`.
Paths resolve relative to the scripts. Verification checks file hashes, failure
denominators, frozen reference values and 300 exhaustive synthetic matching cases.
The confidence analysis reproduces all nine validation selections and reported
fixed-threshold test metrics from pseudonymised scores and pairwise IoU matrices.

## Validation-selected operating points

Version `v0.2-validation` uses the same 149 validation images and image-mean
PQ-like rule for all nine models. All thresholds were frozen before calculating
new fixed-threshold metrics from the existing TEST147 caches.

| Family | 139 training images | 278 training images | 555 training images |
|---|---:|---:|---:|
| RF-DETR-Seg-Small | 0.43 | 0.34 | 0.45 |
| RTMDet-Ins-Tiny | 0.60 | 0.69 | 0.50 |
| Mask R-CNN ResNet50-FPN | 0.95 | 0.92 | 0.94 |

These are operating scores, not calibrated correctness probabilities. Mask R-CNN
with 139 images selects the prespecified upper grid boundary 0.95; this is the
best point within that grid. All outcomes are retained, including reductions in
some RF-DETR test metrics. Validation already supported checkpoint selection;
TEST147 was previously evaluated, and 77 images have documented earlier development
use. This is a post-hoc protocol revision, not an untouched independent test.

Physical measurements and timings are recorded iPhone outputs; the separately
validation-selected original-model CPU thresholds support segmentation
interpretation and are not verified iPhone operating points.

Aggregated [archived first-frame counts](data/derived/native_first_frame_interpretation.json)
retain 416 of 417 available reviewed target observations in the primary cohort;
15 of 432 target/model opportunities have no selected archived observation.[^scores]

[^scores]: First-frame archived candidates only. RF archives omit candidates below
    their original floors, so lower thresholds cannot recover unseen candidates;
    other candidates are not necessarily false positives.

## Data and interpretation

Availability includes all attempted target/configuration pairs; errors are
conditional on numeric outputs. The primary estimator weights captures equally.
Exploratory intervals resample visually assigned front groups and condition on the
selected cohort. These groups are not independently verified building identities.
Requested frame count can exceed accepted frame count. Cached work attribution
is distinct from measured live latency.

See [`data/README.md`](data/README.md), [`data/schema.json`](data/schema.json),
[`config/analysis.json`](config/analysis.json) and
[`data/confidence_schema.md`](data/confidence_schema.md) for exact definitions.
The public arrays reproduce matching and statistics; inference and IoU calculation
from private masks and annotations are outside their scope.

Raw RGB-D data and trained weights may be requested for reasonable research
purposes via info@jettsterbuild.com, subject to privacy, rights and third-party
terms. Nine original checkpoints and detailed training/split provenance are
preserved in a private companion repository. The capture app remains private.
No blanket reuse licence has been assigned; see [`RIGHTS.md`](RIGHTS.md).
