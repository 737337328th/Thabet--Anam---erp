#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-thabet.localhost}"
PROJECT_NAME="${PROJECT_NAME:-thabet}"
HTTP_PORT="${HTTP_PORT:-8080}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$SCRIPT_DIR/.runtime"
COMPOSE_FILE="$RUNTIME_DIR/compose.custom.yaml"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Runtime not found. Run docker_zero_cost.sh first."
  exit 2
fi

echo "== Containers =="
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" ps

echo
echo "== Installed apps =="
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --site "$SITE_NAME" list-apps

echo
echo "== Read-only production check =="
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --site "$SITE_NAME" execute thabet_anam_v4.production_check.run

echo
echo "== HTTP check =="
if command -v curl >/dev/null 2>&1; then
  curl --fail --silent --show-error --max-time 10 "http://127.0.0.1:$HTTP_PORT" >/dev/null
  echo "HTTP OK: http://localhost:$HTTP_PORT"
else
  echo "curl is not installed; skipped HTTP request check."
fi

echo
echo "Health check completed. No write or financial-posting command was executed."
