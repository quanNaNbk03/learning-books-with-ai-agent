---
name: learn-add-source
description: Chỉ dùng trong learning workspace (thư mục có AGENTS.md, docs/CATALOG.md, learning/INDEX.md). Thêm tài liệu mới (PDF, EPUB, Markdown, TXT hoặc bài viết web) vào docs/ — chuyển sang markdown theo chương kèm hình ảnh, viết INDEX.md cho nguồn, cập nhật docs/CATALOG.md và bảng tiến độ trong learning/INDEX.md. Dùng khi người học tạo thư mục mới trong docs/, bỏ file vào docs/inbox/, hoặc nói "thêm tài liệu", "add source", "convert sách này".
---

# Skill: learn-add-source

Mục tiêu: mỗi nguồn mới đều có cùng cấu trúc — markdown theo chương có số trang,
hình ảnh tách riêng, mục lục tốt và ghi chú chất lượng chuyển đổi — để agent tìm
đúng chỗ, xem được hình và trích dẫn chính xác.

## 0. Điều kiện chạy (kiểm tra trước tiên)

Skill này được cài **global**, nên có mặt ở mọi dự án. Chỉ chạy khi thư mục hiện tại là
**learning workspace**, tức là có cả `AGENTS.md`, `docs/CATALOG.md` và `learning/INDEX.md`.

- Thiếu một trong ba → **dừng**, không tạo hay sửa file nào. Nói với người học: đây không phải
  learning workspace; nếu muốn biến thư mục này thành workspace thì dùng skill `learn-new-workspace`.
- Đang ở trong repo code (vd. có `go.mod`, `package.json`) mà người học nói "thêm tài liệu" →
  gần như chắc là ý khác (tài liệu cho code), không phải skill này.

`SKILL_DIR` dưới đây là **thư mục chứa file SKILL.md này** (thường là
`~/.agents/skills/learn-add-source` hoặc `~/.claude/skills/learn-add-source`). Mọi đường dẫn
`docs/`, `learning/` thì tính từ thư mục workspace hiện tại.

## Đầu vào (một trong hai)

- **A. Thư mục nguồn (khuyên dùng):** người học tạo `docs/<id>/` và bỏ file gốc vào,
  vd. `docs/tia-942/TIA-942-B.pdf`. Tên thư mục chính là id.
- **B. Inbox:** file nằm trong `docs/inbox/`, hoặc một URL bài viết.

Khi người học không nói rõ, tìm thư mục trong `docs/` có file gốc nhưng chưa có
`chapters/`, và file trong `docs/inbox/`; liệt kê để người học chọn.

## Quy trình

### 1. Xác nhận thông tin nguồn
- Xem metadata (tên, tác giả, năm, phiên bản) từ file hoặc trang đầu.
- Kiểm tra id: chữ thường, số, gạch nối (`dc-design-handbook`, `tia-942`).
  - Cách A: tên thư mục không hợp lệ → đề xuất tên mới, người học đổi tên.
  - Cách B: đề xuất id.
- Kiểm tra `docs/CATALOG.md` để tránh trùng (cùng sách khác phiên bản → hỏi người học:
  thay thế hay giữ cả hai).
- Hỏi **cách đọc** nguồn này (dùng cho bảng "Tiến độ theo nguồn" ở bước 5):
  `tuần tự` (đọc hết theo thứ tự) · `chọn lọc` (chỉ một số chương; có thể để trống,
  điền sau bước 4 khi đã có mục lục) · `tra cứu` (chỉ dùng khi học theo chủ đề).
  Người học không trả lời → mặc định `tuần tự`.
- **Chờ người học xác nhận** trước khi chạy bước 2.

### 2. Chuyển đổi
Chạy từ **thư mục gốc của workspace** (nơi có `AGENTS.md`):

```bash
# Cách A
python "$SKILL_DIR/scripts/convert.py" docs/<id>
# Cách B
python "$SKILL_DIR/scripts/convert.py" docs/inbox/<file> --id <id>
```

Kết quả: `docs/<id>/chapters/*.md` (có `<!-- page N -->` và link
`![hình tr.N](../images/pNNNN-MM.png)`), `docs/<id>/images/`, `chapters/_manifest.json`.

- Lần đầu cần cài thư viện: `pip install -r "$SKILL_DIR/scripts/requirements.txt"`
  (thường đã cài một lần trên máy; Codex trong sandbox chặn mạng thì nhờ người học tự chạy)
- Chương quá dài (> ~40 trang) → chạy lại với `--toc-level 2 --force`.
- PDF không có mục lục → script chia theo `--pages-per-part` (mặc định 30 trang).
- Hình quá mờ để đọc chữ → chạy lại `--dpi 200 --force`. Quá nhiều hình rác
  (icon, khung trang trí) → tăng `--min-image-px`. Không cần hình → `--no-images`.
- Bài viết web: lấy nội dung, lưu thành `docs/<id>/<id>.md` (dòng đầu ghi `Nguồn: <URL>`
  và ngày truy cập), tải hình quan trọng vào `docs/<id>/images/` nếu được, rồi chạy cách A.
- Không tự sửa nội dung trong `chapters/` ngoài việc người học yêu cầu.

### 3. Kiểm tra chất lượng (bắt buộc)
Đọc `_manifest.json` và các cảnh báo script in ra, rồi:
- Lấy mẫu 3–5 trang để so với bản gốc, ưu tiên trang trong `low_text_pages`,
  chương có nhiều `table_rows`, và chương có nhiều `images`.
- **Mở 2–3 file hình** trong `images/` để xem: hình có đúng là sơ đồ/hình minh họa không,
  có bị cắt mất phần nào không, chữ trong hình đọc được không.
- So số hình đã giữ với bản gốc ở vài trang có hình: hình bị thiếu (vd. sơ đồ vẽ bằng
  nhiều mảnh nhỏ bị lọc) → ghi lại trang đó.
- Kiểm tra chữ có lỗi font/mất dấu không, bảng có lệch cột không, tên chương đúng không.
- **Số trang:** mở 2 trang mẫu, so `<!-- page N printed=M -->` với số in thực tế trên trang
  (thường ở header/footer). PDF không có page labels → tự xác định độ lệch (vd. "số in =
  số PDF − 18 từ trang 19 trở đi") và ghi vào INDEX.md.
- **Thứ tự đọc trong trang:** với trang có 2 cột, sidebar, hộp ghi chú, kiểm tra đoạn văn
  không bị trộn lẫn giữa các cột. Thứ tự *giữa các trang* luôn đúng; thứ tự *trong trang*
  phụ thuộc bố cục. Trang lỗi → ghi vào "Chất lượng chuyển đổi".
- Tỉ lệ trang ít chữ cao (> 20%) → báo người học là PDF scan, cần OCR
  (cài Tesseract rồi chạy lại), chưa nên dùng nguồn này để trích dẫn.

### 4. Viết `docs/<id>/INDEX.md`
Dùng mẫu `$SKILL_DIR/templates/source-INDEX.md`. Với mỗi chương:
đọc lướt nội dung, viết tóm tắt 1–2 dòng, 3–6 thuật ngữ chính, và liệt kê
**hình quan trọng** (file + mô tả ngắn, vd. `p0045-01.png — sơ đồ luồng điện 2N`).
Chỉ mô tả hình đã thực sự mở xem. Ghi các vấn đề từ bước 3 vào
"Chất lượng chuyển đổi" kèm số trang cụ thể.

Với sách dài, làm theo từng nhóm chương và báo tiến độ, không cố đọc cả cuốn một lúc.

### 5. Cập nhật `docs/CATALOG.md` và `learning/INDEX.md`
- `docs/CATALOG.md`:
  - Thêm 1 dòng vào bảng "Danh sách nguồn".
  - Bổ sung bảng "Chủ đề → nguồn": dùng tên chủ đề đã có nếu phù hợp, chỉ tạo
    chủ đề mới khi cần. Ghi **tên chương thật của sách** kèm file
    (vd. `ccna-v1 → Ch.8 VLANs (09-...md)`), vì chế độ học theo chủ đề dựa vào bảng này
    để biết mở chương nào ở từng nguồn. **Đề xuất ánh xạ để người học xác nhận.**
  - Ghi chú độ tin cậy/độ mới (tiêu chuẩn chính thức, sách giáo trình, blog vendor…),
    và **thế mạnh** của nguồn so với các nguồn đã có (lý thuyết, cấu hình, vận hành thực tế…).
- `learning/INDEX.md`, bảng "Tiến độ theo nguồn": thêm 1 dòng
  `| <id> | <cách đọc> | — | chưa đọc | YYYY-MM-DD |`. Với `chọn lọc`, liệt kê tên các chương
  người học đã chọn. Xóa dòng mẫu `_(chưa có)_` nếu còn.

### 6. Báo cáo
Tóm tắt ngắn: id, số chương, số hình, chủ đề chính, các chương/trang chuyển đổi kém
cần chú ý, chủ đề nào giờ đã có từ 2 nguồn trở lên (học theo chủ đề được). Với cách B, nhắc người học có thể xóa file trong `docs/inbox/` (bản gốc đã
sao chép vào `docs/<id>/source.*`). Không tự xóa file của người học.

## Không làm
- Không viết tóm tắt cho chương chưa đọc, không mô tả hình chưa mở xem.
- Không bịa metadata (năm, phiên bản); thiếu thì ghi "chưa rõ".
- Không tạo notes học tập ở bước này — đó là việc của skill `learn-notes`.
