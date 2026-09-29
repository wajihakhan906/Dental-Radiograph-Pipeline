# Results

`Code/run.py` writes, for each radiograph:

- `<image>_report.md`: tooth-by-tooth findings (FDI notation), each sentence citing its detection (`[F1]`),
  a recommendation, and an evidence table. Sentences without valid evidence are marked ⚠️.
- `<image>_findings.png`: the radiograph with every detection drawn as `F# #tooth label`
  (red = pathology, blue = treatment).

Example report from the template backend with two detections (illustrative, not a patient result):

```markdown
## Panoramic radiograph report

- Tooth 36: caries (confidence 88%) [F1].
- Tooth 46: periapical lesion (confidence 70%) [F2].

**Recommendation:** Clinical examination of the listed teeth.

| ID | Tooth | Finding | Confidence |
|---|---|---|---|
| F1 | 36 | caries | 0.88 |
| F2 | 46 | periapical lesion | 0.70 |
```
