# Quick Start

This guide walks through placing your first order on dreamDEX, describing how
you can interact with both the HTTP API and on-chain smart contracts to trade
tokens.

The guide shows three paths: the [dreamDEX CLI](https://github.com/somnia-chain/somnia-dex-cli/) for the fastest experience, the HTTP API with `curl` for full control, and [Foundry's cast](https://book.getfoundry.sh/) for direct contract interaction.

## Prerequisites

Before you can perform any trades, you need:

- An EVM wallet connected to Somnia mainnet (chain ID `5031`).
- Tokens to trade (the base token of the market you want to trade on).
- Your private key is assumed to be in your environment as `$PRIVATE_KEY`.
- An HTTP client that can call REST endpoints; we will assume `curl` is on your path.
- The [dreamDEX CLI](https://github.com/somnia-chain/somnia-dex-cli/) for the simplest workflow (`go install github.com/somnia-chain/somnia-dex-cli/cmd/dreamdex@latest`), and/or [Foundry](https://book.getfoundry.sh/) (`cast`) for direct contract interaction.

## 1. Discover Markets

Fetch the available trading pairs via the [Market Data](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/market-data) endpoint. This step is required regardless of which path you use - it is the
simplest way to obtain the contract and token addresses for a market.

```bash
curl https://api.dreamdex.io/v0/markets
```

```json
{
  "markets": [
    {
      "symbol": "WETH:USDso",
      "contract": "0xa936da11B57b50A344e1293AAaE5232885ea2bDE",
      "base":     "0x936Ab8C674bcb567CD5dEB85D8A216494704E9D8",
      "quote":    "0x00000022dA000002656c64D9eA6011ea952D008A",
      "baseDecimals": 18,
      "quoteDecimals": 18,
      "tickSize": "0.01",
      "lotSize": "0.0001",
      "minQuantity": "0.001"
    }
  ]
}
```

Note the `contract` (Pool address), `base` and `quote` (token addresses), decimal counts, and the `tickSize`, `lotSize`, and `minQuantity` constraints — your order parameters must respect these. See [Spot Contract Specifications](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/contract-specifications) for details on each field.

If you are using the dreamDEX CLI, no manual setup is needed - it fetches market
metadata automatically:

```bash
dreamdex markets
```

If you are using `cast` directly, save these values:

```bash
POOL="0xa936da11B57b50A344e1293AAaE5232885ea2bDE"         # SpotPool (WETH:USDso, Somnia mainnet)
BASE_TOKEN="0x936Ab8C674bcb567CD5dEB85D8A216494704E9D8"   # WETH
QUOTE_TOKEN="0x00000022dA000002656c64D9eA6011ea952D008A"  # USDso
BASE_DECIMALS=18
QUOTE_DECIMALS=18
RPC="https://api.infra.mainnet.somnia.network"
```

Native-token markets (SOMI/USDso). The SOMI/USDso pool uses SOMI as the chain's native token. The vault deposit step uses `depositNative()` with `msg.value` instead of `approve` + `deposit(token, amount)`, and `placeTakerOrderWithoutVault` pulls input from `msg.value` rather than an ERC-20 allowance. The rest of this guide assumes an ERC-20 base
(e.g. WETH); swap in the SOMI/USDso pool address and use the native-deposit
variant when trading SOMI.

## 2. Authenticate (HTTP API only)

Skip this step if you are using the dreamDEX CLI or `cast` - both sign transactions directly with your private key. The CLI handles SIWE
authentication automatically; run `dreamdex login` to import your key on first use, or set `DREAMDEX_PRIVATE_KEY` in your environment for headless/CI workflows.

If you want to use the HTTP API to construct transactions on your behalf, you
will need to authenticate first, to ensure the returned transactions reference
your wallet correctly. This process does not cede any control to your wallet; you
remain in full control.

dreamDEX supports [Sign-In with Ethereum (ERC-4361)](https://eips.ethereum.org/EIPS/eip-4361). First request a nonce, then sign a SIWE message with your wallet and submit it
to receive a JWT bearer token. See [Authentication](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/authentication) for full details.

Request a nonce:

```bash
curl https://api.dreamdex.io/v0/auth/nonce
```

```json
{ "nonce": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" }
```

Sign in:

Construct an ERC-4361 message containing the nonce, sign it with your wallet,
and POST both to the login endpoint:

```bash
curl -X POST https://api.dreamdex.io/v0/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "dreamdex.somnia.host wants you to sign in with your Ethereum account:\n0xYourAddress\n\nSign in to dreamDEX\n\nURI: https://dreamdex.somnia.host\nVersion: 1\nChain ID: 5031\nNonce: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\nIssued At: 2026-01-01T00:00:00.000Z",
    "signature": "0x..."
  }'
```

```json
{
  "token": "eyJhbGciOiJFUzI1NiIs...",
  "expiresAt": 1765537769841
}
```

Include this token in all subsequent HTTP API requests to private endpoints:

```bash
TOKEN="eyJhbGciOiJFUzI1NiIs..."
```

## 3. Choose a Funding Source

dreamDEX supports two ways to fund orders:

### Option A: Wallet Funding (default)

Tokens are pulled directly from your wallet at execution time. This is the
simplest path - no deposit step needed - but if performing many trades, may cost more
in gas fees overall.

Requirements:

- Order type must be [Immediate-or-Cancel (IOC)](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/order-types#immediate-or-cancel-ioc) or [Fill-or-Kill (FOK)](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/order-types#fill-or-kill-fok)
- You must grant the SpotPool contract an ERC-20 allowance to spend your tokens before submitting the order - without this the on-chain transaction will revert.

Approve the SpotPool contract to spend your tokens:

Using the HTTP API:

```bash
curl -X POST https://api.dreamdex.io/v0/markets/WETH:USDso/vault/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "walletAddress": "0xYourAddress",
    "currency": "WETH",
    "amount": "1"
  }'
```

This returns an unsigned `approve(spender, amount)` transaction targeting the token contract, signalling that you grant permission for the contract to spend this token on
your behalf. You need to sign and broadcast it.

To do this using `cast`:

```bash
# Approve the pool to spend 1 WETH (18 decimals)
cast send $BASE_TOKEN \
  "approve(address,uint256)" \
  $POOL $(cast to-wei 1) \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

If you are using the dreamDEX CLI, approval is handled automatically when
placing an order (step 4) - skip ahead.

Once confirmed, the SpotPool contract can transfer up to that amount from your
wallet when your order executes. Then proceed to step 4.

### Option B: Vault Funding

Pre-deposit tokens into the market's on-chain [vault](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/vault). This supports all [order types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/order-types), including resting limit orders (GTC, PostOnly).

Step 1 - Approve (same as Option A above).

Step 2 - Deposit:

Using the HTTP API:

```bash
curl -X POST https://api.dreamdex.io/v0/markets/WETH:USDso/vault/deposit \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "walletAddress": "0xYourAddress",
    "currency": "WETH",
    "amount": "1"
  }'
```

Sign and broadcast the returned transaction, e.g. using `cast`:

```bash
# Deposit 1 WETH into the vault
cast send $POOL \
  "deposit(address,uint256)" \
  $BASE_TOKEN $(cast to-wei 1) \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

Using the dreamDEX CLI:

```bash
dreamdex vault approve WETH:USDso --currency WETH --amount 1
dreamdex vault deposit WETH:USDso --currency WETH --amount 1
```

Then proceed to step 4 with vault funding.

## 4. Place an Order

### Option A: Using the HTTP API

Call the [prepare order](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading) endpoint to get an unsigned transaction:

```bash
curl -X POST https://api.dreamdex.io/v0/markets/WETH:USDso/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "limit",
    "side": "buy",
    "price": "2500.00",
    "amount": "1",
    "walletAddress": "0xYourAddress",
    "fundingSource": "wallet",
    "orderType": "immediateOrCancel"
  }'
```

The server returns an unsigned EVM transaction:

```json
{
  "to": "0xPoolContract",
  "data": "0xabcdef...",
  "value": "0",
  "chainId": "5031"
}
```

Sign and broadcast it to the Somnia network, e.g. using `cast`:

```bash
cast send \
  --to "0xPoolContract" \
  --data "0xabcdef..." \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

### Option B: Using the dreamDEX CLI

The CLI handles transaction construction, signing, and broadcasting in a single
command:

Wallet funding (default):

```bash
dreamdex order place WETH:USDso --side buy --type limit --amount 1 --price 2500
```

Vault funding:

```bash
dreamdex order place WETH:USDso --side buy --type limit --amount 1 --price 2500 \
  --funding-source vault --order-type postOnly
```

The CLI auto-detects whether token approval is needed and submits an approval
transaction first if required. Market orders are also supported:

```bash
dreamdex order place WETH:USDso --side buy --amount 1 --slippage 0.5
```

### Option C: Using `cast`

When calling the [contract](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions) directly, prices and quantities must be in raw on-chain units - the human-readable value multiplied by `10^decimals`:

```bash
# Price: 2500.00 USDso (18 decimals) → 2500 × 10^18
export PRICE=$(cast to-wei 2500)

# Quantity: 1 WETH (18 decimals) → 1 × 10^18
export QUANTITY=$(cast to-wei 1)

# Expiration: 24 hours from now, in nanoseconds
export EXPIRE_NS=$(( ($(date +%s) + 86400) * 1000000000 ))
```

The contract function you call depends on your funding source:

Wallet funding - use `placeTakerOrderWithoutVault`:

```bash
cast send $POOL \
  "placeTakerOrderWithoutVault(bool,uint64,uint256,uint256,uint64,uint8,uint8,address,uint96)" \
  true 0 $PRICE $QUANTITY $EXPIRE_NS 2 0 0x0000000000000000000000000000000000000000 0 \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

Vault funding - use `placeOrder`:

```bash
cast send $POOL \
  "placeOrder(bool,uint64,uint256,uint256,uint64,uint8,uint8,address,uint96)" \
  true 0 $PRICE $QUANTITY $EXPIRE_NS 0 0 0x0000000000000000000000000000000000000000 0 \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

The parameters are:

ParameterDescription
|  |
|  |

Wallet-funded orders (`placeTakerOrderWithoutVault`) must use IOC (`2`) or FOK (`1`) as the order type. GTC and PostOnly require vault funding.

Builder codes ship enabled in v1.1. Passing a non-zero `builder` reverts with `BuilderCodesNotSupported` until the admin raises `maxBuilderFeeBpsTimes1k`. For v1.0, leave both trailing arguments at the zero values shown above.

### Recommended workflow

1. Simulate first. Call the transaction via `eth_call` (or `cast call`). The place-order functions return `(bool success, uint128 orderId)`. If `success` is `false`, check your transaction for potential issues.
2. Sign and broadcast. If the simulation succeeds, sign the transaction and send it to the Somnia
network.
3. Verify after confirmation. Check the transaction receipt for an `OrderPlaced` event. An empty logs array means the order was silently rejected.

## 5. Track Your Order

### Option A: Poll via REST

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.dreamdex.io/v0/markets/WETH:USDso/orders/<orderId>
```

### Option B: Using the dreamDEX CLI

```bash
# List open orders
dreamdex order list WETH:USDso --status open

# Get a specific order
dreamdex order get WETH:USDso <orderId>

# Stream live updates
dreamdex watch order <orderId>

# Cancel an order
dreamdex order cancel WETH:USDso <orderId>
```

### Option C: Stream via WebSocket

Connect to the [WebSocket API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/websocket-api/real-time-feed) at `wss://api.dreamdex.io/v0/ws/public` and subscribe to order updates:

```json
{
  "operation": "subscribe",
  "channel": "order",
  "params": { "orderId": "0xYourOrderId" }
}
```

You will receive a snapshot of the current order state followed by real-time
updates as the order fills or is cancelled.

### Option D: Query via `cast`

```bash
# Get order details by ID (OrderId is a uint128 on-chain)
cast call $POOL \
  "getOrder(uint128)" \
  $ORDER_ID \
  --rpc-url $RPC
```

To cancel an order:

```bash
cast send $POOL \
  "cancelOrder(uint128)" \
  $ORDER_ID \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

## Summary

Useful view functions: Call `getPoolParams()` on any SpotPool to discover its token addresses, fee rates, tick size, lot
size, and min quantity. Call `getWithdrawableBalance(address, token)` to check your available balance before withdrawing. Call `getOwnOpenOrders()` to list your active orders.

## Next Steps

- [Order Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/order-types) - Learn about all supported order types and time-in-force options
- [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) - Set up automated stop-loss and take-profit orders
- [Contracts](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts) - Full contract API reference
- [HTTP API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api) - Full REST API reference
- [WebSocket API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/websocket-api) - Real-time market data and order tracking

Previous Introduction
Next Why dreamDEX
Last updated 4 days ago