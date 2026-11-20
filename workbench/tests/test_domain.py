# -*- coding: utf-8 -*-
"""Test miền tri thức/đánh giá của ANDES (không cần Qt)."""
from andes.domain.assessor import Assessor, StudentModel
from andes.domain.model import Attempt, VectorData, norm_text
from andes.domain.problems import FMA, INCLINE

ASSESSOR = Assessor()


def _fma(vectors=None, equations=None, answer=None) -> Attempt:
    if vectors is None:
        vectors = (VectorData("F", 100.0, 0.0),)
    if equations is None:
        equations = ("F = m * a",)
    return Attempt(tuple(vectors), tuple(equations), answer)


def test_fma_correct():
    ev = ASSESSOR.evaluate(FMA, _fma(answer=5.0))
    assert ev.correct
    assert ev.failed_step is None


def test_fma_buggy_multiply():
    ev = ASSESSOR.evaluate(FMA, _fma(answer=20.0))
    assert not ev.correct
    assert ev.buggy_key == "multiply"
    assert ev.failed_step == "answer"


def test_fma_buggy_subtract_and_invert():
    assert ASSESSOR.evaluate(FMA, _fma(answer=8.0)).buggy_key == "subtract"
    assert ASSESSOR.evaluate(FMA, _fma(answer=0.2)).buggy_key == "invert"


def test_fma_missing_vector():
    ev = ASSESSOR.evaluate(FMA, _fma(vectors=(), answer=5.0))
    assert not ev.correct
    assert ev.failed_step == "vectors"


def test_fma_wrong_direction_is_buggy():
    ev = ASSESSOR.evaluate(
        FMA, _fma(vectors=(VectorData("F", -100.0, 0.0),), answer=5.0)
    )
    assert ev.buggy_key == "vector_left"
    assert ev.failed_step == "vectors"


def test_fma_wrong_equation_plain():
    ev = ASSESSOR.evaluate(FMA, _fma(equations=("F = m",), answer=5.0))
    assert not ev.correct
    assert ev.failed_step == "equation"
    assert ev.buggy_key is None


def test_fma_buggy_equation_add():
    ev = ASSESSOR.evaluate(FMA, _fma(equations=("F = m + a",), answer=5.0))
    assert ev.buggy_key == "eq_add"


def test_fma_wrong_answer():
    ev = ASSESSOR.evaluate(FMA, _fma(answer=4.0))
    assert not ev.correct
    assert ev.failed_step == "answer"


def test_hint_ladder_caps_at_three():
    assert "lực nào" in ASSESSOR.hint(FMA, "vectors", 0)
    assert "Vectơ" in ASSESSOR.hint(FMA, "vectors", 1)
    bottom = ASSESSOR.hint(FMA, "vectors", 2)
    assert ASSESSOR.hint(FMA, "vectors", 99) == bottom


def test_norm_text_handles_greek_and_spaces():
    assert norm_text("F = m × a") == "f=m*a"
    assert norm_text("a = g·sinα") == "a=g*sinalpha"


def test_incline_correct():
    ev = ASSESSOR.evaluate(
        INCLINE, Attempt(equations=("a = g * sin(alpha)",), answer=4.9)
    )
    assert ev.correct


def test_incline_cos_bug():
    ev = ASSESSOR.evaluate(
        INCLINE, Attempt(equations=("a = g * cos(alpha)",), answer=8.49)
    )
    assert not ev.correct
    assert ev.buggy_key == "use_cos"


def test_student_model_mastery_moves_up():
    model = StudentModel()
    before = model.mastery("Tính gia tốc")
    model.record("Tính gia tốc", True)
    after = model.mastery("Tính gia tốc")
    assert after > before