# Product Roadmap — DreamDEX Trading Bot

This document describes **post-competition** development. Do **not** implement these phases while the alpha stress test is running on the VM unless you accept downtime and config drift.

## Current state (competition)

| Component | Role |
|-----------|------|
| [bot/executor.py](../bot/executor.py) | Single-purpose volume taker (IOC, buy/sell alternation) |
| [bot/config.yml](../bot/config.yml) | Local only (gitignored) — VM has its own copy |
| [run_bg.sh](../run_bg.sh) | Production runner on VM |

**VM rule during competition:** keep the running bot stable. Updates = `git pull` + restart only for critical fixes. No refactors on the same branch the VM uses without a maintenance window.

---

## Vision (after competition)

**Telegram-controlled, strategy-selectable algo trading on DreamDEX** — users start/stop grid, DCA, or volume modes; the repo provides the execution engine and control plane.

Aligns with DreamDEX positioning: agents-first, CCXT, WebSocket, third-party apps on the CLOB ([DreamDexdocs/Why dreamDEX.md](../DreamDexdocs/Why%20dreamDEX.md)).

---

## Phase 0 — Competition (now)

- [ ] Keep VM bot running (`SOMI:USDso`, volume mode)
- [ ] Submit [docs/FEEDBACK.md](FEEDBACK.md)
- [ ] Do **not** merge refactors into `main` until competition ends or VM is explicitly updated

---

## Phase 1 — Modular architecture (2–3 days, post-competition)

Split monolithic `LiveDreamDexBot` into layers:

```
bot/
  core/
    market.py      # discovery, book prices
    orders.py      # prepare, sign, broadcast, gas
    wallet.py      # SIWE, allowances
    risk.py        # max order, drawdown, pause
  strategies/
    volume.py      # current competition loop
    grid.py        # future: vault + GTC limits
    dca.py         # future: scheduled buys
  bot.py           # CLI entry
```

**Goal:** plug/unplug strategies without touching execution core. Required before Telegram or new strategies.

---

## Phase 2 — Real trading features (not volume-only)

| Feature | DreamDEX capability | Why |
|---------|---------------------|-----|
| WebSocket order book | `wss://api.dreamdex.io/v0/ws/public` | Less RPC polling, faster reactions |
| Grid / maker | Vault + GTC limits ([Vault.md](../DreamDexdocs/Vault.md)) | Resting liquidity, lower erosion than taker churn |
| Stop / take-profit | SpotStopOrderRegistry ([Stop Orders.md](../DreamDexdocs/Stop%20Orders.md)) | Risk management |
| CCXT layer | [CCXT fork](../DreamDexdocs/CCXT.md) | Standard API for bots and docs |
| PnL dashboard | Balances + metrics | User-facing value beyond volume |

---

## Phase 3 — Telegram control plane (MVP product)

Users manage bots via Telegram; execution stays on server/VPS.

**MVP commands:**

| Command | Action |
|---------|--------|
| `/status` | Balances, open orders, last tx, volume |
| `/start volume` \| `/start grid` | Start strategy |
| `/stop` | Graceful shutdown |
| `/config` | Market, caps, slippage (with confirmation) |
| `/pnl` | Mark-to-market USDso + SOMI |

**Stack (suggested):** `aiogram` or `python-telegram-bot` + asyncio strategy tasks + SQLite for chat_id ↔ config.

**Architecture:**

```
Telegram user → Telegram bot → Control API → StrategyEngine → DreamDEX REST/WS/chain
```

---

## Phase 4 — Security (before any multi-user beta)

| Level | Model | Use when |
|-------|-------|----------|
| A | User runs bot on **own VPS**; Telegram sends remote commands via API key | MVP, trusted users |
| B | Encrypted keys per user on server (KMS / sealed env) | Closed beta |
| C | No keys on server; WalletConnect / session signing | Public product |

**Never** ask users to paste private keys into Telegram chat.

Extend [SECURITY.md](../SECURITY.md) before Phase 3 goes multi-user.

---

## Phase 5 — Product (6–12 months, optional)

- Web dashboard (read-only at first)
- Multiple strategies per user
- Alerts (fill, drawdown, RPC errors)
- Open-source examples for DreamDEX docs / builder program
- Possible builder-code / routing integration (DreamDEX roadmap)

---

## Priority order

| Order | Work | When |
|-------|------|------|
| 0 | VM volume bot + feedback | **During competition** |
| 1 | `core/` + `strategies/volume.py` refactor | After competition |
| 2 | WebSocket book + CLI `/status` | Week 1 post-competition |
| 3 | Telegram: status + start/stop | Week 2 post-competition |
| 4 | Grid + vault strategy | Week 3+ |
| 5 | Multi-user + key security | Beta |

---

## Branch / VM workflow (avoid “everything breaks”)

1. **During competition:** fix-only commits on `main`; VM pulls only when needed.
2. **After competition:** create `develop` (or `v2`) for refactor + Telegram.
3. VM migration:
   - Snapshot current `bot/config.yml` and `.env` on VM
   - Pull new branch on a **second directory** or staging VM
   - Run preflight; switch systemd/`run_bg.sh` when stable
4. Never refactor `executor.py` in place on the live VM without backup config and a rollback plan.

---

## Competition submission hook

Add to feedback / demo narrative:

1. **Today:** Volume taker bot — mapped API, gas, allowance friction.
2. **Next:** Modular engine + WebSocket.
3. **Product:** Telegram control for user-managed DreamDEX bots.
4. **DreamDEX fit:** CCXT-compatible patterns, vault maker path, open bot repo.

---

## Related docs

- [DEPLOY.md](DEPLOY.md) — VM and systemd
- [FEEDBACK.md](FEEDBACK.md) — competition report
- [SECURITY.md](../SECURITY.md) — secrets and deployment
- [bot/README.md](../bot/README.md) — current bot config
