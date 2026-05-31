# Functions

## SpotPool / OrderBook

The SpotPool contract exposes the order book API and the integrated vault API.
Functions are grouped by purpose: order management, vault, market data, mark
price (EMA), and builder codes. Admin-only entrypoints (parameter updates, beacon
upgrades, etc.) are not documented here — they are reserved for the protocol owner
and emit events that are listed on the [Events](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events) page.

### Order Management

#### `placeOrder`

Places a new order in the order book using the caller's internal vault balance.

```text
function placeOrder(bool isBid, uint64 userData, uint256 price, uint256 quantity, uint64 expireTimestampNs, OrderType orderType, SelfMatchingOption selfMatchingOption, address builder, uint96 builderFeeBpsTimes1k) external returns (bool success, OrderId orderId);
```

Returns: `success`: True if the order was accepted (even if partially or fully filled). `orderId`: Unique identifier for the order; use this to cancel or query the order.

Builder codes are gated by the protocol-wide cap. Builder codes ship enabled in v1.1. At v1.0 launch the cap (`getMaxBuilderFeeBpsTimes1k()`) is `0`, so passing a non-zero `builder` reverts with `BuilderCodesNotSupported`. Pass `address(0)` and `0` for the builder arguments until the cap is raised.

#### `placeTakerOrderWithoutVault`

Places a taker order (IOC or FOK) funded directly from the caller's wallet
balance instead of the on-chain vault. The caller must have granted an ERC-20
allowance to the pool contract before calling this function. For native-token markets,
the function is `payable` and pulls the input from `msg.value` instead of an allowance.

```text
function placeTakerOrderWithoutVault(bool isBid, uint64 userData, uint256 price, uint256 quantity, uint64 expireTimestampNs, OrderType orderType, SelfMatchingOption selfMatchingOption, address builder, uint96 builderFeeBpsTimes1k) external payable returns (bool success, OrderId orderId);
```

Parameters are identical to placeOrder, with two restrictions:

- `orderType` must be `ImmediateOrCancel` or `FillOrKill` (GTC and PostOnly require vault funding).
- For non-native pools, `msg.value` must be zero (revert: `UnexpectedNativeDeposit`).

Internally this function pre-deposits the required input (`principal + maxFee`, including the worst-case builder fee), runs the order, and withdraws any
unused balance in the same transaction.

#### `cancelOrder`

Cancels an existing order and returns any remaining locked funds to the owner's
withdrawable vault balance.

```text
function cancelOrder(OrderId orderId) external;
```

#### `reduceOrder`

Reduces the remaining quantity of an existing order. The new quantity must be
smaller than the current remaining and must respect `minQuantity` and `lotSize`. Reverts with `ExpiredOrderMustBeCancelled` if the order is past its expiration — expired orders must be cancelled via cancelOrder.

```text
function reduceOrder(OrderId orderId, uint256 newQuantityRemaining) external;
```

#### `cancelExpiredOrders`

Permissionless cleanup for expired orders identified by ID. For each order,
locked balances are returned to the owner's withdrawable balance and `OrderExpired` is emitted. Orders that are not expired or whose stored ID no longer matches
the supplied ID are silently skipped rather than reverted.

```text
function cancelExpiredOrders(OrderId[] calldata orderIds) external;
```

#### `sweepExpiredAtLevel`

Permissionless cleanup for expired orders at a single price level. Walks the
priority chain from the best order on the requested side and cleans up to `maxCount` expired orders found at exactly `price`. Useful for keeping the top of book clean after the head order expires.

```text
function sweepExpiredAtLevel(bool isBid, uint256 price, uint256 maxCount) external returns (uint256 cleaned);
```

Returns: the number of orders actually cleaned.

### Vault

#### `deposit`

Deposits ERC20 tokens into the on-chain vault, updating the caller's internal
balance. The token must be either the base or quote token of the market.

```text
function deposit(address token, uint256 amount) external;
```

For native-token markets, use `depositNative()` instead. Calling `deposit()` with the native token sentinel reverts with `UseDepositNative`.

#### `depositNative`

Deposits native tokens into the vault. The deposit amount is `msg.value`. Only valid on pools where one side of the pair is the native token.

```text
function depositNative() external payable;
```

#### `withdraw`

Withdraws tokens from the caller's internal vault balance back to their wallet.
Reverts with `InsufficientBalance` if the user's free balance is insufficient.

```text
function withdraw(address token, uint256 amount) external;
```

#### `getWithdrawableBalance`

Returns the free (withdrawable) balance for a given owner and token. This is the
balance not currently locked in open orders.

```text
function getWithdrawableBalance(address owner, address token) external view returns (uint256);
```

### Market Data and Configuration

#### `getOrder`

Retrieves the details of an order by its ID.

```text
function getOrder(OrderId orderId) external view returns (Order memory);
```

See [Order](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#order-struct).

#### `getOwnOpenOrders`

Returns all open (non-expired) order IDs owned by the caller.

```text
function getOwnOpenOrders() external view returns (OrderId[] memory);
```

#### `getBookLevels`

Returns aggregated order book levels for the bid or ask side.

```text
function getBookLevels(bool isBid, uint64 numLevels) external view returns (OrderBookLevel[] memory);
```

See [OrderBookLevel](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#orderbooklevel-struct).

#### `getPoolParams`

Returns all pool configuration parameters in a single call.

```text
function getPoolParams() external view returns (address baseToken_, address quoteToken_, uint256 makerFeeBpsTimes1k_, uint256 takerFeeBpsTimes1k_, uint256 tickSize_, uint256 minQuantity_, uint256 lotSize_);
```

#### `getOrderBookParameters`

Returns the order book configuration parameters as a struct.

```text
function getOrderBookParameters() external view returns (OrderBookParameters memory);
```

See [OrderBookParameters](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#orderbookparameters-struct).

#### `getAllOpenOrdersOffChain`

Paginated iteration of all open orders on one side of the book. This function
can only be called via `eth_call` (off-chain) — `msg.sender` must be `address(0)`.

```text
function getAllOpenOrdersOffChain(bool isBid, uint256 maxCount, uint64 startCursor) external view returns (Order[] memory orders, bool hasMoreOrders, uint64 nextCursor);
```

#### `convertToQuoteAtPriceCeil`

Converts a base token quantity to its equivalent quote token amount at a given
price, rounding up. Useful for estimating the cost of a bid order.

```text
function convertToQuoteAtPriceCeil(uint256 baseQuantity, uint256 priceQuote) external view returns (uint256);
```

### Mark Price (EMA-Smoothed Midpoint)

The SpotPool emits [MarkPriceUpdated](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events#markpriceupdated) whenever the order book midpoint advances. The emitted `markPrice` is an EMA-smoothed value over the raw midpoint `(bestBid + bestAsk) / 2`, advancing at most one step per `updateIntervalSec`. The raw midpoint is also exposed on the event for off-chain consumers (UIs,
indexers) but must not be used as a trigger feed — the smoothing is the protection against
single-block midpoint manipulation.

#### `getMidpointEmaParameters`

Returns the current EMA configuration.

```text
function getMidpointEmaParameters() external view returns (MidpointEmaParameters memory);
```

See [MidpointEmaParameters](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#midpointemaparameters-struct).

#### `getMidpointEmaState`

Returns the live EMA midpoint and the timestamp of the most recent advance.

```text
function getMidpointEmaState() external view returns (uint256 emaValue, uint64 lastUpdateNs);
```

`emaValue` is zero before the first book event triggers the bootstrap branch.

### Builder Codes

Builder codes let an order owner route a per-fill fee to a third-party
integrator (a "builder") that submits the order on their behalf. Two parameters on placeOrder and placeTakerOrderWithoutVault — `builder` and `builderFeeBpsTimes1k` — opt an order into this flow. The fee is paid in addition to the protocol
maker/taker fee, in the same token (quote for bids, base for asks), and is settled
per fill to the builder's vault balance.

v1.0 / v1.1. Builder codes are gated by an admin-controlled protocol cap (`getMaxBuilderFeeBpsTimes1k()`). At v1.0 launch the cap is `0`, so any non-zero `builder` reverts with `BuilderCodesNotSupported`. The feature ships enabled for partners with v1.1 — see the [Roadmap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/roadmap).

#### `approveBuilder`

Approves (or revokes) a builder for the caller, granting the builder the right
to charge a per-fill fee up to `maxFeeBpsTimes1k` on orders the caller submits with that builder code. Set `maxFeeBpsTimes1k` to `0` to revoke.

```text
function approveBuilder(address builder, uint256 maxFeeBpsTimes1k) external;
```

#### `getMaxBuilderFeeBpsTimes1k`

Returns the protocol-wide cap on per-user→builder approvals. A return value of `0` disables builder codes (every non-zero `builder` reverts with `BuilderCodesNotSupported`).

```text
function getMaxBuilderFeeBpsTimes1k() external view returns (uint256);
```

#### `getBuilderApproval`

Returns the raw maximum builder fee a user has approved for a given builder. The
returned value can exceed the current protocol-wide cap if the cap was lowered
after the approval was set — at order time the effective limit is clamped by the
cap.

```text
function getBuilderApproval(address user, address builder) external view returns (uint256);
```

#### `getEffectiveBuilderApproval`

Returns the per-order builder fee actually enforceable at order time: `min(getBuilderApproval(user, builder), getMaxBuilderFeeBpsTimes1k())`. Use this from off-chain consumers (UIs, builder dashboards) to read the same
ceiling the chain will charge.

```text
function getEffectiveBuilderApproval(address user, address builder) external view returns (uint256);
```

## Stop Orders (SpotStopOrderRegistry)

For the full stop-order mechanics, see [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders).

### User Functions

#### `createPendingOrder`

Creates a new pending stop order with a trigger condition. The order remains
pending until the mark price crosses the trigger threshold, at which point it is
automatically placed on the SpotPool as an IOC order. Requires an exact SOMI payment matching `somiPaymentPerOrder()` (both underpayment and overpayment revert with `InsufficientSomiPayment`).

```text
function createPendingOrder(PendingOrderWithTrigger calldata orderWithTrigger) external payable returns (OrderId pendingOrderId);
```

Validation: Quantity must be >= the SpotPool's `minQuantity` and a multiple of `lotSize`. For LIMIT orders, `limitPrice` must be tick-aligned. For MARKET orders, `limitPrice` must be exactly `0` (slippage is applied to the mark price at trigger time). If `minStopDistanceBps` is non-zero, the trigger price must be at least that distance from the current
EMA midpoint. The owner's vault balance must already cover the order's
collateral lock at creation time. The registry must have an active subscription — calls
revert with `NoActiveSubscription` while dormant.

Builder codes: The struct carries `builder` and `builderFeeBpsTimes1k`. When the resulting IOC order is placed on the SpotPool at trigger time it is
validated against the SpotPool's protocol-wide cap and the owner's approveBuilder record — set both fields to `address(0)` / `0` unless the owner has already approved the builder. See Builder Codes.

The registry does not escrow tokens. The vault-balance check at creation time is a point-in-time
snapshot; if the owner withdraws collateral before the order triggers, the triggered
placement fails gracefully and the order is removed.

#### `cancelPendingOrder`

Cancels a pending stop order and refunds the SOMI paid at creation. If the
refund transfer fails (e.g., the owner is a contract without a `receive`/`fallback`), the cancellation still succeeds and the refund is credited to the owner's
unclaimed SOMI balance, withdrawable via claimSomi.

```text
function cancelPendingOrder(OrderId orderId) external;
```

#### `claimSomi`

Withdraws the caller's unclaimed SOMI balance. Reverts with `NothingToClaim` if there is no unclaimed balance.

```text
function claimSomi() external;
```

#### `cancelInertOrders`

Permissionless cleanup for pending orders left behind after the admin removes
the registry's reactivity subscription. Only callable while the registry is
dormant (no active subscription) — reverts with `SubscriptionStillActive` otherwise. Credits each order's `somiPaid` to the original owner's unclaimed SOMI balance.

```text
function cancelInertOrders(OrderId[] calldata orderIds) external;
```

### View Functions

#### `spotPool`

Returns the SpotPool this registry is associated with.

```text
function spotPool() external view returns (address);
```

#### `somiPaymentPerOrder`

Returns the SOMI payment required per stop-order creation (in wei). Read this
immediately before calling `createPendingOrder` and forward the exact amount.

```text
function somiPaymentPerOrder() external view returns (uint256);
```

#### `slippageToleranceBps`

Returns the slippage tolerance (basis points) used when computing limit prices
for MARKET-type stop orders at trigger time.

```text
function slippageToleranceBps() external view returns (uint256);
```

#### `minStopDistanceBps`

Returns the minimum required distance (basis points) between `triggerPrice` and the EMA midpoint at order creation time. Zero means the check is disabled.

```text
function minStopDistanceBps() external view returns (uint256);
```

#### `activeSubscriptionId`

Returns the ID of the active reactivity subscription, or `0` if the registry is dormant. `createPendingOrder` reverts when dormant.

```text
function activeSubscriptionId() external view returns (uint256);
```

#### `gasBuffer` / `gasBufferBps` / `subscriptionGasLimit`

Subscription-derived gas-cap state used by the trigger loop. `gasBuffer = subscriptionGasLimit × gasBufferBps / 10_000`. All three return `0` while the registry is dormant.

```text
function gasBuffer() external view returns (uint256);
function gasBufferBps() external view returns (uint256);
function subscriptionGasLimit() external view returns (uint64);
```

#### `reservedSomi`

Returns the total SOMI reserved for pending order refunds (sum of `somiPaid` across all active pending orders). Admin can only withdraw above this amount.

```text
function reservedSomi() external view returns (uint256);
```

#### `unclaimedSomi`

Returns the unclaimed SOMI balance for a given user. Accumulates when a cancel
refund transfer fails; withdrawable via claimSomi.

```text
function unclaimedSomi(address user) external view returns (uint256);
```

Previous Contracts
Next Events
Last updated 18 days ago