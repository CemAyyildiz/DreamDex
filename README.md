# DreamDEX Volume Bot

Mainnet trading bot for the [DreamDEX](https://docs.dreamdex.io) alpha competition — generates volume via wallet-funded IOC taker orders on `SpotPool` (`placeTakerOrderWithoutVault`).

## Features

- Somnia mainnet (chain `5031`)
- REST market data + SIWE auth + prepared orders
- Volume mode: large trades, buy/sell alternation, gas estimation
- Preflight script before live trading

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
| [docs/FEEDBACK.md](docs/FEEDBACK.md) | Competition feedback report |
| [SECURITY.md](SECURITY.md) | Secrets and deployment hygiene |
| [DreamDexdocs/](DreamDexdocs/) | Local copy of protocol documentation |

## Scripts

| Script | Purpose |
|--------|---------|
| `run_bot.sh` | Foreground bot |
| `run_bg.sh` | Background via `nohup` |
| `run_forever.sh` | Restart loop on crash |

## License

Competition / evaluation submission — see repository owner.
