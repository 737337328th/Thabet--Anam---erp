#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEPLOY_DIR="$ROOT/deploy/oracle"
FRAPPE_DOCKER_DIR="$HOME/frappe_docker"

test -f "$DEPLOY_DIR/.secrets" || {
  echo "Missing $DEPLOY_DIR/.secrets"
  echo "Copy .secrets.example to .secrets and fill real values."
  exit 1
}

set -a
. "$DEPLOY_DIR/.secrets"
set +a

: "${SITE_NAME:?SITE_NAME is required}"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD is required}"
: "${LETSENCRYPT_EMAIL:?LETSENCRYPT_EMAIL is required}"

if [ ! -d "$FRAPPE_DOCKER_DIR/.git" ]; then
  git clone --depth 1 https://github.com/frappe/frappe_docker "$FRAPPE_DOCKER_DIR"
else
  git -C "$FRAPPE_DOCKER_DIR" pull --ff-only
fi

cp "$DEPLOY_DIR/apps.json" "$FRAPPE_DOCKER_DIR/apps.json"
cd "$FRAPPE_DOCKER_DIR"

docker build   --no-cache   --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe   --build-arg=FRAPPE_BRANCH=version-16   --secret=id=apps_json,src=apps.json   --tag=thabet-anam:16   --file=images/layered/Containerfile .

cp example.env thabet.env
cat >> thabet.env <<EOF
CUSTOM_IMAGE=thabet-anam
CUSTOM_TAG=16
PULL_POLICY=missing
SITES_RULE=Host(\`$SITE_NAME\`)
LETSENCRYPT_EMAIL=$LETSENCRYPT_EMAIL
EOF

docker compose --env-file thabet.env   -f compose.yaml   -f overrides/compose.mariadb.yaml   -f overrides/compose.redis.yaml   -f overrides/compose.https.yaml   config > compose.thabet.yaml

docker compose -p thabet -f compose.thabet.yaml up -d

sleep 15

docker compose -p thabet -f compose.thabet.yaml exec backend   bench new-site "$SITE_NAME"   --mariadb-user-host-login-scope='%'   --db-root-password "$DB_ROOT_PASSWORD"   --admin-password "$ADMIN_PASSWORD"   --install-app erpnext   --install-app thabet_anam_v4

docker compose -p thabet -f compose.thabet.yaml exec backend   bench --site "$SITE_NAME" migrate

docker compose -p thabet -f compose.thabet.yaml exec backend   bench --site "$SITE_NAME" list-apps

echo "Deployment complete: https://$SITE_NAME"
