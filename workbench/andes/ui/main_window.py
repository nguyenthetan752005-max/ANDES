# -*- coding: utf-8 -*-
"""Cửa sổ chính: workbench + panel gia sư, menu, toolbar, đồng hồ."""

from __future__ import annotations

import re

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..domain.assessor import Assessor, StudentModel
from ..domain.catalog import rows_for
from ..domain.model import find_step
from ..domain.problems import PROBLEMS, get_problem
from . import theme
from .canvas import CanvasScene, CanvasView, Tool
from .dialogs import CatalogDialog, OptionsDialog
from .options import AppOptions
from .tutor_panel import TutorPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANDES Workbench — Gia sư Vật lý")
        self.resize(1280, 820)

        self.options = AppOptions()
        self.assessor = Assessor()
        self.student = StudentModel()

        self._current = PROBLEMS[0]
        self._last_eval = None
        self._hint_levels: dict = {}
        self._elapsed = 0
        self._problem_actions: dict = {}

        self._build_ui()
        self._build_menus()
        self._build_toolbars()
        self._build_status()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self.tutor.check_requested.connect(self._check)
        self.tutor.hint_requested.connect(self._hint)

        self._load_problem(self._current.id)
        self._apply_timer_option()

    # ------------------------------------------------------------------
    # Dựng giao diện
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.setStyleSheet(theme.QSS)

        self.scene = CanvasScene(self.options)
        self.view = CanvasView(self.scene, self.options)
        self.tutor = TutorPanel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(self.tutor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([900, 360])
        splitter.setChildrenCollapsible(False)

        self.header = QFrame()
        self.header.setObjectName("ProblemHeader")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(6)
        self.title_label = QLabel()
        self.title_label.setObjectName("ProblemTitle")
        self.statement_label = QLabel()
        self.statement_label.setWordWrap(True)
        self.givens_label = QLabel()
        self.givens_label.setObjectName("Muted")
        self.givens_label.setWordWrap(True)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.statement_label)
        header_layout.addWidget(self.givens_label)

        central = QWidget()
        central.setObjectName("Central")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(self.header)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(central)

    def _build_menus(self) -> None:
        bar = self.menuBar()

        problem_menu = bar.addMenu("Bài toán")
        group = QActionGroup(self)
        group.setExclusive(True)
        for problem in PROBLEMS:
            action = QAction(problem.title, self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, pid=problem.id: self._choose_problem(pid)
            )
            group.addAction(action)
            problem_menu.addAction(action)
            self._problem_actions[problem.id] = action

        problem_menu.addSeparator()
        new_action = QAction("Làm mới", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new)
        problem_menu.addAction(new_action)

        quit_action = QAction("Thoát", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        problem_menu.addAction(quit_action)

        edit_menu = bar.addMenu("Sửa")
        options_action = QAction("Tuỳ chọn...", self)
        options_action.setShortcut("Ctrl+,")
        options_action.triggered.connect(self._options)
        edit_menu.addAction(options_action)

        physics_menu = bar.addMenu("Vật lý")
        for title in ("Principles", "Quantities", "Units", "Constants"):
            action = QAction(title, self)
            action.triggered.connect(
                lambda _checked=False, t=title: self._show_catalog(t)
            )
            physics_menu.addAction(action)

        help_menu = bar.addMenu("Trợ giúp")
        guide_action = QAction("Hướng dẫn nhanh", self)
        guide_action.triggered.connect(self._quick_help)
        help_menu.addAction(guide_action)
        about_action = QAction("Giới thiệu ANDES", self)
        about_action.triggered.connect(self._about)
        help_menu.addAction(about_action)

    def _build_toolbars(self) -> None:
        top = QToolBar("Chính", self)
        top.setObjectName("MainBar")
        top.setMovable(False)
        top.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, top)

        self.act_new = QAction("Làm mới", self)
        self.act_new.triggered.connect(self._new)
        top.addAction(self.act_new)

        self.act_check = QAction("Kiểm tra", self)
        self.act_check.triggered.connect(self._check)
        top.addAction(self.act_check)

        self.act_hint = QAction("Gợi ý", self)
        self.act_hint.triggered.connect(self._hint)
        top.addAction(self.act_hint)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top.addWidget(spacer)

        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("Muted")
        font = QFont("Consolas")
        font.setPointSize(12)
        self.timer_label.setFont(font)
        top.addWidget(self.timer_label)

        tools = QToolBar("Công cụ", self)
        tools.setObjectName("ToolStrip")
        tools.setOrientation(Qt.Orientation.Vertical)
        tools.setMovable(False)
        tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, tools)

        group = QActionGroup(self)
        group.setExclusive(True)
        specs = (
            (Tool.SELECT, "Chọn", "Ctrl+1", "Chọn / di chuyển đối tượng"),
            (Tool.VECTOR, "Vectơ", "Ctrl+2", "Vẽ vectơ lực (kéo–thả)"),
            (Tool.AXES, "Trục", "Ctrl+3", "Đặt hệ trục Oxy"),
            (Tool.EQUATION, "Phương trình", "Ctrl+4", "Thêm phương trình"),
            (Tool.TEXT, "Chữ", "Ctrl+5", "Thêm ghi chú"),
            (Tool.LINE, "Đoạn thẳng", "Ctrl+6", "Vẽ đoạn thẳng"),
            (Tool.RECT, "Hình chữ nhật", "Ctrl+7", "Vẽ hình chữ nhật"),
            (Tool.ELLIPSE, "Ellipse", "Ctrl+8", "Vẽ ellipse"),
        )
        self._tool_actions = {}
        for tool, label, shortcut, tip in specs:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setShortcut(QKeySequence(shortcut))
            action.setToolTip(f"{tip} ({shortcut})")
            action.triggered.connect(
                lambda _checked=False, t=tool: self.view.set_tool(t)
            )
            group.addAction(action)
            tools.addAction(action)
            self._tool_actions[tool] = action
        self._tool_actions[Tool.SELECT].setChecked(True)

    def _build_status(self) -> None:
        status = QStatusBar(self)
        self.setStatusBar(status)
        status.showMessage("Sẵn sàng. Chọn công cụ ở thanh bên trái để bắt đầu.")

    # ------------------------------------------------------------------
    # Bài học
    # ------------------------------------------------------------------
    def _choose_problem(self, problem_id: str) -> None:
        if problem_id == self._current.id:
            return
        self._load_problem(problem_id)

    def _load_problem(self, problem_id: str) -> None:
        problem = get_problem(problem_id)
        self._current = problem
        self._last_eval = None
        self._hint_levels.clear()
        self.student.reset()
        self.view.clear_canvas()
        self._elapsed = 0
        self._update_timer_label()

        self.title_label.setText(problem.title)
        self.statement_label.setText(problem.statement)
        givens = "  •  ".join(g.as_text() for g in problem.givens)
        self.givens_label.setText("Dữ kiện: " + givens)

        intro = problem.intro or "Hãy giải bài theo từng bước."
        self.tutor.reset(problem.unit, intro)
        if givens:
            self.tutor.say("Dữ kiện: " + givens, "info")
        self.tutor.set_skills({step.title: 0.0 for step in problem.steps})

        action = self._problem_actions.get(problem.id)
        if action is not None:
            action.setChecked(True)
        self.statusBar().showMessage(f"Đang làm: {problem.title}")

    def _new(self) -> None:
        if self.scene.items():
            answer = QMessageBox.question(
                self,
                "Làm mới",
                "Xoá toàn bộ bài làm hiện tại?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self._load_problem(self._current.id)
        self.statusBar().showMessage("Đã làm mới bài làm.")

    # ------------------------------------------------------------------
    # Kiểm tra & gợi ý
    # ------------------------------------------------------------------
    def _parse_answer(self):
        raw = self.tutor.answer_text().strip().replace(",", ".")
        if not raw:
            return None
        match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", raw)
        if not match:
            return None
        try:
            return float(match.group(0))
        except ValueError:
            return None

    def _check(self) -> None:
        raw = self.tutor.answer_text().strip()
        answer = self._parse_answer()
        if raw and answer is None:
            self.tutor.say("Đáp án phải là một con số, ví dụ 5 hoặc 4.9.", "error")
            self.statusBar().showMessage("Đáp án không hợp lệ.")
            return

        attempt = self.view.build_attempt(answer)
        evaluation = self.assessor.evaluate(self._current, attempt)
        self._last_eval = evaluation
        self.view.mark_status(self._current, attempt)

        kind = "correct" if evaluation.correct else "error"
        self.tutor.say(evaluation.message, kind)
        self._update_student(evaluation)

        if evaluation.correct:
            self.statusBar().showMessage("Chính xác! Em có thể làm bài tiếp theo.")
        else:
            self.statusBar().showMessage("Chưa đúng — xem phản hồi ở panel Gia sư.")

    def _hint(self) -> None:
        evaluation = self._last_eval
        if evaluation is None or evaluation.correct:
            evaluation = self.assessor.evaluate(
                self._current, self.view.build_attempt(self._parse_answer())
            )
            self._last_eval = evaluation

        if evaluation.correct:
            self.tutor.say("Em đã giải đúng bài này rồi.", "info")
            return

        step_key = evaluation.failed_step
        if step_key is None and self._current.steps:
            step_key = self._current.steps[-1].key
        if step_key is None:
            return

        level = self._hint_levels.get(step_key, 0)
        text = self.assessor.hint(self._current, step_key, level)
        self.tutor.say(f"Gợi ý (mức {level + 1}/3): {text}", "hint")
        self._hint_levels[step_key] = min(level + 1, 2)

        step = find_step(self._current, step_key)
        if step is not None:
            self.student.record_hint(step.title)
        self.statusBar().showMessage("Đã đưa ra gợi ý.")

    def _update_student(self, evaluation) -> None:
        steps = self._current.steps
        if evaluation.correct:
            for step in steps:
                self.student.record(step.title, True)
        else:
            failed = evaluation.failed_step
            index = next(
                (i for i, step in enumerate(steps) if step.key == failed),
                len(steps) - 1,
            )
            for i, step in enumerate(steps):
                if i < index:
                    self.student.record(step.title, True)
                elif i == index:
                    self.student.record(step.title, False)
        self._sync_mastery()

    def _sync_mastery(self) -> None:
        snap = self.student.snapshot()
        self.tutor.set_skills(
            {step.title: snap.get(step.title, 0.0) for step in self._current.steps}
        )

    # ------------------------------------------------------------------
    # Tuỳ chọn, tri thức, trợ giúp
    # ------------------------------------------------------------------
    def _options(self) -> None:
        dialog = OptionsDialog(self.options, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.options = dialog.result_options()

        theme.CORRECT = self.options.color_correct
        theme.INCORRECT = self.options.color_incorrect
        self.scene.options = self.options
        self.view.set_options(self.options)
        self.scene.update()

        font = self.tutor.history.font()
        font.setPointSize(self.options.font_size)
        self.tutor.history.setFont(font)

        self._apply_timer_option()
        self.statusBar().showMessage("Đã cập nhật tuỳ chọn.")

    def _show_catalog(self, title: str) -> None:
        headers, rows = rows_for(title)
        CatalogDialog(title, headers, rows, self).exec()

    def _about(self) -> None:
        QMessageBox.about(
            self,
            "Giới thiệu ANDES Workbench",
            "<h3>ANDES Workbench</h3>"
            "<p>Prototype giao diện kiểu <b>Andes Physics Tutor</b> (VanLehn et al.): "
            "workbench vẽ lực – trục – phương trình, panel gia sư theo từng bước, "
            "gợi ý 3 mức và mô hình người học đơn giản.</p>"
            "<p>PyQt6 · dữ liệu bài học tách khỏi giao diện.</p>",
        )

    def _quick_help(self) -> None:
        QMessageBox.information(
            self,
            "Hướng dẫn nhanh",
            "1. Chọn công cụ ở thanh bên trái (Vectơ / Trục / Phương trình...).\n"
            "2. Kéo–thả để vẽ vectơ; nhấp đúp để đổi nhãn.\n"
            "3. Nhập đáp án số ở panel Gia sư rồi bấm Kiểm tra.\n"
            "4. Bấm Gợi ý để nhận gợi ý tăng dần (3 mức).\n\n"
            "Phím tắt: Ctrl+1..8 chọn công cụ, Delete xoá, Ctrl+lăn chuột để zoom, "
            "giữ chuột giữa để pan.",
        )

    # ------------------------------------------------------------------
    # Đồng hồ
    # ------------------------------------------------------------------
    def _apply_timer_option(self) -> None:
        visible = bool(self.options.show_timer)
        self.timer_label.setVisible(visible)
        if visible:
            self._timer.start()
        else:
            self._timer.stop()

    def _tick(self) -> None:
        self._elapsed += 1
        self._update_timer_label()

    def _update_timer_label(self) -> None:
        minutes, seconds = divmod(self._elapsed, 60)
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)