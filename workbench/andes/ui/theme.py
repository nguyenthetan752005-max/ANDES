# -*- coding: utf-8 -*-
"""Bảng màu và QSS cho ANDES workbench (giao diện sáng, hiện đại)."""

BG = "#F4F7FB"
PANEL = "#FFFFFF"
BORDER = "#DDE5F0"
TEXT = "#1F2A44"
MUTED = "#63718C"
ACCENT = "#2F6FEB"
ACCENT_DARK = "#245BC0"
CORRECT = "#1E9E5A"
INCORRECT = "#D64545"
WARN = "#C9861A"


QSS = f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QMainWindow, QDialog {{
    background: {BG};
}}
QWidget#Central {{
    background: {BG};
}}
QMenuBar {{
    background: {PANEL};
    border-bottom: 1px solid {BORDER};
    padding: 2px 6px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 10px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{
    background: #EAF1FE;
    color: {ACCENT_DARK};
}}
QMenu {{
    background: {PANEL};
    border: 1px solid {BORDER};
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 22px 7px 14px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background: #EAF1FE;
    color: {ACCENT_DARK};
}}
QToolBar {{
    background: {PANEL};
    border: none;
    border-bottom: 1px solid {BORDER};
    spacing: 6px;
    padding: 6px 8px;
}}
QToolBar#ToolStrip {{
    border-right: 1px solid {BORDER};
    border-bottom: none;
    padding: 8px 6px;
}}
QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 7px 10px;
    color: {TEXT};
}}
QToolButton:hover {{
    background: #EEF3FC;
}}
QToolButton:checked {{
    background: #E3EDFE;
    border: 1px solid #B9CFF8;
    color: {ACCENT_DARK};
}}
QPushButton {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 14px;
    color: {TEXT};
}}
QPushButton:hover {{
    background: #F1F5FD;
}}
QPushButton:pressed {{
    background: #E5EEFC;
}}
QPushButton#Primary {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
    color: white;
    font-weight: 600;
}}
QPushButton#Primary:hover {{
    background: {ACCENT_DARK};
}}
QPushButton#Ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {ACCENT_DARK};
    padding: 6px 10px;
}}
QPushButton#Ghost:hover {{
    background: #EEF3FC;
}}
QLineEdit, QSpinBox {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 10px;
    selection-background-color: #C9DCFB;
}}
QLineEdit:focus, QSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QTextBrowser {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px;
}}
QProgressBar {{
    background: #EDF1F7;
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 5px;
}}
QLabel#PanelTitle {{
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {ACCENT_DARK};
}}
QLabel#ProblemTitle {{
    font-size: 15px;
    font-weight: 700;
}}
QLabel#Muted {{
    color: {MUTED};
}}
QFrame#Card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QFrame#ProblemHeader {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QStatusBar {{
    background: {PANEL};
    border-top: 1px solid {BORDER};
}}
"""