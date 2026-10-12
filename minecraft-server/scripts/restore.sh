#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/restore.sh backups/<filename>.tgz" >&2
  exit 1
fi

archive=$(realpath -- "$1")
if [[ ! -f "$archive" ]]; then
  echo "Backup file not found: $archive" >&2
  exit 1
fi

# Confirm that the backup archive is readable before stopping the service.
tar -tzf "$archive" > /dev/null
cd "$(dirname "$0")/.."

echo "WARNING: This operation replaces the current Minecraft world and server data."
echo "Archive: $archive"
read -r -p "Type 'restore' to continue: " answer
if [[ "$answer" != "restore" ]]; then
  echo "Canceled."
  exit 1
fi

docker compose stop backups minecraft
snapshot="data.before-restore-$(date +%Y%m%d-%H%M%S)"
if [[ -d data ]]; then
  mv -- data "$snapshot"
  echo "Previous data preserved in: $snapshot"
fi
mkdir -p data
tar -xzf "$archive" -C data
docker compose up -d
printf 'Restore initiated. Inspect logs and verify your world in Minecraft.\n'
