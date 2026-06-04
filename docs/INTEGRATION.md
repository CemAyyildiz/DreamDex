# DreamDEX Trade Bot — Mainnet Integration Notes

Technical notes from building and running the wallet-funded taker bot on Somnia mainnet (`5031`). For protocol reference, see [DreamDexdocs/](../DreamDexdocs/) and [docs.dreamdex.io](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41).

---

## Integration path

| Step | Endpoint / action | Notes |
|------|-------------------|--------|
| Markets | `GET /v0/markets` | Dynamic pool discovery — no hardcoded addresses required |
| Auth | `GET /v0/auth/nonce` → `POST /v0/auth/login` | SIWE JWT; use `Chain ID: 5031` |
| Approve | `POST .../vault/approve` | Prefer API-prepared approve for USDso |
| Trade | `POST .../orders` → sign → broadcast | Wallet funding + IOC/FOK for takers |
| Simulate | `placeTakerOrderWithoutVault` via `eth_call` | Run before every broadcast |

Base URL: `https://api.dreamdex.io`

---

## Code snippets

### Order types (wallet taker)

```python
# bot/executor.py
ORDER_FOK = 1
ORDER_IOC = 2

def _order_type_for_api(self) -> str:
    if self._order_type_on_chain() == ORDER_FOK:
        return "fillOrKill"
    return "immediateOrCancel"
```

### SIWE authentication

```python
# bot/executor.py — _get_api_token()
nonce = self._api_request("GET", "/v0/auth/nonce", auth=False)["nonce"]
# Build SIWE message with chain_id 5031 → POST /v0/auth/login
```

### Prepare order

```python
# bot/executor.py — _prepare_order()
body = {
    "type": "limit",
    "side": "buy" if is_bid else "sell",
    "price": price,
    "amount": amount,
    "walletAddress": self.address,
    "fundingSource": "wallet",
    "orderType": self._order_type_for_api(),
}
return self._api_request("POST", f"/v0/markets/{self.market.symbol}/orders", body=body, auth=True)
```

### Gas estimation (required)

API `gasLimit` in prepare responses is often too low. Simulation can pass while mined txs revert.

```python
# bot/executor.py — _apply_gas_estimate()
estimated = int(self.web3.eth.estimate_gas(estimate_fields))
tx["gas"] = max(int(tx.get("gas", 0)), int(estimated * 1.2))
# fallback_gas in config (default 2_000_000)
```

On `SOMI:USDso`, we observed ~1.5M gas per taker fill after headroom.

### Token approval

Hand-rolled ERC20 `approve()` on USDso reverted in our tests. API path worked reliably:

```python
# bot/executor.py — _approve_via_api()
prepared = self._api_request(
    "POST",
    f"/v0/markets/{self.market.symbol}/vault/approve",
    body={"walletAddress": self.address, "currency": currency, "amount": amount_human},
)
return self._broadcast_prepared_tx(prepared)
```

### Sell sizing (native base)

When base is native SOMI, reserve gas before sizing sells:

```python
# bot/executor.py — _align_quantity_down()
aligned = (quantity_raw // lot) * lot
if aligned < self.market.min_quantity:
    return 0
return aligned
```

---

## Documentation feedback

| Pri | Area | Observation | Suggestion |
|-----|------|-------------|------------|
| P0 | Quick Start / Fees | Simulation OK; mined tx reverted until ~1.5M gas. Examples show low `gasLimit`. | Publish realistic gas ranges; troubleshooting for `estimate_gas` + headroom |
| P1 | Quick Start vs Spot Overview | Vault `deposit()` prominent; wallet-taker path buried | Callout: wallet funding + IOC for automated takers |
| P1 | Market metadata | `minQuantity` easy to miss for small wallets | Highlight min size in market list |
| P2 | Order Types / Errors | `InvalidOrderType` on vault-only types for wallet takers | Link from Quick Start troubleshooting |
| P2 | WebSocket | Documented but we used on-chain book reads | Note when to use WS vs pool reads |

---

## HTTP API feedback

| Pri | Area | Observation | Suggestion |
|-----|------|-------------|------------|
| P0 | Prepare-order `gasLimit` | Often too low vs real taker gas | Conservative default or document client-side override |
| P0 | `vault/approve` (USDso) | API-prepared approve reliable | Doc note to prefer API path for USDso |
| P1 | Polling / RPC | Occasional `ConnectionError` under fast loops | Backoff guidance, backup RPC |
| P2 | Auth JWT | Cache until near expiry works | Document token lifetime for long-running bots |

**Endpoints used successfully:** `GET /v0/markets`, auth nonce/login, orderbook, `POST .../orders`, `POST .../vault/approve`.

---

## On-chain & RPC feedback

| Pri | Topic | Observation | Suggestion |
|-----|-------|-------------|------------|
| P0 | Simulation vs execution | Mismatch was gas-only, not order logic | Same as gas notes above |
| P1 | Sell sizing | Must align quantity down when base is native | Document gas reserve + min qty |
| P1 | Somnia RPC | Intermittent errors on public endpoint | Fallback RPC list |
| P2 | Vault / maker | Not used in current bot | Decision table for vault vs wallet takers |

RPC: `https://api.infra.mainnet.somnia.network/`

---

## What worked well

- **Quick Start** — correct spine for mainnet integration
- **Zero trading fees** — gas (SOMI) is the main recurring cost
- **Prepare-order + SIWE** — wallet custody preserved
- **`GET /v0/markets`** — no hardcoded pools
- **API stability** — REST prepare-order flow usable under continuous automated load

---

## Related

- [bot/README.md](../bot/README.md) — configuration
- [DEPLOY.md](DEPLOY.md) — VPS / systemd
- [ROADMAP.md](ROADMAP.md) — product plan
