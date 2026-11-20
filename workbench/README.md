# ANDES Workbench (prototype)

Bản dựng lại **giao diện kiểu Andes Physics Tutor** (VanLehn et al.) bằng **PyQt6**,
độc lập với `PyPAKMA_2`. Đây là workbench giải bài Vật lý theo từng bước:

- Thanh công cụ bên trái: **Vectơ lực, hệ trục, phương trình, chữ, đoạn, chữ nhật, ellipse**.
- Canvas ở giữa (kéo–thả để vẽ; nhấp đúp để đổi nhãn/phương trình).
- Panel **Gia sư** bên phải: lịch sử phản hồi, mức nắm kỹ năng, ô đáp án,
  nút **Kiểm tra** và **Gợi ý** (thang 3 mức).
- Menu **Vật lý**: Principles / Quantities / Units / Constants.
- **Tuỳ chọn**: bắt góc, lưới, đồng hồ, cỡ chữ, màu đúng/sai.

## Chạy

```powershell
cd D:\PAKMA_final\ANDES
python main.py
```

Yêu cầu: `PyQt6` (đã có trong môi trường của `PyPAKMA_2`).

Ảnh xem trước giao diện: `preview.png` (sinh tự động ở chế độ offscreen).

## Bài mẫu

1. **Định luật II Newton** — m = 2 kg, F = 10 N ngang, bỏ qua ma sát → a = 5 m/s².
   Học sinh cần: vẽ vectơ F sang phải, viết F = m·a (hoặc a = F/m), nhập 5.
2. **Mặt phẳng nghiêng** — m = 2 kg, α = 30°, g = 9.8 → a ≈ 4.9 m/s².
   Học sinh cần: viết a = g·sinα, nhập 4.9.

## Cách hệ thống đánh giá

- Ưu tiên **buggy rules** (hiểu sai phổ biến): nhân thay vì chia, chia ngược,
  dùng cos thay sin, vẽ ngược chiều lực...
- Sau đó kiểm tra lần lượt: **vectơ bắt buộc → phương trình → đáp án số**.
- **Gợi ý** tăng dần theo bước đang hỏng: nhắc → nguyên lý → nói thẳng.
- **Mô hình người học** đếm đúng/sai/số lần gợi ý theo kỹ năng (làm mượt Laplace).

## Cấu trúc

```
ANDES/
  main.py
  andes/
    domain/            # không phụ thuộc Qt, test headless
      model.py         # Given, VectorData, Attempt, Problem, Step, BuggyRule
      problems.py      # hai bài mẫu + buggy rules
      assessor.py      # Assessor + Evaluation + StudentModel
      catalog.py       # dữ liệu Principles/Quantities/Units/Constants
    ui/
      main_window.py   # menu, toolbar, wiring, timer
      canvas.py        # scene, view, các item (vectơ/trục/phương trình...)
      tutor_panel.py   # panel gia sư + mastery bars
      dialogs.py       # Options, Catalog
      theme.py         # QSS + bảng màu
      options.py       # AppOptions
  tests/
    test_domain.py
    test_ui_smoke.py
```

## Kiểm thử

```powershell
cd D:\PAKMA_final\ANDES
python -m pytest tests -q
```

Test UI chạy headless nhờ `QT_QPA_PLATFORM=offscreen` (xem `tests/conftest.py`).

## Ghi chú

- Đây là **prototype giao diện + bộ luật tối giản**, không phải bản port Andes.
- Không sao chép mã/asset từ repo Andes; chỉ học mô hình tương tác
  (workbench – tutor – hint ladder).
- Muốn thêm bài: bổ sung một `Problem` trong `domain/problems.py` (dữ kiện,
  `vector_specs`, mẫu phương trình, 3 mức gợi ý, buggy rules).