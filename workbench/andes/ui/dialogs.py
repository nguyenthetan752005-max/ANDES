# -*- coding: utf-8 -*-
"""Hộp thoại: Tuỳ chọn, danh mục tri thức (Physics), giới thiệu."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from . import theme
from .options import AppOptions


class OptionsDialog(QDialog):
    def __init__(self, options: AppOptions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tuỳ chọn")
        self.setModal(True)
        self.resize(380, 300)

        self._correct = options.color_correct
        self._incorrect = options.color_incorrect

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.snap = QSpinBox()
        self.snap.setRange(0, 90)
        self.snap.setSingleStep(5)
        self.snap.setSuffix("°")
        self.snap.setValue(int(options.angle_snap))
        self.snap.setSpecialValueText("Tắt")
        form.addRow("Bắt góc (snap):", self.snap)

        self.grid = QCheckBox("Hiện lưới nền")
        self.grid.setChecked(bool(options.show_grid))
        form.addRow("", self.grid)

        self.timer = QCheckBox("Hiện đồng hồ làm bài")
        self.timer.setChecked(bool(options.show_timer))
        form.addRow("", self.timer)

        self.font_size = QSpinBox()
        self.font_size.setRange(10, 20)
        self.font_size.setValue(int(options.font_size))
        form.addRow("Cỡ chữ gợi ý:", self.font_size)

        self.correct_button = QPushButton()
        self.correct_button.clicked.connect(lambda: self._pick("correct"))
        self._paint_color_button(self.correct_button, self._correct)
        form.addRow("Màu đúng:", self.correct_button)

        self.incorrect_button = QPushButton()
        self.incorrect_button.clicked.connect(lambda: self._pick("incorrect"))
        self._paint_color_button(self.incorrect_button, self._incorrect)
        form.addRow("Màu sai:", self.incorrect_button)

        layout.addLayout(form)
        layout.addStretch(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _pick(self, which: str) -> None:
        current = self._correct if which == "correct" else self._incorrect
        color = QColorDialog.getColor(QColor(current), self, "Chọn màu")
        if not color.isValid():
            return
        if which == "correct":
            self._correct = color.name()
            self._paint_color_button(self.correct_button, self._correct)
        else:
            self._incorrect = color.name()
            self._paint_color_button(self.incorrect_button, self._incorrect)

    @staticmethod
    def _paint_color_button(button: QPushButton, color: str) -> None:
        c = QColor(color)
        text = "#FFFFFF" if c.lightness() < 140 else "#1F2A44"
        button.setText(color.upper())
        button.setStyleSheet(
            f"QPushButton {{ background: {color}; color: {text}; "
            f"border: 1px solid {theme.BORDER}; border-radius: 8px; padding: 6px 10px; }}"
        )

    def result_options(self) -> AppOptions:
        return AppOptions(
            angle_snap=int(self.snap.value()),
            show_grid=self.grid.isChecked(),
            show_timer=self.timer.isChecked(),
            font_size=int(self.font_size.value()),
            color_correct=self._correct,
            color_incorrect=self._incorrect,
        )


class CatalogDialog(QDialog):
    def __init__(self, title: str, headers, rows, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(720, 440)

        layout = QVBoxLayout(self)
        hint = QLabel("Tham khảo nhanh — không thay đổi bài đang làm.")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(list(headers))
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                table.setItem(r, c, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)