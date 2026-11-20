# D:\ANDES — tổng hợp tài nguyên Andes

Thư mục này gom toàn bộ phần Andes ra khỏi project `D:\PAKMA_final`.

> **Phạm vi repo GitHub:** repo chỉ chứa `workbench/`, `scripts/`, `README.md` và tài liệu
> giới thiệu. Các thư mục `source/`, `references/` (chứa mã bên thứ ba, đề `.prb` và
> installer có bản quyền, rất nặng) **không** được đưa lên Git.

## TL;DR — đi đâu để làm gì
- **Chỉ muốn XEM giao diện** → `workbench\preview.png` hoặc chạy `python main.py` (mục "Chạy workbench").
- **Muốn chạy bản WEB gốc** (server Lisp + web-UI) → mục "Chạy Andes gốc — bản WEB".
- **Muốn bản DESKTOP 2011** (trong máy ảo) → mục "Chạy Andes desktop 2011".
- **Cần script tiện dụng** → thư mục `scripts\` (start_server.lisp, serve_andes.py, problems.asd, patch).

## Mục lục
- [Cấu trúc](#cấu-trúc)
- [Chạy workbench](#chạy-workbench)
- [Chạy Andes gốc — bản WEB](#chạy-andes-gốc--bản-web-lisp-server--web-ui)
- [Chạy Andes desktop 2011 (trong máy ảo)](#chạy-andes-desktop-2011-trong-máy-ảo)
- [Trạng thái: chạy được gì / còn thiếu gì](#trạng-thái-chạy-được-gì--còn-thiếu-gì)
- [Troubleshooting](#troubleshooting)
- [Nguồn trên mạng cho project Andes](#nguồn-trên-mạng-cho-project-andes)

## Cấu trúc

```
D:\ANDES\
  workbench\                     Prototype giao diện Andes (PyQt6)
    main.py                      chạy: cd workbench; python main.py
    andes\domain\                mô hình bài học + assessor (không phụ thuộc Qt)
    andes\ui\                    canvas, tutor panel, dialogs, theme
    tests\                       20 test headless
    preview.png                  ảnh giao diện

  scripts\                       Script tiện dụng cho bản web
    start_server.lisp            chạy help server (không cần DB)
    serve_andes.py               static web-UI + proxy /andes-help
    problems.asd                 stub hệ problems (thiếu repo gốc)
    patch_model_cl.sh            vá Help/model.cl cho SBCL mới

  source\
    andes-master\                Mã nguồn gốc bvds/andes (nhánh master)
    AndysComet-master\           Nhánh sinh viên: whiteboard/chat (CometD)

  references\
    installer\
      Andes1311.exe              Installer Andes 2011 (self-extracting ZIP; chạy trong VM)
    problems\
      Andes1311\                 583 file .prb + KB\ + Review\ (giải nén từ installer)
    archives\
      bvds_andes_stable.zip      Nhánh stable (khuyến nghị để chạy server)
      andes-master.zip           Bản master tải sẵn
      AndysComet-master.zip      Bản AndysComet (mnguyen4)
      MattSmithASU_Andyscomet.zip Bản AndysComet đầy đủ (kèm Maven + CometD)
    papers\
      VanLehn_2005_Andes_Five_Years.pdf
      Andes_Download_2009.html   (thực ra là trang Publications cũ)
```

## Chạy workbench

```powershell
cd D:\ANDES\workbench
python main.py
# test:
python -m pytest tests -q
```

## Ghi chú

- `Andes1311.exe`: bản 2011, **nguồn gốc chưa xác minh** — **đừng chạy trên host**;
  chỉ chạy trong **VM cách ly** (xem mục "Chạy Andes desktop 2011" bên dưới).
- Bộ `problems`/lời giải thuộc **bản quyền Andes**; dùng cho học/nghiên cứu cục bộ.
  **Không commit/redistribute** — đặc biệt là `solutions/` và mọi file `.prb`.
- Mỗi `.prb` chứa **cả đề lẫn lời giải**: `Statement`, `Graphic`, `Choices`, `Features`
  cùng đồ thị `WorkingMemory`/`Bubblegraph`. Cái còn thiếu là metadata KB
  (phrases/entry-tests) nằm trong repo `problems/` (bản quyền, không có).
- Nguồn chính thức: https://github.com/bvds/andes (LGPL-3.0).
- AndysComet: https://github.com/mnguyen4/AndysComet , https://github.com/MattSmithASU/Andyscomet

---

# Chạy Andes gốc — bản WEB (Lisp server + web-UI)

**Kết quả đã kiểm chứng:** dựng được **server + web-UI** (biên dịch sạch, build solver,
JSON-RPC chạy); riêng `open-problem` **còn lỗi** — xem "Troubleshooting".

**Environment đã thử:** WSL2 **Ubuntu 26.04**, `SBCL 2.6.0`, `g++ 15.2`,
`make 4.4.1`, `mysql 8.4.13`.
Ghi chú: `Ubuntu` là **tên distro WSL** của bạn (kiểm tra `wsl -l -v`); `/mnt/d`
giả định ổ D của Windows được mount (mặc định của WSL); thay `tan` bằng user WSL.

## 0. Toolchain (trong Ubuntu/WSL)
```bash
sudo apt update
sudo apt install -y build-essential sbcl unzip curl mysql-server libmysqlclient-dev
```

## 1. Lấy mã nguồn (nhánh stable)
```bash
cd ~
# Cách A — từ GitHub (cần mạng):
git clone -b stable https://github.com/bvds/andes.git andes-stable

# Cách B — dùng zip cục bộ (offline):
# unzip -q /mnt/d/ANDES/references/archives/bvds_andes_stable.zip   # -> ~/andes-stable
```
> Nhánh `stable` **có sẵn trên GitHub** (`git clone -b stable ...`). Repo còn nhiều
> nhánh khác: `master`, `stable-with-logging`, `ubuntu-help-server`, `Andes2`...
> (xem https://api.github.com/repos/bvds/andes/branches). Zip cục bộ chỉ để dùng offline.

## 2. Đưa bộ đề `.prb` vào `solutions/` (+ ảnh đề)
```bash
mkdir -p ~/andes-stable/solutions
cp /mnt/d/ANDES/references/problems/Andes1311/Problems/*.prb ~/andes-stable/solutions/

# Ảnh đề bài: client đọc từ images/ (vd Graphic "amp1.gif" -> /images/amp1.gif).
# Repo stable đã có nhiều ảnh; copy thêm từ bộ đề cho chắc:
cp /mnt/d/ANDES/references/problems/Andes1311/Problems/*.gif ~/andes-stable/images/ 2>/dev/null || true
cp /mnt/d/ANDES/references/problems/Andes1311/Problems/*.jpg ~/andes-stable/images/ 2>/dev/null || true
```
> `.prb` chứa **đề + đồ thị lời giải**, đọc từ `solutions/`.
> ⚠️ **Đừng** copy `references\problems\Andes1311\KB\*.tsv` vào `andes-stable/KB/`
> — đó là dữ liệu DB (features/principles/scalars), **khác** `KB/*.cl` (mã Lisp) của repo.
> Repo `problems/` (định nghĩa đề) có bản quyền, không có.

## 3. Stub hệ `problems` (vì thiếu repo gốc)
Tạo `~/andes-stable/problems/problems.asd`:
```lisp
;;;; -*- Lisp -*-
(in-package :cl-user)
(defpackage :problems-asd (:use :cl :asdf))
(in-package :problems-asd)
(defsystem :problems :name "problems" :components ())
```

## 4. Quicklisp
```bash
cd ~
curl -O https://beta.quicklisp.org/quicklisp.lisp
sbcl --noinform --disable-debugger --load quicklisp.lisp \
     --eval '(quicklisp-quickstart:install)' --quit
```

## 5. Vá 1 dòng cho SBCL mới
Trong `~/andes-stable/Help/model.cl`, thêm **ngay trước** dòng `(use-package :andes-database)`:
```lisp
(shadowing-import (find-symbol "CREATE" :andes-database))
```
> Lý do: SBCL ≥ 2.x export `SB-EXT:CREATE` → xung đột tên với `ANDES-DATABASE:CREATE`.

## 6. Build solver C++
```bash
cd ~/andes-stable/Algebra/src
make executable        # -> ../../solver-program và ../../libSolver.so
```
> **Vì sao không nên dùng `make install-solver` ở thư mục gốc:** bản thân target
> `install-solver` **không sai**; lỗi là **Makefile gốc bị parse lỗi** — mục
> `configure-httpd` (dòng ~35–38) dùng **8 space thay vì TAB**, mà GNU make parse
> **toàn bộ** Makefile trước khi chạy bất kỳ target nào.
> Sửa 3 dòng đó thành TAB rồi mới dùng make ở root:
> ```bash
> sed -i -E 's/^[[:space:]]+a2enmod/\ta2enmod/' ~/andes-stable/Makefile
> ```

## 7. Chạy help server (chế độ KHÔNG cần DB)
Dùng file sẵn có **`scripts\start_server.lisp`** (đã tự dò `$HOME`):
```bash
cp /mnt/d/ANDES/scripts/start_server.lisp ~/start_server.lisp
sbcl --noinform --disable-debugger --script ~/start_server.lisp
```
> `*skip-db*` bỏ qua MySQL. Bỏ dòng đó nếu đã cấu hình DB đúng (xem "Còn thiếu").

## 8. Phục vụ web-UI (static + proxy tới 8080)
Cần **Dojo 1.12** (zip stable không kèm):
```bash
cd /tmp
curl -sL -O https://download.dojotoolkit.org/release-1.12.2/dojo-release-1.12.2.zip
unzip -q -o dojo-release-1.12.2.zip
cp -r dojo-release-1.12.2/{dojo,dijit,dojox} ~/andes-stable/web-UI/
```
Dùng file sẵn có **`scripts\serve_andes.py`** (bind `127.0.0.1`, dùng `ThreadingTCPServer`
để UI không bị treo khi help server chậm):
```bash
cp /mnt/d/ANDES/scripts/serve_andes.py ~/serve_andes.py
python3 ~/serve_andes.py     # web-UI=~/andes-stable/web-UI, upstream=8080, port=8000
```
> Tham số tuỳ chọn: `serve_andes.py [webui_dir] [upstream] [port]`.

## 9. Mở giao diện (từ Windows)
- **http://localhost:8000/login.html** — nhập section / user / problem (vd `s2e`, `kt1a`, `vec1ay`) — gọn nhất
- hoặc thẳng: **http://localhost:8000/index.html?u=joe1&p=s2e&s=54321**
  (thiếu `s` sẽ mặc định `1234`)

Dừng:
```powershell
wsl -d Ubuntu -u root -- pkill -f sbcl
wsl -d Ubuntu -u root -- pkill -f serve_andes.py
```

---

# Chạy Andes desktop 2011 (trong máy ảo)

App 2011 **tự chứa** (workbench + help + solver), không cần server:
- `fbd-tcp.exe` = Andes Physics Workbench (giao diện vẽ)
- `Helpsys.dxl` (13.5 MB) = Help System (ảnh Allegro Lisp)
- `solver.dll` = bộ giải; kèm `Problems\`, `KB\`, `Review\`

**Chỉ cần copy 1 file** vào VM:
```
D:\ANDES\references\installer\Andes1311.exe   (26.5 MB)
```
→ chạy trong VM → tự giải nén → `Setup.exe` → mở Andes từ Start menu.

- Bản **32-bit**; `AndesLicense.txt` (đi kèm installer) ghi **2004** →
  hợp với **Win10 x32 / Windows XP / 7 32-bit**.
- Có sẵn: VMware Workstation 17 + `Win10_21H2_English_x32.iso` (thiếu ISO XP/7).
- **Không cần** copy cả `D:\ANDES` (724 MB) — `source/`, `workbench/`, `archives/` là của bản web.

---

# Trạng thái: chạy được gì / còn thiếu gì

| Hạng mục | Trạng thái |
|---|---|
| Web-UI + server trên WSL | ✅ Chạy, mở được ở `http://localhost:8000` |
| Nạp hệ lõi `:andes` (SGG/KB) | ✅ Biên dịch sạch |
| Nạp `:andes-help` | ✅ Biên dịch sạch (sau patch bước 5) |
| Build solver C++ | ✅ `solver-program` + `libSolver.so` |
| Help server + JSON-RPC | ✅ (Hunchentoot, port 8080) |
| `open-problem` (mở đề + chạy solver) | ⚠️ Nạp `.prb`, chạy solver, dựng đồ thị → **lỗi `TYPE-ERROR: NIL not CONS`** |
| Workbench PyQt6 | ✅ Chạy ngay (`python main.py`) |
| Andes desktop 2011 | ⚠️ **Chưa kiểm chứng** (mới xác nhận installer tự chứa) |

## Còn thiếu / cần xử lý
1. **Repo `problems/` (định nghĩa đề) — KHÔNG công khai, có bản quyền.**
   Là nguyên nhân chính của lỗi `open-problem`. Muốn đủ: xin SSH qua `help@andestutor.org`.
   `.prb` có **đề + đồ thị lời giải**, nhưng thiếu **metadata KB** (phrases/keywords/entry-tests).
2. **MySQL 8.4 không tương thích schema 2011** — `create_REVIEWED_PROBLEMS.sql`
   lỗi foreign key. Nên dùng **MariaDB / MySQL cũ**, hoặc chạy `*skip-db*` (mất log học sinh).
3. **Apache + cấu hình web-UI đầy đủ** — hiện dùng proxy Python thay cho Apache.
4. Nhánh `stable` **vẫn có trên GitHub** (`git clone -b stable`); zip cục bộ chỉ là bản offline.
5. Cảnh báo: **đừng nhầm** `docs.andes.app` / `CURENT/andes` (thư viện hệ thống điện) với Andes gia sư Vật lý.

---

# Troubleshooting

**`open-problem` trả `TYPE-ERROR: NIL is not of type CONS` (tại `SG-PSMG->SYSENTS`)**
- Kiểm tra `~/andes-stable/solutions/` có `.prb` (vd `KT1A.prb`); nếu rỗng → làm lại bước 2.
- Dùng đúng tên problem như gợi ý trong `web-UI/login.html` (`s2e`, `kt1a`, `vec1ay`...).
- Xem log Hunchentoot: `~/andes-stable/help-server.log`.
- Thử trong SBCL: nạp `:andes` rồi gọi `(test-load-prbs)` (định nghĩa ở `KB/makeprob.cl:355`)
  để kiểm tra việc nạp đề.
- Nguyên nhân gốc: **thiếu repo `problems/`** → vài trường KB là NIL. Chưa có repo thì khó tránh.

**Trang web trắng / không load**
- F12 → Console xem lỗi JS; kiểm tra đã copy `dojo/dojo.js` (bước 8).
- Kiểm tra proxy:
  `curl -s -X POST -H 'Content-Type: application/json' --data '{}' http://localhost:8000/andes-help`

**MySQL lỗi khi tạo schema**
- Dùng **MariaDB / MySQL cũ**, hoặc chạy `*skip-db*` (bước 7).

**`make` ở thư mục gốc báo `missing separator`**
- Do `configure-httpd` dùng space thay TAB (xem bước 6) — sửa bằng `sed`, hoặc tránh `make` ở root.

---

# Nguồn trên mạng cho project Andes

Chú thích: ✅ dùng được · ❌ chết/không truy cập · ⚠️ cảnh báo/không liên quan.
(Trạng thái kiểm tra ngày 2026-11-20.)

## 1. Mã nguồn chính thức
- ✅ https://github.com/bvds/andes — repo chính (thứ mình chạy). `default_branch = master`
  nhưng **có nhiều nhánh khác, gồm `stable`** (và `stable-with-logging`, `ubuntu-help-server`,
  `Andes2`...). Commit cuối 2018-05-30; license **LGPL-3.0** (kèm GPL-3.0 trong repo).
  Danh sách nhánh: https://api.github.com/repos/bvds/andes/branches ·
  `git clone -b stable https://github.com/bvds/andes.git`
- ✅ https://github.com/bvds/AndysComet — "Branch for Andes Physics Tutor"
- ✅ https://github.com/mnguyen4/AndysComet — fork sinh viên (whiteboard/chat, CometD)
- ✅ https://github.com/MattSmithASU/Andyscomet — bản AndysComet đầy đủ (Maven + CometD)

## 2. Trang chính thức
- ⚠️ http://www.andestutor.org/ — site chính; khi kiểm tra **không truy cập được**.
  Thử lưu trữ: https://web.archive.org/web/*/andestutor.org
- ❌ https://www.bvds.be/web-UI/ — server demo cũ; trả **503**
- ✅ Problem chooser (link trong `web-UI/login.html`): http://www.andestutor.org/sets/

## 3. Bộ đề (bản quyền — KHÔNG công khai)
- ❌ `problems/`, `solutions/` **không có** trên GitHub. Tìm `Andes-problems` chỉ ra
  các repo đại học không liên quan.
- ❌ Token `"Andes2Problem"` (đặc trưng của file `.prb`) **không được index công khai**.
- ✉️ Xin quyền: `help@andestutor.org` (truy cập SSH, theo `documentation/install.md`).
- Thay thế cục bộ: **583 file `.prb`** trong `references\problems\Andes1311\Problems\`.

## 4. Toolchain tải về
- ✅ SBCL — https://www.sbcl.org/ · bảng tải: https://www.sbcl.org/platform-table.html ·
  SourceForge: https://sourceforge.net/projects/sbcl/files/sbcl/ ·
  git: `git clone git://git.code.sf.net/p/sbcl/sbcl`
  - Windows x64: https://prdownloads.sourceforge.net/sbcl/sbcl-2.6.10-x86-64-windows-binary.msi
- ✅ Quicklisp — https://www.quicklisp.org/beta/ · file cài: https://beta.quicklisp.org/quicklisp.lisp
- ✅ Dojo 1.12 — https://download.dojotoolkit.org/release-1.12.2/dojo-release-1.12.2.zip ·
  git: https://github.com/dojo/dojo (tag `1.12`)
- ✅ Thư viện Lisp (Quicklisp tự tải): `hunchentoot`, `cl-json`, `usocket`, `bordeaux-threads`...
- ✅ MySQL/MariaDB, Apache, PHP (qua `apt`).

## 5. Tài liệu nghiên cứu
- ✅ VanLehn 2005 — *The Andes Physics Tutoring System: Five Years of Evaluations*
  (bản PDF cục bộ: `references\papers\VanLehn_2005_Andes_Five_Years.pdf`)
- ✅ DTIC ADA524093 — *An Assessment of the Andes Tutor* — https://archive.org/details/DTIC_ADA524093
- ✅ *Andes: A Coached Problem Solving Environment for Physics* —
  https://www.researchgate.net/publication/225129001_Andes_A_Coached_Problem_Solving_Environment_for_Physics
- ✅ *The Andes Physics Tutoring System: Lessons Learned* —
  https://www.researchgate.net/publication/220049813_The_Andes_Physics_Tutoring_System_Lessons_Learned
- ✅ Springer chapter — https://link.springer.com/chapter/10.1007/3-540-45108-0_17

## 6. ⚠️ CẢNH BÁO — nguồn KHÔNG liên quan (đừng nhầm)
- https://docs.andes.app/ và https://github.com/CURENT/andes — **ANDES là thư viện Python
  mô phỏng hệ thống điện**, KHÔNG phải gia sư Vật lý.
- https://andesapp.github.io/ — case study điện lực.

## 7. Đường dẫn nội bộ quan trọng (trong repo)
- Tài liệu: `documentation/install.md`, `documentation/server.md`,
  `documentation/develop.md`, `documentation/sgg.txt`, `documentation/data_structures.html`
- Lõi giải: `Knowledge/BubbleGraph.cl`, `KB/*.cl`, `Algebra/src/*.cpp`
- API web: `web-UI/andes/andes3.smd` (mô tả JSON-RPC, target `/andes-help`)
- Schema DB: `LogProcessing/database/*.sql`