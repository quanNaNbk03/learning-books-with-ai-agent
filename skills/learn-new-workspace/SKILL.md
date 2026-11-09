---
name: learn-new-workspace
description: Dựng và bảo trì learning workspace (học từ sách/tài liệu cùng agent) — tạo workspace mới cho một chủ đề, chuyển một thư mục có sẵn (PDF, ghi chú cũ, skill cục bộ cũ) thành workspace, hoặc nâng cấp AGENTS.md của workspace theo template mới nhất. Dùng khi người học nói "tạo workspace học <chủ đề>", "chuyển thư mục này thành learning workspace", "cập nhật/nâng cấp workspace theo template".
---

# Skill: learn-new-workspace

`SKILL_DIR` là **thư mục chứa file SKILL.md này** (thường là `~/.agents/skills/learn-new-workspace`
hoặc `~/.claude/skills/learn-new-workspace`). Khung workspace nằm ở `$SKILL_DIR/templates/`:

| File trong `templates/` | Thành file trong workspace |
|---|---|
| `AGENTS.md` | `AGENTS.md` (luật dạy học, có `{{TOPIC}}`) |
| `README.md` | `README.md` (hướng dẫn cho người) |
| `gitignore` | `.gitignore` |
| `docs/CATALOG.md` | `docs/CATALOG.md` |
| `learning/INDEX.md`, `glossary.md`, `questions.md` | `learning/…` |
| _(tạo mới)_ | `CLAUDE.md` = `@AGENTS.md`, `docs/inbox/`, `learning/notes/`, `labs/` |

Skill `learn-add-source`, `learn-notes` và skill này được cài **global**, không chép vào workspace.

**Workspace được nhận diện** khi có cả `AGENTS.md`, `docs/CATALOG.md`, `learning/INDEX.md`.

## Chọn chế độ

| Thư mục hiện tại | Người học nói | Chế độ |
|---|---|---|
| Trống hoặc gần trống | "tạo workspace học …" | **A. Tạo mới** |
| Có file (PDF, ghi chú, skill cũ…) nhưng chưa là workspace | "chuyển thư mục này…", hoặc "tạo workspace" | **B. Chuyển đổi** |
| Đã là workspace | "cập nhật / nâng cấp theo template" | **C. Nâng cấp** |

Không khớp (vd. người học nói "tạo mới" nhưng thư mục đã là workspace) → nói rõ và hỏi lại.

**Chặn chung cho cả 3 chế độ:**
- Thư mục hiện tại trông như repo code (`go.mod`, `package.json`, `Cargo.toml`, `src/`…)
  → hỏi lại trước khi làm bất cứ gì; đề xuất tạo workspace ở thư mục khác.
- Chỉ làm việc trong **thư mục hiện tại**. Người học muốn tạo ở chỗ khác → hướng dẫn họ tạo
  thư mục, mở agent ở đó rồi gọi lại (Codex trong sandbox thường không ghi được ra ngoài).
- **Mọi thay đổi đều đưa kế hoạch ra trước, chờ người học xác nhận rồi mới ghi.**
- Không xóa file của người học. File cần bỏ → dời vào `_to_delete/` và báo lại.

---

## A. Tạo mới

### 1. Hỏi (gộp trong một lượt, người học có thể bỏ trống câu nào cũng được)
1. Tên chủ đề (vd. "Networking (L2–L4, Linux)").
2. Mục tiêu: học để làm được gì, đến mức nào.
3. Có thực hành không? Nếu có: môi trường lab (vd. "VM trên Proxmox, Linux + Open vSwitch").
4. Đã có sách/tài liệu nào chưa? (liệt kê tên)

### 2. Đề xuất kế hoạch
- Danh sách file sẽ tạo (bảng ở trên).
- Nội dung đề xuất cho mục **0. Cấu hình chủ đề** của `AGENTS.md`: "Có thực hành" lấy từ câu 3;
  "Thuật ngữ giữ tiếng Anh", "Phép so sánh nên dùng", "Sơ đồ hay dùng" do bạn đề xuất dựa
  trên chủ đề và mục "Người học" (người học sửa hoặc bỏ).
- Với mỗi sách ở câu 4: đề xuất id (chữ thường, số, gạch nối, có edition nếu cần,
  vd. `ccna-v1`, `network-warrior-2e`) → sẽ tạo thư mục trống `docs/<id>/`.

Chờ xác nhận.

### 3. Dựng khung
```bash
bash "$SKILL_DIR/scripts/scaffold.sh" . "<Tên chủ đề>"
```
Script không ghi đè: báo xung đột (exit 2) → dừng và hỏi người học (có thể là chế độ B/C).

### 4. Điền nội dung đã xác nhận
- `AGENTS.md` mục 0: thay các ô `_(chưa điền…)_` bằng nội dung đã chốt; ô người học bỏ trống
  thì giữ nguyên `_(chưa điền…)_` để phiên học đầu đề xuất lại.
- `learning/INDEX.md` mục **Mục tiêu**: câu 2.
- Tạo `docs/<id>/` cho từng sách đã chốt.

### 5. Kiểm tra môi trường
- Chạy `python -c "import pymupdf4llm"`. Lỗi → đưa lệnh
  `pip install -r <thư mục skill learn-add-source>/scripts/requirements.txt` để người học tự chạy.
- Kiểm tra skill `learn-add-source` và `learn-notes` có trong danh sách skill hiện có; thiếu →
  báo người học chạy lại `install.sh` của repo template.

### 6. Báo lại
Danh sách file đã tạo (1 dòng/file) và bước tiếp theo:
"Thả PDF vào `docs/<id>/` rồi nói *thêm tài liệu <id>*". Nếu `docs/<id>/` đã có file gốc →
hỏi có chạy `learn-add-source` luôn không.

---

## B. Chuyển đổi thư mục có sẵn

### 1. Quét
Liệt kê (không đọc nội dung sách): file tài liệu (PDF/EPUB/MD/TXT) ở đâu, các file luật cũ
(`AGENTS.md`, `CLAUDE.md`), skill cục bộ cũ (`skills/`, `.agents/skills/`, `.claude/skills/`, kể cả
symlink), thư mục `docs/`, `learning/`, `labs/` đã có, `docs/<id>/chapters/` đã chuyển đổi.

### 2. Đề xuất kế hoạch, ví dụ:
```
Tài liệu:
  - TIA-942-B.pdf (gốc)          → docs/tia-942/TIA-942-B.pdf
  - docs/dc-handbook/ (đã có chapters/) → giữ nguyên
Luật:
  - AGENTS.md cũ                 → _to_delete/AGENTS.md.old; tạo AGENTS.md mới từ template
    · chuyển sang mục 0: "Người học", ví dụ/thuật ngữ riêng của chủ đề tìm thấy trong bản cũ
  - CLAUDE.md                    → thay bằng "@AGENTS.md" (bản cũ → _to_delete/)
Skill cục bộ (đã có bản global, để lại sẽ trùng tên):
  - .agents/skills/add-source, .agents/skills/learning-notes, .claude/skills → _to_delete/
Dữ liệu học (giữ nguyên, chỉ bổ sung phần còn thiếu theo template):
  - learning/notes/*.md, learning/questions.md, learning/glossary.md
  - learning/INDEX.md            → thêm bảng "Tiến độ theo nguồn" (1 dòng/nguồn trong docs/)
                                   và cột "Phạm vi" cho Nhật ký phiên
  - docs/CATALOG.md              → giữ; nếu chưa có thì tạo từ template
Tạo thêm: docs/inbox/, labs/
```
Chờ xác nhận. Người học có thể bỏ bớt từng dòng.

### 3. Thực hiện
- Dời file bằng `mv`/`git mv` (nếu là repo git). Không xóa: dùng `_to_delete/`.
- File khung còn thiếu → chép từ `$SKILL_DIR/templates/` (thay `{{TOPIC}}`).
- Bổ sung bảng/cột vào file `learning/` đã có: **chỉ thêm**, không xóa hay viết lại dòng dữ liệu cũ.
- Tài liệu gốc chưa có `chapters/` → không chuyển đổi ở đây; liệt kê để chạy `learn-add-source`.

### 4. Báo lại
File đã dời/tạo/sửa (1 dòng/file), nội dung `_to_delete/` để người học tự xóa, và các nguồn cần
chạy `learn-add-source`.

---

## C. Nâng cấp theo template

### 1. So sánh
- `AGENTS.md` của workspace với `$SKILL_DIR/templates/AGENTS.md`, **theo từng mục `## N.`**.
- Cấu trúc các file `learning/INDEX.md`, `learning/questions.md`, `docs/CATALOG.md` (chỉ tên mục
  và tiêu đề cột bảng) với bản template.

### 2. Đề xuất
Tóm tắt thay đổi theo mục (mục nào đổi, đổi gì — 1–2 dòng mỗi mục, không in cả file), và:
- **Giữ nguyên** mục `## 0. Cấu hình chủ đề` (kể cả `### Người học`) của workspace.
- Mục 1–12 (và mọi mục mới trong template) lấy theo template, thay `{{TOPIC}}` bằng chủ đề trong mục 0.
- Workspace có mục tự thêm mà template không có → hỏi giữ (đặt cuối file) hay bỏ.
- File `learning/` / `CATALOG.md` thiếu mục hoặc cột mà template có → đề xuất **thêm** (cột mới
  để trống ở các dòng cũ).
- `README.md` → thay bằng bản template (là hướng dẫn chung, không chứa dữ liệu học).

Chờ xác nhận.

### 3. Thực hiện và báo lại
Bản `AGENTS.md` cũ → `_to_delete/AGENTS.md.<YYYY-MM-DD>`. Ghi bản mới, liệt kê file đã đổi.

**Không bao giờ** sửa `docs/<id>/`, nội dung `learning/notes/`, `labs/`, hay dòng dữ liệu cũ
trong các bảng.

---

## Không làm
- Không chuyển đổi tài liệu (việc của `learn-add-source`), không ghi kiến thức (việc của `learn-notes`).
- Không ghi gì trước khi người học xác nhận kế hoạch.
- Không chép skill vào workspace.
- Không xóa file; không ghi đè file luật/dữ liệu mà không đưa bản cũ vào `_to_delete/`.
