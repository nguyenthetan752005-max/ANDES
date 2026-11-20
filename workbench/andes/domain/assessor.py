# -*- coding: utf-8 -*-
"""Bộ đánh giá (assessor) và mô hình người học kiểu Andes.

Assessor chạy trên `Attempt` (ảnh chụp canvas + đáp án số), hoàn toàn tất định:
- Ưu tiên nhận diện lỗi hiểu sai qua `BuggyRule` để phản hồi đúng chỗ.
- Sau đó kiểm tra lần lượt: vectơ bắt buộc -> phương trình -> đáp án số.
- Mỗi bước có thang gợi ý 3 mức; Hint lấy theo mức hiện tại của bước hỏng.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .model import (
    Attempt,
    Problem,
    equation_matches,
    find_step,
    norm_label,
    vector_matches,
)


@dataclass
class Evaluation:
    correct: bool
    failed_step: Optional[str]
    message: str
    buggy_key: Optional[str] = None


class Assessor:
    """Chấm một lần làm bài và trả về bước hỏng + thông điệp."""

    def evaluate(self, problem: Problem, attempt: Attempt) -> Evaluation:
        # 1) Hiểu sai phổ biến được ưu tiên (phản hồi nhắm đúng lỗi).
        for rule in problem.buggy:
            try:
                if rule.match(attempt, problem):
                    return Evaluation(
                        correct=False,
                        failed_step=rule.step_key,
                        message=rule.message,
                        buggy_key=rule.key,
                    )
            except Exception:
                continue

        # 2) Vectơ bắt buộc.
        for spec in problem.vector_specs:
            if spec.optional:
                continue
            if not any(vector_matches(v, spec) for v in attempt.vectors):
                return Evaluation(
                    correct=False,
                    failed_step="vectors",
                    message=(
                        f"Biểu diễn lực chưa đúng: cần vectơ '{spec.label}'"
                        + (f" hướng {spec.direction}" if spec.direction != "any" else "")
                        + "."
                    ),
                )

        # 3) Phương trình.
        expected_eq = bool(problem.equation_patterns) or problem.equation_checker is not None
        if expected_eq:
            if not attempt.equations:
                return Evaluation(
                    correct=False,
                    failed_step="equation",
                    message="Chưa có phương trình nào trên bảng.",
                )
            if not any(equation_matches(eq, problem) for eq in attempt.equations):
                return Evaluation(
                    correct=False,
                    failed_step="equation",
                    message="Phương trình chưa đúng.",
                )

        # 4) Đáp án số.
        if attempt.answer is None:
            return Evaluation(
                correct=False,
                failed_step="answer",
                message="Chưa nhập đáp án số.",
            )
        if abs(attempt.answer - problem.answer) > problem.tolerance:
            return Evaluation(
                correct=False,
                failed_step="answer",
                message="Đáp án chưa đúng.",
            )

        return Evaluation(
            correct=True,
            failed_step=None,
            message=f"Chính xác! {problem.target} = {problem.answer:g} {problem.unit}.",
        )

    def hint(self, problem: Problem, step_key: Optional[str], level: int) -> str:
        """Gợi ý mức `level` (0..2) cho bước `step_key`."""
        step = find_step(problem, step_key)
        if step is None:
            step = problem.steps[-1] if problem.steps else None
        if step is None:
            return ""
        idx = max(0, min(int(level), len(step.hints) - 1))
        return step.hints[idx]

    def wrong_vector_labels(self, problem: Problem, attempt: Attempt) -> set:
        """Nhãn các vectơ có tên trùng yêu cầu nhưng sai chiều/độ lớn."""
        out = set()
        for spec in problem.vector_specs:
            if spec.optional:
                continue
            same = [v for v in attempt.vectors if norm_label(v.label) == norm_label(spec.label)]
            if same and not any(vector_matches(v, spec) for v in same):
                out.add(norm_label(spec.label))
        return out


class StudentModel:
    """Mô hình người học đơn giản: đếm đúng/sai/số lần gợi ý theo kỹ năng."""

    def __init__(self) -> None:
        self._stats: Dict[str, list] = {}

    def _row(self, skill: str) -> list:
        return self._stats.setdefault(skill, [0, 0, 0])  # attempts, correct, hints

    def record(self, skill: str, correct: bool) -> None:
        row = self._row(skill)
        row[0] += 1
        if correct:
            row[1] += 1

    def record_hint(self, skill: str) -> None:
        self._row(skill)[2] += 1

    def mastery(self, skill: str) -> float:
        attempts, correct, _hints = self._row(skill)
        return (correct + 1.0) / (attempts + 2.0)  # làm mượt Laplace

    def snapshot(self) -> Dict[str, float]:
        return {skill: self.mastery(skill) for skill in self._stats}

    def reset(self) -> None:
        self._stats.clear()