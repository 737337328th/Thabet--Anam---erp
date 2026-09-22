#!/usr/bin/env bash
set -euo pipefail

SITE="${1:-}"
REPO="https://github.com/737337328th/Thabet--Anam---erp"
APP="thabet_anam_v4"

if [[ -z "$SITE" ]]; then
  echo "Usage: $0 <site-name>"
  exit 2
fi

if ! command -v bench >/dev/null 2>&1; then
  echo "bench is not installed or not in PATH."
  exit 3
fi

if [[ ! -d apps/erpnext ]]; then
  echo "ERPNext is not present in this bench. Install ERPNext v16 first."
  exit 4
fi

if [[ ! -d "apps/$APP" ]]; then
  bench get-app "$REPO"
fi

if ! bench --site "$SITE" list-apps | grep -qx "$APP"; then
  bench --site "$SITE" install-app "$APP"
fi

bench --site "$SITE" migrate
bench --site "$SITE" list-apps
bench --site "$SITE" execute thabet_anam_v4.production_check.run

echo "V4 installation and read-only production check completed."
