#!/usr/bin/env sh
set -eu

output="${1:-platform-backup.sql}"

docker compose exec -T db pg_dump   -U monitor   -d public_data_monitor   --clean   --if-exists   --no-owner   --no-privileges > "$output"

printf 'backup written: %s\n' "$output"
