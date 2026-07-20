#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-ocean-park-production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.https.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKEND_READY_URL="${BACKEND_READY_URL:-}"
FRONTEND_URL="${FRONTEND_URL:-}"
SKIP_BACKUP="${SKIP_BACKUP:-false}"

required_env_keys=(
  APP_ENV
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  JWT_SECRET_KEY
  ADMIN_EMAIL
  ADMIN_PASSWORD
  CORS_ORIGINS
  NEXT_PUBLIC_API_URL
  BACKEND_IMAGE
  FRONTEND_IMAGE
  FRONTEND_DOMAIN
  API_DOMAIN
  ACME_EMAIL
)

echo "Deploying production project: ${PROJECT_NAME}"

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "ERROR: ${COMPOSE_FILE} not found. Run this script from the project root."
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found. Copy .env.production.example to .env and fill it first."
  exit 1
fi

bash scripts/deploy/check_vps_prerequisites.sh

for key in "${required_env_keys[@]}"; do
  if ! grep -Eq "^${key}=.+" "${ENV_FILE}"; then
    echo "ERROR: ${key} is missing or empty in ${ENV_FILE}."
    exit 1
  fi
done

if ! grep -Eq "^APP_ENV=production$" "${ENV_FILE}"; then
  echo "ERROR: APP_ENV must be exactly production."
  exit 1
fi

if grep -Eq "replace-with|your-github-user-or-org|your-repo|example.com" "${ENV_FILE}"; then
  echo "ERROR: ${ENV_FILE} still contains placeholder values."
  exit 1
fi

get_env_value() {
  local key="$1"
  grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2-
}

API_DOMAIN_VALUE="$(get_env_value API_DOMAIN)"
FRONTEND_DOMAIN_VALUE="$(get_env_value FRONTEND_DOMAIN)"
BACKEND_READY_URL="${BACKEND_READY_URL:-https://${API_DOMAIN_VALUE}/ready}"
FRONTEND_URL="${FRONTEND_URL:-https://${FRONTEND_DOMAIN_VALUE}}"

echo "Validating production compose config..."
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" config --quiet

if [ "${SKIP_BACKUP}" != "true" ]; then
  echo "Running pre-deploy PostgreSQL backup..."
  PROJECT_NAME="${PROJECT_NAME}" COMPOSE_FILE="${COMPOSE_FILE}" ENV_FILE="${ENV_FILE}" \
    bash scripts/deploy/backup_postgres.sh
else
  echo "Skipping pre-deploy backup because SKIP_BACKUP=true."
fi

echo "Pulling production images..."
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" pull

echo "Starting production services..."
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d

echo "Current service status:"
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" ps

echo "Checking production backend readiness..."
for attempt in $(seq 1 45); do
  if curl -fsS "${BACKEND_READY_URL}" >/dev/null; then
    curl -fsS "${BACKEND_READY_URL}"
    echo
    break
  fi

  if [ "${attempt}" -eq 45 ]; then
    echo "ERROR: production backend readiness check failed."
    docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs caddy backend --tail 120
    exit 1
  fi

  sleep 2
done

echo "Checking production frontend..."
for attempt in $(seq 1 30); do
  if curl -fsS "${FRONTEND_URL}" >/dev/null; then
    break
  fi

  if [ "${attempt}" -eq 30 ]; then
    echo "ERROR: production frontend readiness check failed."
    docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs caddy frontend --tail 120
    exit 1
  fi

  sleep 2
done

echo "Production deployment completed successfully."
