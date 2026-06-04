# Product Roadmap — DreamDEX Trade Bot

## Current state (v0.1)

| Component | Role |
|-----------|------|
| [bot/executor.py](../bot/executor.py) | Live trading engine — SIWE, prepare-order, gas, IOC taker loop |
| [bot/preflight.py](../bot/preflight.py) | Pre-live balance, book, and simulation checks |
| [bot/config.yml](../bot/config.yml) | Local config (gitignored) |
| [run_bg.sh](../run_bg.sh) / [run_forever.sh](../run_forever.sh) | Production runners |

**Today:** wallet-funded IOC taker on `SpotPool`, configurable standard or high-turnover mode, REST + on-chain execution.

---

## Vision

**Telegram-controlled, strategy-selectable algo trading on DreamDEX** — users start/stop grid, DCA, or taker strategies; the repo provides the execution engine and control plane.

Aligns with DreamDEX positioning: agents-first, CCXT, WebSocket, third-party apps on the CLOB ([DreamDexdocs/Why dreamDEX.md](../DreamDexdocs/Why%20dreamDEX.md)).

---

## Phase 1 — Modular architecture

Split monolithic `LiveDreamDexBot` into layers:

```
bot/
  core/
    market.py      # discovery, book prices
    orders.py      # prepare, sign, broadcast, gas
    wallet.py      # SIWE, allowances
    risk.py        # max order, drawdown, pause
  strategies/
    taker.py       # current buy/sell loop
    grid.py        # vault + GTC limits
    dca.py         # scheduled buys
  bot.py           # CLI entry
```

**Goal:** plug/unplug strategies without touching execution core.

---

## Phase 2 — Trading features

| Feature | DreamDEX capability | Why |
|---------|---------------------|-----|
| WebSocket order book | `wss://api.dreamdex.io/v0/ws/public` | Less RPC polling, faster reactions |
| Grid / maker | Vault + GTC limits ([Vault.md](../DreamDexdocs/Vault.md)) | Resting liquidity, spread capture |
| Stop / take-profit | SpotStopOrderRegistry ([Stop Orders.md](../DreamDexdocs/Stop%20Orders.md)) | Risk management |
| CCXT layer | [CCXT fork](../DreamDexdocs/CCXT.md) | Standard API for bots |
| PnL dashboard | Balances + metrics | User-facing status |

---

## Phase 3 — Telegram control plane (MVP product)

Users manage bots via Telegram; execution stays on server/VPS.

| Command | Action |
|---------|--------|
| `/status` | Balances, open orders, last tx |
| `/start taker` \| `/start grid` | Start strategy |
| `/stop` | Graceful shutdown |
| `/config` | Market, caps, slippage (with confirmation) |
| `/pnl` | Mark-to-market USDso + base asset |

**Stack (suggested):** `aiogram` or `python-telegram-bot` + asyncio strategy tasks + SQLite for chat_id ↔ config.

```
Telegram user → Telegram bot → Control API → StrategyEngine → DreamDEX REST/WS/chain
```

---

## Phase 4 — Security (before multi-user beta)

| Level | Model | Use when |
|-------|-------|----------|
| A | User runs bot on **own VPS**; Telegram sends remote commands via API key | MVP |
| B | Encrypted keys per user on server (KMS / sealed env) | Closed beta |
| C | No keys on server; WalletConnect / session signing | Public product |

**Never** ask users to paste private keys into Telegram chat.

Extend [SECURITY.md](../SECURITY.md) before Phase 3 goes multi-user.

---

## Phase 5 — Product (optional)

- Web dashboard (read-only at first)
- Multiple strategies per user
- Alerts (fill, drawdown, RPC errors)
- Open-source examples for DreamDEX builder program
- Builder-code / routing integration

---

## Priority order

| Order | Work |
|-------|------|
| 1 | `core/` + `strategies/taker.py` refactor |
| 2 | WebSocket book + CLI status |
| 3 | Telegram: status + start/stop |
| 4 | Grid + vault strategy |
| 5 | Multi-user + key security |

---

## Branch / deployment workflow

1. **`main`** — stable releases; tag before VPS upgrades.
2. **`develop`** — refactors and new strategies.
3. **VPS migration:** snapshot `bot/config.yml` and `.env`; test on staging path or second directory; run preflight; switch systemd when stable.

---

## Related docs

- [DEPLOY.md](DEPLOY.md) — VPS and systemd
- [INTEGRATION.md](INTEGRATION.md) — mainnet integration notes
- [SECURITY.md](../SECURITY.md) — secrets and deployment
- [bot/README.md](../bot/README.md) — configuration
