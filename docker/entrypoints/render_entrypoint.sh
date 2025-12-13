#!/bin/bash

# ---------------------------------------------------------------------------
# Creative Commons CC BY 4.0 - David Romero - Diverso Lab
# ---------------------------------------------------------------------------
# This script is licensed under the Creative Commons Attribution 4.0 
# International License. You are free to share and adapt the material 
# as long as appropriate credit is given, a link to the license is provided, 
# and you indicate if changes were made.
#
# For more details, visit:
# https://creativecommons.org/licenses/by/4.0/
# ---------------------------------------------------------------------------

# Don't exit on error - let gunicorn start even if migrations fail
# set -e

echo "Starting application with the following environment:"
echo "FLASK_ENV: $FLASK_ENV"
echo "MARIADB_HOSTNAME: $MARIADB_HOSTNAME"
echo "MARIADB_DATABASE: $MARIADB_DATABASE"

# Try to run migrations, but don't fail if they error
if [ -d "migrations/versions" ]; then
    echo "Running database migrations..."
    flask db upgrade || echo "Warning: Database migration failed, but continuing startup"
else
    echo "No migrations directory found, skipping migrations"
fi

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:80 \
    --workers 2 \
    --worker-class sync \
    --timeout 3600 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
