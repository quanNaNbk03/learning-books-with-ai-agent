#!/usr/bin/env bash
# scaffold.sh — dựng khung learning workspace từ templates/ của skill learn-new-workspace.
#
#   bash <skill-dir>/scripts/scaffold.sh <thư-mục-đích> "<Tên chủ đề>"
#   vd: bash ~/.agents/skills/learn-new-workspace/scripts/scaffold.sh . "Networking (L2–L4, Linux)"
#
# - Không ghi đè: nếu bất kỳ file khung nào đã tồn tại ở đích → dừng, không ghi gì.
#   (File khác như PDF, .git, ghi chú cũ được giữ nguyên, không bị đụng tới.)
# - Thay {{TOPIC}} bằng tên chủ đề; tạo CLAUDE.md chứa "@AGENTS.md" cho Claude Code.
# - Skill KHÔNG được chép vào workspace: chúng được cài global (~/.agents/skills, ~/.claude/skills).
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Cách dùng: bash scaffold.sh <thư-mục-đích> \"<Tên chủ đề>\"" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$SKILL_DIR/templates"
DEST="$1"
TOPIC="$2"

[ -d "$TPL" ] || { echo "Lỗi: không thấy $TPL" >&2; exit 1; }
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

# Danh sách file khung: <nguồn trong templates/>:<đích trong workspace>
FILES=(
  "AGENTS.md:AGENTS.md"
  "README.md:README.md"
  "gitignore:.gitignore"
  "docs/CATALOG.md:docs/CATALOG.md"
  "learning/INDEX.md:learning/INDEX.md"
  "learning/glossary.md:learning/glossary.md"
  "learning/questions.md:learning/questions.md"
)

# 1. Kiểm tra xung đột trước khi ghi bất cứ gì
conflicts=()
for pair in "${FILES[@]}"; do
  dst="${pair#*:}"
  if [ -e "$DEST/$dst" ]; then conflicts+=("$dst"); fi
done
if [ -e "$DEST/CLAUDE.md" ]; then conflicts+=("CLAUDE.md"); fi
if [ ${#conflicts[@]} -gt 0 ]; then
  echo "Dừng: các file sau đã tồn tại ở $DEST, không ghi đè:" >&2
  printf '  - %s\n' "${conflicts[@]}" >&2
  echo "Nếu muốn nâng cấp workspace có sẵn, dùng chế độ 'nâng cấp' của skill." >&2
  exit 2
fi

# 2. Chép khung
for pair in "${FILES[@]}"; do
  src="${pair%%:*}"; dst="${pair#*:}"
  mkdir -p "$DEST/$(dirname "$dst")"
  cp "$TPL/$src" "$DEST/$dst"
done
mkdir -p "$DEST/docs/inbox" "$DEST/learning/notes" "$DEST/labs"
touch "$DEST/docs/inbox/.gitkeep" "$DEST/learning/notes/.gitkeep" "$DEST/labs/.gitkeep"
printf '@AGENTS.md\n' > "$DEST/CLAUDE.md"

# 3. Điền tên chủ đề
for f in AGENTS.md README.md learning/INDEX.md; do
  TOPIC="$TOPIC" perl -pi -e 's/\{\{TOPIC\}\}/$ENV{TOPIC}/g' "$DEST/$f"
done

echo "OK: đã dựng workspace '$TOPIC' tại $DEST"
for pair in "${FILES[@]}"; do echo "  + ${pair#*:}"; done
echo "  + CLAUDE.md, docs/inbox/, learning/notes/, labs/"
