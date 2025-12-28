#!/bin/bash
set -e

echo "Starting application..."

# Run Prisma migrations
echo "Running Prisma migrations..."
prisma migrate deploy

# Check migration status
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

# Start the application
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
