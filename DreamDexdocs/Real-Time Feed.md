# Real-Time Feed

WebSocket API for receiving real-time information about market state.

## Subscription Model

Use `subscribe` and `unsubscribe` operations to manage channel subscriptions:

```text
{"operation": "subscribe", "channel": "orderbook", "params": {"symbols": ["SOMI:USDso"]}}
{"operation": "unsubscribe", "channel": "orderbook", "params": {"symbols": ["SOMI:USDso"]}}
```

## Heartbeat

Send `{"operation": "ping"}` to receive `{"operation": "pong"}`. Connections close after 60 seconds of inactivity. Send a ping at least every 30 seconds to avoid being disconnected.

## Table of Contents

- Connection
- Close Codes
- Client Messages
- Server Messages
- Data Types

## Connection

Endpoint: `wss://api.dreamdex.io/v0/ws/public`

## Close Codes

The server uses standard and application-specific WebSocket close codes. See the [Errors](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/websocket-api/errors) page for close codes, connection-level failures, and application-level error messages.

## Client Messages

Messages sent by the client to the server.

### `ping` - Heartbeat ping

Receives a ping message from the client. The server immediately responds with a pong message. Clients should send pings periodically to prevent the connection from timing out after 60 seconds of inactivity.

#### Request Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Response

The server responds with:

- Pong: Server heartbeat response

### `subscribe` - Subscribe to data feed

Receives a subscription request from the client. The server validates the request parameters and, if successful, begins streaming the requested data. The client receives a subscribed confirmation followed by an initial snapshot, then incremental updates as data changes.

#### Request Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Subscribe to order book

```text
{
  "operation": "subscribe",
  "channel": "orderbook",
  "params": {
    "symbols": [
      "SOMI:USDso",
      "WBTC:USDso"
    ]
  }
}
```

Subscribe to OHLCV

```text
{
  "operation": "subscribe",
  "channel": "ohlcv",
  "params": {
    "symbol": "SOMI:USDso",
    "timeframe": "1m"
  }
}
```

Subscribe to trades

```text
{
  "operation": "subscribe",
  "channel": "trades",
  "params": {
    "symbols": [
      "SOMI:USDso"
    ],
    "limit": 100
  }
}
```

Subscribe to order updates

```text
{
  "operation": "subscribe",
  "channel": "order",
  "params": {
    "orderId": "0x1234567890abcdef"
  }
}
```

#### Response

The server responds with one of:

- Subscribed: Subscription successful
- Error: Request failed

### `unsubscribe` - Unsubscribe from data feed

Receives an unsubscription request from the client. The server stops sending updates for the specified data feed and confirms with an unsubscribed message.

#### Request Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Response

The server responds with one of:

- Unsubscribed: Unsubscription successful
- Error: Request failed

## Server Messages

Messages sent by the server to connected clients.

### `pong` - Heartbeat pong

Sends a pong response to the client after receiving a ping. This confirms the connection is alive and resets the inactivity timeout.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### `subscribed` - Subscription confirmed

Confirms a successful subscription. Sent immediately after processing a valid subscribe request. The confirmation echoes back the subscription parameters so the client can verify which data feed was activated.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Order book subscription confirmed

```text
{
  "channel": "orderbook",
  "type": "subscribed",
  "symbols": [
    "SOMI:USDso"
  ]
}
```

### `unsubscribed` - Unsubscription confirmed

Confirms a successful unsubscription. After this message, the client will no longer receive updates for the specified data feed.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### `error:error` - Error response

Sends an error message when a client request cannot be processed. This may occur due to invalid parameters, unknown channels, or server-side issues. The message field contains a human-readable error description.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### `orderbook:snapshot` - Order book snapshot

Sends the complete order book state immediately after a client subscribes to the orderbook channel. Contains aggregated price levels with total quantity at each price. Bids are sorted by price descending (highest first), asks are sorted ascending (lowest first). Clients should use this to initialize their local order book state before applying incremental updates.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

SOMI:USDso order book with 2 bid and 2 ask levels

```text
{
  "channel": "orderbook",
  "type": "snapshot",
  "symbol": "SOMI:USDso",
  "bids": [
    {
      "price": "1.24",
      "quantity": "1500"
    },
    {
      "price": "1.23",
      "quantity": "3200"
    }
  ],
  "asks": [
    {
      "price": "1.26",
      "quantity": "800"
    },
    {
      "price": "1.27",
      "quantity": "2100"
    }
  ],
  "timestamp": 1765534169841
}
```

### `orderbook:update` - Order book update

Sends incremental order book changes as they occur. Each update contains changed price levels in the `bids` and/or `asks` arrays. A quantity of zero means the level was removed from the book.

Apply updates by replacing the quantity at each price level, or removing the level if the quantity is zero.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

New bid and removed ask

```text
{
  "channel": "orderbook",
  "type": "update",
  "symbol": "SOMI:USDso",
  "bids": [
    {
      "price": "1.25",
      "quantity": "500"
    }
  ],
  "asks": [
    {
      "price": "1.26",
      "quantity": "0"
    }
  ],
  "timestamp": 1765534170000
}
```

### `ohlcv:snapshot` - OHLCV candle history

Sends historical candlestick data immediately after a client subscribes to the ohlcv channel. Contains recent candles for the requested symbol and timeframe. Clients should use this to populate charts before receiving live updates.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Two 1-minute candles for SOMI:USDso

```text
{
  "channel": "ohlcv",
  "type": "snapshot",
  "symbol": "SOMI:USDso",
  "timeframe": "1m",
  "candles": [
    {
      "timestamp": 1765534080000,
      "open": "1.24",
      "high": "1.27",
      "low": "1.23",
      "close": "1.26",
      "volume": "15000.5"
    },
    {
      "timestamp": 1765534140000,
      "open": "1.26",
      "high": "1.28",
      "low": "1.25",
      "close": "1.27",
      "volume": "12300"
    }
  ]
}
```

### `ohlcv:update` - OHLCV candle update

Sends a new or updated candlestick as trading occurs. If the candle timestamp matches an existing candle, the client should replace it (the candle is still forming). A new timestamp indicates the previous candle closed and a new one started.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Updated 1-minute candle

```text
{
  "channel": "ohlcv",
  "type": "update",
  "symbol": "SOMI:USDso",
  "timeframe": "1m",
  "candle": {
    "timestamp": 1765534200000,
    "open": "1.27",
    "high": "1.29",
    "low": "1.26",
    "close": "1.28",
    "volume": "8500"
  }
}
```

### `trades:snapshot` - Recent trades history

Sends recent trade history immediately after a client subscribes to the trades channel. Contains the most recent trades up to the requested limit (default 100). Trades are ordered by timestamp descending (newest first).

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Two recent trades for SOMI:USDso

```text
{
  "channel": "trades",
  "type": "snapshot",
  "symbol": "SOMI:USDso",
  "trades": [
    {
      "id": "trade001",
      "price": "1.25",
      "quantity": "100",
      "side": "buy",
      "timestamp": 1765534169000
    },
    {
      "id": "trade002",
      "price": "1.26",
      "quantity": "50",
      "side": "sell",
      "timestamp": 1765534168000
    }
  ]
}
```

### `trades:update` - New trade executed

Sends a trade notification when an order is filled. Each update contains a single trade with its price, quantity, and aggressor side. Clients receive this in real-time as trades execute on the exchange.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Buy order filled

```text
{
  "channel": "trades",
  "type": "update",
  "symbol": "SOMI:USDso",
  "trade": {
    "id": "trade003",
    "price": "1.27",
    "quantity": "75",
    "side": "buy",
    "timestamp": 1765534170000
  }
}
```

### `order:snapshot` - Order state snapshot

Sends the current state of a specific order immediately after a client subscribes to the order channel. Contains full order details including filled quantity and current status. Use this to initialize order tracking before receiving status updates.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Partially filled buy order

```text
{
  "channel": "order",
  "type": "snapshot",
  "order": {
    "id": "0x1234567890abcdef",
    "market": "SOMI:USDso",
    "side": "buy",
    "price": "1.25",
    "quantity": "1000",
    "filled": "250",
    "status": "partial",
    "createdAt": 1765534160000,
    "updatedAt": 1765534169000
  }
}
```

### `order:update` - Order status changed

Sends an order status update when the order state changes. This includes partial fills, complete fills, and cancellations. The update contains the complete current order state, not just the changes.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Order partially filled

```text
{
  "channel": "order",
  "type": "update",
  "order": {
    "id": "0x1234567890abcdef",
    "market": "SOMI:USDso",
    "side": "buy",
    "price": "1.25",
    "quantity": "1000",
    "filled": "500",
    "status": "partial",
    "createdAt": 1765534160000,
    "updatedAt": 1765534175000
  }
}
```

Order fully filled

```text
{
  "channel": "order",
  "type": "update",
  "order": {
    "id": "0x1234567890abcdef",
    "market": "SOMI:USDso",
    "side": "buy",
    "price": "1.25",
    "quantity": "1000",
    "filled": "1000",
    "status": "filled",
    "createdAt": 1765534160000,
    "updatedAt": 1765534180000
  }
}
```

### `shutdown` - Server shutting down

Notifies all connected clients that the server is shutting down gracefully. Clients should close their connections and reconnect to a different server or retry after a delay. This message is broadcast to all clients before the server terminates connections.

#### Message Format

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### Examples

Graceful shutdown notification

```text
{
  "type": "shutdown",
  "message": "server shutting down"
}
```

## Data Types

Reusable schema definitions.

### PriceLevel

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### Candle

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### Trade

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### Order

| Field | Type | Description | Constraints | Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

Previous WebSocket API
Next Operations
Last updated 16 days ago