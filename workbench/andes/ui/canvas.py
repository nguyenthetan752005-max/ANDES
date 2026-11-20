# -*- coding: utf-8 -*-
"""Canvas workbench: vectơ lực, trục toạ độ, phương trình, hình cơ bản.

- `CanvasScene`: nền lưới.
- `CanvasView`: công cụ vẽ (kéo–thả hoặc click), pan/zoom, chụp trạng thái.
- Item: `VectorItem`, `AxesItem`, `EquationItem`, `TextNoteItem`.
"""
from __future__ import annotations

import math
from enum import Enum

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QGraphicsView,
    QInputDialog,
)

from ..domain.model import (
    Attempt,
    Problem,
    VectorData,
    equation_matches,
    norm_label,
    vector_matches,
)
from . import theme
from .options import AppOptions


class Tool(Enum):
    SELECT = "select"
    VECTOR = "vector"
    AXES = "axes"
    EQUATION = "equation"
    TEXT = "text"
    LINE = "line"
    RECT = "rect"
    ELLIPSE = "ellipse"


_ITEM_FLAGS = (
    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
    | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
)


# --------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------

class VectorItem(QGraphicsItem):
    """Vectơ lực: gốc ở pos(), đầu mút ở pos() + vector nội bộ."""

    def __init__(self, start: QPointF, end: QPointF, label: str = "F"):
        super().__init__()
        self.setPos(start)
        self._vec = QPointF(end) - QPointF(start)
        self.setFlags(_ITEM_FLAGS)
        self._status = None
        self.setZValue(10)

        self._label_item = QGraphicsSimpleTextItem(label, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self._label_item.setFont(font)
        self._label_item.setBrush(QColor(theme.TEXT))
        self._place_label()

    # -- dữ liệu ---------------------------------------------------------
    def label(self) -> str:
        return self._label_item.text()

    def set_label(self, text: str) -> None:
        self._label_item.setText(text)
        self._place_label()
        self.update()

    def set_end(self, scene_end: QPointF) -> None:
        self.prepareGeometryChange()
        self._vec = QPointF(scene_end) - self.pos()
        self._place_label()
        self.update()

    def vector_data(self) -> VectorData:
        return VectorData(self.label(), self._vec.x(), self._vec.y())

    def set_status(self, status) -> None:
        self._status = status
        self.update()

    # -- hình học --------------------------------------------------------
    def boundingRect(self) -> QRectF:
        r = QRectF(QPointF(0.0, 0.0), self._vec).normalized()
        return r.adjusted(-20.0, -20.0, 20.0, 20.0)

    def shape(self) -> QPainterPath:
        path = QPainterPath(QPointF(0.0, 0.0))
        path.lineTo(self._vec)
        stroker = QPainterPathStroker()
        stroker.setWidth(16.0)
        return stroker.createStroke(path)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(theme.ACCENT)
        if self._status is True:
            color = QColor(theme.CORRECT)
        elif self._status is False:
            color = QColor(theme.INCORRECT)

        pen = QPen(color, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        if self.isSelected():
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setWidthF(3.4)
        painter.setPen(pen)
        painter.drawLine(QPointF(0.0, 0.0), self._vec)

        ang = math.atan2(self._vec.y(), self._vec.x())
        size = 13.0
        tip = self._vec
        a1 = QPointF(tip.x() - size * math.cos(ang - 0.42),
                     tip.y() - size * math.sin(ang - 0.42))
        a2 = QPointF(tip.x() - size * math.cos(ang + 0.42),
                     tip.y() - size * math.sin(ang + 0.42))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(QPolygonF([tip, a1, a2]))

    def _place_label(self) -> None:
        mid = QPointF(self._vec.x() / 2.0, self._vec.y() / 2.0)
        br = self._label_item.boundingRect()
        self._label_item.setPos(mid.x() + 8.0, mid.y() - br.height() - 2.0)

    def mouseDoubleClickEvent(self, event) -> None:
        text, ok = QInputDialog.getText(None, "Nhãn vectơ", "Tên lực:", text=self.label())
        if ok and text.strip():
            self.set_label(text.strip())
        event.accept()


class AxesItem(QGraphicsItem):
    """Hệ trục Oxy: Ox sang phải, Oy hướng lên (vẽ bằng -y)."""

    def __init__(self, origin: QPointF, length: float = 150.0):
        super().__init__()
        self.setPos(origin)
        self.L = float(length)
        self.setFlags(_ITEM_FLAGS)
        self.setZValue(1)

    def boundingRect(self) -> QRectF:
        L = self.L
        return QRectF(-L - 20.0, -L - 20.0, 2.0 * L + 40.0, 2.0 * L + 40.0)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(theme.ACCENT) if self.isSelected() else QColor(theme.MUTED)
        painter.setPen(QPen(color, 1.6))
        painter.drawLine(QPointF(0.0, 0.0), QPointF(self.L, 0.0))
        painter.drawLine(QPointF(0.0, 0.0), QPointF(0.0, -self.L))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(QPolygonF([
            QPointF(self.L, 0.0),
            QPointF(self.L - 9.0, -4.5),
            QPointF(self.L - 9.0, 4.5),
        ]))
        painter.drawPolygon(QPolygonF([
            QPointF(0.0, -self.L),
            QPointF(-4.5, -self.L + 9.0),
            QPointF(4.5, -self.L + 9.0),
        ]))

        painter.setPen(QColor(theme.MUTED))
        painter.drawText(QPointF(self.L + 6.0, 5.0), "x")
        painter.drawText(QPointF(-16.0, -self.L - 2.0), "y")


class EquationItem(QGraphicsTextItem):
    """Phương trình có nền bo góc; đổi màu theo đúng/sai."""

    def __init__(self, text: str, pos: QPointF):
        super().__init__(text)
        self.setPos(pos)
        font = QFont("Consolas")
        font.setPointSize(12)
        self.setFont(font)
        self.setDefaultTextColor(QColor(theme.TEXT))
        self.setFlags(_ITEM_FLAGS)
        self._status = None
        self.setZValue(20)

    def boundingRect(self) -> QRectF:
        return super().boundingRect().adjusted(-10.0, -7.0, 10.0, 7.0)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._status is True:
            bg, border = QColor("#E8F6EE"), QColor(theme.CORRECT)
        elif self._status is False:
            bg, border = QColor("#FDECEC"), QColor(theme.INCORRECT)
        else:
            bg, border = QColor(theme.PANEL), QColor(theme.BORDER)
        painter.setPen(QPen(border, 1.6))
        painter.setBrush(bg)
        painter.drawRoundedRect(self.boundingRect(), 8.0, 8.0)
        super().paint(painter, option, widget)

    def set_status(self, status) -> None:
        self._status = status
        self.update()

    def mouseDoubleClickEvent(self, event) -> None:
        text, ok = QInputDialog.getText(None, "Phương trình", "Nhập phương trình:", text=self.toPlainText())
        if ok and text.strip():
            self.setPlainText(text.strip())
        event.accept()


class TextNoteItem(QGraphicsTextItem):
    """Ghi chú; nhấp đúp để sửa tại chỗ."""

    def __init__(self, text: str, pos: QPointF):
        super().__init__(text)
        self.setPos(pos)
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.setDefaultTextColor(QColor(theme.TEXT))
        self.setFlags(_ITEM_FLAGS)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def mouseDoubleClickEvent(self, event) -> None:
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event) -> None:
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        super().focusOutEvent(event)


# --------------------------------------------------------------------------
# Scene & View
# --------------------------------------------------------------------------

class CanvasScene(QGraphicsScene):
    def __init__(self, options: AppOptions, parent=None):
        super().__init__(parent)
        self.options = options
        self.setSceneRect(-3000.0, -3000.0, 6000.0, 6000.0)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, QColor(theme.BG))
        if not self.options.show_grid:
            return
        step = 25
        pen = QPen(QColor("#E7EDF6"), 1.0)
        painter.setPen(pen)
        x = math.floor(rect.left() / step) * step
        while x < rect.right():
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += step
        y = math.floor(rect.top() / step) * step
        while y < rect.bottom():
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += step


class CanvasView(QGraphicsView):
    """Vùng vẽ với công cụ kiểu Andes."""

    MIN_SIZE = 8.0

    def __init__(self, scene: CanvasScene, options: AppOptions, parent=None):
        super().__init__(scene, parent)
        self.options = options
        self._tool = Tool.SELECT
        self._create_start = None
        self._creating_item = None
        self.prompt_labels = True

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(QColor(theme.BG))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._panning = False
        self._pan_start = None
        self._pan_h = 0
        self._pan_v = 0

    # -- công cụ ---------------------------------------------------------
    def tool(self) -> Tool:
        return self._tool

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool
        if tool == Tool.SELECT:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)

    def set_options(self, options: AppOptions) -> None:
        self.options = options
        self.viewport().update()

    # -- dữ liệu cho assessor -------------------------------------------
    def iter_vectors(self):
        for item in self.scene().items():
            if isinstance(item, VectorItem):
                yield item

    def iter_equations(self):
        for item in self.scene().items():
            if isinstance(item, EquationItem):
                yield item

    def snapshot(self) -> tuple:
        vectors = tuple(v.vector_data() for v in self.iter_vectors())
        equations = tuple(e.toPlainText() for e in self.iter_equations())
        return vectors, equations

    def build_attempt(self, answer) -> Attempt:
        vectors, equations = self.snapshot()
        return Attempt(vectors=vectors, equations=equations, answer=answer)

    def clear_canvas(self) -> None:
        self.scene().clear()

    def mark_status(self, problem: Problem, attempt: Attempt) -> None:
        required = {norm_label(spec.label) for spec in problem.vector_specs if not spec.optional}
        for item in self.iter_vectors():
            label = norm_label(item.label())
            if not required or label not in required:
                item.set_status(None)
                continue
            ok = any(vector_matches(item.vector_data(), spec) for spec in problem.vector_specs)
            item.set_status(ok)

        expect_eq = bool(problem.equation_patterns) or problem.equation_checker is not None
        for item in self.iter_equations():
            item.set_status(equation_matches(item.toPlainText(), problem) if expect_eq else None)

    def clear_status(self) -> None:
        for item in self.iter_vectors():
            item.set_status(None)
        for item in self.iter_equations():
            item.set_status(None)

    # -- tạo item --------------------------------------------------------
    def _snap(self, start: QPointF, end: QPointF) -> QPointF:
        snap = int(getattr(self.options, "angle_snap", 0) or 0)
        if snap <= 0:
            return end
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return end
        ang = math.degrees(math.atan2(dy, dx))
        ang = round(ang / snap) * snap
        rad = math.radians(ang)
        return QPointF(start.x() + length * math.cos(rad),
                       start.y() + length * math.sin(rad))

    def _make_item(self, tool: Tool, pos: QPointF):
        if tool == Tool.VECTOR:
            return VectorItem(pos, pos, "F")
        if tool == Tool.LINE:
            item = QGraphicsLineItem(0.0, 0.0, 0.0, 0.0)
            item.setPos(pos)
            item.setPen(QPen(QColor(theme.TEXT), 2.0))
            item.setFlags(_ITEM_FLAGS)
            return item
        if tool == Tool.RECT:
            item = QGraphicsRectItem(0.0, 0.0, 0.0, 0.0)
            item.setPos(pos)
            item.setPen(QPen(QColor(theme.TEXT), 2.0))
            item.setBrush(QColor(255, 255, 255, 0))
            item.setFlags(_ITEM_FLAGS)
            return item
        if tool == Tool.ELLIPSE:
            item = QGraphicsEllipseItem(0.0, 0.0, 0.0, 0.0)
            item.setPos(pos)
            item.setPen(QPen(QColor(theme.TEXT), 2.0))
            item.setBrush(QColor(255, 255, 255, 0))
            item.setFlags(_ITEM_FLAGS)
            return item
        if tool == Tool.AXES:
            return AxesItem(pos)
        if tool == Tool.EQUATION:
            return EquationItem("F = m * a", pos)
        if tool == Tool.TEXT:
            return TextNoteItem("Ghi chú", pos)
        return None

    def _update_item(self, item, start: QPointF, end: QPointF) -> None:
        if isinstance(item, VectorItem):
            item.set_end(self._snap(start, end))
            return
        if isinstance(item, QGraphicsLineItem):
            end = self._snap(start, end)
            item.setLine(0.0, 0.0, end.x() - start.x(), end.y() - start.y())
            return
        if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            r = QRectF(start, end).normalized()
            item.setPos(r.topLeft())
            item.setRect(0.0, 0.0, r.width(), r.height())
            # rect/ellipse: giữ nguyên vị trí gốc để không nhảy khi kéo ngược
            return

    def _too_small(self, item, start: QPointF, end: QPointF) -> bool:
        if isinstance(item, VectorItem):
            return (end - start).manhattanLength() < self.MIN_SIZE
        if isinstance(item, QGraphicsLineItem):
            return (end - start).manhattanLength() < self.MIN_SIZE
        if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            r = QRectF(start, end).normalized()
            return r.width() < self.MIN_SIZE or r.height() < self.MIN_SIZE
        return False

    def _finalize(self, item, tool: Tool, start: QPointF, end: QPointF) -> None:
        if item is None:
            return
        if isinstance(item, VectorItem):
            if self.prompt_labels:
                text, ok = QInputDialog.getText(None, "Nhãn vectơ", "Tên lực:", text=item.label())
                if ok and text.strip():
                    item.set_label(text.strip())
        elif isinstance(item, EquationItem):
            text, ok = QInputDialog.getText(
                None, "Phương trình", "Nhập phương trình:", text=item.toPlainText()
            )
            if not ok or not text.strip():
                self.scene().removeItem(item)
                return
            item.setPlainText(text.strip())
        elif isinstance(item, TextNoteItem):
            text, ok = QInputDialog.getText(
                None, "Ghi chú", "Nội dung:", text=item.toPlainText()
            )
            if not ok or not text.strip():
                self.scene().removeItem(item)
                return
            item.setPlainText(text.strip())

    # -- sự kiện chuột ---------------------------------------------------
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position().toPoint()
            self._pan_h = self.horizontalScrollBar().value()
            self._pan_v = self.verticalScrollBar().value()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if self._tool == Tool.SELECT:
            super().mousePressEvent(event)
            return

        pos = self.mapToScene(event.position().toPoint())
        self._create_start = pos
        self._creating_item = self._make_item(self._tool, pos)
        if self._creating_item is not None:
            self.scene().addItem(self._creating_item)
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._panning and self._pan_start is not None:
            delta = event.position().toPoint() - self._pan_start
            self.horizontalScrollBar().setValue(self._pan_h - delta.x())
            self.verticalScrollBar().setValue(self._pan_v - delta.y())
            event.accept()
            return

        if self._creating_item is not None and self._create_start is not None:
            pos = self.mapToScene(event.position().toPoint())
            self._update_item(self._creating_item, self._create_start, pos)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._panning:
            self._panning = False
            self.setCursor(
                Qt.CursorShape.ArrowCursor
                if self._tool == Tool.SELECT
                else Qt.CursorShape.CrossCursor
            )
            event.accept()
            return

        if self._creating_item is not None:
            pos = self.mapToScene(event.position().toPoint())
            item = self._creating_item
            start = self._create_start
            self._creating_item = None
            self._create_start = None

            self._update_item(item, start, pos)
            if self._too_small(item, start, pos):
                self.scene().removeItem(item)
            else:
                self._finalize(item, self._tool, start, pos)
            event.accept()
            return

        super().mouseReleaseEvent(event)

    # -- phóng to / bàn phím --------------------------------------------
    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in list(self.scene().selectedItems()):
                self.scene().removeItem(item)
            event.accept()
            return
        super().keyPressEvent(event)