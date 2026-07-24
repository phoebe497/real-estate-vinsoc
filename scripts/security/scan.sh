#!/usr/bin/env bash
set -Eeuo pipefail

mode="${1:-all}"
keep_application="${KEEP_APPLICATION:-false}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
reports="${repo_root}/security-reports"
dast_project="ai-real-estate-dast"
application_started=false

if ! docker info --format '{{.ServerVersion}}' >/dev/null 2>&1; then
  echo "Docker daemon is unavailable. Start Docker Desktop, switch to Linux containers, and retry." >&2
  exit 1
fi

if [[ ! "${mode}" =~ ^(sast|dast|all)$ ]]; then
  echo "Usage: $0 [sast|dast|all]" >&2
  exit 2
fi

mkdir -p "${reports}/.zap-home"
chmod 0777 "${reports}" "${reports}/.zap-home"

cleanup() {
  if [[ "${application_started}" == "true" && "${keep_application}" != "true" ]]; then
    docker compose --project-directory "${repo_root}" -p "${dast_project}" \
      down --remove-orphans --volumes
  fi
}
trap cleanup EXIT

if [[ "${mode}" =~ ^(sast|all)$ ]]; then
  echo "Running Semgrep SAST..."
  SEMGREP_FORMAT=json SEMGREP_REPORT=semgrep.json \
    docker compose --project-directory "${repo_root}" -p ai-real-estate-sast \
      -f "${repo_root}/compose.security.yml" run --rm semgrep
fi

if [[ "${mode}" =~ ^(dast|all)$ ]]; then
  if [[ ! -f "${repo_root}/.env" ]]; then
    echo "Missing .env. Copy .env.example to .env and set the local values before DAST." >&2
    exit 1
  fi

  echo "Starting the application for OWASP ZAP..."
  AUTO_SEED_CATALOG=false docker compose --project-directory "${repo_root}" \
    -p "${dast_project}" \
    -f "${repo_root}/docker-compose.yml" -f "${repo_root}/compose.dast.yml" \
    up -d --build frontend
  application_started=true

  ready=false
  for _ in $(seq 1 60); do
    if curl --fail --silent http://localhost:8000/ready >/dev/null &&
       curl --fail --silent http://localhost:8000/openapi.json >/dev/null &&
       curl --fail --silent http://localhost:3000 >/dev/null; then
      ready=true
      break
    fi
    sleep 5
  done
  if [[ "${ready}" != "true" ]]; then
    docker compose --project-directory "${repo_root}" -p "${dast_project}" \
      logs --no-color
    echo "The application did not become ready within 5 minutes." >&2
    exit 1
  fi

  echo "Running ZAP baseline scan against the frontend..."
  ZAP_TARGET=http://frontend:3000 ZAP_REPORT=zap-frontend.json \
    docker compose --project-directory "${repo_root}" \
      -p "${dast_project}" \
      -f "${repo_root}/docker-compose.yml" -f "${repo_root}/compose.dast.yml" \
      -f "${repo_root}/compose.security.yml" \
      run --rm --no-deps zap-baseline

  echo "Running ZAP baseline scan against the backend Swagger UI..."
  set +e
  ZAP_API_TARGET=http://backend:8000/docs ZAP_API_REPORT=zap-backend.json \
    docker compose --project-directory "${repo_root}" \
      -p "${dast_project}" \
      -f "${repo_root}/docker-compose.yml" -f "${repo_root}/compose.dast.yml" \
      -f "${repo_root}/compose.security.yml" \
      run --rm --no-deps zap-api
  zap_status=$?
  set -e
  if [[ "${zap_status}" -ne 0 ]]; then
    echo "ZAP backend baseline scan could not complete. Backend and database logs follow:" >&2
    docker compose --project-directory "${repo_root}" -p "${dast_project}" \
      -f "${repo_root}/docker-compose.yml" -f "${repo_root}/compose.dast.yml" \
      logs --no-color backend database >&2 || true
    exit "${zap_status}"
  fi
fi

echo "Aggregating available scanner outputs..."
aggregate_inputs=()
if [[ "${mode}" =~ ^(sast|all)$ && -f "${reports}/semgrep.json" ]]; then
  aggregate_inputs+=("${reports}/semgrep.json")
fi
if [[ "${mode}" =~ ^(dast|all)$ ]]; then
  [[ -f "${reports}/zap-frontend.json" ]] && aggregate_inputs+=("${reports}/zap-frontend.json")
  [[ -f "${reports}/zap-backend.json" ]] && aggregate_inputs+=("${reports}/zap-backend.json")
fi
if ((${#aggregate_inputs[@]})); then
  python "${repo_root}/scripts/security/aggregate_security_reports.py" \
    "${aggregate_inputs[@]}" --output-dir "${repo_root}/security-data-lake"
fi

echo "Security reports are available in ${reports}"
echo "Unified data lake is available in ${repo_root}/security-data-lake"
