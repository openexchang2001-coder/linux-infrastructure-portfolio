#!/bin/bash
set -euo pipefail

# バックアップ元と保存先
SOURCE="$HOME/linux-infrastructure-portfolio"
DEST="$HOME/backups/linux-portfolio"

# バックアップファイルに日時を付ける
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$DEST/portfolio_$DATE.tar.gz"

# バックアップのアクセス権限を制限
umask 077

# 保存先フォルダを作成
mkdir -p "$DEST"

# ファイルを圧縮して保存
tar -czf "$BACKUP_FILE" -C "$SOURCE" \
    README.md docs scripts site

# バックアップファイルを検査
tar -tzf "$BACKUP_FILE" > /dev/null

echo "OK: Backup completed"
echo "Saved to: $BACKUP_FILE"

# 7日以上経過したバックアップを削除
find "$DEST" -maxdepth 1 -type f \
    -name 'portfolio_????????_??????.tar.gz' \
    -mtime +6 -print -delete
