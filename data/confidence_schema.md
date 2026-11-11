# Original-model CPU operating-point data

The confidence analysis interprets segmentation behaviour. The physical study
continues to use the original iPhone measurements and timings unchanged. There
are no reconstructed physical measurements or physical-replay outputs here.

`validation_score_iou.json.gz` and `test_score_iou.json.gz` contain derived arrays
for nine original trained models. Each model has 149 validation or 147 test
images. These are the existing image splits, not a new independent collection.
Validation already supported checkpoint selection; TEST147 had already been
evaluated before this protocol revision. The validation split contains only two
approximate proxy groups. Proxy groups are not verified building identities.
Earlier development use is documented for 77 of the TEST147 images. Exact-content
and stored-group separation does not establish physical building independence.

Each image record has:

| Field | Meaning |
|---|---|
| `image` | Pseudonymous ID scoped to the validation (`V`) or test (`T`) split. |
| `group` | Pseudonym for the original approximate grouping. |
| `ground_truth_instances` | Number of annotated `measurement_glass` instances. |
| `candidate_scores` | Unchanged scores for the native retained candidate set, at most 100. |
| `instance_iou` | Ground-truth-by-candidate IoU matrix on the common 768-pixel grid. Row and column indices are local to the image. |
| `mask_union_iou_at_reported_thresholds` | Scalar union IoU from the private masks at each reported selected/baseline threshold. |

The arrays contain no original image UUIDs, filenames, coordinates, masks or
photographs. They permit independent threshold retention, maximum-cardinality
spatial matching, PQ-like/F1/count metrics, validation threshold selection and
fixed-threshold test calculations. **They do not reproduce model inference or
the calculation of IoU from masks and annotations.** A pairwise IoU matrix is
insufficient to reconstruct a mask union; the exported union-IoU scalars are
aggregated without pretending to reconstruct that geometry.

The label means the annotated measurement-glass targets under the original
annotation contract. It does not guarantee that every visible glass object was
annotated. All annotated instances and all retained candidates contribute to the
counts. There are no negative images, so absence-of-glass behaviour is untested.

The primary score is the arithmetic mean across images of a **PQ-like** score:
`sum(matched IoU) / (TP + 0.5*FP + 0.5*FN)`. It is not the product of the
image-mean IoU and image-mean F1, and it is not official panoptic quality: instance
masks may overlap. Pairs require IoU >= 0.5 and a one-to-one maximum-cardinality
matching, with maximum total IoU as the secondary assignment objective. Correct
instance count and the exact spatially matched set are reported separately.

All nine operating points are selected on validation before the fixed TEST147
metrics are calculated. The highest image-mean PQ-like value wins; ties within
1e-12 choose the lowest threshold. The grid is 0.05 to 0.95 in 0.01 steps. Native
family candidate floors/caps and NMS remain unchanged. Confidence values are
operating scores, not statistically calibrated correctness probabilities.

`config/validation_protocol.json` is a sanitised methodological extract. Its
`private_original_protocol_sha256` identifies the frozen private original. The
public extract and private original intentionally have **different bytes and
different hashes**. The file manifest records the public extract's own hash.
The private companion preserves complete protocol, source, QA and cache metadata.

Data access and third-party rights remain as described in the repository README
and `RIGHTS.md`. Publishing these derived arrays grants no new licence to raw
images, annotations, model weights or the capture application.
