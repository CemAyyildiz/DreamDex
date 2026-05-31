# DreamDEX Alpha Trading Competition — Feedback Report

**Participant:** Cem Ayyıldız  
**Wallet (competition):** `0x7273B462333a02C4933C009BF2F589a1467B89B4`  
**Strategy:** Automated volume bot on Somnia mainnet (`SOMI:USDso`), wallet-funded IOC taker orders via REST + `placeTakerOrderWithoutVault`  
**Repository / bot:** DreamDex project (`bot/executor.py`, `bot/bot.py`)

---

## Executive summary

Integration is feasible on mainnet, but several documentation gaps and API/chain edge cases caused failed transactions until workarounds were implemented. The most impactful issues were: incorrect on-chain order-type enum usage in sample logic, insufficient gas limits on prepared transactions, and non-obvious USDso approval flow (direct ERC-20 `approve` reverts; API-prepared approve works). After fixes, the bot successfully places fills on `SOMI:USDso`.

---

## Feedback 1 — Documentation

### 1.1 README / getting-started drift

**Area:** Developer onboarding  
**Severity:** High (blocks first successful trade)

**Issue:** Repository README referenced testnet chain `50312`, SpotRouter (`swapExactIn`), and env vars `DREAMDEX_API_KEY` / `WALLET_KEY`. Actual mainnet integration uses chain `5031`, SpotPool `placeTakerOrderWithoutVault`, and wallet `PRIVATE_KEY` with SIWE auth.

**Suggestion:** Align README with [Quick Start](https://docs.dreamdex.io) mainnet flow: pool taker orders, `PRIVATE_KEY`, chain 5031, link to `vault/approve` for wallet funding.

### 1.2 Order type enum values

**Area:** Order Types / Quick Start  
**Severity:** Critical

**Issue:** Wallet taker orders must use IOC (`2`) or FOK (`1`). Easy to confuse with PostOnly (`3`), which reverts for wallet-funded takers (`InvalidOrderType` / `0x688c176f`).

**Suggestion:** Add a single table in Quick Start:

| Enum | Name | Wallet taker? |
|------|------|----------------|
| 0 | NormalOrder | Vault only |
| 1 | FillOrKill | Yes |
| 2 | ImmediateOrCancel | Yes |
| 3 | PostOnly | Vault only |

### 1.3 Gas for prepared order transactions

**Area:** Trading / prepare order response  
**Severity:** High

**Issue:** Docs recommend simulating before broadcast, but do not state that prepared orders often require **~1.5M gas** on `SOMI:USDso`. Using default 300k causes on-chain `status=0` while `eth_call` still succeeds.

**Suggestion:** Document typical gas ranges per market or always return a safe `gasLimit` in the prepare-order response; note that clients should `estimate_gas` before send.

### 1.4 Native vs ERC-20 funding on SOMI:USDso

**Area:** Quick Start — native markets  
**Severity:** Medium

**Issue:** SOMI sells require `msg.value`; USDso buys require allowance. The split is documented but easy to miss when copying generic WETH examples.

**Suggestion:** Dedicated “SOMI:USDso bot checklist” (approve quote, attach native on sell, min quantity 1 SOMI).

---

## Feedback 2 — HTTP API

### 2.1 Vault approve for USDso

**Area:** `POST /v0/markets/{symbol}/vault/approve`  
**Severity:** High

**Issue:** Direct on-chain `approve()` on USDso (`0x00000022dA…`) from web3 reverted (`execution reverted`, empty data). API-prepared approve transactions worked.

**Suggestion:** State explicitly in Trading docs: “For USDso, use `vault/approve` to generate the approve transaction” with a minimal Python/curl example.

### 2.2 Prepare order + gas

**Area:** `POST /v0/markets/{symbol}/orders`  
**Severity:** Medium

**Issue:** Response includes optional `gasLimit`; when absent or low, clients fail on-chain. Clients should run `estimate_gas` before broadcast.

**Suggestion:** Return conservative `gasLimit` always; document `estimate_gas` as a mandatory client step.

### 2.3 SIWE login

**Area:** `/v0/auth/nonce`, `/v0/auth/login`  
**Severity:** Low

**Issue:** Worked as documented when `Chain ID: 5031` matched config.

---

## Feedback 3 — On-chain / RPC

### 3.1 Simulation vs execution mismatch

**Area:** `placeTakerOrderWithoutVault`  
**Severity:** Medium

**Issue:** `eth_call` returned `success=true` while mined transaction reverted with low gas.

**Suggestion:** Add troubleshooting: “if `status=0` with empty logs, retry with higher gas.”

### 3.2 RPC stability

**Area:** Somnia RPC `https://api.infra.mainnet.somnia.network/`  
**Severity:** Medium

**Issue:** Intermittent `ConnectionError` under frequent polling.

**Suggestion:** Publish recommended rate limits or secondary RPC endpoints for bots.

### 3.3 Minimum quantity on SOMI:USDso

**Area:** Market metadata  
**Severity:** Medium

**Issue:** `minQuantity: 1` SOMI can block small competition allocations (~$50 USDso).

**Suggestion:** Clarify in market list when min size excludes small wallets.

---

## Bot deliverable (snippet summary)

**What we built**

- Python bot: market discovery, SIWE auth, book polling, IOC taker orders, alternating buy/sell for volume.
- Volume mode: `trade_fraction`, gas reserve, API fallback approve, gas estimation before broadcast.
- Scripts: `run_bg.sh`, `run_forever.sh`, `bot/preflight.py`.

**How to run**

```bash
pip install -r requirements.txt
cp bot/config.yml.example bot/config.yml
# .env: PRIVATE_KEY=0x...
python3 bot/preflight.py --config bot/config.yml
./run_bg.sh   # or systemd on VPS — see docs/DEPLOY.md
```

**Metrics:** `metrics.json` — `volume_in_raw` + `volume_out_raw` (18-decimal USDso notional, cumulative).

---

## Suggested attachments for submission

1. Leaderboard row showing volume / tx count  
2. Explorer link to a successful `placeTakerOrderWithoutVault` transaction  
3. Log excerpt with `order ok` lines  
4. `metrics.json` snapshot  

---

## Positive notes

- Zero trading fees make volume strategies viable; gas is the main cost.
- Prepare-order API + SIWE keeps wallet custody clear.
- Market metadata endpoint is enough to bootstrap bots without hardcoding pools.

---

*This report covers documentation, API, and on-chain/RPC feedback for the alpha competition.*
