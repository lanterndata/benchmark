#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "${SCRIPT_DIR}/install_pgvector.sh"

# Check if pgvector extension is already enabled, and update / enable the extension accordingly
EXTENSION_INSTALLED=$(psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_extension WHERE extname = 'vector';" -t)
if [[ "$EXTENSION_INSTALLED" -eq 1 ]]; then
    echo "Updating pgvector extension..."
    psql -U postgres -c "ALTER EXTENSION vector UPDATE;"
fi
