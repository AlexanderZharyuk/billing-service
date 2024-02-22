#!/bin/bash
set -e

umask 0002

case "$1" in
    start)
      alembic upgrade head
      gunicorn --bind 0.0.0.0:${PORT:-8000} -w ${WORKERS:-5} \
               -k uvicorn.workers.UvicornWorker --access-logfile - \
               --log-level ${LOG_LEVEL:-info} main:app
      ;;
    *)
      printenv
      exec "$@"
esac
