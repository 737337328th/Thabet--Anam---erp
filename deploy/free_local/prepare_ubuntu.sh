#!/usr/bin/env bash
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
  SUDO=""
else
  if ! command -v sudo >/dev/null 2>&1; then
    echo "sudo is required for package installation."
    exit 2
  fi
  SUDO="sudo"
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This helper supports Ubuntu/Debian systems using apt."
  exit 3
fi

echo "Installing free local prerequisites: Git, Python 3, Docker Engine and Compose..."
$SUDO apt-get update
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 ca-certificates curl docker.io docker-compose-v2

if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
  $SUDO systemctl enable --now docker
else
  $SUDO service docker start || true
fi

if [[ "$(id -u)" -ne 0 ]]; then
  if ! id -nG "$USER" | grep -qw docker; then
    $SUDO usermod -aG docker "$USER"
    echo
    echo "Your user was added to the docker group."
    echo "Close this WSL/terminal window and open it again before running docker_zero_cost.sh."
  fi
fi

echo
docker --version || true
docker compose version || true
echo "Prerequisite installation completed."
