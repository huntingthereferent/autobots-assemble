#!/usr/bin/env sh
set -eu

input="${1:-platform-backup.sql}"

test -f "$input"
docker compose exec -T db psql   -v ON_ERROR_STOP=1   -U monitor   -d public_data_monitor < "$input"

printf 'backup restored: %s\n' "$input"
