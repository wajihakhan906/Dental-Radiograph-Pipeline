"""Grounded dental report generation with LLaMA 3 (via Ollama) and citation checking."""
import json
import re
import urllib.request
from dataclasses import dataclass, field
from typing import List

CITATION = re.compile(r"\[(F\d+)\]")

REPORT_PROMPT = """You are a dental radiology assistant. Write a concise report for a panoramic radiograph using ONLY
the detections below. Group by tooth (FDI notation). End EVERY sentence with the detection ID(s) it is based on in
square brackets, e.g. "Tooth 36 shows deep caries approaching the pulp [F2]." Do not add findings that are not
listed. Finish with a line starting "RECOMMENDATION:".

Detections:
{table}
"""

QA_PROMPT = """Answer the clinician's question about this radiograph using ONLY the detections below.
Cite detection IDs in square brackets. If the detections do not answer the question, say so.

Detections:
{table}

Question: {question}
Answer:"""


def table(findings):
    if not findings:
        return "(none)"
    return "\n".join(f"{f.id}: {f.label} on tooth {f.tooth}, confidence {f.confidence:.2f}" for f in findings)


class Llama3:
    def __init__(self, model="llama3", host="http://localhost:11434"):
        self.model, self.host = model, host

    def __call__(self, prompt):
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}})
        req = urllib.request.Request(f"{self.host}/api/generate", body.encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"]


class TemplateLLM:
    """Offline fallback: deterministic sentences, one per detection."""

    def __call__(self, prompt):
        rows = re.findall(r"^(F\d+): (.+?) on tooth (\S+), confidence ([\d.]+)", prompt, re.M)
        if "Question:" in prompt:
            q = prompt.rsplit("Question:", 1)[1].lower()
            hits = [r for r in rows if r[2] in q or r[1] in q]
            if not hits:
                return "The automated detections do not answer this question."
            return " ".join(f"Tooth {t} has {lab} (confidence {float(c):.0%}) [{fid}]." for fid, lab, t, c in hits)
        if not rows:
            return "No pathology detected by the automated system.\nRECOMMENDATION: Routine review."
        lines = [f"Tooth {t}: {lab} (confidence {float(c):.0%}) [{fid}]." for fid, lab, t, c in rows]
        return "\n".join(lines + ["RECOMMENDATION: Clinical examination of the listed teeth."])


@dataclass
class Sentence:
    text: str
    ids: List[str]
    grounded: bool


@dataclass
class DentalReport:
    findings: list
    sentences: List[Sentence] = field(default_factory=list)
    recommendation: str = ""

    def to_markdown(self):
        out = ["## Panoramic radiograph report", ""]
        out += [f"- {s.text}" + ("" if s.grounded else " ⚠️ *(no image evidence; verify)*") for s in self.sentences]
        if self.recommendation:
            out += ["", f"**Recommendation:** {self.recommendation}"]
        out += ["", "| ID | Tooth | Finding | Confidence |", "|---|---|---|---|"]
        out += [f"| {f.id} | {f.tooth} | {f.label} | {f.confidence:.2f} |" for f in self.findings]
        return "\n".join(out)


def verify(text, findings):
    valid = {f.id for f in findings}
    sentences, rec = [], ""
    for s in (x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()):
        if s.upper().startswith("RECOMMENDATION:"):
            rec = s.split(":", 1)[1].strip()
            continue
        ids = CITATION.findall(s)
        ok = (bool(ids) and all(i in valid for i in ids)) or (not findings and "no pathology" in s.lower())
        sentences.append(Sentence(s, [i for i in ids if i in valid], ok))
    return sentences, rec


def generate_report(findings, llm):
    sentences, rec = verify(llm(REPORT_PROMPT.format(table=table(findings))), findings)
    return DentalReport(findings, sentences, rec)


def answer_question(question, findings, llm):
    text = llm(QA_PROMPT.format(table=table(findings), question=question))
    return text, verify(text, findings)[0]
