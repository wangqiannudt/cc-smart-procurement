#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$FRONTEND_DIR/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

BACKEND_PYTHON="${BACKEND_PYTHON:-$BACKEND_DIR/venv/bin/python}"
BACKEND_LOG="${BACKEND_LOG:-/tmp/cc-smart-procurement-backend-e2e.log}"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required for backend health checks."
  exit 1
fi

if [[ "$BACKEND_PYTHON" == */* ]]; then
  if [[ ! -x "$BACKEND_PYTHON" ]]; then
    echo "Backend python executable not found: $BACKEND_PYTHON"
    echo "Set BACKEND_PYTHON to a valid python executable."
    exit 1
  fi
else
  if ! command -v "$BACKEND_PYTHON" >/dev/null 2>&1; then
    echo "Backend python executable not found in PATH: $BACKEND_PYTHON"
    echo "Set BACKEND_PYTHON to a valid python executable."
    exit 1
  fi
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

(
  cd "$BACKEND_DIR"
  "$BACKEND_PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >"$BACKEND_LOG" 2>&1
) &
BACKEND_PID=$!

for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
  echo "Backend failed to start. Check log: $BACKEND_LOG"
  exit 1
fi

cd "$FRONTEND_DIR"
npx playwright test --grep @integration
