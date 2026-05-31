# Security

## Secrets — never commit

| File | Purpose |
|------|---------|
| `.env` | `PRIVATE_KEY` for the competition wallet |
| `bot/config.yml` | Local overrides (copied from example) |
| `metrics.json` | Runtime trading metrics |
| `bot_state.json` | Last tx / wallet state |
| `bot.log`, `logs/` | Logs may include addresses and errors |

All of the above are listed in `.gitignore`. Use `.env.example` and `bot/config.yml.example` only.

## Wallet hygiene

- Use a **dedicated competition wallet** with only the allocated capital (~$50 USDso + gas SOMI).
- Do not reuse personal wallets or commit private keys to Git, screenshots, or chat.
- Register the wallet with the competition before trading.

## Server deployment

- Restrict `.env` permissions: `chmod 600 .env`
- Prefer SSH keys over password login on VPS
- Do not expose `.env` or logs via public HTTP
- Rotate or destroy the VPS after the competition if the key was stored on disk

## Dependencies

```bash
pip install -r requirements.txt
```

Pin versions in production; review updates before upgrading `web3` / `eth-account`.

## Reporting issues

If you discover a key committed by mistake, rotate the wallet immediately with organizers and purge history before pushing again.
