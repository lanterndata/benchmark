#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "${SCRIPT_DIR}/install_lantern.sh"

# Check if lantern extension is already enabled, and update / enable the extension accordingly
EXTENSION_INSTALLED=$(psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_extension WHERE extname = 'lantern';" -t)
if [[ "$EXTENSION_INSTALLED" -eq 1 ]]; then
    echo "Updating lantern extension..."
    psql "$DATABASE_URL" -c "ALTER EXTENSION lantern UPDATE;"
fi
