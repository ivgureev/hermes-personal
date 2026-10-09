#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
mkdir -p data/uploads
chmod 700 data || true
docker compose up -d --build
sleep 3
docker compose ps
