"""Gradio GUI: upload a radiograph -> overlay + grounded report; ask questions by text or voice.

    python app.py --weights weights/dental_yolov8.pt            # LLaMA 3 via Ollama
    python app.py --weights weights/dental_yolov8.pt --llm template
"""
import argparse

import numpy as np

from dental.detect import DentalDetector
from dental.overlay import draw
from dental.report import Llama3, TemplateLLM, answer_question, generate_report


def build(detector, llm, transcriber=None):
    import gradio as gr

    def analyse(image):
        findings = detector(np.asarray(image))
        report = generate_report(findings, llm)
        return draw(image, findings), report.to_markdown(), findings

    def ask(question, audio, findings):
        if audio and transcriber is not None:
            question = transcriber(audio)
        if not question:
            return "", "Ask a question by typing or recording."
        text, sentences = answer_question(question, findings or [], llm)
        flagged = [s.text for s in sentences if not s.grounded]
        note = f"\n\n⚠️ Not linked to image evidence: {flagged}" if flagged else ""
        return question, text + note

    with gr.Blocks(title="Dental Radiograph Assistant") as demo:
        state = gr.State([])
        gr.Markdown("# Dental Radiograph Assistant\nDetection → segmentation → grounded report. Research use only.")
        with gr.Row():
            inp = gr.Image(type="numpy", label="Panoramic radiograph")
            out = gr.Image(label="Findings")
        report = gr.Markdown()
        gr.Button("Analyse").click(analyse, inp, [out, report, state])
        with gr.Row():
            q = gr.Textbox(label="Question (e.g. 'Is there caries on tooth 36?')")
            mic = gr.Audio(sources=["microphone"], type="filepath", label="…or ask by voice")
        heard, ans = gr.Textbox(label="Heard"), gr.Markdown()
        gr.Button("Ask").click(ask, [q, mic, state], [heard, ans])
    return demo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--llm", default="llama3", help="Ollama model name, or 'template'")
    ap.add_argument("--whisper", default="base", help="Faster Whisper model size; 'none' disables voice")
    args = ap.parse_args()
    llm = TemplateLLM() if args.llm == "template" else Llama3(args.llm)
    transcriber = None
    if args.whisper != "none":
        from dental.voice import Transcriber

        transcriber = Transcriber(args.whisper)
    build(DentalDetector(args.weights), llm, transcriber).launch()


if __name__ == "__main__":
    main()
