import numpy as np
from PIL import Image, ImageDraw

COLORS = {"pathology": (230, 40, 60), "treatment": (40, 140, 230), "other": (250, 200, 30)}


def draw(image, findings):
    img = Image.fromarray(np.asarray(image)).convert("RGB")
    d = ImageDraw.Draw(img)
    for f in findings:
        c = COLORS[f.kind]
        d.rectangle(f.bbox, outline=c, width=3)
        tag = f"{f.id} #{f.tooth} {f.label}"
        x, y = f.bbox[0], max(f.bbox[1] - 14, 0)
        d.rectangle([x, y, x + 7 * len(tag), y + 13], fill=c)
        d.text((x + 2, y), tag, fill=(255, 255, 255))
    return img
