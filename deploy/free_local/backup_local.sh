#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-thabet.localhost}"
PROJECT_NAME="${PROJECT_NAME:-thabet}"
RETENTION_COUNT="${RETENTION_COUNT:-14}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$SCRIPT_DIR/.runtime"
COMPOSE_FILE="$RUNTIME_DIR/compose.custom.yaml"
BACKUP_DIR="$SCRIPT_DIR/backups"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Local Docker runtime is not prepared. Run docker_zero_cost.sh first."
  exit 2
fi

if ! [[ "$RETENTION_COUNT" =~ ^[1-9][0-9]*$ ]]; then
  echo "RETENTION_COUNT must be a positive integer."
  exit 3
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --site "$SITE_NAME" backup --with-files

STAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="$BACKUP_DIR/$SITE_NAME-$STAMP.tar.gz"

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  tar -C "/home/frappe/frappe-bench/sites/$SITE_NAME/private/backups" -czf - . > "$ARCHIVE"

tar -tzf "$ARCHIVE" >/dev/null
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
(cd "$BACKUP_DIR" && sha256sum -c "$(basename "$ARCHIVE.sha256")")

mapfile -t OLD_ARCHIVES < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "$SITE_NAME-*.tar.gz" -printf "%T@ %p\n" | sort -nr | tail -n "+$((RETENTION_COUNT + 1))" | cut -d" " -f2-)
for old in "${OLD_ARCHIVES[@]:-}"; do
  [[ -n "$old" ]] || continue
  rm -f "$old" "$old.sha256"
done

echo "Backup created and verified:"
echo "$ARCHIVE"
echo "$ARCHIVE.sha256"
echo "Retention: latest $RETENTION_COUNT archives."
