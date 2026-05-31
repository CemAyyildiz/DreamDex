# Overview

dreamDEX provides a high-performance spot market for trading crypto assets with
zero protocol fees and atomic on-chain settlement.

## Features

- Zero Fees: 0% maker and 0% taker fees.
- Deep Liquidity: Institutional-grade market makers providing tight spreads.
- Atomic Settlement: Funds are swapped instantly and are fully non-custodial.
- Simple Swap: One-click multi-hop swap surface routed through the [SpotRouter](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/contracts/spot-router); see [Simple Swap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/simple-swap) for the user flow and testnet live preview.
- Stop Orders: Conditional stop-loss and take-profit orders via the [SpotStopOrderRegistry](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders), triggered automatically by Somnia's on-chain reactivity against the SpotPool's EMA-smoothed mark price.
- Shared Matching Engine: Spot uses the same matching engine that will power perpetuals in v2.0, so the execution semantics carry over to leveraged trading later.

## Getting Started

To trade on the spot market:

1. Discover available markets via the [HTTP API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/market-data) or by calling `getPoolParams()` on a SpotPool contract.
2. Deposit tokens into the vault via `deposit()`.
3. Place a limit or market order via `placeOrder()`, or use `placeTakerOrderWithoutVault()` for one-shot wallet-funded IOC / FOK orders.
4. Optionally set up [stop orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders) for automated risk management.

See the [Quick Start](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/quick-start) guide for a step-by-step walkthrough.

Previous Spot
Next Contract Specifications
Last updated 4 days ago