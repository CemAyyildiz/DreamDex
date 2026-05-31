# DreamDEX SpotPool Volume Bot (Mainnet)

Automated taker orders on dreamDEX **SpotPool** (`placeTakerOrderWithoutVault`) for the alpha trading competition.

- **Chain:** Somnia mainnet (`5031`)
- **API:** `https://api.dreamdex.io` (market data + SIWE + order preparation)
- **Funding:** Wallet (IOC taker orders; no vault)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp bot/config.yml.example bot/config.yml
# Add PRIVATE_KEY to .env in repo root (competition wallet only)

./run_bot.sh
```

## Volume mode

Set `volume_mode: true` in `bot/config.yml` (see example). The bot will:

- Use ~90% of spendable balance per trade (`trade_fraction`)
- Reserve quote + native SOMI for gas
- Max-approve ERC-20 tokens once at startup
- Alternate buy/sell for cumulative volume
- Log approximate cumulative USDso volume after each fill

Recommended market for ~$50 capital: **`USDC.e:USDso`** (min size 1 USDC.e).

## Config

| Key | Description |
|-----|-------------|
| `PRIVATE_KEY` | Env var name in `.env` (default `PRIVATE_KEY`) |
| `market_symbol` | e.g. `USDC.e:USDso`, `WETH:USDso`, `SOMI:USDso` |
| `volume_mode` | Large trades, fewer txs, volume-focused |
| `freq_sec` | Seconds between attempts after errors / idle |
| `min_loop_sec` | Shorter delay after a successful fill (volume mode default 3s) |
| `volume_target_quote_raw` | Optional — bot **stops** at this volume; omit to run forever |

## Metrics

`metrics.json` tracks `volume_in_raw`, `volume_out_raw`, `orders`, `errors`.  
Approximate USDso volume ≈ `(volume_in_raw + volume_out_raw) / 1e18`.

## Run 24/7

See [docs/DEPLOY.md](../docs/DEPLOY.md) for VPS + systemd setup. Use `./run_forever.sh` to auto-restart on crash.

## Notes

- This is **not** the SpotRouter swap path; it uses the CLOB pool directly.
- Wallet-funded taker orders must use **IOC** or **FOK** on-chain (bot defaults to IOC).
- Register your wallet with the competition before trading.
