# -*- coding: utf-8 -*-
"""Tuỳ chọn giao diện (angle snap, lưới, timer, cỡ chữ, màu đúng/sai)."""
from dataclasses import dataclass

from . import theme


@dataclass
class AppOptions:
    angle_snap: int = 15          # độ; 0 = tắt
    show_grid: bool = True
    show_timer: bool = True
    font_size: int = 13
    color_correct: str = theme.CORRECT
    color_incorrect: str = theme.INCORRECT