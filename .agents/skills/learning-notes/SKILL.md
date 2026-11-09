---
name: learning-notes
description: Lưu kiến thức trọng tâm của phiên học vào learning/ (notes theo chủ đề gộp nhiều nguồn, glossary, câu hỏi ôn tập, tiến độ theo nguồn và theo chủ đề) và bài thực hành vào labs/. Dùng khi người học nói "lưu lại", "save", "kết thúc phiên", "lưu bài lab", hoặc khi agent đề xuất lưu cuối một chủ đề.
---

# Skill: learning-notes

Mục tiêu: biến cuộc hội thoại thành ghi chú **ngắn, có dẫn chứng, dễ ôn lại**.
Không phải chép lại hội thoại.

Nguyên tắc chính: **notes theo chủ đề, tiến độ theo nguồn.** Dù phiên học một cuốn hay
nhiều cuốn, kiến thức luôn được gộp vào file chủ đề; vị trí đọc của từng cuốn ghi riêng
trong bảng tiến độ.

## Quy trình

### 1. Đề xuất trước khi ghi
Liệt kê các ý định lưu (mỗi ý 1 dòng, kèm nhãn nguồn) và file đích, ví dụ:

```
Phạm vi phiên: một nguồn: ccna-v1, Ch.8
Sẽ lưu vào learning/notes/vlan-8021q.md (file đã có, thêm vào "Ý chính"):
  1. Trunk 802.1Q chèn tag 4 byte giữa MAC nguồn và EtherType  [ccna-v1 tr.210 (sách 188), §8.2]
  2. Native VLAN không gắn tag → lệch native VLAN hai đầu trunk gây rò traffic giữa VLAN  [ccna-v1 tr.214]
Thuật ngữ mới → glossary.md: native VLAN, DTP
Câu hỏi ôn tập → questions.md: 3 câu (2 câu bạn trả lời sai hôm nay)
Tiến độ: ccna-v1 → "Ch.8 §8.2 · tr.214"
```

**Chờ người học xác nhận / bỏ bớt / sửa** rồi mới ghi.

### 2. Ghi notes — `learning/notes/<chủ-đề>.md`
- Một file cho một chủ đề (tên slug, vd. `vlan-8021q`, `lacp-bonding`, `stp-rstp`), không tạo
  file theo ngày, **không tạo file theo sách**.
- File đã có (kể cả do phiên với nguồn khác tạo ra) → **cập nhật vào đúng mục**, gộp ý trùng,
  không chép lặp. Một ý được nhiều nguồn xác nhận → giữ 1 dòng, gắn đủ nhãn:
  `[ccna-v1 tr.210] [network-warrior tr.95]`.
- Chưa có → tạo theo mẫu bên dưới và thêm vào "Bản đồ chủ đề" trong `learning/INDEX.md`.
- Mỗi ý giữ nguyên nhãn nguồn: `[<id> tr.X]` (kèm `(sách N)`, `§mục` nếu có), `[kiến thức chung]`, `[suy luận]`.
- Ý quan trọng (định nghĩa cốt lõi, số liệu, hình) → biến nhãn thành link tới file chương để
  mở lại nhanh: `[ccna-v1 tr.210](../../docs/ccna-v1/chapters/09-vlans.md)`.
  Kiểm tra file chương đó thực sự chứa `<!-- page 210 ` trước khi ghi link.
- Hình từ tài liệu → nhúng luôn: `![ccna-v1 tr.210](../../docs/ccna-v1/images/p0210-01.png)`.
- Viết ngắn, theo ý; giữ sơ đồ Mermaid/ASCII đã dùng trong phiên nếu nó giúp hiểu.
- Các nguồn có góc nhìn khác nhau hoặc bổ sung nhau → ghi vào mục "Góc nhìn từ các nguồn".
- Ghi lại **hiểu lầm đã được sửa** của người học. Đây là phần giá trị nhất để ôn.

Mẫu file chủ đề:

```markdown
# <Chủ đề>

> Cập nhật: YYYY-MM-DD · Nguồn đã dùng: <id>, <id>

## Ý chính
- ...  [nguồn]

## Sơ đồ
(mermaid / ascii)

## Ví dụ thực tế
- ...

## Góc nhìn từ các nguồn
| Nguồn | Mạnh ở | Ghi chú |
|---|---|---|
| <id> | lý thuyết / cấu hình / vận hành… | cũ ở điểm nào, khác nguồn khác ở đâu |

## Hiểu lầm đã sửa
- ❌ Tưởng rằng ... → ✅ Thực ra ...  [nguồn]

## Liên kết
- Liên quan: [stp-rstp](stp-rstp.md) — vì ...
- Bài lab: [../../labs/<slug>.md]

## Câu hỏi còn mở
- ...
```

Mục "Góc nhìn từ các nguồn" chỉ thêm khi đã có từ 2 nguồn trở lên.

### 3. Glossary — `learning/glossary.md`
Thêm thuật ngữ mới theo thứ tự ABC, mỗi dòng: thuật ngữ — định nghĩa 1 câu — nguồn.
Đã có thì chỉ sửa nếu định nghĩa mới chính xác hơn.

### 4. Câu hỏi ôn tập — `learning/questions.md`
- Thêm 2–4 câu trắc nghiệm, **ưu tiên câu người học trả lời sai** trong phiên.
- Định dạng theo mẫu có sẵn trong file (đáp án và giải thích để trong `<details>`).
  Dòng tiêu đề câu ghi chủ đề (slug của file notes), không ghi tên sách.
- Cập nhật cột trạng thái của câu cũ đã được hỏi lại trong phiên:
  đúng → tăng `đúng liên tiếp`; sai → về 0.
- Câu có `đúng liên tiếp` ≥ 3 → chuyển xuống mục "Đã thuộc".

### 5. Bài thực hành — `labs/<slug>.md` (chỉ khi phiên có làm lab)
- Một file cho một bài lab (vd. `lacp-bond-ovs.md`). Ghi: mục tiêu, môi trường, các bước
  và lệnh **người học đã thực sự chạy**, kết quả quan sát được, lỗi đã gặp và cách sửa,
  bước gây lỗi có chủ đích và triệu chứng.
- Đánh dấu ⚠️ các lệnh có thể làm mất kết nối/dữ liệu.
- Thêm link từ file notes chủ đề liên quan (mục "Liên kết").

### 6. Tiến độ — `learning/INDEX.md`
- **Tiến độ theo nguồn**: cập nhật dòng của nguồn đã đọc theo trình tự trong phiên (chế độ
  một nguồn): "Vị trí hiện tại" = chương/mục + trang PDF cuối cùng đã học xong, "Trạng thái",
  "Cập nhật". Chế độ theo chủ đề hoặc hỏi nhanh **không** đẩy vị trí đọc tuần tự; chỉ ghi
  nguồn vào nhật ký.
  Nguồn chưa có dòng → thêm dòng (cách đọc: hỏi người học, mặc định `tra cứu`).
- **Bản đồ chủ đề**: cập nhật trạng thái (chưa học / đang học / đã học / cần ôn) và cột
  "Nguồn đã dùng".
- **Nhật ký phiên**: thêm 1 dòng: ngày, phạm vi (`một nguồn: <id>` / `chủ đề: <slug>` / `hỏi nhanh`),
  đã học gì, nguồn đã đọc.
- **Gợi ý phiên tới** (1–3 mục): dựa trên vị trí đọc, câu hỏi còn mở và câu sai. Khi một chủ
  đề vừa học từ một nguồn đã có thêm nguồn khác trong CATALOG, có thể gợi ý một phiên
  "theo chủ đề" để đối chiếu.

### 7. Báo lại
Liệt kê các file đã thay đổi, 1 dòng mỗi file. Không in lại nội dung đã ghi.

## Không làm
- Không ghi ý chưa có nguồn mà gắn nhãn như có nguồn.
- Không ghi những gì người học đã bỏ ở bước 1.
- Không tạo file notes riêng cho từng sách.
- Không ghi vào bài lab những lệnh người học chưa chạy như thể đã chạy.
- Không xóa notes cũ; nếu ý cũ sai → sửa và ghi chú ngắn "(đã sửa YYYY-MM-DD: ...)".
