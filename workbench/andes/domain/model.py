# -*- coding: utf-8 -*-
"""Mô hình miền cho ANDES.

Không import Qt ở đây: toàn bộ logic bài học/đánh giá chạy được headless và
unit-test độc lập với giao diện.

Quy ước toạ độ trên canvas: gốc ở góc trên-trái, y hướng XUỐNG (giống Qt).
Vì vậy "up" = dy < 0, "down" = dy > 0. Các bài hiện tại chỉ cần trái/phải.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Tuple


@dataclass(frozen=True)
class Given:
    """Một dữ kiện của đề bài, ví dụ m = 2 kg."""

    name: str
    value: float
    unit: str = ""
    desc: str = ""

    def as_text(self) -> str:
        unit = f" {self.unit}" if self.unit else ""
        return f"{self.name} = {self.value:g}{unit}".strip()


@dataclass(frozen=True)
class VectorData:
    """Vectơ đã vẽ trên canvas (toạ độ tương đối, đơn vị pixel)."""

    label: str
    dx: float
    dy: float

    @property
    def magnitude(self) -> float:
        return math.hypot(self.dx, self.dy)

    @property
    def angle_deg(self) -> float:
        return math.degrees(math.atan2(self.dy, self.dx))


@dataclass(frozen=True)
class Attempt:
    """Ảnh chụp trạng thái làm bài tại thời điểm bấm Kiểm tra."""

    vectors: Tuple[VectorData, ...] = ()
    equations: Tuple[str, ...] = ()
    answer: Optional[float] = None


@dataclass(frozen=True)
class VectorSpec:
    """Yêu cầu cho một vectơ lực bắt buộc.

    direction: any | right | left | up | down (theo quy ước canvas ở trên).
    """

    label: str
    direction: str = "any"
    min_mag: float = 0.0
    max_mag: float = 1e18
    optional: bool = False


@dataclass(frozen=True)
class Step:
    """Một bước giải, kèm thang gợi ý 3 mức (nhắc → nguyên lý → nói thẳng)."""

    key: str
    title: str
    hints: Tuple[str, str, str]


@dataclass(frozen=True)
class BuggyRule:
    """Luật mô tả một hiểu sai phổ biến -> phản hồi nhắm đúng lỗi."""

    key: str
    step_key: str
    message: str
    match: Callable[[Attempt, "Problem"], bool]


@dataclass
class Problem:
    id: str
    title: str
    statement: str
    givens: Tuple[Given, ...]
    target: str
    unit: str
    answer: float
    tolerance: float
    steps: Tuple[Step, ...]
    vector_specs: Tuple[VectorSpec, ...] = ()
    equation_patterns: Tuple[str, ...] = ()
    equation_checker: Optional[Callable[[str], bool]] = None
    buggy: Tuple[BuggyRule, ...] = ()
    intro: str = ""


# --------------------------------------------------------------------------
# Chuẩn hoá & so khớp
# --------------------------------------------------------------------------

def norm_label(text: str) -> str:
    """Chuẩn hoá nhãn vectơ: 'F ', 'f_1' -> 'f'/'f1'."""
    return (text or "").strip().lower().replace(" ", "").replace("_", "")


def norm_text(text: str) -> str:
    """Chuẩn hoá biểu thức để so khớp: bỏ khoảng trắng, đồng nhất ký hiệu."""
    s = (text or "").strip().lower()
    s = (
        s.replace("α", "alpha")
        .replace("β", "beta")
        .replace("θ", "theta")
        .replace("×", "*")
        .replace("·", "*")
        .replace("⋅", "*")
        .replace("−", "-")
        .replace("–", "-")
        .replace(" ", "")
    )
    return s


def vector_matches(vec: VectorData, spec: VectorSpec) -> bool:
    """Vectơ đã vẽ có thoả yêu cầu (nhãn + chiều + độ lớn) không."""
    if norm_label(vec.label) != norm_label(spec.label):
        return False
    m = vec.magnitude
    if not (spec.min_mag <= m <= spec.max_mag):
        return False
    d = (spec.direction or "any").lower()
    if d == "any":
        return True
    if d == "right":
        return vec.dx > 0 and abs(vec.dx) >= abs(vec.dy)
    if d == "left":
        return vec.dx < 0 and abs(vec.dx) >= abs(vec.dy)
    if d == "up":
        return vec.dy < 0 and abs(vec.dy) > abs(vec.dx)
    if d == "down":
        return vec.dy > 0 and abs(vec.dy) > abs(vec.dx)
    return True


def equation_matches(text: str, problem: Problem) -> bool:
    """Phương trình có được chấp nhận không."""
    if problem.equation_checker is not None:
        try:
            return bool(problem.equation_checker(text))
        except Exception:
            return False
    return norm_text(text) in set(problem.equation_patterns)


def find_step(problem: Problem, key: Optional[str]) -> Optional[Step]:
    if not key:
        return None
    for step in problem.steps:
        if step.key == key:
            return step
    return None