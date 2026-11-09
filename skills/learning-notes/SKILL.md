---
name: learning-notes
description: Lưu kiến thức trọng tâm của phiên học vào learning/ (notes theo chủ đề, glossary, câu hỏi ôn tập, tiến độ). Dùng khi người học nói "lưu lại", "save", "kết thúc phiên", hoặc khi agent đề xuất lưu cuối một chủ đề.
---

# Skill: learning-notes

Mục tiêu: biến cuộc hội thoại thành ghi chú **ngắn, có dẫn chứng, dễ ôn lại**.
Không phải chép lại hội thoại.

## Quy trình

### 1. Đề xuất trước khi ghi
Liệt kê các ý định lưu (mỗi ý 1 dòng, kèm nhãn nguồn) và file đích, ví dụ:

```
Sẽ lưu vào learning/notes/power.md:
  1. UPS online double-conversion: luôn chạy qua inverter → không có thời gian chuyển mạch  [dc-design-handbook tr.34 (sách 18), §2.3]
  2. N+1 vs 2N: ...  [tia-942 tr.12]
Thuật ngữ mới → glossary.md: UPS, PDU, ATS
Câu hỏi ôn tập → questions.md: 3 câu (2 câu bạn trả lời sai hôm nay)
```

**Chờ người học xác nhận / bỏ bớt / sửa** rồi mới ghi.

### 2. Ghi notes — `learning/notes/<chủ-đề>.md`
- Một file cho một chủ đề (power, cooling, network, tier…), không tạo file theo ngày.
- File đã có → **cập nhật vào đúng mục**, gộp ý trùng, không chép lặp.
- Chưa có → tạo theo mẫu bên dưới và thêm vào `learning/INDEX.md`.
- Mỗi ý giữ nguyên nhãn nguồn: `[<id> tr.X]` (kèm `(sách N)`, `§mục` nếu có), `[kiến thức chung]`, `[suy luận]`.
- Ý quan trọng (định nghĩa cốt lõi, số liệu, hình) → biến nhãn thành link tới file chương để
  mở lại nhanh: `[tia-942 tr.45](../../docs/tia-942/chapters/03-power.md)`.
  Kiểm tra file chương đó thực sự chứa `<!-- page 45 ` trước khi ghi link.
- Hình từ tài liệu → nhúng luôn: `![tia-942 tr.45](../../docs/tia-942/images/p0045-01.png)`.
- Viết ngắn, theo ý; giữ sơ đồ Mermaid/ASCII đã dùng trong phiên nếu nó giúp hiểu.
- Ghi lại **hiểu lầm đã được sửa** của người học — đây là phần giá trị nhất để ôn.

Mẫu file chủ đề:

```markdown
# <Chủ đề>

> Cập nhật: YYYY-MM-DD · Nguồn chính: <id>, <id>

## Ý chính
- ...  [nguồn]

## Sơ đồ
(mermaid / ascii)

## Ví dụ thực tế
- ...

## Hiểu lầm đã sửa
- ❌ Tưởng rằng ... → ✅ Thực ra ...  [nguồn]

## Liên kết
- Liên quan: [cooling](cooling.md) — vì ...

## Câu hỏi còn mở
- ...
```

### 3. Glossary — `learning/glossary.md`
Thêm thuật ngữ mới theo thứ tự ABC, mỗi dòng: thuật ngữ — định nghĩa 1 câu — nguồn.
Đã có thì chỉ sửa nếu định nghĩa mới chính xác hơn.

### 4. Câu hỏi ôn tập — `learning/questions.md`
- Thêm 2–4 câu trắc nghiệm, **ưu tiên câu người học trả lời sai** trong phiên.
- Định dạng theo mẫu có sẵn trong file (đáp án và giải thích để trong `<details>`).
- Cập nhật cột trạng thái của câu cũ đã được hỏi lại trong phiên:
  đúng → tăng `đúng liên tiếp`; sai → về 0.
- Câu có `đúng liên tiếp` ≥ 3 → chuyển xuống mục "Đã thuộc".

### 5. Tiến độ — `learning/INDEX.md`
- Cập nhật trạng thái chủ đề: chưa học / đang học / đã học / cần ôn.
- Thêm 1 dòng vào "Nhật ký phiên": ngày, đã học gì, nguồn đã đọc.
- Ghi "Gợi ý phiên tới" (1–3 mục) dựa trên câu hỏi còn mở và câu sai.

### 6. Báo lại
Liệt kê các file đã thay đổi, 1 dòng mỗi file. Không in lại nội dung đã ghi.

## Không làm
- Không ghi ý chưa có nguồn mà gắn nhãn như có nguồn.
- Không ghi những gì người học đã bỏ ở bước 1.
- Không xóa notes cũ; nếu ý cũ sai → sửa và ghi chú ngắn "(đã sửa YYYY-MM-DD: ...)".
