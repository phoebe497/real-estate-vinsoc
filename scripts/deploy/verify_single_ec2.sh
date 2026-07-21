#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
APP_COMPOSE="${PROJECT_ROOT}/deploy/compose/application.yml"
EDGE_COMPOSE="${PROJECT_ROOT}/deploy/compose/edge.yml"
CD_WORKFLOW="${PROJECT_ROOT}/.github/workflows/cd-single-ec2.yml"
CI_WORKFLOW="${PROJECT_ROOT}/.github/workflows/ci.yml"
AWS_TEMPLATE="${PROJECT_ROOT}/deploy/aws/single-ec2-cicd.yml"

for command_name in docker python; do
  command -v "${command_name}" >/dev/null 2>&1 || {
    echo "ERROR: ${command_name} is required." >&2
    exit 1
  }
done
docker compose version >/dev/null 2>&1 || {
  echo "ERROR: Docker Compose plugin is required." >&2
  exit 1
}

tmp_dir="$(mktemp -d)"
cleanup() {
  [[ -n "${tmp_dir:-}" && -d "${tmp_dir}" ]] && rm -rf -- "${tmp_dir}"
}
trap cleanup EXIT

write_app_fixture() {
  local environment="$1"
  local file="$2"
  local tag_prefix="$3"
  cat > "${file}" <<EOF
APP_ENV=${environment}
POSTGRES_DB=ocean_park_${environment}
POSTGRES_USER=ocean_${environment}
POSTGRES_PASSWORD=verification-only-password
DATABASE_URL=postgresql+psycopg://ocean_${environment}:verification-only-password@database:5432/ocean_park_${environment}
JWT_SECRET_KEY=verification-only-jwt-secret-key
ADMIN_EMAIL=verification@example.invalid
ADMIN_PASSWORD=verification-only-admin-password
CORS_ORIGINS=https://${environment}.example.invalid
NEXT_PUBLIC_API_URL=https://api-${environment}.example.invalid/api/v1
AUTO_SEED_CATALOG=true
BACKEND_IMAGE=ghcr.io/example/ocean-park-backend:${tag_prefix}-sha-0123456789abcdef0123456789abcdef01234567
FRONTEND_IMAGE=ghcr.io/example/ocean-park-frontend:${tag_prefix}-sha-0123456789abcdef0123456789abcdef01234567
DEPLOY_IMAGE_PREFIX=ghcr.io/example/ocean-park
BACKEND_READY_URL=https://api-${environment}.example.invalid/ready
FRONTEND_URL=https://${environment}.example.invalid
API_DOMAIN=api-${environment}.example.invalid
FRONTEND_DOMAIN=${environment}.example.invalid
DATABASE_CPU_LIMIT=0.5
DATABASE_MEMORY_LIMIT=512M
BACKEND_CPU_LIMIT=0.5
BACKEND_MEMORY_LIMIT=512M
FRONTEND_CPU_LIMIT=0.25
FRONTEND_MEMORY_LIMIT=256M
EOF
}

write_app_fixture development "${tmp_dir}/dev.env" dev
write_app_fixture production "${tmp_dir}/prod.env" prod

cat > "${tmp_dir}/edge.env" <<'EOF'
ACME_EMAIL=verification@example.invalid
DEV_FRONTEND_DOMAIN=dev.example.invalid
DEV_API_DOMAIN=api-dev.example.invalid
PROD_FRONTEND_DOMAIN=example.invalid
PROD_API_DOMAIN=api.example.invalid
EOF

DEPLOY_ENV=dev APP_ENV_FILE="${tmp_dir}/dev.env" \
  docker compose --env-file "${tmp_dir}/dev.env" --project-name ocean-park-dev \
  --file "${APP_COMPOSE}" config --format json > "${tmp_dir}/dev.json"

DEPLOY_ENV=prod APP_ENV_FILE="${tmp_dir}/prod.env" \
  docker compose --env-file "${tmp_dir}/prod.env" --project-name ocean-park-prod \
  --file "${APP_COMPOSE}" config --format json > "${tmp_dir}/prod.json"

docker compose --env-file "${tmp_dir}/edge.env" --project-name ocean-park-edge \
  --file "${EDGE_COMPOSE}" config --format json > "${tmp_dir}/edge.json"

python - "${tmp_dir}/dev.json" "${tmp_dir}/prod.json" "${tmp_dir}/edge.json" <<'PY'
import json
import sys

dev, prod, edge = (json.load(open(path, encoding="utf-8")) for path in sys.argv[1:])

def service_networks(service):
    networks = service.get("networks", {})
    return set(networks if isinstance(networks, list) else networks.keys())

def aliases(config, service):
    network = config["services"][service]["networks"]["edge"]
    return set(network.get("aliases", []))

def check(condition, message):
    if not condition:
        raise RuntimeError(message)

for environment, config in (("dev", dev), ("prod", prod)):
    services = config["services"]
    check(services["database"]["image"].startswith("pgvector/pgvector:pg16"), f"{environment} does not use pgvector pg16")
    check(service_networks(services["database"]) == {"private"}, f"{environment} database is not private-only")
    check("edge" in service_networks(services["backend"]), f"{environment} backend is absent from edge")
    check("edge" in service_networks(services["frontend"]), f"{environment} frontend is absent from edge")
    check(aliases(config, "backend") == {f"{environment}-backend"}, f"{environment} backend alias is wrong")
    check(aliases(config, "frontend") == {f"{environment}-frontend"}, f"{environment} frontend alias is wrong")
    for name, service in services.items():
        check(not service.get("ports"), f"{environment}/{name} publishes a host port")
        check(not service.get("privileged", False), f"{environment}/{name} is privileged")
        for volume in service.get("volumes", []):
            source = volume.get("source", "") if isinstance(volume, dict) else str(volume)
            check("docker.sock" not in source, f"{environment}/{name} mounts Docker socket")

check(dev["volumes"]["postgres_data"]["name"] != prod["volumes"]["postgres_data"]["name"], "dev/prod share a database volume")
check(dev["networks"]["private"]["name"] != prod["networks"]["private"]["name"], "dev/prod share a private network")
check(aliases(dev, "backend").isdisjoint(aliases(prod, "backend")), "dev/prod backend aliases overlap")
check(aliases(dev, "frontend").isdisjoint(aliases(prod, "frontend")), "dev/prod frontend aliases overlap")

edge_services = edge["services"]
check(set(edge_services) == {"caddy"}, "edge stack contains services other than Caddy")
published = {(int(port["published"]), port.get("protocol", "tcp")) for port in edge_services["caddy"]["ports"]}
check(published == {(80, "tcp"), (443, "tcp"), (443, "udp")}, f"edge publishes unexpected ports: {published}")
check(not edge_services["caddy"].get("privileged", False), "Caddy is privileged")
for volume in edge_services["caddy"].get("volumes", []):
    source = volume.get("source", "") if isinstance(volume, dict) else str(volume)
    check("docker.sock" not in source, "Caddy mounts Docker socket")

print("Rendered Compose invariants passed for edge, development, and production.")
PY

grep -q 'id-token: write' "${CD_WORKFLOW}"
grep -q 'group: ocean-park-single-ec2-${{ github.event.workflow_run.head_branch }}' "${CD_WORKFLOW}"
grep -q 'actions/upload-artifact@v4' "${CI_WORKFLOW}"
grep -q 'steps.backend_build.outputs.digest' "${CI_WORKFLOW}"
grep -q 'actions/download-artifact@v4' "${CD_WORKFLOW}"
grep -q '@sha256:' "${CD_WORKFLOW}"
if grep -q 'AWS-RunShellScript' "${CD_WORKFLOW}" "${AWS_TEMPLATE}"; then
  echo "ERROR: arbitrary AWS-RunShellScript usage detected." >&2
  exit 1
fi
grep -q '/usr/local/sbin/ocean-park-deploy dev' "${AWS_TEMPLATE}"
grep -q '/usr/local/sbin/ocean-park-deploy prod' "${AWS_TEMPLATE}"

echo "Single-EC2 CI/CD verification passed."
