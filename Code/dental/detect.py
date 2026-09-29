"""YOLOv8 detection (and optional YOLOv8-seg masks) for dental radiographs."""
from pathlib import Path

from .findings import Finding
from .teeth import FDI, assign_teeth


class DentalDetector:
    """`weights` is a YOLOv8 detect or segment model whose classes include pathologies/treatments and,
    optionally, FDI tooth numbers ("11" ... "48")."""

    def __init__(self, weights, conf=0.25):
        from ultralytics import YOLO

        if not Path(weights).exists():
            raise FileNotFoundError(f"weights not found: {weights}")
        self.model, self.conf = YOLO(weights), conf

    def __call__(self, image):
        res = self.model.predict(image, conf=self.conf, verbose=False)[0]
        masks = res.masks.data.cpu().numpy() if getattr(res, "masks", None) is not None else None
        teeth, findings = {}, []
        for i, (box, c, k) in enumerate(zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist(), res.boxes.cls.tolist())):
            name = res.names[int(k)]
            if FDI.match(name):
                teeth[name] = tuple(box)
                continue
            f = Finding(id=f"F{len(findings) + 1}", label=name, confidence=float(c), bbox=tuple(box))
            if masks is not None:
                f.mask_area_px = int(masks[i].sum())
            findings.append(f)
        h, w = image.shape[:2]
        return assign_teeth(findings, teeth, w, h)
