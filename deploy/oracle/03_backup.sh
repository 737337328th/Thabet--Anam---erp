#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEPLOY_DIR="$ROOT/deploy/oracle"
FRAPPE_DOCKER_DIR="$HOME/frappe_docker"

set -a
. "$DEPLOY_DIR/.secrets"
set +a

cd "$FRAPPE_DOCKER_DIR"
docker compose -p thabet -f compose.thabet.yaml exec backend   bench --site "$SITE_NAME" backup --with-files
