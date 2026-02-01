#!/bin/sh

set -e

# Wait for the database connection
until nc -z -v -w30 db 5432
do
  echo "Waiting for connection to DB"
  sleep 5

done

echo "✅ Database are ready!"

echo "Apply migrations..."
uv run alembic upgrade head

echo "Starting application..."
echo "🚀 Starting command (exec $@)..."
exec "$@"