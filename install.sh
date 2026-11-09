#!/usr/bin/env bash
# install.sh — cài các skill học (learn-*) thành skill global cho Codex và Claude Code.
#
#   bash install.sh          # tạo symlink (khuyên dùng: sửa trong repo là có hiệu lực ngay)
#   bash install.sh --copy   # chép thư mục (dùng khi agent không đọc được symlink)
#
# Đích:  ~/.agents/skills/<skill>   (Codex)
#        ~/.claude/skills/<skill>   (Claude Code)
# Không ghi đè thứ gì không phải do script này tạo; chạy lại nhiều lần an toàn.
set -euo pipefail

MODE=link
[ "${1:-}" = "--copy" ] && MODE=copy

REPO="$(cd "$(dirname "$0")" && pwd)"
TARGETS=("$HOME/.agents/skills" "$HOME/.claude/skills")

for t in "${TARGETS[@]}"; do
  mkdir -p "$t"
  for src in "$REPO"/skills/learn-*/; do
    src="${src%/}"; name="$(basename "$src")"; dst="$t/$name"
    if [ -L "$dst" ]; then
      if [ "$(readlink "$dst")" = "$src" ] && [ $MODE = link ]; then
        echo "  = $dst (đã có)"; continue
      fi
      rm "$dst"                                   # symlink cũ/sai → thay
    elif [ -e "$dst" ]; then
      if [ -f "$dst/.installed-from-learning-template" ]; then
        rm -rf "$dst"                             # bản copy cũ do script này tạo → thay
      else
        echo "  ! $dst đã tồn tại và không phải do install.sh tạo — bỏ qua (tự kiểm tra)." >&2
        continue
      fi
    fi
    if [ $MODE = link ]; then
      ln -s "$src" "$dst"
    else
      cp -R "$src" "$dst"
      touch "$dst/.installed-from-learning-template"
    fi
    echo "  + $dst"
  done
  # Cảnh báo tên skill cũ còn sót (trước khi đổi tên sang learn-*)
  for old in add-source learning-notes; do
    [ -e "$t/$old" ] && echo "  ! Còn skill tên cũ: $t/$old — nên xóa để tránh trùng." >&2
  done
done

cat <<EOF

Xong. Kiểm tra:
  - Codex:       gõ \$ hoặc /skills, thấy learn-new-workspace, learn-add-source, learn-notes
  - Claude Code: gõ /, thấy cùng 3 skill
Thư viện chuyển đổi PDF (một lần trên máy):
  pip install -r "$REPO/skills/learn-add-source/scripts/requirements.txt"
EOF
