# Model weights

Put the trained YOLOv8 model here (not tracked in git), e.g. `dental_yolov8.pt`.

Class names should include the pathologies/treatments to report (`caries`, `deep caries`, `periapical lesion`,
`impacted tooth`, `filling`, `crown`, `root canal treatment`, `implant`, ...) and, optionally, FDI tooth
numbers `11`–`48`. When tooth boxes are present, each finding is assigned to the tooth it overlaps most;
otherwise the tooth number is estimated from its position on the panoramic image.

Train with Ultralytics:
```bash
yolo detect train data=../Dataset/dentex/dentex.yaml model=yolov8m.pt imgsz=1024 epochs=150
# or instance masks:
yolo segment train data=... model=yolov8m-seg.pt imgsz=1024
```
