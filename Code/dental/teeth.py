"""Assigning FDI tooth numbers to findings on a panoramic radiograph (OPG).

On a standard OPG the patient's right is on the image left. Quadrants (FDI):
    1 = upper right (image upper-left)   2 = upper left (image upper-right)
    4 = lower right (image lower-left)   3 = lower left (image lower-right)
If the detector already predicts tooth numbers (e.g. classes "11" ... "48"), those boxes are used and each
finding is attached to the tooth box it overlaps most; otherwise a geometric estimate is used.
"""
import re

FDI = re.compile(r"^[1-4][1-8]$")


def iou_overlap(a, b):
    """Fraction of box `a` covered by box `b`."""
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area = (a[2] - a[0]) * (a[3] - a[1])
    return inter / area if area > 0 else 0.0


def geometric_fdi(bbox, width, height, occlusal_y=None):
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    occlusal_y = occlusal_y if occlusal_y is not None else height / 2
    upper, image_left = cy < occlusal_y, cx < width / 2
    quadrant = {(True, True): 1, (True, False): 2, (False, False): 3, (False, True): 4}[(upper, image_left)]
    # tooth index 1 (central incisor) at the midline to 8 (third molar) at the edge of the dental arch
    arch_half = 0.38 * width
    dist = min(abs(cx - width / 2) / arch_half, 0.999)
    return f"{quadrant}{int(dist * 8) + 1}"


def assign_teeth(findings, tooth_boxes, width, height):
    """tooth_boxes: {fdi: bbox} from the detector (may be empty)."""
    for f in findings:
        if f.tooth:
            continue
        best, score = None, 0.0
        for fdi, box in tooth_boxes.items():
            s = iou_overlap(f.bbox, box)
            if s > score:
                best, score = fdi, s
        f.tooth = best if score >= 0.3 else geometric_fdi(f.bbox, width, height)
    return findings
