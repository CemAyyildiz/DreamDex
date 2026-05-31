# Contracts

Smart contract API reference for the Somnia DEX order book.

The Somnia DEX uses a distinct contract for each trading pair. To discover
available markets and their contract addresses, query the [GET /v0/markets](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/market-data) endpoint.

## OrderBook API (SpotPool)

- [Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types) — structs and enums used in function signatures and event payloads.
- [Functions](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions) — place, cancel, reduce, and query orders; deposit and withdraw from the vault; manage builder approvals.
- [Events](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events) — on-chain events emitted by the order book contract.

## StopOrderRegistry API (SpotStopOrderRegistry)

Each SpotPool has a corresponding StopOrderRegistry for stop-loss, take-profit,
and stop-buy orders. See [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) for how they work.

- [Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/types#stop-order-types) — `PendingOrderType`, `Operator`, `PendingOrder`, `PendingOrderWithTrigger`
- [Functions](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/functions#stop-orders-spotstoporderregistry) — `createPendingOrder`, `cancelPendingOrder`, `claimSomi`, and view functions
- [Events](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/events#stop-order-events) — `PendingOrderCreated`, `PendingOrderTriggered`, `PendingOrderCancelled`, `SomiRefundFailed`

## SpotRouter API

A multi-stage swap router that walks ordered SpotPool legs as taker orders in a
single transaction. Powers the [Simple Swap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/simple-swap) frontend. The router is a pure orchestrator — pools auto-pull / auto-deliver
between the user's wallet and the router never custodies funds across legs.

- [SpotRouter reference](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/spot-router) — functions (`swapExactIn` / `swapExactOut` / `quoteMarketExactIn` / `quoteExactIn` / `quoteExactOut`), events, errors, caller prerequisites, and the quote → swap recipe.

Previous Overview
Next Functions
Last updated 4 days ago