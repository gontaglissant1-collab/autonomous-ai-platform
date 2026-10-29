#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$ROOT/.openclaw-stack"
for name in bridge gateway cloudflared; do
  f="$STATE/$name.pid"
  if [[ -f "$f" ]]; then
    pid="$(cat "$f")"
    if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; fi
    rm -f "$f"
  fi
done
printf '%s\n' 'stack_stopped=true'
