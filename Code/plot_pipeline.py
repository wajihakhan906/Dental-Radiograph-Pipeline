"""Draws the dental pipeline to ../Figures/pipeline.png."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

MAIN = [
    ("Panoramic\nradiograph", "#8172B2"),
    ("YOLOv8\ndetection", "#4C72B0"),
    ("Segmentation\n+ FDI numbering", "#55A868"),
    ("LLaMA 3\ngrounded report", "#C44E52"),
    ("Citation\nverification", "#DD8452"),
]


def box(ax, x, y, text, color, w=1.9, h=0.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=color, ec="black"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", weight="bold", fontsize=9)


def main():
    fig, ax = plt.subplots(figsize=(12.5, 4))
    step = 2.4
    for i, (t, c) in enumerate(MAIN):
        box(ax, i * step, 1.6, t, c)
        if i < len(MAIN) - 1:
            ax.annotate("", (i * step + step - 0.05, 2.05), (i * step + 1.95, 2.05), arrowprops=dict(arrowstyle="->", lw=1.5))
    box(ax, 1 * step, 0, "Clinician voice\n(Faster Whisper)", "#64B5CD")
    box(ax, 3 * step, 0, "Grounded Q&A\n(cites F1…Fn)", "#C44E52")
    box(ax, 4 * step, 0, "Gradio GUI\noverlay + report", "#937860")
    ax.annotate("", (3 * step - 0.05, 0.45), (1 * step + 1.95, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", (3 * step + 0.95, 0.95), (3 * step + 0.95, 1.55), arrowprops=dict(arrowstyle="->", lw=1.2, ls="--"))
    ax.annotate("", (4 * step - 0.05, 0.45), (3 * step + 1.95, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", (4 * step + 0.95, 0.95), (4 * step + 0.95, 1.55), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(3 * step + 1.05, 1.25, "findings", fontsize=8, style="italic")
    ax.set_xlim(-0.2, 5 * step - 0.3); ax.set_ylim(-0.2, 2.7); ax.axis("off")
    fig.tight_layout(); fig.savefig("../Figures/pipeline.png", dpi=200)


if __name__ == "__main__":
    main()
