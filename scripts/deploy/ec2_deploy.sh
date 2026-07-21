#!/usr/bin/env bash
set -Eeuo pipefail

readonly COMPOSE_FILE="/opt/ocean-park/shared/application.yml"
readonly LOCK_FILE="/var/lock/ocean-park-deploy.lock"
readonly STATE_DIR="/var/lib/ocean-park/deployments"
readonly BACKUP_DIR="/var/backups/ocean-park/postgres"
readonly EDGE_ENV_FILE="/etc/ocean-park/edge.env"

usage() {
  echo "Usage: ocean-park-deploy <dev|prod> <backend-image> <frontend-image> <full-commit-sha>" >&2
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

get_file_env_value() {
  local path="$1"
  local key="$2"
  local value
  value="$(grep -E "^${key}=" "${path}" | tail -n 1 | cut -d '=' -f 2- || true)"
  value="${value%$'\r'}"
  [[ -n "${value}" ]] || fail "${key} is missing or empty in ${path}."
  printf '%s' "${value}"
}

get_env_value() {
  get_file_env_value "${ENV_FILE}" "$1"
}

assert_root_owned_config() {
  local path="$1"
  local mode
  [[ -f "${path}" ]] || fail "Required file not found: ${path}"
  [[ "$(stat -c '%U' "${path}")" == "root" ]] || fail "${path} must be owned by root."
  mode="$(stat -c '%a' "${path}")"
  (( (8#${mode} & 022) == 0 )) || fail "${path} must not be group/world writable."
}

validate_requested_image() {
  local image="$1"
  local component="$2"
  local tag_prefix="${IMAGE_PREFIX}-${component}:${ENVIRONMENT}-sha-"
  local digest_prefix="${IMAGE_PREFIX}-${component}@sha256:"
  local identity
  if [[ "${image}" == "${tag_prefix}"* ]]; then
    identity="${image#"${tag_prefix}"}"
    [[ "${identity}" =~ ^[a-f0-9]{40}$ ]] || fail "Requested ${component} tag has an invalid commit SHA."
  elif [[ "${image}" == "${digest_prefix}"* ]]; then
    identity="${image#"${digest_prefix}"}"
    [[ "${identity}" =~ ^[a-f0-9]{64}$ ]] || fail "Requested ${component} digest is invalid."
  else
    fail "Rejected ${component} image; expected an environment-qualified full-commit tag or repository digest."
  fi
}

validate_stored_image() {
  local image="$1"
  local component="$2"
  local tag_prefix="${IMAGE_PREFIX}-${component}:${ENVIRONMENT}-sha-"
  local digest_prefix="${IMAGE_PREFIX}-${component}@sha256:"
  local identity

  if [[ "${image}" == "${tag_prefix}"* ]]; then
    identity="${image#"${tag_prefix}"}"
    [[ "${identity}" =~ ^[a-f0-9]{40}$ ]] || fail "Stored ${component} tag is invalid."
  elif [[ "${image}" == "${digest_prefix}"* ]]; then
    identity="${image#"${digest_prefix}"}"
    [[ "${identity}" =~ ^[a-f0-9]{64}$ ]] || fail "Stored ${component} digest is invalid."
  else
    fail "Stored ${component} image is outside the deployment repository allowlist."
  fi
}

pull_and_resolve_image() {
  local image="$1"
  local repository
  if [[ "${image}" == *@sha256:* ]]; then
    repository="${image%@sha256:*}"
  else
    repository="${image%%:*}"
  fi
  local digest_prefix="${repository}@sha256:"
  local candidate digest

  timeout --signal=TERM --kill-after=30s 5m docker pull "${image}" >/dev/null
  while IFS= read -r candidate; do
    if [[ "${candidate}" == "${digest_prefix}"* ]]; then
      digest="${candidate#"${digest_prefix}"}"
      if [[ "${digest}" =~ ^[a-f0-9]{64}$ ]]; then
        printf '%s' "${candidate}"
        return 0
      fi
    fi
  done < <(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "${image}")
  fail "Docker did not return an immutable digest for ${image}."
}

write_image_pair() {
  local backend="$1"
  local frontend="$2"
  local temporary
  temporary="$(mktemp "${ENV_FILE}.tmp.XXXXXX")"

  awk -v backend="${backend}" -v frontend="${frontend}" '
    BEGIN { backend_seen = 0; frontend_seen = 0 }
    /^BACKEND_IMAGE=/ { print "BACKEND_IMAGE=" backend; backend_seen = 1; next }
    /^FRONTEND_IMAGE=/ { print "FRONTEND_IMAGE=" frontend; frontend_seen = 1; next }
    { print }
    END {
      if (!backend_seen) print "BACKEND_IMAGE=" backend
      if (!frontend_seen) print "FRONTEND_IMAGE=" frontend
    }
  ' "${ENV_FILE}" > "${temporary}"

  chmod --reference="${ENV_FILE}" "${temporary}"
  chown --reference="${ENV_FILE}" "${temporary}"
  mv -f "${temporary}" "${ENV_FILE}"
}

compose() {
  docker compose \
    --env-file "${ENV_FILE}" \
    --project-name "${PROJECT_NAME}" \
    --project-directory "${APP_DIR}" \
    --file "${COMPOSE_FILE}" "$@"
}

compose_timed() {
  local duration="$1"
  shift
  timeout --signal=TERM --kill-after=30s "${duration}" docker compose \
    --env-file "${ENV_FILE}" \
    --project-name "${PROJECT_NAME}" \
    --project-directory "${APP_DIR}" \
    --file "${COMPOSE_FILE}" "$@"
}

wait_for_service() {
  local service="$1"
  local timeout_seconds="${2:-300}"
  local deadline=$((SECONDS + timeout_seconds))
  local call_timeout container_id status

  while (( SECONDS < deadline )); do
    call_timeout=$((deadline - SECONDS))
    (( call_timeout > 15 )) && call_timeout=15
    container_id="$(compose_timed "${call_timeout}s" ps -q "${service}" 2>/dev/null || true)"
    if [[ -n "${container_id}" ]]; then
      call_timeout=$((deadline - SECONDS))
      (( call_timeout <= 0 )) && break
      (( call_timeout > 15 )) && call_timeout=15
      status="$(timeout --signal=TERM --kill-after=5s "${call_timeout}s" docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${container_id}" 2>/dev/null || true)"
      [[ "${status}" == "healthy" ]] && return 0
      [[ "${status}" == "exited" || "${status}" == "dead" ]] && return 1
    fi
    (( SECONDS < deadline )) && sleep 5
  done
  return 1
}

check_public_endpoints() {
  [[ "$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 15 "${BACKEND_READY_URL}")" == "200" ]]
  [[ "$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 15 "${FRONTEND_URL}")" == "200" ]]
}

rollback() {
  echo "Deployment failed after image mutation; restoring the previous ${ENVIRONMENT} image pair." >&2
  write_image_pair "${PREVIOUS_BACKEND_IMAGE}" "${PREVIOUS_FRONTEND_IMAGE}"
  if ! compose_timed 2m up -d --pull never; then
    echo "Cached rollback image unavailable; attempting an exact tag/digest pull." >&2
    compose_timed 2m pull backend frontend
    compose_timed 2m up -d
  fi
  wait_for_service backend 300
  wait_for_service frontend 300
  check_public_endpoints
  echo "Previous ${ENVIRONMENT} image pair restored." >&2
}

on_exit() {
  local exit_code="$1"
  trap - EXIT
  if [[ "${exit_code}" -ne 0 && -n "${BACKUP_FILE:-}" && "${BACKUP_VALIDATED:-false}" != "true" ]]; then
    rm -f -- "${BACKUP_FILE}"
  fi
  if [[ "${exit_code}" -ne 0 && "${MUTATED}" == "true" ]]; then
    set +e
    rollback
    local rollback_code="$?"
    set -e
    if [[ "${rollback_code}" -ne 0 ]]; then
      echo "CRITICAL: automatic rollback also failed; inspect ${PROJECT_NAME} immediately." >&2
    fi
  fi
  exit "${exit_code}"
}

[[ "$#" -eq 4 ]] || { usage; exit 2; }
[[ "${EUID}" -eq 0 ]] || fail "This host-owned deployment wrapper must run as root."

ENVIRONMENT="$1"
BACKEND_IMAGE="$2"
FRONTEND_IMAGE="$3"
COMMIT_SHA="$4"

case "${ENVIRONMENT}" in
  dev)
    PROJECT_NAME="ocean-park-dev"
    APP_DIR="/opt/ocean-park/dev"
    ENV_FILE="/etc/ocean-park/dev.env"
    ;;
  prod)
    PROJECT_NAME="ocean-park-prod"
    APP_DIR="/opt/ocean-park/prod"
    ENV_FILE="/etc/ocean-park/prod.env"
    ;;
  *)
    fail "Environment must be exactly dev or prod."
    ;;
esac

[[ "${COMMIT_SHA}" =~ ^[a-f0-9]{40}$ ]] || fail "Commit SHA must contain exactly 40 lowercase hexadecimal characters."

for command_name in awk curl df docker flock grep mktemp rm stat timeout tr; do
  require_command "${command_name}"
done
docker compose version >/dev/null 2>&1 || fail "Docker Compose plugin is unavailable."

assert_root_owned_config "${COMPOSE_FILE}"
assert_root_owned_config "${ENV_FILE}"
assert_root_owned_config "${EDGE_ENV_FILE}"
[[ -d "${APP_DIR}" ]] || fail "Application directory not found: ${APP_DIR}"

IMAGE_PREFIX="$(get_env_value DEPLOY_IMAGE_PREFIX)"
[[ "${IMAGE_PREFIX}" =~ ^ghcr\.io/[a-z0-9._-]+/[a-z0-9._-]+$ ]] || fail "DEPLOY_IMAGE_PREFIX must be a lowercase ghcr.io/owner/repository path."
BACKEND_READY_URL="$(get_env_value BACKEND_READY_URL)"
FRONTEND_URL="$(get_env_value FRONTEND_URL)"
API_DOMAIN="$(get_env_value API_DOMAIN)"
FRONTEND_DOMAIN="$(get_env_value FRONTEND_DOMAIN)"
[[ "${BACKEND_READY_URL}" =~ ^https://[^[:space:]]+/ready$ ]] || fail "BACKEND_READY_URL must be an HTTPS /ready URL."
[[ "${FRONTEND_URL}" =~ ^https://[^[:space:]]+/?$ ]] || fail "FRONTEND_URL must be an HTTPS origin URL."
[[ "${API_DOMAIN}" =~ ^[a-z0-9.-]+$ ]] || fail "API_DOMAIN must be a lowercase DNS hostname."
[[ "${FRONTEND_DOMAIN}" =~ ^[a-z0-9.-]+$ ]] || fail "FRONTEND_DOMAIN must be a lowercase DNS hostname."
[[ "${BACKEND_READY_URL}" == "https://${API_DOMAIN}/ready" ]] || fail "BACKEND_READY_URL must use API_DOMAIN."
[[ "${FRONTEND_URL%/}" == "https://${FRONTEND_DOMAIN}" ]] || fail "FRONTEND_URL must use FRONTEND_DOMAIN."
if [[ "${ENVIRONMENT}" == "dev" ]]; then
  EDGE_API_DOMAIN="$(get_file_env_value "${EDGE_ENV_FILE}" DEV_API_DOMAIN)"
  EDGE_FRONTEND_DOMAIN="$(get_file_env_value "${EDGE_ENV_FILE}" DEV_FRONTEND_DOMAIN)"
else
  EDGE_API_DOMAIN="$(get_file_env_value "${EDGE_ENV_FILE}" PROD_API_DOMAIN)"
  EDGE_FRONTEND_DOMAIN="$(get_file_env_value "${EDGE_ENV_FILE}" PROD_FRONTEND_DOMAIN)"
fi
[[ "${API_DOMAIN}" == "${EDGE_API_DOMAIN}" ]] || fail "API_DOMAIN does not match the shared edge configuration."
[[ "${FRONTEND_DOMAIN}" == "${EDGE_FRONTEND_DOMAIN}" ]] || fail "FRONTEND_DOMAIN does not match the shared edge configuration."

validate_requested_image "${BACKEND_IMAGE}" backend
validate_requested_image "${FRONTEND_IMAGE}" frontend
EXPECTED_IMAGE_SHA="${COMMIT_SHA}"
if [[ "${BACKEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* ]]; then
  [[ "${BACKEND_IMAGE##*-sha-}" == "${EXPECTED_IMAGE_SHA}" ]] || fail "Backend image tag does not match the requested commit."
fi
if [[ "${FRONTEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* ]]; then
  [[ "${FRONTEND_IMAGE##*-sha-}" == "${EXPECTED_IMAGE_SHA}" ]] || fail "Frontend image tag does not match the requested commit."
fi

mkdir -p "${APP_DIR}" "${STATE_DIR}" "${BACKUP_DIR}" "$(dirname "${LOCK_FILE}")"
chmod 700 "${STATE_DIR}" "${BACKUP_DIR}"

exec 9>"${LOCK_FILE}"
flock -w "${DEPLOY_LOCK_TIMEOUT_SECONDS:-300}" 9 || fail "Timed out waiting for the host deployment lock."

PREVIOUS_BACKEND_IMAGE="$(get_env_value BACKEND_IMAGE)"
PREVIOUS_FRONTEND_IMAGE="$(get_env_value FRONTEND_IMAGE)"
validate_stored_image "${PREVIOUS_BACKEND_IMAGE}" backend
validate_stored_image "${PREVIOUS_FRONTEND_IMAGE}" frontend
if [[ "${PREVIOUS_BACKEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* || "${PREVIOUS_FRONTEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* ]]; then
  [[ "${PREVIOUS_BACKEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* && "${PREVIOUS_FRONTEND_IMAGE}" == *":${ENVIRONMENT}-sha-"* ]] || fail "Previous image pair mixes a tag and digest."
  [[ "${PREVIOUS_BACKEND_IMAGE##*-sha-}" == "${PREVIOUS_FRONTEND_IMAGE##*-sha-}" ]] || fail "Previous backend/frontend images are not from the same commit."
fi

export DEPLOY_ENV="${ENVIRONMENT}"
export APP_ENV_FILE="${ENV_FILE}"

compose_timed 1m config --quiet

BACKUP_FILE=""
BACKUP_VALIDATED="false"
MUTATED="false"
trap 'on_exit $?' EXIT
if [[ "${ENVIRONMENT}" == "prod" ]]; then
  database_id="$(compose_timed 15s ps -q database 2>/dev/null || true)"
  [[ -n "${database_id}" ]] || fail "Production database is not running; bootstrap and verify it before enabling automated CD."

  BACKUP_FILE="$(mktemp "${BACKUP_DIR}/ocean-park-prod_$(date -u +%Y%m%dT%H%M%SZ).XXXXXX.dump")"
  chmod 600 "${BACKUP_FILE}"
  database_size="$(compose_timed 1m exec -T database sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atqc "SELECT pg_database_size(current_database())"')"
  [[ "${database_size}" =~ ^[0-9]+$ ]] || fail "Could not determine production database size."
  backup_free_bytes="$(df --output=avail -B1 "${BACKUP_DIR}" | tail -n 1 | tr -d '[:space:]')"
  [[ "${backup_free_bytes}" =~ ^[0-9]+$ ]] || fail "Could not determine backup filesystem free space."
  required_free_bytes=$((database_size * 2 + 1073741824))
  (( backup_free_bytes >= required_free_bytes )) || fail "Insufficient backup space: require twice the database size plus 1 GiB free."
  echo "Creating and validating the production database backup before image mutation."
  compose_timed 5m exec -T database sh -lc \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' \
    > "${BACKUP_FILE}"
  [[ -s "${BACKUP_FILE}" ]] || fail "Production backup is empty."
  compose_timed 2m exec -T database pg_restore --list < "${BACKUP_FILE}" >/dev/null || fail "Production backup validation failed."
  BACKUP_VALIDATED="true"
fi

RESOLVED_BACKEND_IMAGE="$(pull_and_resolve_image "${BACKEND_IMAGE}")"
RESOLVED_FRONTEND_IMAGE="$(pull_and_resolve_image "${FRONTEND_IMAGE}")"
validate_stored_image "${RESOLVED_BACKEND_IMAGE}" backend
validate_stored_image "${RESOLVED_FRONTEND_IMAGE}" frontend

write_image_pair "${RESOLVED_BACKEND_IMAGE}" "${RESOLVED_FRONTEND_IMAGE}"
MUTATED="true"

compose_timed 1m config --quiet
compose_timed 2m up -d

wait_for_service backend 300 || fail "Backend did not become healthy."
wait_for_service frontend 300 || fail "Frontend did not become healthy."
check_public_endpoints || fail "Public readiness checks failed."

ledger_tmp="$(mktemp "${STATE_DIR}/${ENVIRONMENT}.json.tmp.XXXXXX")"
printf '{\n  "environment": "%s",\n  "commit": "%s",\n  "backend_image": "%s",\n  "frontend_image": "%s",\n  "deployed_at": "%s",\n  "backup_file": "%s"\n}\n' \
  "${ENVIRONMENT}" "${COMMIT_SHA}" "${RESOLVED_BACKEND_IMAGE}" "${RESOLVED_FRONTEND_IMAGE}" \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${BACKUP_FILE}" > "${ledger_tmp}"
chmod 600 "${ledger_tmp}"
mv -f "${ledger_tmp}" "${STATE_DIR}/${ENVIRONMENT}.json"

MUTATED="false"
trap - EXIT
echo "${ENVIRONMENT} deployment completed successfully for ${COMMIT_SHA}."
