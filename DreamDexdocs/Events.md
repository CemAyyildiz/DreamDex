# Events

## SpotPool / OrderBook Events

### `OrderPlaced`

Emitted for every accepted order, regardless of whether any quantity ultimately
rests on the book.

```text
event OrderPlaced(OrderId indexed orderId, Order placedOrder);
```

### `OrderRested`

Emitted when an order comes to rest on the book after placement. Only emitted
for the residual quantity that is actually inserted into the priority index.
Orders that fully fill on placement, IOC residuals, and FOK orders do not emit this
event. The resting order's details are available on the paired `OrderPlaced`.

```text
event OrderRested(OrderId indexed orderId);
```

### `OrderFilled`

Emitted when two orders are matched and filled.

```text
event OrderFilled(OrderId indexed takerOrderId, OrderId indexed makerOrderId, uint256 quantityFilled, uint256 takerRemainingQuantity, uint256 makerRemainingQuantity);
```

### `OrderCancelled`

Emitted when an order is cancelled by its owner.

```text
event OrderCancelled(OrderId indexed orderId);
```

### `OrderExpired`

Emitted when an expired order is removed — either inline during matching, or via
the permissionless `cancelExpiredOrders` / `sweepExpiredAtLevel` cleanup paths.

```text
event OrderExpired(OrderId indexed orderId);
```

### `OrderReduced`

Emitted when an order's quantity is reduced by its owner.

```text
event OrderReduced(OrderId indexed orderId, uint256 newQuantity);
```

### `MarkPriceUpdated`

Emitted when the midpoint price advances. `markPrice` is the EMA-smoothed midpoint and is the value the `SpotStopOrderRegistry` consumes to evaluate triggers. `rawMidpoint` is the unsmoothed `(bestBid + bestAsk) / 2` snapshot at emission time, exposed for off-chain consumers (UIs, indexers) — it
must not be used as a trigger feed.

```text
event MarkPriceUpdated(address indexed asset, uint256 markPrice, uint256 rawMidpoint);
```

During the bootstrap branch (first emission) and the defensive zero-params
fallback, `markPrice == rawMidpoint`. In steady state they diverge by the EMA smoothing factor.

### `MidpointEmaParametersUpdated`

Emitted when the admin updates the midpoint EMA parameters.

```text
event MidpointEmaParametersUpdated();
```

### `MidpointEmaReset`

Emitted when the admin resets the EMA state via `resetMidpointEma`. The next book event after this re-runs the bootstrap branch.

```text
event MidpointEmaReset();
```

### `FeeRecipientUpdated`

Emitted when the fee recipient is rotated by the current recipient via `updateFeeRecipient`.

```text
event FeeRecipientUpdated(address indexed oldRecipient, address indexed newRecipient);
```

### `BuilderApproved`

Emitted when a user updates their approval for a builder via [approveBuilder](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#approvebuilder). `maxFeeBpsTimes1k = 0` indicates a revocation.

```text
event BuilderApproved(address indexed user, address indexed builder, uint256 maxFeeBpsTimes1k);
```

### `BuilderFeeCharged`

Emitted on every fill of a builder-tagged order with the per-fill fee amount
credited to the builder. Fires once per side per fill (maker side and taker side
each emit if they carry a builder). Skipped when the order has no builder. `amount` may be `0` on small fills because the fee is floor-rounded; the event still fires so
consumers can detect that the builder path executed.

```text
event BuilderFeeCharged(OrderId indexed orderId, address indexed builder, address indexed token, uint256 amount);
```

### `MaxBuilderFeeUpdated`

Emitted when the admin updates the protocol-wide cap on per-user→builder
approvals (`maxBuilderFeeBpsTimes1k`).

```text
event MaxBuilderFeeUpdated(uint256 oldMax, uint256 newMax);
```

### `OrderBookParametersUpdated`

Emitted when the order book parameters (tick size, lot size, min quantity) are
updated by the admin.

```text
event OrderBookParametersUpdated(OrderBookParameters newParameters);
```

### `ContractApprovalUpdated`

Emitted once per address whose approval to place orders on behalf of users is
updated via `updateIsApprovedContractToPlaceOrders`. Emitted regardless of whether the new approval state differs from the prior
state.

```text
event ContractApprovalUpdated(address indexed contractAddress, bool isApproved);
```

## Stop Order Events

These events are emitted by the `SpotStopOrderRegistry` contract. See [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) for details.

### `PendingOrderCreated`

Emitted when a new pending stop order is created.

```text
event PendingOrderCreated(OrderId indexed orderId, address indexed owner, bool isBid, uint256 quantity, uint256 triggerPrice, Operator triggerOperator, PendingOrderType orderType, address builder, uint96 builderFeeBpsTimes1k);
```

### `PendingOrderTriggered`

Emitted when a pending order is triggered by a mark-price update and submitted
to the order book.

```text
event PendingOrderTriggered(OrderId indexed pendingOrderId, bool success, OrderId indexed spotOrderId);
```

### `PendingOrderCancelled`

Emitted when a pending order is cancelled by its owner. The SOMI payment is
refunded (or credited to unclaimed SOMI if the transfer fails — see `SomiRefundFailed`).

```text
event PendingOrderCancelled(OrderId indexed orderId);
```

### `InertOrderCancelled`

Emitted when an inert pending order is cleaned up via `cancelInertOrders` (or the `removeSubscription(OrderId[])` overload). Only emitted while the registry has no active subscription. The
order's stored `somiPaid` is credited to the original owner's unclaimed SOMI balance.

```text
event InertOrderCancelled(OrderId indexed orderId, address indexed owner, uint256 somiCredited);
```

### `SomiRefundFailed`

Emitted when a SOMI refund transfer fails during order cancellation (for
example, the order owner is a contract without a `receive`/`fallback`). The refund amount is credited to the owner's unclaimed balance, withdrawable
via `claimSomi()`.

```text
event SomiRefundFailed(OrderId indexed orderId, address indexed owner, uint256 amount);
```

## Stop Order Admin Events

### `SomiPaymentPerOrderUpdated`

Emitted when the admin updates the SOMI payment required per stop order.

```text
event SomiPaymentPerOrderUpdated(uint256 oldValue, uint256 newValue);
```

### `SlippageToleranceUpdated`

Emitted when the admin updates the slippage tolerance for MARKET-type stop
orders.

```text
event SlippageToleranceUpdated(uint256 oldValue, uint256 newValue);
```

### `MinStopDistanceUpdated`

Emitted when the admin updates the minimum allowed distance between `triggerPrice` and the EMA midpoint at order creation time.

```text
event MinStopDistanceUpdated(uint256 oldValue, uint256 newValue);
```

### `GasBufferBpsUpdated`

Emitted when the admin updates the per-iteration gas buffer used by the trigger
loop. The cached effective `gasBuffer` (= `subscriptionGasLimit × bps / 10_000`) is recomputed atomically with this update.

```text
event GasBufferBpsUpdated(uint256 oldBps, uint256 newBps);
```

### `SomiWithdrawn`

Emitted when the admin withdraws excess SOMI from the contract. Only SOMI not
reserved for pending order refunds or unclaimed cancel refunds can be withdrawn.

```text
event SomiWithdrawn(address indexed recipient, uint256 amount);
```

### `SubscriptionCreated`

Emitted when the admin creates a Somnia reactivity subscription, activating the
registry.

```text
event SubscriptionCreated(uint256 subscriptionId);
```

### `SubscriptionRemoved`

Emitted when the admin removes the active reactivity subscription, making the
registry dormant.

```text
event SubscriptionRemoved(uint256 subscriptionId);
```

Previous Functions
Next Types
Last updated 18 days ago