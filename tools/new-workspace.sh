#!/usr/bin/env bash
# new-workspace.sh — tạo workspace học mới từ template này.
#
#   bash tools/new-workspace.sh <thư-mục-đích> "<Tên chủ đề>"
#   vd: bash tools/new-workspace.sh ~/learning/network "Networking (L2–L4, Linux)"
#
# Kết quả: thư mục mới có AGENTS.md, skills, docs/, learning/, labs/ sạch,
#          {{TOPIC}} đã thay bằng tên chủ đề, và cấu hình sẵn cho cả Codex lẫn Claude Code:
#            .claude/skills/        ← Codex đọc
#            .claude/skills  → ../.claude/skills   (symlink, Claude Code đọc)
#            CLAUDE.md       → import AGENTS.md    (Claude Code đọc)
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Cách dùng: bash tools/new-workspace.sh <thư-mục-đích> \"<Tên chủ đề>\"" >&2
  exit 1
fi

TEMPLATE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$1"
TOPIC="$2"

if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  echo "Lỗi: '$DEST' đã tồn tại và không rỗng. Chọn thư mục khác." >&2
  exit 1
fi
PARENT="$(dirname "$DEST")"
if [ -d "$PARENT" ]; then
  case "$(cd "$PARENT" && pwd)/" in
    "$TEMPLATE_DIR"/*) echo "Lỗi: không tạo workspace bên trong thư mục template." >&2; exit 1 ;;
  esac
fi
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

# Chỉ chép phần khung (danh sách cố định), không chép tools/ hay dữ liệu học.
cd "$TEMPLATE_DIR"
for f in AGENTS.md README.md .gitignore docs/CATALOG.md \
         learning/INDEX.md learning/glossary.md learning/questions.md; do
  mkdir -p "$DEST/$(dirname "$f")"
  cp "$f" "$DEST/$f"
done
cp -R .claude "$DEST/.claude"
find "$DEST/.claude" \( -name '.DS_Store' -o -name '__pycache__' \) -prune -exec rm -rf {} +
mkdir -p "$DEST/docs/inbox" "$DEST/learning/notes" "$DEST/labs"
touch "$DEST/docs/inbox/.gitkeep" "$DEST/learning/notes/.gitkeep" "$DEST/labs/.gitkeep"

# Thay {{TOPIC}}
for f in AGENTS.md README.md learning/INDEX.md; do
  [ -f "$DEST/$f" ] && TOPIC="$TOPIC" perl -pi -e 's/\{\{TOPIC\}\}/$ENV{TOPIC}/g' "$DEST/$f"
done

# Claude Code: CLAUDE.md import AGENTS.md; skills dùng chung qua symlink
printf '@AGENTS.md\n' > "$DEST/CLAUDE.md"
mkdir -p "$DEST/.claude"
ln -s ../.claude/skills "$DEST/.claude/skills"

cat <<EOF
Đã tạo workspace: $DEST  (chủ đề: $TOPIC)

Bước tiếp theo:
  1. cd "$DEST"
  2. Cài thư viện chuyển đổi (một lần trên máy):
       pip install -r .claude/skills/add-source/scripts/requirements.txt
  3. Điền mục 0 "Cấu hình chủ đề" trong AGENTS.md (hoặc để agent đề xuất ở phiên đầu)
     và mục "Mục tiêu" trong learning/INDEX.md.
  4. Tạo docs/<id>/ cho từng sách, bỏ file gốc vào, rồi gọi skill add-source.
EOF
