# DreamDEX Trading Bot

Automated spot trading on [DreamDEX](https://docs.dreamdex.io) — wallet-funded orders on Somnia mainnet via `SpotPool` (`placeTakerOrderWithoutVault`).

## Features

- Somnia mainnet (chain `5031`)
- REST market discovery, SIWE auth, and prepared orders
- Configurable buy/sell loop with slippage control and gas estimation
- Optional high-turnover mode (`volume_mode`) for larger per-trade sizing
- Preflight checks before live trading

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp bot/config.yml.example bot/config.yml
cp .env.example .env
# Edit .env — set PRIVATE_KEY (never commit)

python3 bot/preflight.py --config bot/config.yml
./run_bg.sh
```

See [bot/README.md](bot/README.md) for configuration details.

## Operations

| Doc | Description |
|-----|-------------|
| [docs/DEPLOY.md](docs/DEPLOY.md) | 24/7 VPS + systemd |
| [docs/INTEGRATION.md](docs/INTEGRATION.md) | Mainnet integration notes (gas, approvals, API) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Product roadmap |
| [SECURITY.md](SECURITY.md) | Secrets and deployment hygiene |
| [DreamDexdocs/](DreamDexdocs/) | Local copy of protocol documentation |

## Scripts

| Script | Purpose |
|--------|---------|
| `run_bot.sh` | Foreground bot |
| `run_bg.sh` | Background via `nohup` |
| `run_forever.sh` | Restart loop on crash |

## License

See repository owner.
