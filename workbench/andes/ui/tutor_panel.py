# -*- coding: utf-8 -*-
"""Panel gia sư: lịch sử phản hồi, mức nắm kỹ năng, ô đáp án, nút Kiểm tra/Gợi ý."""

from __future__ import annotations

import html

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import theme

_COLORS = {
    "info": theme.MUTED,
    "correct": theme.CORRECT,
    "error": theme.INCORRECT,
    "hint": theme.WARN,
}


class TutorPanel(QWidget):
    check_requested = pyqtSignal()
    hint_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(330)
        self.setMaximumWidth(460)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 0, 0, 0)
        root.setSpacing(10)

        title = QLabel("GIA SƯ ANDES")
        title.setObjectName("PanelTitle")
        root.addWidget(title)

        subtitle = QLabel("Theo dõi từng bước giải và gợi ý khi em cần.")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.history = QTextBrowser()
        self.history.setMinimumHeight(200)
        root.addWidget(self.history, 1)

        skills_card = QFrame()
        skills_card.setObjectName("Card")
        skills_layout = QVBoxLayout(skills_card)
        skills_layout.setContentsMargins(12, 10, 12, 10)
        skills_layout.setSpacing(6)
        skills_title = QLabel("Mức nắm kỹ năng")
        skills_title.setObjectName("Muted")
        skills_layout.addWidget(skills_title)
        self._skills_box = QVBoxLayout()
        self._skills_box.setSpacing(6)
        skills_layout.addLayout(self._skills_box)
        root.addWidget(skills_card)

        answer_card = QFrame()
        answer_card.setObjectName("Card")
        answer_layout = QVBoxLayout(answer_card)
        answer_layout.setContentsMargins(12, 10, 12, 12)
        answer_layout.setSpacing(8)

        answer_row = QHBoxLayout()
        self.answer_edit = QLineEdit()
        self.answer_edit.setPlaceholderText("Nhập đáp án số...")
        self.answer_edit.returnPressed.connect(self.check_requested.emit)
        self.unit_label = QLabel("")
        self.unit_label.setObjectName("Muted")
        answer_row.addWidget(self.answer_edit, 1)
        answer_row.addWidget(self.unit_label)
        answer_layout.addLayout(answer_row)

        button_row = QHBoxLayout()
        self.check_button = QPushButton("Kiểm tra")
        self.check_button.setObjectName("Primary")
        self.check_button.clicked.connect(self.check_requested.emit)
        self.hint_button = QPushButton("Gợi ý")
        self.hint_button.setObjectName("Ghost")
        self.hint_button.clicked.connect(self.hint_requested.emit)
        button_row.addWidget(self.check_button, 1)
        button_row.addWidget(self.hint_button)
        answer_layout.addLayout(button_row)

        root.addWidget(answer_card)

    # -- nội dung --------------------------------------------------------
    def say(self, text: str, kind: str = "info") -> None:
        color = _COLORS.get(kind, theme.MUTED)
        body = html.escape(text).replace("\n", "<br/>")
        self.history.append(
            f'<div style="margin:7px 0;color:{color};">{body}</div>'
        )
        bar = self.history.verticalScrollBar()
        bar.setValue(bar.maximum())

    def reset(self, unit: str, intro: str = "") -> None:
        self.history.clear()
        self.answer_edit.clear()
        self.unit_label.setText(unit)
        self._clear_skills()
        if intro:
            self.say(intro, "info")

    def answer_text(self) -> str:
        return self.answer_edit.text()

    def focus_answer(self) -> None:
        self.answer_edit.setFocus()

    # -- kỹ năng ---------------------------------------------------------
    def _clear_skills(self) -> None:
        while self._skills_box.count():
            item = self._skills_box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def set_skills(self, skills: dict) -> None:
        self._clear_skills()
        if not skills:
            placeholder = QLabel("Chưa có dữ liệu — hãy làm bài.")
            placeholder.setObjectName("Muted")
            self._skills_box.addWidget(placeholder)
            return
        for name, value in skills.items():
            pct = max(0, min(100, int(round(value * 100))))
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            label = QLabel(name)
            label.setObjectName("Muted")
            value_label = QLabel(f"{pct}%")
            value_label.setObjectName("Muted")
            row_layout.addWidget(label, 1)
            row_layout.addWidget(value_label)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(False)
            self._skills_box.addWidget(row)
            self._skills_box.addWidget(bar)