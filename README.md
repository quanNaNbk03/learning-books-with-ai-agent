# Learning engineering — bộ skill học cùng agent

Bộ skill để học từ sách/tài liệu cùng AI agent (Codex, Claude Code): đọc tài liệu đã chuyển sang
markdown, giải thích có dẫn chứng và sơ đồ, kiểm tra bằng trắc nghiệm, hướng dẫn lab, lưu kiến
thức theo chủ đề để ôn.

Repo này là **bản gốc duy nhất** của cả skill lẫn khung workspace. Skill được cài **global** bằng
symlink, nên sửa ở đây là mọi workspace dùng bản mới ngay.

## Cấu trúc

```
.
├── install.sh                         # cài 3 skill thành global (symlink vào ~/.agents/skills, ~/.claude/skills)
└── skills/
    ├── learn-new-workspace/           # dựng / chuyển đổi / nâng cấp workspace
    │   ├── SKILL.md
    │   ├── scripts/scaffold.sh        # dựng khung (không ghi đè), dùng được cả khi không có agent
    │   └── templates/                 # KHUNG WORKSPACE: AGENTS.md, README.md, gitignore, docs/, learning/
    ├── learn-add-source/              # thêm tài liệu: PDF/EPUB/MD → markdown theo chương, INDEX, CATALOG
    │   ├── SKILL.md
    │   ├── scripts/convert.py
    │   ├── scripts/requirements.txt
    │   └── templates/source-INDEX.md
    └── learn-notes/                   # lưu kiến thức, câu hỏi ôn, tiến độ, bài lab
        └── SKILL.md
```

## Cài đặt (một lần trên mỗi máy)

```bash
bash install.sh                 # symlink 3 skill vào ~/.agents/skills (Codex) và ~/.claude/skills (Claude Code)
pip install -r skills/learn-add-source/scripts/requirements.txt
# tùy chọn, cho PDF scan: brew install tesseract
```

Kiểm tra: trong Codex gõ `$` hoặc `/skills`, trong Claude Code gõ `/` → thấy `learn-new-workspace`,
`learn-add-source`, `learn-notes`. Không thấy → khởi động lại agent; vẫn không thấy thì cài bằng bản
sao thay cho symlink: `bash install.sh --copy` (khi đó sửa skill xong phải chạy lại lệnh này).

Đã từng cài skill tên cũ (`add-source`, `learning-notes`) ở `~/.agents/skills` hoặc `~/.claude/skills`,
hoặc còn bản skill nằm trong một workspace (`.agents/skills/`, `.claude/skills/`) → xóa đi để tránh
trùng tên. `install.sh` sẽ cảnh báo các bản global còn sót; bản trong workspace thì dùng chế độ
"chuyển đổi" bên dưới.

## Dùng

| Việc | Mở agent ở | Nói |
|---|---|---|
| Tạo workspace cho chủ đề mới | thư mục trống, vd. `~/learning/network/` | "Tạo workspace học networking" |
| Biến thư mục cũ thành workspace (có PDF, ghi chú, skill cũ…) | thư mục đó | "Chuyển thư mục này thành learning workspace" |
| Thêm sách | gốc workspace | "Thêm tài liệu ccna-v1" |
| Học | gốc workspace | "Đọc tiếp ccna-v1", "Học LACP từ các sách", "Native VLAN là gì?" |
| Lưu | gốc workspace | "Lưu lại" |
| Nâng cấp luật sau khi sửa template | gốc workspace | "Cập nhật workspace theo template" |

Không có agent: `bash skills/learn-new-workspace/scripts/scaffold.sh ~/learning/k8s "Kubernetes"`.

Hướng dẫn chi tiết cho từng workspace (chế độ học, quy trình thêm tài liệu, tùy chọn `convert.py`,
xử lý sự cố) nằm ở `skills/learn-new-workspace/templates/README.md`, được chép vào mỗi workspace.

## Sửa luật hoặc skill

| Muốn đổi | Sửa file | Có hiệu lực |
|---|---|---|
| Cách skill làm việc | `skills/<skill>/SKILL.md`, script | Ngay (symlink) |
| Luật dạy học cho workspace mới | `skills/learn-new-workspace/templates/AGENTS.md` | Workspace tạo sau đó |
| Luật dạy học cho workspace đang dùng | như trên, rồi trong workspace nói "cập nhật workspace theo template" | Sau khi xác nhận (mục 0 được giữ) |

Lưu ý: `templates/AGENTS.md` có biến `{{TOPIC}}`; giữ nguyên biến này khi sửa.
Không đặt `CLAUDE.md` vào `templates/` (scaffold tự tạo), để Claude Code không đọc nhầm nó khi
bạn đang sửa repo này.

## Giới hạn
- Skill global trong `~/.claude/skills` chỉ dùng được trên máy này; phiên cloud không thấy chúng.
- Codex trong sandbox có thể không ghi được ra ngoài thư mục đang mở → luôn mở agent tại đúng
  thư mục workspace.
