# -*- coding: utf-8 -*-
"""Smoke test giao diện ANDES (chạy headless, offscreen)."""
import pytest
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from andes.ui.canvas import EquationItem, Tool, VectorItem
from andes.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _add_solution(win: MainWindow) -> None:
    win.scene.addItem(VectorItem(QPointF(0.0, 0.0), QPointF(100.0, 0.0), "F"))
    win.scene.addItem(EquationItem("F = m * a", QPointF(0.0, 60.0)))


def test_window_builds(app):
    win = MainWindow()
    try:
        assert win._current.id == "fma"
        assert win.title_label.text() == "Định luật II Newton"
        assert "m/s" in win.tutor.unit_label.text()
        assert win.view.tool() == Tool.SELECT
    finally:
        win.close()


def test_check_correct_solution(app):
    win = MainWindow()
    try:
        _add_solution(win)
        win.tutor.answer_edit.setText("5")
        win._check()
        assert win._last_eval is not None
        assert win._last_eval.correct
    finally:
        win.close()


def test_buggy_answer_feedback(app):
    win = MainWindow()
    try:
        _add_solution(win)
        win.tutor.answer_edit.setText("20")
        win._check()
        assert win._last_eval.buggy_key == "multiply"
        assert "nhân" in win.tutor.history.toPlainText()
    finally:
        win.close()


def test_hint_ladder_in_ui(app):
    win = MainWindow()
    try:
        win._hint()
        assert "mức 1/3" in win.tutor.history.toPlainText()
        win._hint()
        assert "mức 2/3" in win.tutor.history.toPlainText()
        win._hint()
        assert "mức 3/3" in win.tutor.history.toPlainText()
    finally:
        win.close()


def test_switch_problem(app):
    win = MainWindow()
    try:
        win._load_problem("incline")
        assert win._current.id == "incline"
        assert win.title_label.text() == "Mặt phẳng nghiêng"
    finally:
        win.close()


def test_draw_vector_with_mouse(app):
    win = MainWindow()
    win.resize(900, 700)
    win.show()
    try:
        win.view.prompt_labels = False
        win.view.set_tool(Tool.VECTOR)
        viewport = win.view.viewport()
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=QPoint(150, 150))
        QTest.mouseMove(viewport, QPoint(280, 150))
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=QPoint(280, 150))
        app.processEvents()

        vectors = list(win.view.iter_vectors())
        assert len(vectors) == 1
        assert vectors[0].vector_data().dx > 0
    finally:
        win.close()


def test_options_roundtrip(app):
    from andes.ui.dialogs import OptionsDialog

    win = MainWindow()
    try:
        dialog = OptionsDialog(win.options)
        dialog.snap.setValue(30)
        dialog.grid.setChecked(False)
        options = dialog.result_options()
        assert options.angle_snap == 30
        assert options.show_grid is False
        dialog.close()
    finally:
        win.close()