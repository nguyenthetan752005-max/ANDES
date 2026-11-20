# -*- coding: utf-8 -*-
"""Hai bài mẫu cho prototype: Định luật II Newton và mặt phẳng nghiêng.

Mỗi bài gồm: dữ kiện, yêu cầu vectơ, mẫu phương trình, thang gợi ý 3 mức và
các luật "hiểu sai" (buggy rules) để phản hồi nhắm đúng lỗi.
"""
from __future__ import annotations

from .model import (
    Attempt,
    BuggyRule,
    Given,
    Problem,
    Step,
    VectorSpec,
    norm_label,
    norm_text,
)


# --------------------------------------------------------------------------
# Hàm so khớp dùng cho buggy rules
# --------------------------------------------------------------------------

def _ans_near(att: Attempt, value: float, tol: float) -> bool:
    return att.answer is not None and abs(att.answer - value) <= tol


def _eq_has(att: Attempt, needle: str) -> bool:
    return any(needle in norm_text(eq) for eq in att.equations)


def _only_wrong_way(att: Attempt, label: str) -> bool:
    vs = [v for v in att.vectors if norm_label(v.label) == norm_label(label)]
    if not vs:
        return False
    has_right = any(v.dx > 5 for v in vs)
    return (not has_right) and all(v.dx < -5 for v in vs)


def _incline_equation_ok(text: str) -> bool:
    n = norm_text(text)
    if "sin" not in n or "=" not in n or "g" not in n:
        return False
    return ("a=" in n) or ("=a" in n)


# --------------------------------------------------------------------------
# Bài 1 — Định luật II Newton
# --------------------------------------------------------------------------

FMA = Problem(
    id="fma",
    title="Định luật II Newton",
    statement=(
        "Một vật khối lượng m = 2 kg chịu lực kéo F = 10 N theo phương ngang. "
        "Bỏ qua ma sát. Hãy biểu diễn lực kéo, viết phương trình và tính gia tốc a."
    ),
    givens=(
        Given("m", 2.0, "kg", "khối lượng"),
        Given("F", 10.0, "N", "lực kéo theo phương ngang"),
    ),
    target="a",
    unit="m/s²",
    answer=5.0,
    tolerance=0.05,
    steps=(
        Step(
            key="vectors",
            title="Biểu diễn lực",
            hints=(
                "Vật đang chịu lực nào theo phương chuyển động?",
                "Dùng công cụ Vectơ, vẽ mũi tên từ vật hướng sang phải và đặt nhãn 'F'.",
                "Vẽ một vectơ nhãn F, chiều sang phải, độ dài tượng trưng cho 10 N.",
            ),
        ),
        Step(
            key="equation",
            title="Viết phương trình",
            hints=(
                "Định luật II Newton có dạng thế nào?",
                "F = m·a, suy ra a = F/m.",
                "Nhập phương trình 'F = m * a' (hoặc 'a = F / m').",
            ),
        ),
        Step(
            key="answer",
            title="Tính gia tốc",
            hints=(
                "Thay các số đã cho vào công thức vừa viết.",
                "a = F/m = 10/2.",
                "Đáp án là 5 m/s².",
            ),
        ),
    ),
    vector_specs=(
        VectorSpec(label="F", direction="right", min_mag=30.0),
    ),
    equation_patterns=(
        "f=m*a",
        "f=ma",
        "a=f/m",
        "f/m=a",
        "m*a=f",
        "ma=f",
    ),
    buggy=(
        BuggyRule(
            key="multiply",
            step_key="answer",
            message=(
                "Có vẻ em đã nhân F với m (ra 20). Định luật II là F = m·a, "
                "nên phải chia: a = F/m."
            ),
            match=lambda att, pr: _ans_near(att, 20.0, 0.6),
        ),
        BuggyRule(
            key="subtract",
            step_key="answer",
            message=(
                "Trừ F cho m (ra 8) không phải công thức. Hãy dùng a = F/m."
            ),
            match=lambda att, pr: _ans_near(att, 8.0, 0.6),
        ),
        BuggyRule(
            key="invert",
            step_key="answer",
            message=(
                "Em chia ngược thành m/F (ra 0.2). Đúng phải là F/m."
            ),
            match=lambda att, pr: _ans_near(att, 0.2, 0.05),
        ),
        BuggyRule(
            key="eq_add",
            step_key="equation",
            message=(
                "Phương trình đúng là F = m·a, không phải F = m + a."
            ),
            match=lambda att, pr: _eq_has(att, "f=m+a"),
        ),
        BuggyRule(
            key="vector_left",
            step_key="vectors",
            message=(
                "Lực F đang vẽ ngược chiều (sang trái), trong khi đề cho lực kéo "
                "sang phải."
            ),
            match=lambda att, pr: _only_wrong_way(att, "F"),
        ),
    ),
    intro="Bài mở đầu: áp dụng định luật II Newton khi bỏ qua ma sát.",
)


# --------------------------------------------------------------------------
# Bài 2 — Mặt phẳng nghiêng (không ma sát)
# --------------------------------------------------------------------------

INCLINE = Problem(
    id="incline",
    title="Mặt phẳng nghiêng",
    statement=(
        "Một vật khối lượng m = 2 kg trượt không ma sát trên mặt phẳng nghiêng "
        "góc α = 30°. Lấy g = 9.8 m/s². Viết phương trình và tính gia tốc a dọc "
        "theo mặt phẳng."
    ),
    givens=(
        Given("m", 2.0, "kg", "khối lượng"),
        Given("alpha", 30.0, "°", "góc nghiêng"),
        Given("g", 9.8, "m/s²", "gia tốc trọng trường"),
    ),
    target="a",
    unit="m/s²",
    answer=4.9,
    tolerance=0.05,
    steps=(
        Step(
            key="equation",
            title="Viết phương trình",
            hints=(
                "Thành phần lực kéo vật xuống dọc mặt phẳng là bao nhiêu?",
                "F_dọc = m·g·sinα, nên a = g·sinα.",
                "Nhập 'a = g * sin(alpha)'.",
            ),
        ),
        Step(
            key="answer",
            title="Tính gia tốc",
            hints=(
                "Thay α = 30° vào công thức.",
                "a = 9.8 · sin30° = 9.8 · 0.5.",
                "Đáp án ≈ 4.9 m/s².",
            ),
        ),
    ),
    vector_specs=(),
    equation_checker=_incline_equation_ok,
    buggy=(
        BuggyRule(
            key="use_cos",
            step_key="answer",
            message=(
                "Dùng cos thay vì sin (ra ≈ 8.49). Thành phần dọc mặt phẳng dùng sinα."
            ),
            match=lambda att, pr: _ans_near(att, 9.8 * 0.8660254, 0.4),
        ),
        BuggyRule(
            key="forgot_sin",
            step_key="answer",
            message=(
                "Em quên nhân với sinα (ra 9.8). Gia tốc là a = g·sinα."
            ),
            match=lambda att, pr: _ans_near(att, 9.8, 0.3),
        ),
        BuggyRule(
            key="eq_cos",
            step_key="equation",
            message="Phương trình dùng cos là sai hướng; phải là a = g·sinα.",
            match=lambda att, pr: _eq_has(att, "cos"),
        ),
    ),
    intro="Bài vận dụng: phân tích lực trên mặt phẳng nghiêng.",
)


PROBLEMS = (FMA, INCLINE)


def get_problem(problem_id: str) -> Problem:
    for problem in PROBLEMS:
        if problem.id == problem_id:
            return problem
    return PROBLEMS[0]