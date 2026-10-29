#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  # shellcheck disable=SC1090
  source "$NVM_DIR/nvm.sh"
  nvm use 24.22.1 >/dev/null
fi

OPENCLAW="node dist/entry.js"
STATE="$ROOT/.openclaw-stack"
mkdir -p "$STATE"
chmod 700 "$STATE"
: "${OPENAI_API_BASE:?OPENAI_API_BASE doit être défini}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY doit être défini}"

is_running() { [[ -f "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; }

# Reuse healthy services already running in the sandbox; otherwise start them.
if ! curl -fsS --max-time 2 http://127.0.0.1:19090/v1/models >/dev/null 2>&1; then
  : > "$STATE/bridge.log"
  nohup python3 "$ROOT/manus_stream_bridge.py" >>"$STATE/bridge.log" 2>&1 &
  echo $! > "$STATE/bridge.pid"
fi

if ! curl -fsS --max-time 2 http://127.0.0.1:18789/health >/dev/null 2>&1; then
  : > "$STATE/gateway.log"
  nohup bash -lc "cd '$ROOT' && exec $OPENCLAW gateway run --bind lan --auth token --port 18789 --ws-log compact" >>"$STATE/gateway.log" 2>&1 &
  echo $! > "$STATE/gateway.pid"
  for _ in $(seq 1 60); do
    curl -fsS --max-time 1 http://127.0.0.1:18789/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 5 http://127.0.0.1:18789/health >/dev/null

# A Quick Tunnel is intentionally recreated so the QR always matches its URL.
pkill -f '/home/ubuntu/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:18789' 2>/dev/null || true
sleep 1
: > "$STATE/cloudflared.log"
nohup /home/ubuntu/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:18789 >>"$STATE/cloudflared.log" 2>&1 &
echo $! > "$STATE/cloudflared.pid"

PUBLIC=""
for _ in $(seq 1 60); do
  PUBLIC="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$STATE/cloudflared.log" | head -1 || true)"
  [[ -n "$PUBLIC" ]] && break
  sleep 1
done
[[ -n "$PUBLIC" ]] || { echo "URL Cloudflare introuvable; voir $STATE/cloudflared.log" >&2; exit 1; }

cat > "$STATE/public-origin-patch.json" <<JSON
{"gateway":{"publicOrigin":"$PUBLIC","controlUi":{"allowedOrigins":["$PUBLIC"]}}}
JSON
$OPENCLAW config patch --file "$STATE/public-origin-patch.json" >/dev/null
$OPENCLAW config validate >/dev/null

TOKEN="$(python3 - <<'PY'
import json, pathlib
p=pathlib.Path.home()/'.openclaw/openclaw.json'
print(json.loads(p.read_text())['gateway']['auth']['token'])
PY
)"
$OPENCLAW qr --json --no-ascii --public-url "$PUBLIC" --token "$TOKEN" > "$STATE/qr.json"
python3 - "$STATE/qr.json" "$ROOT/openclaw-mobile-pairing-qr-latest.png" "$PUBLIC" <<'PY'
import json, pathlib, qrcode, sys
raw=pathlib.Path(sys.argv[1]).read_text(errors='replace')
obj=json.loads(raw[raw.find('{'):])
out=pathlib.Path(sys.argv[2])
qrcode.make(obj['setupCode'], error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4).save(out)
out.chmod(0o600)
out.with_name('openclaw-mobile-pairing-latest-meta.txt').write_text(
    f'gateway_url={obj.get("gatewayUrl")}\npublic_url={sys.argv[3]}\nwebsocket_transport=requires_retest\n'
)
PY
chmod 600 "$ROOT/openclaw-mobile-pairing-latest-meta.txt"
printf 'gateway_health=ok\npublic_url=%s\nqr=%s\nstate=%s\n' "$PUBLIC" "$ROOT/openclaw-mobile-pairing-qr-latest.png" "$STATE"
