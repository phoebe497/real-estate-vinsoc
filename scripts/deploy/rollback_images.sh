#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-ocean-park-production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.https.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKEND_IMAGE_ROLLBACK="${1:-}"
FRONTEND_IMAGE_ROLLBACK="${2:-}"

if [ -z "${BACKEND_IMAGE_ROLLBACK}" ] || [ -z "${FRONTEND_IMAGE_ROLLBACK}" ]; then
  echo "Usage: bash scripts/deploy/rollback_images.sh <backend-image> <frontend-image>"
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found."
  exit 1
fi

env_backup="${ENV_FILE}.rollback.$(date -u +%Y%m%dT%H%M%SZ)"
cp "${ENV_FILE}" "${env_backup}"

tmp_env="$(mktemp)"
awk -v backend="${BACKEND_IMAGE_ROLLBACK}" -v frontend="${FRONTEND_IMAGE_ROLLBACK}" '
  /^BACKEND_IMAGE=/ { print "BACKEND_IMAGE=" backend; next }
  /^FRONTEND_IMAGE=/ { print "FRONTEND_IMAGE=" frontend; next }
  { print }
' "${ENV_FILE}" > "${tmp_env}"
mv "${tmp_env}" "${ENV_FILE}"

echo "Updated rollback images in ${ENV_FILE}."
echo "Previous env backup: ${env_backup}"

docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" pull
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" ps
