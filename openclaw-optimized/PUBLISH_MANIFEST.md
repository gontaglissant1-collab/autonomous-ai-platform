# OpenClaw Optimized — publication manifest

This directory contains the non-secret runtime additions prepared for the personal OpenClaw/Moltbot stack:

- `manus_stream_bridge.py`: local OpenAI-compatible bridge with controlled models and tool-call forwarding.
- `start-openclaw-stack.sh`: reproducible startup for the bridge, Gateway, Quick Tunnel and Android QR.
- `stop-openclaw-stack.sh`: clean shutdown helper.
- `OPENCLAW_STACK_README.md`: architecture, operation and persistence limitations.
- `.devcontainer/devcontainer.json`: Codespaces/Dev Container bootstrap for syntax checks.

Excluded intentionally: gateway tokens, API keys, QR images, `.openclaw` state, runtime logs, local tunnel URLs, credentials and environment files.
