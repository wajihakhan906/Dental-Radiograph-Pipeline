# Datasets

No patient images are stored in this repository. Public panoramic-radiograph datasets:

| Dataset | Content | Link |
|---|---|---|
| **DENTEX** (MICCAI 2023) | panoramic X-rays with hierarchical labels: quadrant → FDI tooth → diagnosis (caries, deep caries, periapical lesion, impacted) | https://dentex.grand-challenge.org/ |
| **Tufts Dental Database** | 1,000 panoramic X-rays, tooth masks, abnormality annotations, expert gaze maps | http://tdd.ece.tufts.edu/ |

Expected YOLO layout:
```
Dataset/dentex/
├── images/{train,val}/*.png
├── labels/{train,val}/*.txt      # class cx cy w h  (normalised)
└── dentex.yaml                   # names: [caries, deep caries, periapical lesion, impacted tooth, ...]
```
