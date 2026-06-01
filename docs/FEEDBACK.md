# DreamDEX Alpha Trading Competition — Feedback Report

**Participant:** Cem Ayyıldız (Lykan)  
**Leaderboard:** Trader-10  
**Wallet (competition):** `0x7273B462333a02C4933C009BF2F589a1467B89B4`  
**Strategy:** Automated volume bot on Somnia mainnet — wallet-funded IOC taker orders via REST and `placeTakerOrderWithoutVault`  
**Repository:** DreamDex bot (`bot/executor.py`, `bot/bot.py`) — share your public GitHub URL when submitting  
**Documentation reviewed:** [dreamDEX docs](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41) (Quick Start, Order Types, Trading/Vault API, Developers overview)

---

## 1. Competition results & stress test

Following the team’s request (DM + group announcement), this document records **documentation feedback**, **HTTP API feedback**, and **representative code snippets** from our live integration.

**What we ran**

- Mainnet volume bot on a Linux VPS, 24/7, alternating buy/sell on **`SOMI:USDso`**
- Wallet-funded **IOC** taker orders (`fundingSource: "wallet"`, `placeTakerOrderWithoutVault`)
- Increased loop frequency after the stack was stable, leaning on **Somnia’s throughput** for a high-transaction stress test

**Outcome (approximate)**

- **10,000+ on-chain transactions in under 24 hours** while climbing the leaderboard as **Trader-10**
- ~$50 competition starting capital; primary goal was **volume / API stress**, not P&L
- After client-side fixes (gas, allowance, sell sizing), fills were consistent and the API remained usable under load

**Integration path (mainnet CLOB only)**

We used the [Quick Start](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/quick-start) wallet-taker flow. We did **not** use [Simple Swap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/simple-swap) / SpotRouter (separate surface; testnet preview in docs). Early confusion was from prototyping swap-style logic before committing to the documented CLOB path.

| Step | Endpoint / action | Result |
|------|-------------------|--------|
| Markets | `GET /v0/markets` | OK |
| Auth | `GET /v0/auth/nonce` → `POST /v0/auth/login` (SIWE, chain `5031`) | OK |
| Approve | `POST .../vault/approve` | OK (see API section) |
| Trade | `POST .../orders` → sign → broadcast | OK after gas + allowance handling |
| Deploy | VPS + `run_bg.sh` / systemd | Stable |

**Markets tested:** `USDC.e:USDso` (initial), then **`SOMI:USDso`** (primary).

---

## 2. Code & repository

### How to run

```bash
git clone <your-repo-url> && cd DreamDex
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp bot/config.yml.example bot/config.yml
# .env: PRIVATE_KEY=0x...  (competition wallet only — never commit)
python3 bot/preflight.py --config bot/config.yml
./run_bg.sh
```

See also [docs/DEPLOY.md](DEPLOY.md) for 24/7 VPS / systemd.

**Local metrics:** `metrics.json` — `volume_in_raw`, `volume_out_raw` (18-decimal USDso notional, cumulative).

### Code snippets (integration highlights)

The snippets below map directly to the **documentation** and **API** sections that follow.

#### 2.1 Order types — IOC for wallet takers (matches Quick Start)

On-chain enum and API field aligned with docs (`immediateOrCancel` / IOC `2`):

```python
# bot/executor.py
ORDER_FOK = 1
ORDER_IOC = 2

def _order_type_on_chain(self) -> int:
    if self.volume_mode:
        return ORDER_IOC
    if self.bulk_mode and self.use_fok_for_bulk:
        return ORDER_FOK
    return ORDER_IOC

def _order_type_for_api(self) -> str:
    if self._order_type_on_chain() == ORDER_FOK:
        return "fillOrKill"
    return "immediateOrCancel"
```

#### 2.2 SIWE authentication (mainnet `5031`)

```python
# bot/executor.py — _get_api_token()
nonce = self._api_request("GET", "/v0/auth/nonce", auth=False)["nonce"]
message = (
    f"api.dreamdex.io wants you to sign in with your Ethereum account:\n{self.address}\n\n"
    f"Sign in to dreamDEX\n\n"
    f"URI: https://api.dreamdex.io\n"
    f"Version: 1\n"
    f"Chain ID: {int(self.cfg.get('chain_id', 5031))}\n"
    f"Nonce: {nonce}\n"
    f"Issued At: {issued_at}"
)
# POST /v0/auth/login with message + signature → Bearer token
```

#### 2.3 Prepare order — HTTP API body

Equivalent to Quick Start `POST /v0/markets/{symbol}/orders`:

```python
# bot/executor.py — _prepare_order()
body = {
    "type": "limit",
    "side": "buy" if is_bid else "sell",
    "price": price,
    "amount": amount,
    "walletAddress": self.address,
    "fundingSource": "wallet",
    "orderType": self._order_type_for_api(),  # "immediateOrCancel"
}
return self._api_request("POST", f"/v0/markets/{self.market.symbol}/orders", body=body, auth=True)
```

#### 2.4 Gas estimation before broadcast

Simulation passed with low gas; mined txs reverted until we added headroom (~1.5M on `SOMI:USDso`):

```python
# bot/executor.py — _apply_gas_estimate()
estimated = int(self.web3.eth.estimate_gas(estimate_fields))
tx["gas"] = max(int(tx.get("gas", 0)), int(estimated * 1.2))
# fallback: fallback_gas from config (default 2_000_000)
```

#### 2.5 Token approval — API `vault/approve` fallback

Documented path; used when direct ERC-20 `approve` on USDso reverted:

```python
# bot/executor.py — _approve_via_api()
prepared = self._api_request(
    "POST",
    f"/v0/markets/{self.market.symbol}/vault/approve",
    body={
        "walletAddress": self.address,
        "currency": self._currency_code_for_token(token),
        "amount": amount_human,
    },
)
return self._broadcast_prepared_tx(prepared)
```

#### 2.6 Submit flow — approval hint + broadcast

```python
# bot/executor.py — _submit_order()
prepared_order = self._prepare_order(is_bid, quantity_raw, price_raw)
if prepared_order.get("approval"):
    self._prepare_approval(prepared_order["approval"])
return self._broadcast_prepared_tx(prepared_order)
```

---

## 3. Documentation feedback

Cross-checked against [docs.dreamdex.io](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41).

### What worked well

- **[Quick Start](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/quick-start)** — mainnet `5031`, three paths (CLI / HTTP / `cast`), wallet vs vault funding, IOC warning for `placeTakerOrderWithoutVault`, simulate-then-send workflow.
- **[Order Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/order-types)** — IOC/FOK for wallet; GTC/PostOnly for vault.
- **Native SOMI** callout in Quick Start (`msg.value` on sell).
- **`vault/approve`** in Quick Start step 3 and [Vault API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/vault).
- **WebSocket** documented (`wss://api.dreamdex.io/v0/ws/public`) — we used REST polling; streaming is there for lower latency.
- **[Introduction](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41)** — agents-first positioning matches our Python bot approach.

### Suggestions for the next bot builder

| # | Area | Observation | Suggestion |
|---|------|-------------|------------|
| 1 | Trading API / Quick Start | `eth_call` OK; mined tx reverted until ~1.5M gas on `SOMI:USDso`. API examples show `gasLimit: "250000"`; [Fees](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/fees) gas table is `[TODO]`. | Publish realistic gas ranges for wallet taker fills; troubleshooting: *if simulation passes but tx reverts, `estimate_gas` + headroom*. |
| 2 | Quick Start / Spot Overview | Spot Overview leads with vault `deposit()`; wallet-taker shortcut is in Quick Start. | One-line callout at top of Quick Start: *volume / competition bots → wallet funding (Option A) + IOC*. |
| 3 | Market metadata | `minQuantity: 1` SOMI tight for ~$50 wallets. | Highlight min size in market list for small allocations. |
| 4 | Order Types / Errors | Early client bug used PostOnly (`3`) → `InvalidOrderType`. Docs already warn IOC/FOK for wallet. | Optional: link `InvalidOrderType` from Quick Start troubleshooting. |

We did **not** treat missing testnet/Simple Swap docs as a mainnet gap — that path is documented separately for testnet preview.

---

## 4. HTTP API feedback

Base URL: `https://api.dreamdex.io` (mainnet).

### What worked well

| Endpoint | Use | Result |
|----------|-----|--------|
| `GET /v0/markets` | Pool + token discovery | OK |
| `GET /v0/auth/nonce` + `POST /v0/auth/login` | SIWE JWT | OK with `Chain ID: 5031` |
| `GET /v0/markets/{symbol}/orderbook` (and related market data) | Pricing / book | OK |
| `POST /v0/markets/{symbol}/orders` | Unsigned prepare tx | OK |
| `POST /v0/markets/{symbol}/vault/approve` | Approve tx generation | OK |

**Prepare-order `approval` field** — when allowance is insufficient, the inline approval object is well described; we used it together with startup max-approve.

**OpenAPI / Authentication reference** — lists mainnet vs staging servers clearly.

### Suggestions

| Area | Our experience | Suggestion |
|------|----------------|------------|
| `vault/approve` (USDso) | API-prepared approve reliable; hand-rolled `approve()` on USDso reverted (empty data). | Short note: *prefer API-prepared approve for USDso* if token-specific. |
| Prepare-order `gasLimit` | Optional field often low vs real taker gas. | Return conservative default or document mandatory `estimate_gas`. |
| Rate limits / RPC | Occasional `ConnectionError` under fast polling; bot retried. | Optional bot guidance: polling intervals, backup RPC. |

---

## 5. On-chain & RPC feedback

| Topic | Experience | Suggestion |
|-------|------------|------------|
| Simulation vs execution | Mismatch only due to gas, not order logic | Same as doc §3.1 — `estimate_gas` + headroom |
| `placeTakerOrderWithoutVault` | Stable after IOC + gas fixes | — |
| Somnia RPC | `https://api.infra.mainnet.somnia.network/` — intermittent errors, no long outage | See API rate-limit note |
| Sell sizing (`SOMI:USDso`) | Align quantity **down** to balance; skip if below min after gas reserve | Market min-quantity visibility (doc §3.3) |

---

## 6. What worked well (summary)

- **Quick Start** was the right spine for mainnet bot integration.
- **Zero trading fees** — volume strategies viable; **SOMI gas** is the main recurring cost.
- **Prepare-order + SIWE** — wallet custody preserved; API composes unsigned txs.
- **`GET /v0/markets`** — no hardcoded pools required.
- **Stress test** — 10k+ txs in &lt;24h on VPS without sustained API failure after client fixes; good signal for the competition’s goals.

---

## 7. Suggested attachments (submission package)

When sharing with the DreamDEX team (Google Doc / form / Telegram), include:

1. **This document** (or export to PDF / Google Doc)  
2. **Public repository link** (code — no `.env` or `bot/config.yml` with keys)  
3. **Leaderboard screenshot** — Trader-10, volume / tx count  
4. **Explorer link** — one successful `placeTakerOrderWithoutVault` transaction  
5. **Log excerpt** — lines showing successful fills (`order ok` or similar)  
6. **Optional** — `metrics.json` snapshot  

---

*Prepared for the DreamDEX alpha trading competition — documentation, API, and code feedback from a live mainnet volume bot (Trader-10), as requested by the team. Cross-checked against [docs.dreamdex.io](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41).*
