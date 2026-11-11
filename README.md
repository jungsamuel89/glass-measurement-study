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

## Interpretation and availability

Availability includes every attempted target/configuration pair. Width/height
errors are conditional on numeric results. The main estimator gives each capture
equal weight; exploratory intervals resample visual front groups. These intervals
condition on the selected cohort and do not remove selection bias. Exploratory
S5/S10/S20 tolerances are reported as descriptive analyses, not established
construction acceptance limits. The best S20 configuration was selected on this
same cohort and is not an independently validated winner.

These are the original native results. A shared validation-based confidence rule
and its full physical-measurement replay are separate work; this snapshot does
not claim them completed. Requested K is not necessarily the accepted frame count.
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
