#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-ocean-park-staging}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.registry.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKEND_READY_URL="${BACKEND_READY_URL:-http://localhost:8000/ready}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

required_env_keys=(
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
)

echo "Deploying staging project: ${PROJECT_NAME}"

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "ERROR: ${COMPOSE_FILE} not found. Run this script from the project root."
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found. Copy .env.staging.example to .env and fill it first."
  exit 1
fi

bash scripts/deploy/check_vps_prerequisites.sh

for key in "${required_env_keys[@]}"; do
  if ! grep -Eq "^${key}=.+" "${ENV_FILE}"; then
    echo "ERROR: ${key} is missing or empty in ${ENV_FILE}."
    exit 1
  fi
done

if grep -Eq "replace-with|your-github-user-or-org|your-repo|example.com" "${ENV_FILE}"; then
  echo "ERROR: ${ENV_FILE} still contains placeholder values."
  exit 1
fi

echo "Validating compose config..."
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" config --quiet

echo "Pulling latest images..."
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" pull

echo "Starting services..."
if ! docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d; then
  echo "ERROR: docker compose failed to start all services."
  echo "Current service status:"
  docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" ps || true
  echo "Database logs:"
  docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs database --tail 100 || true
  echo "Backend logs:"
  docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs backend --tail 200 || true
  exit 1
fi

echo "Current service status:"
docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" ps

echo "Checking backend readiness..."
for attempt in $(seq 1 30); do
  if curl -fsS "${BACKEND_READY_URL}" >/dev/null; then
    curl -fsS "${BACKEND_READY_URL}"
    echo
    break
  fi

  if [ "${attempt}" -eq 30 ]; then
    echo "ERROR: backend readiness check failed."
    docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs backend --tail 100
    exit 1
  fi

  sleep 2
done

echo "Checking frontend..."
for attempt in $(seq 1 30); do
  if curl -fsS "${FRONTEND_URL}" >/dev/null; then
    break
  fi

  if [ "${attempt}" -eq 30 ]; then
    echo "ERROR: frontend readiness check failed."
    docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" logs frontend --tail 100
    exit 1
  fi

  sleep 2
done

echo "Staging deployment completed successfully."
