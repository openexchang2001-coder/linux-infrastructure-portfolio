#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
printf '\n[1/2] Docker Compose status\n'
docker compose ps
printf '\n[2/2] Server response via RCON\n'
docker compose exec -T minecraft rcon-cli list
