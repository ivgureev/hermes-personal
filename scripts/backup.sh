#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
stamp=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/hermes_backup_${stamp}.tar.gz" data .env
ls -lh "backups/hermes_backup_${stamp}.tar.gz"
