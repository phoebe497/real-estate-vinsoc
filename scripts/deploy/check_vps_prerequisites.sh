#!/usr/bin/env bash
set -euo pipefail

echo "Checking VPS deployment prerequisites..."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found. Install Docker Engine first."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: docker compose plugin not found. Install docker-compose-plugin first."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git command not found."
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl command not found."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: current user cannot access Docker daemon."
  echo "Try running with sudo or add the user to the docker group, then re-login."
  exit 1
fi

echo "Docker: $(docker --version)"
echo "Compose: $(docker compose version)"
echo "Git: $(git --version)"
echo "Prerequisites OK."
