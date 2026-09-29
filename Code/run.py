"""Batch CLI: python run.py --weights weights/dental_yolov8.pt --images ../Dataset/test/*.png"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from dental.detect import DentalDetector
from dental.overlay import draw
from dental.report import Llama3, TemplateLLM, generate_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--images", nargs="+", required=True)
    ap.add_argument("--llm", default="llama3")
    ap.add_argument("--out", default="../Results")
    args = ap.parse_args()
    det, llm = DentalDetector(args.weights), TemplateLLM() if args.llm == "template" else Llama3(args.llm)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for p in map(Path, args.images):
        img = np.asarray(Image.open(p).convert("RGB"))
        findings = det(img)
        (out / f"{p.stem}_report.md").write_text(generate_report(findings, llm).to_markdown())
        draw(img, findings).save(out / f"{p.stem}_findings.png")
        print(f"{p.name}: {len(findings)} findings")


if __name__ == "__main__":
    main()
