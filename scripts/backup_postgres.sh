#!/usr/bin/env bash
# Backup PostgreSQL volume data from the running container.
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-./backups}"
mkdir -p "$OUT_DIR"
FILE="${OUT_DIR}/psychologue_${STAMP}.sql.gz"

docker compose exec -T postgres \
  pg_dump -U psychologue psychologue | gzip > "$FILE"

echo "Backup written to ${FILE}"
