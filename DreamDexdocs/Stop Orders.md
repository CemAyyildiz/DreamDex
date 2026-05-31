# Stop Orders

dreamDEX supports conditional stop orders for spot markets via the SpotStopOrderRegistry contract. These are pending orders that activate automatically when the spot
pool's mark price crosses a trigger threshold.

## How It Works

1. You create a pending order specifying a trigger price and condition (above or below), paying an exact SOMI fee with the transaction.
2. The order sits in the registry — it is not on the order book yet.
3. When the SpotPool's mark price crosses your trigger, [Somnia reactivity](https://docs.somnia.network/developer/reactivity) automatically fires the order.
4. The order is placed on the SpotPool as an Immediate-or-Cancel (IOC) order.
5. It fills whatever is available; any unfilled remainder is discarded.

## Mark Price (Trigger Feed)

Triggers are evaluated against the EMA-smoothed midpoint the SpotPool emits on [MarkPriceUpdated](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events#markpriceupdated). The EMA advances at most one step per `updateIntervalSec` and is the load-bearing protection against single-block midpoint manipulation — an attacker would need to sustain a manipulated raw midpoint across multiple intervals to drag the EMA past a stop's trigger band.

The same event also carries the raw `(bestBid + bestAsk) / 2` snapshot for off-chain consumers (UIs, indexers); that raw value is not the trigger feed.

## Order Types

### Limit Stop Order

You specify a limit price. When triggered, the order is placed at your limit price.

- Gives you price control over execution.
- Order may not fill if the book doesn't have liquidity at your limit price.

### Market Stop Order

When triggered, the limit price is calculated automatically from the current mark price using the registry's slippage tolerance (`slippageToleranceBps`). You must pass `limitPrice = 0` at creation — any other value is rejected.

- For buys: `limitPrice = markPrice + (markPrice * slippageBps / 10000)`, rounded down to tick.
- For sells: `limitPrice = markPrice - (markPrice * slippageBps / 10000)`, rounded up to tick.
- Maximizes chance of fill at the cost of price control.

## Trigger Operators

| Operator | Meaning | Triggers when... |
| --- | --- | --- |
| GTE | Greater than or equal | Mark price rises to or above trigger price |
| LTE | Less than or equal | Mark price falls to or below trigger price |

## Use Cases

### Stop-Loss Sell

"If the price drops to $90 or below, sell my tokens."

- Side: Sell (`isBid = false`)
- Trigger: LTE, triggerPrice = $90
- LIMIT example: limitPrice = $85 (willing to sell as low as $85)
- MARKET: limit price auto-calculated with slippage tolerance; `limitPrice` must be `0`

For LIMIT orders: `limitPrice` must be ≤ `triggerPrice`.

### Breakout Buy

"If the price rises to $110 or above, buy tokens."

- Side: Buy (`isBid = true`)
- Trigger: GTE, triggerPrice = $110
- LIMIT example: limitPrice = $120 (willing to buy as high as $120)
- MARKET: limit price auto-calculated with slippage tolerance; `limitPrice` must be `0`

For LIMIT orders: `limitPrice` must be ≥ `triggerPrice`.

### Buy the Dip

"If the price drops to $80 or below, buy tokens."

- Side: Buy (`isBid = true`)
- Trigger: LTE, triggerPrice = $80
- No limit/trigger price constraint for LIMIT orders.

### Take-Profit Sell

"If the price rises to $120 or above, sell my tokens."

- Side: Sell (`isBid = false`)
- Trigger: GTE, triggerPrice = $120
- No limit/trigger price constraint for LIMIT orders.

## Creating a Stop Order

### Using `cast`

```bash
# Create a stop-loss sell: sell if price drops to 90 USDso (6 decimals → 90000000)
# LIMIT type (0), LTE operator (1), limit price 85 USDso (→ 85000000)
# Trailing zeros are the builder address and builder fee — leave empty until v1.1
# --value sends SOMI to cover the per-order fee — must equal somiPaymentPerOrder() exactly
cast send $STOP_REGISTRY \
  "createPendingOrder(((bool,address,uint64,uint256),uint8,uint256,uint8,uint256,address,uint96))" \
  "((false,$WALLET_ADDRESS,0,$QUANTITY),0,90000000,1,85000000,0x0000000000000000000000000000000000000000,0)" \
  --value $SOMI_PAYMENT \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

The argument is a single `PendingOrderWithTrigger` struct:

- order: `(isBid, owner, userData, quantity)` — `owner` must be `msg.sender`; `quantity` must be >= `minQuantity` and a multiple of `lotSize` (both from the SpotPool).
- orderType: `0` = LIMIT, `1` = MARKET.
- triggerPrice: in raw quote token units.
- triggerOperator: `0` = GTE, `1` = LTE.
- limitPrice: in raw quote token units for LIMIT orders (must be tick-aligned). Must be exactly `0` for MARKET orders.
- builder / builderFeeBpsTimes1k: see [Builder Codes](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#builder-codes). Pass `address(0)` and `0` until v1.1.

SOMI payment must be exact. `createPendingOrder` is `payable` and requires `msg.value` to equal `somiPaymentPerOrder()` exactly. Both underpayment and overpayment revert with `InsufficientSomiPayment`. Read `somiPaymentPerOrder()` immediately before calling and forward that exact amount. The SOMI is refunded on cancel and consumed on trigger.

Minimum stop distance. Registries may be configured with a non-zero `minStopDistanceBps`, which rejects pending orders whose `triggerPrice` is closer to the current EMA midpoint than the configured threshold. Tightens the defense against trigger manipulation for tight stops. Defaults to `0` (disabled) — check `minStopDistanceBps()` on the registry before placing tight stops.

### Cancelling

Cancelling a pending order refunds the full SOMI payment to the order owner. If the transfer fails (e.g., the owner is a contract without a `receive`/`fallback`), the cancellation still succeeds and the refund is credited to the owner's unclaimed SOMI balance, withdrawable via `claimSomi()`.

```bash
cast send $STOP_REGISTRY \
  "cancelPendingOrder(uint128)" \
  $PENDING_ORDER_ID \
  --rpc-url $RPC --private-key $PRIVATE_KEY
```

The OrderId type is a `uint128` on-chain — pass the raw integer returned from `createPendingOrder`.

## SOMI Payment Model

Creating a stop order requires an exact SOMI (native token) payment sent with the transaction. This funds the Somnia
reactivity handler that monitors prices and triggers orders on-chain.

| Scenario | SOMI Behavior |
| --- | --- |
| Order creation | `msg.value` must equal `somiPaymentPerOrder()` exactly |
| Order cancellation | Full SOMI payment is refunded to the owner (or credited to unclaimed balance if the transfer fails) |
| Order triggered | SOMI is consumed (not refunded), whether the resulting fill succeeds or fails |
| Under-/overpayment | Reverts with `InsufficientSomiPayment` |

The admin can rotate `somiPaymentPerOrder` mid-life via `setSomiPaymentPerOrder`. Each stored order remembers the SOMI it paid at creation, so refunds remain correct across rate changes.

## Registry Lifecycle and Dormant State

The registry must hold an active Somnia reactivity subscription before it can accept orders. Calls to `createPendingOrder` revert with `NoActiveSubscription` while the registry is dormant.

If the admin ever removes the subscription, any pending orders become inert — they cannot be triggered. To recover funds in that state, anyone can call `cancelInertOrders` with the affected order IDs; each order's `somiPaid` is credited to the original owner's unclaimed balance, recoverable via `claimSomi()`.

## Important Notes

- No token escrow. The registry does not lock your tokens. You must have sufficient balance deposited in the SpotPool vault when the order triggers. The registry performs a point-in-time balance check at creation; if your free balance drops before the trigger fires, the resulting placement fails gracefully (`PendingOrderTriggered(success=false)`), and the order is removed.
- All triggered orders are IOC. They never rest on the order book. If there isn't enough counterparty liquidity at the limit price, unfilled quantity is discarded.
- Orders are one-shot. Once triggered — whether the fill succeeds or fails — the pending order is permanently removed. It cannot be re-triggered.
- Trigger feed. The mark price is the EMA-smoothed midpoint emitted by the SpotPool. Triggers are processed automatically via Somnia's on-chain reactivity system.
- Batch processing. When a price update triggers multiple stop orders, they are processed in a single transaction. A failed order does not block the others. The trigger loop respects a configurable gas buffer to leave headroom for the precompile's own bookkeeping.
- Quantity constraints. Order quantity must be >= `minQuantity` and a multiple of `lotSize` from the SpotPool. Orders that don't meet these constraints are rejected at creation time.

## Contract Reference

- [Functions](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#stop-orders-spotstoporderregistry) — `createPendingOrder`, `cancelPendingOrder`, `claimSomi`, admin functions and view helpers.
- [Events](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events#stop-order-events) — `PendingOrderCreated`, `PendingOrderTriggered`, `PendingOrderCancelled`, `InertOrderCancelled`, `SomiRefundFailed`.
- [Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#stop-order-types) — `PendingOrderType`, `Operator`, `PendingOrder`, `PendingOrderWithTrigger`, `StoredPendingOrder`.

Previous Simple Swap
Next Perpetuals
Last updated 17 days ago