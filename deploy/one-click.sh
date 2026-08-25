#!/usr/bin/env bash
# One-click deploy for InstaCertify ERP on ERPNext 16.32.3
# Target domain: instacertify.in
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STACK_DIR="${STACK_DIR:-$HOME/instacertify-frappe-docker}"
SITE_NAME="${SITE_NAME:-instacertify.in}"
CUSTOM_IMAGE="${CUSTOM_IMAGE:-instacertify-erp}"
CUSTOM_TAG="${CUSTOM_TAG:-16.32.3}"
APP_BRANCH="${APP_BRANCH:-cursor/instacertify-erpnext-7b69}"

echo "==> InstaCertify one-click deploy (ERPNext ${ERPNEXT_VERSION:-v16.32.3})"
echo "    Site: ${SITE_NAME}"
echo "    Stack: ${STACK_DIR}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }
need git
need docker
docker compose version >/dev/null

if [[ ! -d "$STACK_DIR/.git" ]]; then
  echo "==> Cloning frappe_docker"
  git clone --depth 1 https://github.com/frappe/frappe_docker "$STACK_DIR"
fi

cd "$STACK_DIR"

# apps.json — ERPNext 16.32.3 + this custom app only
cp "$ROOT/apps.json" ./apps.json
# rewrite branch if overridden
python3 - <<PY
import json, os
from pathlib import Path
apps = json.loads(Path("apps.json").read_text())
branch = os.environ.get("APP_BRANCH", "${APP_BRANCH}")
for a in apps:
    if "ERPNEXTCODE" in a.get("url", "") or "instacertify" in a.get("url", "").lower():
        a["branch"] = branch
Path("apps.json").write_text(json.dumps(apps, indent=2) + "\n")
print("apps.json ready:", apps)
PY

echo "==> Building custom image ${CUSTOM_IMAGE}:${CUSTOM_TAG}"
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --secret=id=apps_json,src=apps.json \
  --tag="${CUSTOM_IMAGE}:${CUSTOM_TAG}" \
  --file=images/layered/Containerfile \
  .

ENV_FILE="$ROOT/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ROOT/.env.example" "$ENV_FILE"
  echo "Created $ENV_FILE — edit passwords before production use."
fi

# ensure image vars
grep -q '^CUSTOM_IMAGE=' "$ENV_FILE" || echo "CUSTOM_IMAGE=${CUSTOM_IMAGE}" >> "$ENV_FILE"
sed -i "s|^CUSTOM_IMAGE=.*|CUSTOM_IMAGE=${CUSTOM_IMAGE}|" "$ENV_FILE"
sed -i "s|^CUSTOM_TAG=.*|CUSTOM_TAG=${CUSTOM_TAG}|" "$ENV_FILE"
sed -i "s|^SITE_NAME=.*|SITE_NAME=${SITE_NAME}|" "$ENV_FILE" || true
grep -q '^PULL_POLICY=' "$ENV_FILE" || echo "PULL_POLICY=missing" >> "$ENV_FILE"

echo "==> Composing stack"
docker compose --env-file "$ENV_FILE" \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > "$ROOT/compose.generated.yaml"

docker compose --env-file "$ENV_FILE" -f "$ROOT/compose.generated.yaml" up -d

echo "==> Waiting for backend"
sleep 20

echo "==> Creating site ${SITE_NAME} (idempotent)"
docker compose --env-file "$ENV_FILE" -f "$ROOT/compose.generated.yaml" exec -T backend \
  bench new-site "${SITE_NAME}" \
    --mariadb-root-password "$(grep ^DB_PASSWORD= "$ENV_FILE" | cut -d= -f2-)" \
    --admin-password "${ADMIN_PASSWORD:-admin}" \
    --install-app erpnext \
    --install-app instacertify \
    --set-default || true

docker compose --env-file "$ENV_FILE" -f "$ROOT/compose.generated.yaml" exec -T backend \
  bench --site "${SITE_NAME}" migrate || true

docker compose --env-file "$ENV_FILE" -f "$ROOT/compose.generated.yaml" exec -T backend \
  bench --site "${SITE_NAME}" seed-instacertify || \
docker compose --env-file "$ENV_FILE" -f "$ROOT/compose.generated.yaml" exec -T backend \
  bench --site "${SITE_NAME}" execute instacertify.setup.seed.seed_demo_data || true

echo ""
echo "✅ InstaCertify ERP is up"
echo "   Open: http://localhost:${HTTP_PUBLISH_PORT:-8080}  (map DNS ${SITE_NAME} → host)"
echo "   Desk dashboard: /app/ic-home"
echo "   Stack: ERPNext ${ERPNEXT_VERSION:-v16.32.3} + instacertify (nothing else)"
echo "   Next: point ${SITE_NAME} DNS / TLS (use compose.traefik overrides for Let's Encrypt)"
