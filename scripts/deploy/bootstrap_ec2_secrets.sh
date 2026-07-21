#!/usr/bin/env bash
set -Eeuo pipefail

readonly DOMAIN="vsocintern.online"
readonly EXPECTED_IPV4="52.221.55.193"
readonly IMAGE_PREFIX="ghcr.io/phoebe497/real-estate-vinsoc"
readonly CONFIG_DIR="/etc/ocean-park"
readonly INSTALL_ROOT="/opt/ocean-park"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
START_TARGET="none"
FORCE=false

usage() {
  cat <<'EOF'
Usage:
  sudo bash scripts/deploy/bootstrap_ec2_secrets.sh [options]

Options:
  --start none|prod|dev|both  Start selected stacks after writing configuration.
                              Default: none
  --force                     Replace existing environment files without asking.
  -h, --help                  Show this help.

The script is intentionally interactive so API keys and passwords do not appear
in shell history or process arguments.
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --start)
      (($# >= 2)) || fail "--start requires none, prod, dev, or both"
      START_TARGET="$2"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

case "${START_TARGET}" in
  none|prod|dev|both) ;;
  *) fail "--start must be none, prod, dev, or both" ;;
esac

[[ "${EUID}" -eq 0 ]] || fail "Run this script with sudo."
command -v openssl >/dev/null || fail "openssl is required."
command -v install >/dev/null || fail "install is required."

for source_file in \
  "${PROJECT_ROOT}/deploy/compose/application.yml" \
  "${PROJECT_ROOT}/deploy/compose/edge.yml" \
  "${PROJECT_ROOT}/deploy/caddy/Caddyfile.single-ec2" \
  "${PROJECT_ROOT}/scripts/deploy/ec2_deploy.sh"; do
  [[ -f "${source_file}" ]] || fail "Missing repository file: ${source_file}"
done

if [[ "${FORCE}" != true ]] && compgen -G "${CONFIG_DIR}/*.env" >/dev/null 2>&1; then
  read -r -p "Environment files already exist in ${CONFIG_DIR}. Replace them? [y/N] " replace_answer
  [[ "${replace_answer}" =~ ^[Yy]$ ]] || fail "Cancelled without changing existing files."
fi

read_required() {
  local prompt="$1"
  local variable_name="$2"
  local value
  while true; do
    read -r -p "${prompt}: " value
    if [[ -n "${value}" ]]; then
      printf -v "${variable_name}" '%s' "${value}"
      return
    fi
    printf 'A value is required.\n' >&2
  done
}

read_secret() {
  local prompt="$1"
  local variable_name="$2"
  local minimum_length="$3"
  local value
  while true; do
    read -r -s -p "${prompt}: " value
    printf '\n'
    if ((${#value} >= minimum_length)); then
      printf -v "${variable_name}" '%s' "${value}"
      return
    fi
    printf 'Value must contain at least %s characters.\n' "${minimum_length}" >&2
  done
}

read_sha() {
  local prompt="$1"
  local variable_name="$2"
  local value
  while true; do
    read -r -p "${prompt}: " value
    if [[ "${value}" =~ ^[0-9a-f]{40}$ ]]; then
      printf -v "${variable_name}" '%s' "${value}"
      return
    fi
    printf 'Enter the full lowercase 40-character commit SHA.\n' >&2
  done
}

printf 'Configuring %s on EC2 %s\n' "${DOMAIN}" "${EXPECTED_IPV4}"
printf 'Secrets are read silently and are never passed as command-line arguments.\n\n'

read_required "ACME/Let's Encrypt email" ACME_EMAIL
read_required "Production admin email" PROD_ADMIN_EMAIL
read_secret "Production admin password" PROD_ADMIN_PASSWORD 16
read_required "Development admin email" DEV_ADMIN_EMAIL
read_secret "Development admin password" DEV_ADMIN_PASSWORD 16
read_secret "OpenRouter API key" OPENROUTER_API_KEY 16
read_sha "Commit SHA whose prod-sha image exists in GHCR" PROD_SHA
read_sha "Commit SHA whose dev-sha image exists in GHCR" DEV_SHA

PROD_DB_PASSWORD="$(openssl rand -hex 32)"
PROD_JWT_SECRET="$(openssl rand -hex 32)"
PROD_ADMIN_API_KEY="$(openssl rand -hex 32)"
DEV_DB_PASSWORD="$(openssl rand -hex 32)"
DEV_JWT_SECRET="$(openssl rand -hex 32)"
DEV_ADMIN_API_KEY="$(openssl rand -hex 32)"

install -d -m 0755 \
  "${INSTALL_ROOT}/shared" \
  "${INSTALL_ROOT}/edge" \
  "${INSTALL_ROOT}/dev" \
  "${INSTALL_ROOT}/prod"
install -d -m 0700 \
  "${CONFIG_DIR}" \
  /var/lib/ocean-park/deployments \
  /var/backups/ocean-park/postgres

install -o root -g root -m 0644 \
  "${PROJECT_ROOT}/deploy/compose/application.yml" \
  "${INSTALL_ROOT}/shared/application.yml"
install -o root -g root -m 0644 \
  "${PROJECT_ROOT}/deploy/compose/edge.yml" \
  "${INSTALL_ROOT}/shared/edge.yml"
install -o root -g root -m 0644 \
  "${PROJECT_ROOT}/deploy/caddy/Caddyfile.single-ec2" \
  "${INSTALL_ROOT}/shared/Caddyfile.single-ec2"
install -o root -g root -m 0755 \
  "${PROJECT_ROOT}/scripts/deploy/ec2_deploy.sh" \
  /usr/local/sbin/ocean-park-deploy

umask 077

edge_tmp="$(mktemp "${CONFIG_DIR}/edge.env.tmp.XXXXXX")"
prod_tmp="$(mktemp "${CONFIG_DIR}/prod.env.tmp.XXXXXX")"
dev_tmp="$(mktemp "${CONFIG_DIR}/dev.env.tmp.XXXXXX")"

cleanup() {
  rm -f "${edge_tmp:-}" "${prod_tmp:-}" "${dev_tmp:-}"
  unset PROD_DB_PASSWORD PROD_JWT_SECRET PROD_ADMIN_API_KEY
  unset DEV_DB_PASSWORD DEV_JWT_SECRET DEV_ADMIN_API_KEY
  unset PROD_ADMIN_PASSWORD DEV_ADMIN_PASSWORD OPENROUTER_API_KEY
}
trap cleanup EXIT

cat >"${edge_tmp}" <<EOF
ACME_EMAIL=${ACME_EMAIL}
DEV_FRONTEND_DOMAIN=dev.${DOMAIN}
DEV_API_DOMAIN=api-dev.${DOMAIN}
PROD_FRONTEND_DOMAIN=${DOMAIN}
PROD_API_DOMAIN=api.${DOMAIN}
CADDYFILE_PATH=${INSTALL_ROOT}/shared/Caddyfile.single-ec2
CADDY_CPU_LIMIT=0.50
CADDY_MEMORY_LIMIT=256M
EOF

cat >"${prod_tmp}" <<EOF
APP_ENV=production
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000
POSTGRES_DB=ocean_park_production
POSTGRES_USER=ocean_production
POSTGRES_PASSWORD=${PROD_DB_PASSWORD}
DATABASE_URL=postgresql+psycopg://ocean_production:${PROD_DB_PASSWORD}@database:5432/ocean_park_production
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true
JWT_SECRET_KEY=${PROD_JWT_SECRET}
ACCESS_TOKEN_EXPIRE_MINUTES=120
ADMIN_EMAIL=${PROD_ADMIN_EMAIL}
ADMIN_PASSWORD=${PROD_ADMIN_PASSWORD}
ADMIN_API_KEY=${PROD_ADMIN_API_KEY}
ADMIN_FULL_NAME=Production Administrator
CORS_ORIGINS=https://${DOMAIN}
NEXT_PUBLIC_API_URL=https://api.${DOMAIN}/api/v1
BACKEND_READY_URL=https://api.${DOMAIN}/ready
FRONTEND_URL=https://${DOMAIN}
FRONTEND_DOMAIN=${DOMAIN}
API_DOMAIN=api.${DOMAIN}
ACME_EMAIL=${ACME_EMAIL}
PROJECT_NAME=ocean-park-prod
DEPLOY_IMAGE_PREFIX=${IMAGE_PREFIX}
BACKEND_IMAGE=${IMAGE_PREFIX}-backend:prod-sha-${PROD_SHA}
FRONTEND_IMAGE=${IMAGE_PREFIX}-frontend:prod-sha-${PROD_SHA}
DATABASE_CPU_LIMIT=1.50
DATABASE_MEMORY_LIMIT=2G
BACKEND_CPU_LIMIT=1.50
BACKEND_MEMORY_LIMIT=2G
FRONTEND_CPU_LIMIT=1.00
FRONTEND_MEMORY_LIMIT=1G
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat
OPENROUTER_SITE_URL=https://${DOMAIN}
OPENROUTER_APP_NAME=Vinhomes AI Real Estate Advisor
RAG_PROVIDER=pgvector
RAG_EMBEDDING_PROVIDER=openrouter
LANGCHAIN_TRACING_V2=false
EOF

cat >"${dev_tmp}" <<EOF
APP_ENV=staging
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000
POSTGRES_DB=ocean_park_development
POSTGRES_USER=ocean_development
POSTGRES_PASSWORD=${DEV_DB_PASSWORD}
DATABASE_URL=postgresql+psycopg://ocean_development:${DEV_DB_PASSWORD}@database:5432/ocean_park_development
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true
JWT_SECRET_KEY=${DEV_JWT_SECRET}
ACCESS_TOKEN_EXPIRE_MINUTES=480
ADMIN_EMAIL=${DEV_ADMIN_EMAIL}
ADMIN_PASSWORD=${DEV_ADMIN_PASSWORD}
ADMIN_API_KEY=${DEV_ADMIN_API_KEY}
ADMIN_FULL_NAME=Development Administrator
CORS_ORIGINS=https://dev.${DOMAIN}
NEXT_PUBLIC_API_URL=https://api-dev.${DOMAIN}/api/v1
BACKEND_READY_URL=https://api-dev.${DOMAIN}/ready
FRONTEND_URL=https://dev.${DOMAIN}
FRONTEND_DOMAIN=dev.${DOMAIN}
API_DOMAIN=api-dev.${DOMAIN}
ACME_EMAIL=${ACME_EMAIL}
PROJECT_NAME=ocean-park-dev
DEPLOY_IMAGE_PREFIX=${IMAGE_PREFIX}
BACKEND_IMAGE=${IMAGE_PREFIX}-backend:dev-sha-${DEV_SHA}
FRONTEND_IMAGE=${IMAGE_PREFIX}-frontend:dev-sha-${DEV_SHA}
DATABASE_CPU_LIMIT=0.75
DATABASE_MEMORY_LIMIT=768M
BACKEND_CPU_LIMIT=0.75
BACKEND_MEMORY_LIMIT=768M
FRONTEND_CPU_LIMIT=0.50
FRONTEND_MEMORY_LIMIT=512M
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat
OPENROUTER_SITE_URL=https://dev.${DOMAIN}
OPENROUTER_APP_NAME=Vinhomes AI Real Estate Advisor Development
RAG_PROVIDER=pgvector
RAG_EMBEDDING_PROVIDER=openrouter
LANGCHAIN_TRACING_V2=false
EOF

chown root:root "${edge_tmp}" "${prod_tmp}" "${dev_tmp}"
chmod 600 "${edge_tmp}" "${prod_tmp}" "${dev_tmp}"
mv -f "${edge_tmp}" "${CONFIG_DIR}/edge.env"
mv -f "${prod_tmp}" "${CONFIG_DIR}/prod.env"
mv -f "${dev_tmp}" "${CONFIG_DIR}/dev.env"

printf '\nCreated protected environment files:\n'
stat -c '%a %U:%G %n' \
  "${CONFIG_DIR}/edge.env" \
  "${CONFIG_DIR}/dev.env" \
  "${CONFIG_DIR}/prod.env"

if command -v getent >/dev/null; then
  printf '\nDNS check (every name should resolve to %s):\n' "${EXPECTED_IPV4}"
  for hostname in \
    "${DOMAIN}" \
    "api.${DOMAIN}" \
    "dev.${DOMAIN}" \
    "api-dev.${DOMAIN}"; do
    resolved_ip="$(getent ahostsv4 "${hostname}" 2>/dev/null | awk 'NR == 1 { print $1 }')"
    if [[ "${resolved_ip}" == "${EXPECTED_IPV4}" ]]; then
      printf '  OK   %-30s %s\n' "${hostname}" "${resolved_ip}"
    else
      printf '  WARN %-30s resolved to %s\n' "${hostname}" "${resolved_ip:-nothing}"
    fi
  done
fi

start_edge() {
  command -v docker >/dev/null || fail "Docker is required for --start."
  docker compose version >/dev/null || fail "Docker Compose plugin is required for --start."
  docker network inspect ocean-park-edge >/dev/null 2>&1 || docker network create ocean-park-edge
  docker compose \
    --env-file "${CONFIG_DIR}/edge.env" \
    --project-name ocean-park-edge \
    --project-directory "${INSTALL_ROOT}/edge" \
    --file "${INSTALL_ROOT}/shared/edge.yml" \
    config --quiet
  docker compose \
    --env-file "${CONFIG_DIR}/edge.env" \
    --project-name ocean-park-edge \
    --project-directory "${INSTALL_ROOT}/edge" \
    --file "${INSTALL_ROOT}/shared/edge.yml" \
    up -d
}

start_app() {
  local environment="$1"
  local project_name env_file
  if [[ "${environment}" == "prod" ]]; then
    project_name="ocean-park-prod"
    env_file="${CONFIG_DIR}/prod.env"
  else
    project_name="ocean-park-dev"
    env_file="${CONFIG_DIR}/dev.env"
  fi

  env DEPLOY_ENV="${environment}" APP_ENV_FILE="${env_file}" \
    docker compose \
    --env-file "${env_file}" \
    --project-name "${project_name}" \
    --project-directory "${INSTALL_ROOT}/${environment}" \
    --file "${INSTALL_ROOT}/shared/application.yml" \
    config --quiet
  env DEPLOY_ENV="${environment}" APP_ENV_FILE="${env_file}" \
    docker compose \
    --env-file "${env_file}" \
    --project-name "${project_name}" \
    --project-directory "${INSTALL_ROOT}/${environment}" \
    --file "${INSTALL_ROOT}/shared/application.yml" \
    up -d
}

if [[ "${START_TARGET}" != "none" ]]; then
  printf '\nStarting the shared edge...\n'
  start_edge
  case "${START_TARGET}" in
    prod) start_app prod ;;
    dev) start_app dev ;;
    both)
      start_app dev
      start_app prod
      ;;
  esac
  printf '\nContainers:\n'
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
else
  printf '\nConfiguration is ready. Re-run with --start prod, dev, or both to start containers.\n'
fi

printf '\nNext checks:\n'
printf '  curl -I https://%s\n' "${DOMAIN}"
printf '  curl -fsS https://api.%s/ready\n' "${DOMAIN}"
