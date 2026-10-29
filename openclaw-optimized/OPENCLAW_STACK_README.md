# OpenClaw / Moltbot — stack personnel

Ce dossier contient une installation locale d’OpenClaw (successeur de Moltbot) avec un Gateway, un relais LLM compatible streaming et une connexion Android via Cloudflare Quick Tunnel.

## Démarrage reproductible

Depuis `/home/ubuntu/openclaw`, avec `OPENAI_API_BASE` et `OPENAI_API_KEY` disponibles dans l’environnement :

```bash
./start-openclaw-stack.sh
```

Le script démarre le relais LLM, le Gateway, attend le health check, crée un nouveau Quick Tunnel, met à jour l’origine autorisée du Control UI et recrée automatiquement le QR Android dans :

```text
openclaw-mobile-pairing-qr-latest.png
```

Pour arrêter uniquement les processus lancés par le script :

```bash
./stop-openclaw-stack.sh
```

Les journaux et PID sont conservés dans `.openclaw-stack/`.

## Architecture actuelle

- Gateway OpenClaw : port local `18789`, authentification par token.
- Relais LLM : `127.0.0.1:19090`, uniquement accessible localement.
- Modèle principal : `manus-bridge/gpt-6-luna`.
- Fallbacks : `gpt-6-sol`, `gpt-6.1-sol`, `gpt-5.5`, `gpt-5-mini`.
- Mémoire : recherche par mots-clés, sans embeddings OpenAI invalides.
- Android : pairing OpenClaw avec WebSocket `wss://` via Cloudflare.

## Limite importante

Le sandbox par défaut hiberne lorsqu’il est inactif. Un Quick Tunnel sans compte Cloudflare est temporaire et n’offre aucune garantie de disponibilité. Si le sandbox s’arrête, il faut relancer `start-openclaw-stack.sh` et scanner le nouveau QR.

Pour un accès Android permanent, il faut exécuter ces fichiers sur une machine qui reste allumée ou utiliser un hébergement persistant, puis remplacer le Quick Tunnel par un Cloudflare Named Tunnel. Le script ne crée pas de compte Cloudflare et ne peut pas obtenir de credentials Cloudflare qui ne sont pas présents dans l’environnement.

## Sécurité

Le Gateway utilise un token et une limitation anti-brute-force. Le Control UI accepte uniquement l’origine publique courante. Le relais LLM écoute sur loopback et n’accepte qu’une liste de modèles connue.

Les capacités d’exécution personnelle restent larges pour préserver l’autonomie de l’agent. Pour un environnement multi-utilisateur, il faut réduire `exec` et les accès fichiers, utiliser un workspace dédié et séparer les comptes OS.
