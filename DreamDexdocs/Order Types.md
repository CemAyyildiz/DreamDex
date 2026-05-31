# Order Types

dreamDEX supports a range of order types to accommodate different trading
strategies.

## Basic Order Types

### Limit Order

Place an order at a specific price. The order rests on the book until filled or
cancelled.

- Use case: When you want to control your entry/exit price
- Execution: Fills at your specified price or better

### Market Order

Execute immediately at the best available price. Market orders are implemented
as Immediate-or-Cancel (IOC) orders with an aggressive price — set a price well above the best ask for buys,
or well below the best bid for sells. The order fills whatever is available and
any unfilled remainder is cancelled.

- Use case: When speed of execution is more important than price
- Execution: Fills against resting liquidity at current market prices

## Time-in-Force Options

### Good-Till-Cancelled (GTC)

Order remains active until filled or manually cancelled. This is the `NormalOrder` type on the contract.

- Funding: Requires vault funding (deposit tokens first via `deposit()`)

### Immediate-or-Cancel (IOC)

Order executes immediately for any available quantity; unfilled portion is
cancelled.

- Use case: Large orders where partial fills are acceptable
- Funding: Supports both vault and wallet funding

### Fill-or-Kill (FOK)

Order must be filled entirely or not at all.

- Use case: When you need the full quantity or nothing
- Funding: Supports both vault and wallet funding

### Post-Only

Order is rejected if it would immediately match (take liquidity).

- Use case: Ensure your order always provides liquidity (maker order)
- Funding: Requires vault funding

## Advanced Order Types

### Stop-Loss

Triggers a market or limit order when the mark price drops to a specified level.
The mark price is the EMA-smoothed midpoint emitted by the SpotPool.

- Trigger: LTE — when mark price falls to or below your stop price
- Use case: Limit downside risk on open positions
- See [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) for full details

### Take-Profit

Triggers an order when the mark price rises to your profit target. The mark
price is the EMA-smoothed midpoint emitted by the SpotPool.

- Trigger: GTE — when mark price rises to or above your target price
- Use case: Lock in gains automatically
- See [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) for full details

## Order Matching

Orders are matched using Price-Time Priority (PTP):

1. Best price has priority
2. Among orders at the same price, earlier orders fill first

All matching occurs on-chain with atomic settlement.

## Self-Trade Prevention (STP)

dreamDEX prevents users from trading against themselves. When placing an order,
you specify one of the following behaviors for when it would match against your
own resting order:

- Cancel Taker (Default): The incoming (taker) order is cancelled. This prevents the trade without
affecting your resting orders.
- Cancel Maker: The resting (maker) order is cancelled, allowing the taker order to continue
matching against other orders.

Self-trading is never permitted — one side is always cancelled.

Previous Collateral Yield Algorithm
Next Spot
Last updated 18 days ago