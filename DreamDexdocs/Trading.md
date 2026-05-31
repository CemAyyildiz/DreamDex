# Trading

These endpoints provide access to trade history, ticker snapshots, and candlestick data for a given market. The Order Management section below covers preparing, querying, and cancelling orders.

Note that the prepare-order endpoint returns an unsigned transaction — the client must sign and broadcast it to the Somnia network. See the [Quick Start](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/quick-start) guide for a full walkthrough.

### List recent trades

GET https://api.dreamdex.io

/v0/markets/{symbol}/trades

Returns the most recent executed trades for a specific market. Each trade includes the price, quantity, side (buy/sell), and timestamp. This data is useful for displaying trade history feeds and analyzing recent market activity. Trades are returned newest-first (reverse chronological order).

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Query parameters

since integer · int64 Optional
Return trades after this unix millisecond timestamp

Example: `1765530000000`

limit integer · min: 1 · max: 1000 Optional
Maximum number of trades to return (default 100, max 1000)

Default: `100`
Example: `100`

Responses

200
Recent trades for a market

application/json

symbol string Required
Market symbol

trades object[] Required
A single executed trade

404
Error response

application/json

500
Error response

application/json

```text
GET /v0/markets/{symbol}/trades HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "symbol": "SOM:USD",
  "trades": [
    {
      "amount": "100",
      "cost": "125",
      "id": "123:456",
      "price": "1.25",
      "side": "buy",
      "symbol": "SOM:USD",
      "timestamp": 1765534169841
    }
  ]
}
```

### Get ticker

GET https://api.dreamdex.io

/v0/markets/{symbol}/tickers

Returns 24-hour OHLCV market statistics for a specific trading pair. Includes open, high, low, close prices and total trade volume. All fields are "0" if no trades occurred in the period.

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Responses

200
List of tickers

application/json

symbols object[] Required
24-hour OHLCV ticker statistics for a market

```text
GET /v0/markets/{symbol}/tickers HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "symbols": [
    {
      "close": "1.30",
      "high": "1.35",
      "low": "1.18",
      "open": "1.20",
      "symbol": "SOM:USD",
      "timestamp": 1765534169841,
      "volume": "125000"
    }
  ]
}
```

## Order Management

### Prepare order

POST https://api.dreamdex.io

/v0/markets/{symbol}/orders

Generates an unsigned EVM transaction for placing a new order on-chain. The response contains the transaction payload (to, data, value, chainId) that must be signed and broadcast by the client's wallet. This non-custodial approach ensures the server never handles private keys. Supports both market orders (immediate execution at best price) and limit orders (execution at specified price or better).

For conditional stop orders, see `POST /v0/markets/{symbol}/stop-orders`.

#### Token approval for wallet funding source

When using `fundingSource: "wallet"`, the SpotPool contract must have sufficient ERC-20 allowance to pull tokens from the caller's wallet. The server checks the caller's current on-chain allowance and only includes an `approval` field in the response when additional approval is needed. If `approval` is absent, the existing allowance already covers the order and the caller can submit the order transaction directly.

When `approval` is present, the caller must submit a `token.approve(spotPoolAddress, amount)` transaction before sending the order transaction. For buy orders, approve the quote token (you spend quote to buy base). For sell orders, approve the base token. Use `POST /v0/markets/{symbol}/vault/approve` to generate the approve transaction. The `approval.amount` covers the order cost plus taker fee overhead from ceiling rounding.

Note: Market buy orders with `fundingSource: "wallet"` are not supported and return a 400 error. The contract must deposit quote tokens upfront, but the fill price is unknown for market buys. Use a limit order with `orderType: "immediateOrCancel"` and a price above the best ask to achieve equivalent immediate-fill behavior.

#### Recommended workflow

1. Simulate before submitting. Call the returned transaction via `eth_call` before sending it. The `placeOrder` function returns `(bool success, uint256 orderId)`. If `success` is `false`, the order will be rejected on-chain -- do not submit the transaction.
2. Sign and broadcast. If the simulation returns `success = true`, sign the transaction and send it.
3. Verify after confirmation. Once the transaction confirms, check the receipt logs for the `OrderPlaced` event. If the logs array is empty, the order was silently rejected.

#### Why an order can be rejected

A `placeOrder` transaction can succeed (receipt `status = 1`) yet not actually place an order. When this happens the call returns `(false, 0)` and emits no events. This occurs when the order passes basic validation (price, quantity, lot size) but is rejected for a runtime reason such as:

- The order expired before execution
- It would match against the sender's own resting order (self-trade)
- A PostOnly order would have filled immediately
- A FillOrKill order could not be completely filled
- An ImmediateOrCancel order found nothing to fill against

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Body

application/json

object Optional
OR object Optional

Responses

200
EVM transaction payload the client MUST sign and send from their wallet

application/json

Unsigned EVM transaction payload for the client to sign and broadcast. For vault/approve on the native token, the API returns JSON `null` instead of this object — see the OrderTransactionOrNull response.

approval object Optional
ERC-20 pre-approval needed for a wallet-funded order. Only present when the caller's current on-chain allowance is insufficient for the order. When present, the client MUST submit `token.approve(spotPoolAddress, amount)` before broadcasting the order transaction. The amount includes the taker fee so the on-chain transferFrom never reverts due to insufficient allowance. When absent, the existing allowance already covers the order.

chainId string Required
EVM chain ID, as a decimal string

Example: `1`

data string Required
Hex-encoded data (0x-prefixed)

Example: `0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678`

Pattern: `^0x[a-fA-F0-9]*$`

gasLimit string Optional
Recommended gas limit, as a decimal string

Example: `250000`

nonce string Optional
A once-only value

Example: `abc123`

to string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`

Pattern: `^0x[a-fA-F0-9]{40}$`

value string Required
Wei value to send, as a decimal string. Non-zero for payable calls such as vault `depositNative()` when depositing the chain's native token; zero for ERC-20 deposits and withdrawals.

Example: `0`

400
Error response

application/json

```text
POST /v0/markets/{symbol}/orders HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Content-Type: application/json
Accept: */*
Content-Length: 61

{
  "amount": "12.34",
  "price": "1.50",
  "side": "buy",
  "type": "limit"
}
```

```json
{
  "approval": {
    "amount": "100.1",
    "token": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "chainId": "1",
  "data": "0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678",
  "gasLimit": "250000",
  "nonce": "abc123",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "value": "0"
}
```

### Get order

GET https://api.dreamdex.io

/v0/markets/{symbol}/orders/{id}

Returns detailed information about a specific order by its unique identifier. The response includes the order's current status, original parameters, fill progress (filled vs remaining amounts), and the on-chain transaction hash if available. Use this endpoint to poll for order status updates or display order details.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

id string Required
Unique uint128 order identifier, encoded as a decimal string

Example: `340282366920938463463374607431768211455`

Pattern: `^[0-9]+$`

Responses

200
Order details

application/json

A trading order

amount string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`

Pattern: `^[0-9]+(\.[0-9]+)?$`

createdAt integer · int64 Required
Unix Timestamp (ms)

Example: `1765534169841`

executionPrice string Optional
Price as decimal string for precision (e.g., "1.23456789")

Example: `13.37`

Pattern: `^[0-9]+(\.[0-9]+)?$`

filled string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`

Pattern: `^[0-9]+(\.[0-9]+)?$`

id string Required
Unique uint128 order identifier, encoded as a decimal string

Example: `340282366920938463463374607431768211455`

Pattern: `^[0-9]+$`

price string Required
Price as decimal string for precision (e.g., "1.23456789")

Example: `13.37`

Pattern: `^[0-9]+(\.[0-9]+)?$`

remaining string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`

Pattern: `^[0-9]+(\.[0-9]+)?$`

side string · enum Required
Order side (bid/ask)

Example: `buy`

Possible values: `buy` `sell`

status string · enum Required
Current status of the order

Example: `open`

Possible values: `open` `closed` `canceled` `expired` `rejected`

symbol string Required
Market symbol

Example: `SOM:USD`

txHash string Optional
On-chain transaction hash that placed the order

Example: `0xabc123...deadbeef`

walletAddress string Optional
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`

Pattern: `^0x[a-fA-F0-9]{40}$`

400
Error response

application/json

404
Error response

application/json

```text
GET /v0/markets/{symbol}/orders/{id} HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Accept: */*
```

```json
{
  "amount": "500",
  "createdAt": 1765534169841,
  "filled": "150",
  "id": "340282366920938463463374607431768211455",
  "price": "1.25",
  "remaining": "350",
  "side": "buy",
  "status": "open",
  "symbol": "SOM:USD",
  "txHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
  "walletAddress": "0x1234567890abcdef1234567890abcdef12345678"
}
```

### Prepare order cancellation

DELETE https://api.dreamdex.io

/v0/markets/{symbol}/orders/{id}

Generates an unsigned EVM transaction for canceling an open order. Only orders with status "open" can be canceled. The response contains the transaction payload (to, data, value, chainId) that must be signed and broadcast by the client's wallet. Once confirmed on-chain, the order is canceled and any unfilled portion is returned to the vault.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

id string Required
Unique uint128 order identifier, encoded as a decimal string

Example: `340282366920938463463374607431768211455`

Pattern: `^[0-9]+$`

Responses

200
EVM transaction payload the client MUST sign and send from their wallet

application/json

Unsigned EVM transaction payload for the client to sign and broadcast. For vault/approve on the native token, the API returns JSON `null` instead of this object — see the OrderTransactionOrNull response.

approval object Optional
ERC-20 pre-approval needed for a wallet-funded order. Only present when the caller's current on-chain allowance is insufficient for the order. When present, the client MUST submit token.approve(spotPoolAddress, amount) before broadcasting the order transaction. The amount includes the taker fee so the on-chain transferFrom never reverts due to insufficient allowance. When absent, the existing allowance already covers the order.

chainId string Required
EVM chain ID, as a decimal string

Example: `1`

data string Required
Hex-encoded data (0x-prefixed)

Example: `0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678`

Pattern: `^0x[a-fA-F0-9]*$`

gasLimit string Optional
Recommended gas limit, as a decimal string

Example: `250000`

nonce string Optional
A once-only value

Example: `abc123`

to string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`

Pattern: `^0x[a-fA-F0-9]{40}$`

value string Required
Wei value to send, as a decimal string. Non-zero for payable calls such as vault `depositNative()` when depositing the chain's native token; zero for ERC-20 deposits and withdrawals.

Example: `0`

400
Error response

application/json

404
Error response

application/json

```text
DELETE /v0/markets/{symbol}/orders/{id} HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Accept: */*
```

```json
{
  "approval": {
    "amount": "100.1",
    "token": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "chainId": "1",
  "data": "0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678",
  "gasLimit": "250000",
  "nonce": "abc123",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "value": "0"
}
```

### List orders

GET https://api.dreamdex.io

/v0/markets/{symbol}/orders

Returns all orders for the authenticated account in a specific market. Orders can be filtered by status (open, closed, canceled, expired, rejected) using the optional status query parameter. Each order includes its current state, fill progress, and associated transaction hash. Use this endpoint to display order history and track pending orders.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Query parameters

status string · enum Optional
Current status of the order

Example: `open`

Possible values: `open` `closed` `canceled` `expired` `rejected`

Responses

200
List of orders

application/json

orders object[] Required
A trading order

```text
GET /v0/markets/{symbol}/orders HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Accept: */*
```

```json
{
  "orders": [
    {
      "amount": "500",
      "createdAt": 1765534169841,
      "filled": "0",
      "id": "340282366920938463463374607431768211455",
      "price": "1.25",
      "remaining": "500",
      "side": "buy",
      "status": "open",
      "symbol": "SOM:USD",
      "txHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      "walletAddress": "0x1234567890abcdef1234567890abcdef12345678"
    },
    {
      "amount": "100",
      "createdAt": 1765533069841,
      "filled": "100",
      "id": "340282366920938463463374607431768211456",
      "price": "1.30",
      "remaining": "0",
      "side": "sell",
      "status": "closed",
      "symbol": "SOM:USD",
      "txHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
      "walletAddress": "0x1234567890abcdef1234567890abcdef12345678"
    }
  ]
}
```

### Get OHLCV candles

GET https://api.dreamdex.io

/v0/markets/{symbol}/candles

Returns historical OHLCV (Open, High, Low, Close, Volume) candlestick data for charting purposes. Each candle represents price action over a specific time interval. This endpoint supports various timeframes and is essential for rendering price charts and performing technical analysis.

To page backwards through history, supply `endTime` as a unix millisecond timestamp. Only candles whose bucket timestamp is strictly less than `endTime` are returned. Combined with `limit`, this lets a client load successive older windows by passing the oldest returned timestamp as the next request's `endTime`.

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Query parameters

interval string · enum Required
Candle time interval

Example: `1h`

Possible values: `1m` `5m` `15m` `1h` `4h` `1d`

limit integer · min: 1 · max: 1000 Optional
Maximum number of candles to return (default 100, max 1000)

Default: `100`
Example: `100`

endTime integer · int64 Optional
Return only candles whose bucket timestamp is strictly less than this unix millisecond timestamp. Used to page backwards through history.

Example: `1745875200000`

Responses

200
OHLCV candle data for a market

application/json

candles object[] Required
OHLCV candlestick data for a time interval

interval string Required
Candle time interval

Example: `1h`

symbol string Required
Market symbol

Example: `SOM:USD`

404
Error response

application/json

500
Error response

application/json

```text
GET /v0/markets/{symbol}/candles?interval=1m HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "candles": [
    {
      "close": "1.28",
      "high": "1.30",
      "low": "1.20",
      "open": "1.25",
      "timestamp": 1765530000000,
      "volume": "50000"
    }
  ],
  "interval": "1h",
  "symbol": "SOM:USD"
}
```

Previous Market Data
Next Vault
Last updated 2 months ago