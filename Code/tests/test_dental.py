from dental.findings import Finding
from dental.report import TemplateLLM, answer_question, generate_report, verify
from dental.teeth import assign_teeth, geometric_fdi

W, H = 2000, 1000


def test_quadrants_follow_fdi_on_opg():
    # image-left upper -> patient's upper right (quadrant 1); image-right lower -> quadrant 3
    assert geometric_fdi((400, 200, 480, 300), W, H)[0] == "1"
    assert geometric_fdi((1500, 200, 1580, 300), W, H)[0] == "2"
    assert geometric_fdi((1500, 600, 1580, 700), W, H)[0] == "3"
    assert geometric_fdi((400, 600, 480, 700), W, H)[0] == "4"
    assert geometric_fdi((975, 200, 995, 300), W, H) == "11"    # just image-left of the midline -> central incisor


def test_detected_tooth_boxes_take_priority():
    f = [Finding("F1", "caries", 0.9, (1300, 600, 1340, 640))]
    assign_teeth(f, {"36": (1280, 580, 1380, 760)}, W, H)
    assert f[0].tooth == "36"


def test_report_is_fully_grounded():
    f = [Finding("F1", "caries", 0.88, (0, 0, 1, 1), "36"), Finding("F2", "periapical lesion", 0.7, (0, 0, 1, 1), "46")]
    r = generate_report(f, TemplateLLM())
    assert all(s.grounded for s in r.sentences) and r.recommendation
    assert "| F2 | 46 | periapical lesion |" in r.to_markdown()


def test_invented_statements_are_flagged():
    f = [Finding("F1", "caries", 0.88, (0, 0, 1, 1), "36")]
    s, _ = verify("Tooth 36 has caries [F1]. Tooth 11 is fractured. Tooth 48 impacted [F7].", f)
    assert [x.grounded for x in s] == [True, False, False]


def test_question_answering_cites_evidence():
    f = [Finding("F1", "caries", 0.88, (0, 0, 1, 1), "36")]
    text, sents = answer_question("Is there caries on tooth 36?", f, TemplateLLM())
    assert "[F1]" in text and all(x.grounded for x in sents)
