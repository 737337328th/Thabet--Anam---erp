#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-thabet.localhost}"
HTTP_PORT="${HTTP_PORT:-8080}"
APP_REPO="${APP_REPO:-https://github.com/737337328th/Thabet--Anam---erp}"
APP_BRANCH="${APP_BRANCH:-main}"
PROJECT_NAME="${PROJECT_NAME:-thabet}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$SCRIPT_DIR/.runtime"
FRAPPE_DOCKER_DIR="$RUNTIME_DIR/frappe_docker"
SECRETS_FILE="$RUNTIME_DIR/.secrets"
ENV_FILE="$RUNTIME_DIR/custom.env"
COMPOSE_FILE="$RUNTIME_DIR/compose.custom.yaml"

for cmd in git docker python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    exit 2
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required."
  exit 3
fi

mkdir -p "$RUNTIME_DIR"
chmod 700 "$RUNTIME_DIR"

if [[ ! -f "$SECRETS_FILE" ]]; then
  umask 077
  DB_PASSWORD="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(24))
PY
)"
  ADMIN_PASSWORD="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(24))
PY
)"
  cat > "$SECRETS_FILE" <<EOF
DB_PASSWORD=$DB_PASSWORD
ADMIN_PASSWORD=$ADMIN_PASSWORD
EOF
fi

# shellcheck disable=SC1090
source "$SECRETS_FILE"

if [[ ! -d "$FRAPPE_DOCKER_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/frappe/frappe_docker "$FRAPPE_DOCKER_DIR"
else
  git -C "$FRAPPE_DOCKER_DIR" fetch origin main --depth 1
  git -C "$FRAPPE_DOCKER_DIR" checkout main
  git -C "$FRAPPE_DOCKER_DIR" pull --ff-only
fi

cd "$FRAPPE_DOCKER_DIR"

cat > apps.json <<EOF
[
  {
    "url": "https://github.com/frappe/erpnext",
    "branch": "version-16"
  },
  {
    "url": "$APP_REPO",
    "branch": "$APP_BRANCH"
  }
]
EOF

echo "Building ERPNext v16 + Thabet Anam V4 image..."
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --secret=id=apps_json,src=apps.json \
  --tag=thabet-anam-erp:16 \
  --file=images/layered/Containerfile .

cat > "$ENV_FILE" <<EOF
CUSTOM_IMAGE=thabet-anam-erp
CUSTOM_TAG=16
PULL_POLICY=missing
DB_PASSWORD=$DB_PASSWORD
FRAPPE_SITE_NAME_HEADER=$SITE_NAME
HTTP_PUBLISH_PORT=$HTTP_PORT
EOF
chmod 600 "$ENV_FILE"

docker compose --env-file "$ENV_FILE" \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > "$COMPOSE_FILE"

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d

READY=0
for _ in $(seq 1 60); do
  if docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bash -lc "bench --version >/dev/null 2>&1"; then
    READY=1
    break
  fi
  sleep 2
done

if [[ "$READY" -ne 1 ]]; then
  echo "Frappe backend did not become ready. Check: docker compose -p $PROJECT_NAME -f $COMPOSE_FILE logs"
  exit 4
fi

if ! docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bash -lc "test -f sites/$SITE_NAME/site_config.json"; then
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
    bench new-site "$SITE_NAME" \
      --mariadb-user-host-login-scope='%' \
      --db-root-password "$DB_PASSWORD" \
      --admin-password "$ADMIN_PASSWORD"
fi

if ! docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" list-apps | grep -qx "erpnext"; then
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" install-app erpnext
fi

if ! docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" list-apps | grep -qx "thabet_anam_v4"; then
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" install-app thabet_anam_v4
fi

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" migrate

echo
echo "Read-only production check:"
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --site "$SITE_NAME" execute thabet_anam_v4.production_check.run

echo
echo "Local URL: http://localhost:$HTTP_PORT"
echo "Administrator password is stored locally in: $SECRETS_FILE"
echo "No financial vouchers, opening balances, or GL postings were created."
