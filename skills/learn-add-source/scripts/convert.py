#!/usr/bin/env python3
"""
convert.py — Chuyển một tài liệu (PDF / EPUB / Markdown / TXT) thành các file
markdown theo chương, giữ dấu số trang và xuất hình ảnh, để agent đọc và trích
dẫn chính xác.

Hai cách dùng:

  A. Tạo thư mục nguồn rồi bỏ file vào (khuyên dùng):
       docs/tia-942/TIA-942-B.pdf
       python convert.py docs/tia-942            # id = tên thư mục

  B. Bỏ file vào inbox, script tạo thư mục và sao chép bản gốc:
       python convert.py docs/inbox/book.pdf --id tia-942

Kết quả:
    docs/tia-942/
    ├── TIA-942-B.pdf (hoặc source.pdf)   # bản gốc
    ├── chapters/
    │   ├── 00-front-matter.md
    │   ├── 01-introduction.md            # có <!-- page N --> và ![..](../images/..)
    │   └── _manifest.json                # chương, trang, hình, cảnh báo chất lượng
    └── images/
        ├── p0012-01.png                  # hình ở trang PDF 12
        └── ...

Tùy chọn:
    --id <slug>            bắt buộc với cách B; cách A lấy theo tên thư mục
    --docs-dir docs        thư mục chứa các nguồn
    --toc-level 1          tách chương theo cấp mục lục/heading
    --pages-per-part 30    số trang mỗi phần khi PDF không có mục lục
    --no-images            không xuất hình
    --dpi 150              độ phân giải khi xuất hình
    --image-format png     png hoặc jpg
    --min-image-px 60      bỏ hình có cạnh nhỏ hơn ngưỡng (icon, bullet)
    --repeat-pages 3       bỏ hình giống hệt nhau lặp lại trên >= N trang (logo, header)
    --no-copy              (cách B) không sao chép bản gốc
    --force                ghi đè chapters/ và images/ đã có

Ghi chú về số trang:
    <!-- page N --> là số trang PDF (vị trí vật lý, bắt đầu từ 1), có thể
    KHÁC số trang in trên sách. Nếu PDF có page labels, marker có thêm số in:
    <!-- page 45 printed=27 -->. Mỗi trang PDF xuất hiện đúng một lần, theo thứ tự.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

LOW_TEXT_THRESHOLD = 30  # ký tự; trang ít chữ hơn ngưỡng này nhiều khả năng là ảnh/scan
PAGED_EXT = {".pdf", ".epub", ".xps", ".fb2", ".mobi"}
TEXT_EXT = {".md", ".markdown", ".txt"}
SKIP_NAMES = {"index.md", "readme.md"}

for stream in (sys.stdout, sys.stderr):  # tránh lỗi in tiếng Việt trên Windows console
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------- tiện ích


def slugify(text: str, max_len: int = 50) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text[:max_len].rstrip("-")) or "untitled"


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


@dataclass
class Chapter:
    title: str
    start: int  # trang PDF, 1-based
    end: int
    pages: list[tuple[int, str]] = field(default_factory=list)
    low_text_pages: list[int] = field(default_factory=list)
    images: list[str] = field(default_factory=list)


@dataclass
class ImageStats:
    kept: int = 0
    dropped_small: int = 0
    dropped_repeated: int = 0


# ---------------------------------------------------------------- xác định nguồn


def resolve_input(args) -> tuple[Path, str, Path, bool]:
    """Trả về (file nguồn, id, thư mục đích, in_place)."""
    inp: Path = args.input
    docs_dir: Path = args.docs_dir

    if inp.is_dir():
        candidates = sorted(
            p for p in inp.iterdir()
            if p.is_file() and p.suffix.lower() in PAGED_EXT | TEXT_EXT
            and p.name.lower() not in SKIP_NAMES and not p.name.startswith(".")
        )
        if not candidates:
            sys.exit(f"Không thấy file tài liệu (.pdf .epub .md .txt) trong {inp}")
        if len(candidates) > 1:
            names = "\n  ".join(p.name for p in candidates)
            sys.exit(f"Có nhiều file trong {inp}, hãy chỉ rõ file:\n  {names}")
        src = candidates[0]
    elif inp.is_file():
        src = inp
    else:
        sys.exit(f"Không tìm thấy: {inp}")

    in_place = src.parent.resolve().parent == docs_dir.resolve() and src.parent.name != "inbox"
    if in_place:
        source_id = args.id or src.parent.name
        if source_id != src.parent.name:
            sys.exit(f"--id '{args.id}' khác tên thư mục '{src.parent.name}'. "
                     "Bỏ --id hoặc đổi tên thư mục.")
        out = src.parent
    else:
        if not args.id:
            sys.exit("Cần --id khi file không nằm trong docs/<id>/ (vd: --id tia-942)")
        source_id = args.id
        out = docs_dir / source_id

    if source_id != slugify(source_id):
        sys.exit(f"id/tên thư mục '{source_id}' không hợp lệ, gợi ý: {slugify(source_id)}")
    return src, source_id, out, in_place


# ---------------------------------------------------------------- PDF / EPUB


def plan_chapters(toc, page_count: int, toc_level: int, pages_per_part: int):
    """Trả về danh sách Chapter (chưa có nội dung) dựa trên mục lục (bookmark)."""
    entries = []
    for level, title, page in toc:
        if level <= toc_level and 1 <= page <= page_count:
            title = " ".join(str(title).split()) or "Untitled"
            if entries and entries[-1][1] == page:
                entries[-1] = (entries[-1][0] + " / " + title, page)
            else:
                entries.append((title, page))
    entries.sort(key=lambda e: e[1])

    chapters: list[Chapter] = []
    if entries:
        if entries[0][1] > 1:
            chapters.append(Chapter("Front matter", 1, entries[0][1] - 1))
        for i, (title, start) in enumerate(entries):
            end = entries[i + 1][1] - 1 if i + 1 < len(entries) else page_count
            if end >= start:
                chapters.append(Chapter(title, start, end))
        return chapters, True

    for start in range(1, page_count + 1, pages_per_part):
        end = min(start + pages_per_part - 1, page_count)
        chapters.append(Chapter(f"Part (pages {start}-{end})", start, end))
    return chapters, False


IMG_LINK = re.compile(r"!\[([^\]]*)\]\(([^)\s]*?src\.\w+-(\d+)-(\d+)\.(\w+))\)")


def process_images(page_text: dict[int, str], tmp_img: Path, images_dir: Path, opts,
                   stats: ImageStats) -> dict[int, list[str]]:
    """Lọc hình rác, đổi tên p<trang>-<số>.<ext>, sửa link về ../images/. Trả về hình theo trang."""
    import pymupdf

    refs = []  # (page, match)
    for pno, text in page_text.items():
        for m in IMG_LINK.finditer(text):
            refs.append((pno, m))

    info: dict[str, tuple[str, int, int]] = {}  # tên file -> (hash, w, h)
    pages_of_hash: dict[str, set[int]] = {}
    for pno, m in refs:
        f = tmp_img / Path(m.group(2)).name
        if not f.is_file() or f.name in info:
            continue
        data = f.read_bytes()
        h = hashlib.md5(data).hexdigest()
        try:
            pix = pymupdf.Pixmap(str(f))
            w, hgt = pix.width, pix.height
        except Exception:
            w = hgt = 0
        info[f.name] = (h, w, hgt)
        pages_of_hash.setdefault(h, set()).add(pno)

    images_dir.mkdir(parents=True, exist_ok=True)
    per_page: dict[int, list[str]] = {}
    seen_new: dict[str, str] = {}  # hash -> tên mới (hình trùng trong cùng trang/chương dùng chung file)

    def replace(pno: int):
        def _sub(m: re.Match) -> str:
            name = Path(m.group(2)).name
            if name not in info:
                return ""
            h, w, hgt = info[name]
            if min(w, hgt) < opts.min_image_px:
                stats.dropped_small += 1
                return ""
            if len(pages_of_hash[h]) >= opts.repeat_pages:
                stats.dropped_repeated += 1
                return ""
            if h in seen_new:
                new = seen_new[h]
            else:
                idx = len(per_page.get(pno, [])) + 1
                new = f"p{pno:04d}-{idx:02d}.{m.group(5)}"
                shutil.copy2(tmp_img / name, images_dir / new)
                seen_new[h] = new
                stats.kept += 1
            per_page.setdefault(pno, []).append(new)
            return f"![hình tr.{pno}](../images/{new})"
        return _sub

    for pno in sorted(page_text):
        text = IMG_LINK.sub(replace(pno), page_text[pno])
        page_text[pno] = re.sub(r"\n{4,}", "\n\n\n", text)
    return per_page


def convert_paged(src: Path, out: Path, opts):
    try:
        import pymupdf  # PyMuPDF >= 1.24
        import pymupdf4llm
    except ImportError:
        sys.exit("Thiếu thư viện. Chạy: pip install -r requirements.txt")

    doc = pymupdf.open(src)
    if doc.needs_pass:
        sys.exit("File được bảo vệ bằng mật khẩu, không chuyển được.")
    page_count = doc.page_count
    chapters, has_toc = plan_chapters(doc.get_toc(), page_count, opts.toc_level, opts.pages_per_part)
    meta = doc.metadata or {}

    # Làm việc trên bản sao tên cố định để tên file ảnh không chứa dấu cách/ngoặc
    tmp = out / ".convert-tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    work = tmp / f"src{src.suffix.lower()}"
    shutil.copy2(src, work)

    print(f"Đang chuyển {page_count} trang"
          f"{' (kèm hình)' if opts.images else ''}...", file=sys.stderr)
    kwargs = dict(page_chunks=True)
    if opts.images:
        kwargs.update(write_images=True, image_path=str(tmp / "img"),
                      image_format=opts.image_format, dpi=opts.dpi)
    chunks = pymupdf4llm.to_markdown(str(work), **kwargs)

    page_text: dict[int, str] = {}
    for i, chunk in enumerate(chunks):
        m = chunk.get("metadata") or {}
        pno = m.get("page_number") or m.get("page") or (i + 1)
        page_text[int(pno)] = chunk.get("text", "")

    stats = ImageStats()
    per_page: dict[int, list[str]] = {}
    if opts.images:
        per_page = process_images(page_text, tmp / "img", out / "images", opts, stats)
    shutil.rmtree(tmp, ignore_errors=True)

    for ch in chapters:
        for pno in range(ch.start, ch.end + 1):
            ch.pages.append((pno, page_text.get(pno, "")))
            if len(doc[pno - 1].get_text().strip()) < LOW_TEXT_THRESHOLD:
                ch.low_text_pages.append(pno)
            for img in per_page.get(pno, []):
                if img not in ch.images:
                    ch.images.append(img)

    # Số trang in trên sách (page labels: i, ii, 1, 2...) nếu PDF có định nghĩa
    labels = {}
    for pno in range(1, page_count + 1):
        try:
            label = doc[pno - 1].get_label()
        except Exception:
            label = ""
        if label:
            labels[pno] = label

    info = {
        "format": src.suffix.lower().lstrip("."),
        "page_count": page_count,
        "has_toc": has_toc,
        "page_labels": labels,
        "title": meta.get("title") or "",
        "author": meta.get("author") or "",
        "images": {"kept": stats.kept, "dropped_small": stats.dropped_small,
                   "dropped_repeated": stats.dropped_repeated} if opts.images else None,
    }
    return chapters, info


# ---------------------------------------------------------------- Markdown / TXT

MD_IMG = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)(\))")


def convert_markdown(src: Path, out: Path, toc_level: int):
    text = src.read_text(encoding="utf-8", errors="replace")
    chapters_dir = out / "chapters"
    outside = []

    def fix_link(m: re.Match) -> str:  # giữ link ảnh tương đối đúng khi file chuyển vào chapters/
        link = m.group(2)
        if re.match(r"^[a-z]+:", link, re.I) or link.startswith("/"):
            return m.group(0)
        target = (src.parent / link).resolve()
        if out.resolve() not in target.parents:
            outside.append(link)
        rel = os.path.relpath(target, chapters_dir.resolve()).replace(os.sep, "/")
        return f"{m.group(1)}{rel}{m.group(3)}"

    text = MD_IMG.sub(fix_link, text)
    heading = re.compile(rf"^#{{1,{toc_level}}}\s+(.+?)\s*#*\s*$", re.MULTILINE)
    fences = [m.span() for m in re.finditer(r"^```.*?^```", text, re.MULTILINE | re.DOTALL)]
    marks = [m for m in heading.finditer(text) if not any(a <= m.start() < b for a, b in fences)]

    chapters: list[Chapter] = []
    if not marks:
        chapters.append(Chapter(src.stem, 1, 1, pages=[(0, text)]))
    else:
        if text[: marks[0].start()].strip():
            chapters.append(Chapter("Front matter", 1, 1, pages=[(0, text[: marks[0].start()])]))
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            chapters.append(Chapter(m.group(1), 1, 1, pages=[(0, text[m.start():end])]))
    info = {"format": "md", "page_count": None, "has_toc": bool(marks), "title": "",
            "author": "", "images": None, "images_outside": sorted(set(outside))}
    return chapters, info


# ---------------------------------------------------------------- ghi kết quả


def table_rows(text: str) -> int:
    return len(re.findall(r"^\|.*\|\s*$", text, re.MULTILINE))


def write_output(chapters: list[Chapter], info: dict, src_name: str, out: Path, source_id: str):
    chapters_dir = out / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    paged = info["page_count"] is not None
    manifest_chapters = []
    width = max(2, len(str(len(chapters))))
    n = 0

    for ch in chapters:
        is_front = ch.title == "Front matter"
        num = 0 if is_front else (n := n + 1)
        fname = f"{num:0{width}d}-{'front-matter' if is_front else slugify(ch.title)}.md"

        labels = info.get("page_labels") or {}
        head = ["---", f"source: {source_id}", f"chapter: {yaml_str(ch.title)}"]
        if paged:
            head.append(f"pdf_pages: {ch.start}-{ch.end}")
            if labels.get(ch.start) or labels.get(ch.end):
                head.append(f"printed_pages: {yaml_str(labels.get(ch.start, '?') + '-' + labels.get(ch.end, '?'))}")
        head += ["---", ""]
        if paged:
            def marker(p: int) -> str:
                return f"<!-- page {p} printed={labels[p]} -->" if p in labels else f"<!-- page {p} -->"
            body = "\n".join(f"{marker(p)}\n\n{t.strip()}\n" for p, t in ch.pages)
        else:
            body = "\n".join(t.strip() + "\n" for _, t in ch.pages)
            if not body.lstrip().startswith("#"):
                body = f"# {ch.title}\n\n{body}"
        (chapters_dir / fname).write_text("\n".join(head) + "\n" + body, encoding="utf-8")

        manifest_chapters.append({
            "file": fname,
            "title": ch.title,
            "pdf_pages": [ch.start, ch.end] if paged else None,
            "printed_pages": [labels.get(ch.start), labels.get(ch.end)] if paged and labels else None,
            "chars": len(body),
            "table_rows": table_rows(body),
            "low_text_pages": ch.low_text_pages,  # nghi trang scan/ảnh -> cần đối chiếu
            "images": ch.images,                  # file trong images/
        })

    warnings = []
    if paged and not info.get("page_labels"):
        warnings.append("PDF không có page labels: chỉ có số trang PDF; số in trên sách có thể lệch "
                        "(xác định độ lệch thủ công rồi ghi vào INDEX.md nếu cần).")
    if paged and not info["has_toc"]:
        warnings.append("PDF không có mục lục (bookmark): đã chia đều theo số trang; "
                        "nên đặt lại tên các phần trong INDEX.md.")
    low = [p for c in chapters for p in c.low_text_pages]
    if paged and low:
        ratio = len(low) / info["page_count"]
        warnings.append(f"{len(low)} trang ít/không có chữ ({ratio:.0%}): có thể là trang scan "
                        "hoặc chỉ có hình. Nếu tỉ lệ cao, cần OCR (cài Tesseract).")
    empty = [c["file"] for c in manifest_chapters if c["chars"] < 100]
    if empty:
        warnings.append(f"Chương gần như rỗng: {', '.join(empty)}")
    if info.get("images_outside"):
        warnings.append("Markdown tham chiếu hình nằm ngoài thư mục nguồn (nên chuyển vào "
                        f"docs/{source_id}/images/): {', '.join(info['images_outside'])}")

    manifest = {"id": source_id, "source_file": src_name, **info,
                "chapters": manifest_chapters, "warnings": warnings}
    (chapters_dir / "_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="Chuyển tài liệu thành markdown theo chương, kèm hình.")
    ap.add_argument("input", type=Path, help="thư mục docs/<id>/ hoặc file .pdf .epub .md .txt")
    ap.add_argument("--id", help="id dạng slug (bắt buộc nếu file không nằm trong docs/<id>/)")
    ap.add_argument("--docs-dir", type=Path, default=Path("docs"))
    ap.add_argument("--toc-level", type=int, default=1)
    ap.add_argument("--pages-per-part", type=int, default=30)
    ap.add_argument("--no-images", dest="images", action="store_false")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--image-format", choices=["png", "jpg"], default="png")
    ap.add_argument("--min-image-px", type=int, default=60)
    ap.add_argument("--repeat-pages", type=int, default=3)
    ap.add_argument("--no-copy", action="store_true")
    ap.add_argument("--force", action="store_true")
    opts = ap.parse_args()

    src, source_id, out, in_place = resolve_input(opts)

    existing = [d for d in ("chapters", "images") if (out / d).exists()]
    if existing and not opts.force:
        sys.exit(f"{out} đã có {', '.join(existing)}/. Dùng --force để tạo lại.")
    for d in existing:
        shutil.rmtree(out / d)
    out.mkdir(parents=True, exist_ok=True)

    src_name = src.name
    if not in_place and not opts.no_copy:
        src_name = f"source{src.suffix.lower()}"
        shutil.copy2(src, out / src_name)

    ext = src.suffix.lower()
    if ext in PAGED_EXT:
        chapters, info = convert_paged(src, out, opts)
    elif ext in TEXT_EXT:
        chapters, info = convert_markdown(src, out, opts.toc_level)
    else:
        sys.exit(f"Chưa hỗ trợ định dạng {ext}. Với HTML/web: lưu thành .md rồi chạy lại.")

    manifest = write_output(chapters, info, src_name, out, source_id)

    print(f"\n{source_id}: {len(manifest['chapters'])} chương → {out}/chapters/")
    for c in manifest["chapters"]:
        pages = f"tr.{c['pdf_pages'][0]}-{c['pdf_pages'][1]}" if c["pdf_pages"] else ""
        flags = []
        if c["low_text_pages"]:
            flags.append(f"{len(c['low_text_pages'])} trang ít chữ")
        if c["images"]:
            flags.append(f"{len(c['images'])} hình")
        if c["table_rows"]:
            flags.append(f"{c['table_rows']} dòng bảng")
        print(f"  {c['file']:<45} {pages:<12} {', '.join(flags)}")
    if info.get("images"):
        s = info["images"]
        print(f"Hình: giữ {s['kept']} → {out}/images/ · bỏ {s['dropped_small']} hình nhỏ, "
              f"{s['dropped_repeated']} hình lặp (logo/header)")
    for w in manifest["warnings"]:
        print(f"⚠ {w}")


if __name__ == "__main__":
    main()
