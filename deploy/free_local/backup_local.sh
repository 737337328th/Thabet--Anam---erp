#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-thabet.localhost}"
PROJECT_NAME="${PROJECT_NAME:-thabet}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$SCRIPT_DIR/.runtime"
COMPOSE_FILE="$RUNTIME_DIR/compose.custom.yaml"
BACKUP_DIR="$SCRIPT_DIR/backups"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Local Docker runtime is not prepared. Run docker_zero_cost.sh first."
  exit 2
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --site "$SITE_NAME" backup --with-files

STAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="$BACKUP_DIR/$SITE_NAME-$STAMP.tar.gz"

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  tar -C "/home/frappe/frappe-bench/sites/$SITE_NAME/private/backups" -czf - . > "$ARCHIVE"

sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"

echo "Backup created:"
echo "$ARCHIVE"
echo "$ARCHIVE.sha256"
