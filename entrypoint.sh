#!/bin/bash
set -e

echo "[ENTRYPOINT] Starting Security Playground..."
echo "[ENTRYPOINT] Python version: $(python --version)"
echo "[ENTRYPOINT] Gunicorn version: $(gunicorn --version)"

# Run gunicorn with proper signal handling
exec gunicorn \
    -b :8080 \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
