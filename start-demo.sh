#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_URL="http://127.0.0.1:5173"
BACKEND_PID=""
ANALYZER_PID=""
OLLAMA_PID=""
FRONTEND_PID=""

cleanup() {
  for service_pid in "$FRONTEND_PID" "$ANALYZER_PID" "$BACKEND_PID" "$OLLAMA_PID"; do
    if [[ -n "$service_pid" ]]; then kill "$service_pid" 2>/dev/null || true; fi
  done
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if ! curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  ollama serve >/tmp/issuelens-ollama.log 2>&1 &
  OLLAMA_PID=$!
fi

if ! curl -fsS --max-time 2 http://127.0.0.1:5001/api/health >/dev/null 2>&1; then
  (cd "$PROJECT_DIR/backend" && exec node src/server.js) >/tmp/issuelens-backend.log 2>&1 &
  BACKEND_PID=$!
fi

if ! curl -fsS --max-time 2 http://127.0.0.1:8001/health >/dev/null 2>&1; then
  (cd "$PROJECT_DIR/analyzer" && exec .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8001) >/tmp/issuelens-analyzer.log 2>&1 &
  ANALYZER_PID=$!
fi

if ! curl -fsS --max-time 2 "$APP_URL" >/dev/null 2>&1; then
  (cd "$PROJECT_DIR/frontend" && exec ./node_modules/.bin/vite --host 127.0.0.1 --port 5173 --strictPort) >/tmp/issuelens-frontend.log 2>&1 &
  FRONTEND_PID=$!
fi

wait_for() {
  local service_url="$1"
  local attempt=0
  until curl -fsS --max-time 2 "$service_url" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [[ "$attempt" -ge 30 ]]; then echo "Service did not start: $service_url" >&2; exit 1; fi
    sleep 1
  done
}

wait_for http://127.0.0.1:11434/api/tags
wait_for http://127.0.0.1:5001/api/health
wait_for http://127.0.0.1:8001/health
wait_for "$APP_URL"
if ! curl -fsS http://127.0.0.1:11434/api/tags | grep -q 'qwen2.5-coder:3b'; then
  echo "Required local model is missing. Run: ollama pull qwen2.5-coder:3b" >&2
  exit 1
fi

printf 'IssueLens is ready at %s\n' "$APP_URL"
printf 'Guided demo works offline; for live GitHub analysis, enter a read-only token in the app.\n'
open "$APP_URL" 2>/dev/null || true
if [[ -z "$FRONTEND_PID$ANALYZER_PID$BACKEND_PID$OLLAMA_PID" ]]; then
  printf 'All services were already running. Press Ctrl+C to close this launcher.\n'
  while true; do sleep 3600; done
fi
wait
