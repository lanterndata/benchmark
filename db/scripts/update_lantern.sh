#!/bin/bash
set -e

source ./install_lantern.sh

# Check if lantern extension is already enabled, and update / enable the extension accordingly
EXTENSION_INSTALLED=$(psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_extension WHERE extname = 'lanterndb';" -t)
if [[ "$EXTENSION_INSTALLED" -eq 1 ]]; then
    echo "Updating lantern extension..."
    psql "$DATABASE_URL" -c "ALTER EXTENSION lanterndb UPDATE;"
else
    echo "Enabling lantern extension..."
    psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS lanterndb;"
fi
