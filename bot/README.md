# DreamDEX Trade Bot — SpotPool engine

Automated taker orders on DreamDEX **SpotPool** (`placeTakerOrderWithoutVault`).

- **Chain:** Somnia mainnet (`5031`)
- **API:** `https://api.dreamdex.io` (market data + SIWE + order preparation)
- **Funding:** Wallet (IOC/FOK taker orders; vault optional for future strategies)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp bot/config.yml.example bot/config.yml
# Add PRIVATE_KEY to .env in repo root

./run_bot.sh
```

## Trading modes

**Standard (default)** — `volume_mode: false`

- Uses available wallet balance per side (respecting market min size and gas reserve)
- Alternates buy/sell when both sides are affordable
- Suitable for small accounts and conservative sizing

**High-turnover** — `volume_mode: true`

- Trades a configured fraction of spendable balance (`trade_fraction`)
- Reserves quote and native SOMI for gas
- Faster loop after fills (`min_loop_sec`)
- Useful when you want fewer, larger IOC fills

## Config

| Key | Description |
|-----|-------------|
| `PRIVATE_KEY` | Env var name in `.env` (default `PRIVATE_KEY`) |
| `market_symbol` | e.g. `USDC.e:USDso`, `WETH:USDso`, `SOMI:USDso` |
| `volume_mode` | `false` = standard sizing; `true` = high-turnover mode |
| `trade_fraction` | Fraction of spendable balance per trade (high-turnover mode) |
| `freq_sec` | Seconds between attempts after errors / idle |
| `min_loop_sec` | Shorter delay after a successful fill |
| `slippage_bps` | Aggression vs best bid/ask (basis points) |
| `only_buy` / `only_sell` | Restrict to one side |
| `max_orders` | Stop after N fills (optional) |
| `volume_target_quote_raw` | Stop at cumulative notional (optional; high-turnover) |

**Market notes:** check `minQuantity` via `GET /v0/markets` before choosing a pair. `USDC.e:USDso` has a 1 USDC.e minimum; native-base pairs need extra SOMI for gas.

## Metrics

`metrics.json` tracks `orders`, `errors`, `volume_in_raw`, and `volume_out_raw` for local monitoring on your server.

## Run 24/7

See [docs/DEPLOY.md](../docs/DEPLOY.md). Use `./run_forever.sh` to auto-restart on crash.

## Notes

- Uses the CLOB pool directly, not the SpotRouter swap path.
- Wallet-funded taker orders must use **IOC** or **FOK** on-chain (bot defaults to IOC).
- Run `python3 bot/preflight.py` before first live session.
