#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "${SCRIPT_DIR}/install_neon.sh"

# Check if neon extension is already enabled, and update / enable the extension accordingly
EXTENSION_INSTALLED=$(psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_extension WHERE extname = 'embedding';" -t)
if [[ "$EXTENSION_INSTALLED" -eq 1 ]]; then
    echo "Updating neon extension..."
    psql -U postgres -c "ALTER EXTENSION embedding UPDATE;"
fi
