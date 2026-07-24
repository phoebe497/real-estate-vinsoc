#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-ocean-park-prod}"
COMPOSE_FILE="${COMPOSE_FILE:-/opt/ocean-park/shared/application.yml}"
ENV_FILE="${ENV_FILE:-/etc/ocean-park/prod.env}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ocean-park/postgres}"
DEPLOY_ENV="${DEPLOY_ENV:-prod}"
APP_ENV_FILE="${APP_ENV_FILE:-${ENV_FILE}}"

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "ERROR: ${COMPOSE_FILE} not found. Run this script from the project root."
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found."
  exit 1
fi

mkdir -p "${BACKUP_DIR}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="${BACKUP_DIR}/${PROJECT_NAME}_${timestamp}.dump"

echo "Creating PostgreSQL backup: ${backup_file}"

DEPLOY_ENV="${DEPLOY_ENV}" APP_ENV_FILE="${APP_ENV_FILE}" \
  docker compose --env-file "${ENV_FILE}" -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" exec -T database \
  sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' \
  > "${backup_file}"

if [ ! -s "${backup_file}" ]; then
  echo "ERROR: backup file is empty."
  exit 1
fi

echo "Backup completed: ${backup_file}"
