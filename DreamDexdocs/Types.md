# Types

## SpotPool / OrderBook Types

### `Order` (struct)

```text
struct Order {
    OrderId orderId;
    bool isBid;
    address owner;
    uint64 userData;
    uint256 price;
    uint256 fullQuantity;
    uint256 quantityRemaining;
    uint64 expireTimestampNs;
}
```

### `OrderBookLevel` (struct)

```text
struct OrderBookLevel {
    uint256 price;
    uint256 quantity;
}
```

### `OrderType` (enum)

| Value | Description |
| --- | --- |
| `NormalOrder` | Order will be filled or placed into the book depending on current state |
| `FillOrKill` | Order will only execute if it can be fully filled immediately, otherwise rejected |
| `ImmediateOrCancel` | Order will fill as much as possible immediately, remaining quantity is cancelled |
| `PostOnly` | Order will be rejected if any portion would fill immediately (maker-only) |

### `SelfMatchingOption` (enum)

| Value | Description |
| --- | --- |
| `CancelTaker` | Cancel the taker order if it would match against own maker order |
| `CancelMaker` | Cancel the maker order if taker would match against it, then continue matching |

### `OrderBookParameters` (struct)

```text
struct OrderBookParameters {
    uint256 tickSize;
    uint256 minQuantity;
    uint256 lotSize;
}
```

| Field | Type | Description |
| --- | --- | --- |
| `tickSize` | `uint256` | Minimum price increment in quote token units |
| `minQuantity` | `uint256` | Minimum order quantity in base token units |
| `lotSize` | `uint256` | Minimum quantity increment in base token units |

### `SpotPoolParameters` (struct)

```text
struct SpotPoolParameters {
    uint256 takerFeeBpsTimes1k;
    uint256 makerFeeBpsTimes1k;
    address feeRecipient;
    uint256 maxBuilderFeeBpsTimes1k;
}
```

| Field | Type | Description |
| --- | --- | --- |
| `takerFeeBpsTimes1k` | `uint256` | Taker fee rate in basis points x 1000 (1 BPS = 1000) |
| `makerFeeBpsTimes1k` | `uint256` | Maker fee rate in basis points x 1000 (1 BPS = 1000) |
| `feeRecipient` | `address` | Address that receives collected trading fees |
| `maxBuilderFeeBpsTimes1k` | `uint256` | Protocol-wide cap on per-user→builder approvals (BPS_TIMES_1K). `0` disables [Builder Codes](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#builder-codes). |

### `MidpointEmaParameters` (struct)

Configuration for the EMA-smoothed midpoint trigger feed emitted on [MarkPriceUpdated](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events#markpriceupdated). The smoothing factor is the load-bearing protection against single-block midpoint manipulation — an attacker would need to sustain a manipulated raw midpoint across multiple intervals to drag the EMA past a stop's trigger band.

```text
struct MidpointEmaParameters {
    uint256 updateIntervalSec;
    uint256 emaSmoothingAlpha;
}
```

| Field | Type | Description |
| --- | --- | --- |
| `updateIntervalSec` | `uint256` | How often the EMA advances by one step, in seconds. Must be > 0 and <= 86400 (one day). |
| `emaSmoothingAlpha` | `uint256` | EMA smoothing factor scaled by 1e18. Must be in (0, 1e18]. Higher = less smoothing. |

## Stop Order Types

### `PendingOrderType` (enum)

| Value | Description |
| --- | --- |
| `LIMIT` | Triggered order uses a user-specified limit price |
| `MARKET` | Triggered order uses a slippage-adjusted limit price computed from the mark price |

### `Operator` (enum)

| Value | Description |
| --- | --- |
| `GTE` | Triggers when mark price is greater than or equal to trigger price |
| `LTE` | Triggers when mark price is less than or equal to trigger price |

### `PendingOrder` (struct)

```text
struct PendingOrder {
    bool isBid;
    address owner;
    uint64 userData;
    uint256 quantity;
}
```

### `PendingOrderWithTrigger` (struct)

```text
struct PendingOrderWithTrigger {
    PendingOrder order;
    PendingOrderType orderType;
    uint256 triggerPrice;
    Operator triggerOperator;
    uint256 limitPrice;
    address builder;
    uint96 builderFeeBpsTimes1k;
}
```

| Field | Type | Description |
| --- | --- | --- |
| `order` | `PendingOrder` | Core order parameters (side, owner, userData, quantity) |
| `orderType` | `PendingOrderType` | Whether this is a LIMIT or MARKET order |
| `triggerPrice` | `uint256` | The EMA midpoint threshold that activates this order |
| `triggerOperator` | `Operator` | GTE or LTE comparison against the mark price |
| `limitPrice` | `uint256` | Limit price for LIMIT orders. Must be exactly `0` for MARKET orders. |
| `builder` | `address` | Optional builder address that earns a fee on the triggered IOC order's fills. `address(0)` for none. See [Builder Codes](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#builder-codes). |
| `builderFeeBpsTimes1k` | `uint96` | Per-order builder fee rate in BPS_TIMES_1K units. Must be `0` when `builder` is `address(0)`. |

### `StoredPendingOrder` (struct)

The on-chain representation of a pending order. Returned by registry view functions.

```text
struct StoredPendingOrder {
    PendingOrderWithTrigger orderWithTrigger;
    OrderId orderId;
    uint256 somiPaid;
}
```

| Field | Type | Description |
| --- | --- | --- |
| `orderWithTrigger` | `PendingOrderWithTrigger` | The original order specification |
| `orderId` | `OrderId` | Globally unique pending-order identifier |
| `somiPaid` | `uint256` | SOMI paid at creation. Refunded on cancel, consumed on trigger. |

Previous Events
Next SpotRouter
Last updated 18 days ago
