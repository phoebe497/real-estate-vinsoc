#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-ocean-park-production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.https.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKUP_FILE="${1:-}"

if [ -z "${BACKUP_FILE}" ]; then
  echo "Usage: bash scripts/deploy/restore_postgres.sh <backup-file.dump>"
  exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
  echo "ERROR: backup file not found: ${BACKUP_FILE}"
  exit 1
fi

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "ERROR: ${COMPOSE_FILE} not found. Run this script from the project root."
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found."
  exit 1
fi

if [ "${RESTORE_CONFIRM:-}" != "I_UNDERSTAND" ]; then
  echo "ERROR: restore is destructive."
  echo "Re-run with RESTORE_CONFIRM=I_UNDERSTAND after confirming this is the right environment."
  exit 1
fi

echo "Restoring PostgreSQL backup: ${BACKUP_FILE}"

docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" exec -T database \
  sh -lc 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-acl' \
  < "${BACKUP_FILE}"

echo "Restore completed."
