# -*- coding: utf-8 -*-
"""Danh mục tri thức hiển thị ở menu Physics (Principles/Quantities/Units/Constants)."""

PRINCIPLES = [
    ("Định luật II Newton", "F = m·a", "Gia tốc tỉ lệ thuận với hợp lực và tỉ lệ nghịch với khối lượng."),
    ("Định luật III Newton", "F₁₂ = −F₂₁", "Hai vật tác dụng lực lên nhau bằng nhau và ngược chiều."),
    ("Động năng", "Eₖ = ½·m·v²", "Năng lượng do chuyển động của vật."),
    ("Thế năng trọng trường", "Eₚ = m·g·h", "Năng lượng theo độ cao trong trọng trường."),
    ("Công của lực", "A = F·s·cosα", "Công phụ thuộc góc giữa lực và độ dời."),
    ("Định luật Hooke", "F = k·Δl", "Lực đàn hồi tỉ lệ với độ biến dạng."),
    ("Định luật Ohm", "I = U/R", "Cường độ dòng điện tỉ lệ với hiệu điện thế."),
]

QUANTITIES = [
    ("Khối lượng", "m", "kg"),
    ("Gia tốc", "a", "m/s²"),
    ("Vận tốc", "v", "m/s"),
    ("Quãng đường", "s", "m"),
    ("Lực", "F", "N"),
    ("Công", "A", "J"),
    ("Động năng", "Eₖ", "J"),
    ("Thời gian", "t", "s"),
]

UNITS = [
    ("Newton", "N", "kg·m/s²"),
    ("Joule", "J", "N·m"),
    ("Watt", "W", "J/s"),
    ("Met trên giây bình phương", "m/s²", "m·s⁻²"),
    ("Kilogram", "kg", "khối lượng"),
    ("Giây", "s", "thời gian"),
]

CONSTANTS = [
    ("Gia tốc trọng trường", "g", "9.8", "m/s²"),
    ("Hằng số hấp dẫn", "G", "6.674×10⁻¹¹", "N·m²/kg²"),
    ("Tốc độ ánh sáng", "c", "3.0×10⁸", "m/s"),
    ("Điện tích nguyên tố", "e", "1.602×10⁻¹⁹", "C"),
]


def rows_for(title: str):
    """Trả (headers, rows) cho hộp thoại theo tiêu đề menu."""
    if title == "Principles":
        return (("Nguyên lý", "Công thức", "Mô tả"), PRINCIPLES)
    if title == "Quantities":
        return (("Đại lượng", "Ký hiệu", "Đơn vị"), QUANTITIES)
    if title == "Units":
        return (("Đơn vị", "Ký hiệu", "Thứ nguyên"), UNITS)
    if title == "Constants":
        return (("Hằng số", "Ký hiệu", "Giá trị", "Đơn vị"), CONSTANTS)
    return (("Mục", "Giá trị"), [])