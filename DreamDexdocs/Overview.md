# Overview

dreamDEX is a fully on-chain central limit order book (CLOB) where the protocol
takes nothing off the top. v1.0 ships spot trading in USDso-quoted markets. Perpetual futures arrive next. See the [Roadmap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/roadmap).

The same code path serves a $10 retail order and a $10m institutional fill. No
centralised matching engine, no private sequencer, no 'forced API' gating.

## What makes trading here different

- Zero fees, every pair. 0% maker, 0% taker. Funded by yield on resting capital. The book pays its own makers; the protocol takes nothing.
- Gas sponsorship on SOMI and stablecoin pairs. The protocol sponsors gas on the core assets of the Somnia economy. Elsewhere, gas fees are still paid by users in the native SOMI token, but are negligible compared to fees charged by alternative DEXs/CEXs.
- Yield-bearing CLOB. USDso yield is redistributed to active makers each period, weighted by proximity to mid-price. The closer your quote sits to the middle of the book, the larger your share. See the [Yield Algorithm](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/yield-algorithm).
- USDso-native settlement. Frax-backed stablecoin makes zero fees economically viable, and the same balances flow into perpetuals when they launch.
- Reactivity built in. Strategies subscribe to price levels, fills, or book events and react in the same block they fire, no polling required.
- Agent-native access. MCP, CCXT, AGENTS.md, REST and WebSocket. Existing bot infrastructure works without modification.

## How matching works

dreamDEX runs a price-time priority order book. Orders match first by best price, then by submission time. All matching, settlement, and position updates happen atomically on-chain.

### Order flow

1. Submit. Sign and submit an order transaction.
2. Validate. The smart contract verifies parameters, vault balance, and (for takers) free balance.
3. Match. The order matches against resting liquidity or joins the book as a maker quote.
4. Settle. Vault balances update atomically; events fire for off-chain consumers and reactive contracts in the same block.

## Settlement

Spot trades settle in USDso, Somnia's USD stablecoin, backed 1:1 by FraxUSD via LayerZero. USDso is also the collateral currency for perpetuals when they launch, so balances accumulated through spot trading flow naturally into perps.

The ~3.3% yield on USDso's backing is paid to active market makers, not held by the protocol. That is what makes the zero-fee model economically viable. Deeper books, tighter spreads, no taxes on flow.

## Build on the book

dreamDEX is liquidity infrastructure. Frontends, DEXs, vaults, aggregators,
structured-product issuers, and agent apps can route order flow through dreamDEX and
keep the spread, the rebate, or the user relationship for themselves.

A formal builder-codes / fee-rebate program is on the near-term roadmap.

## Next steps

### Common

- [Fees](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/fees): understand the zero-fee model
- [Yield Algorithm](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/yield-algorithm): how market makers earn the yield stream
- [Order Types](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/order-types): available order types and time-in-force options

### Spot

- [Spot Overview](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/spot): trading spot assets with zero fees
- [Contract Specifications](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/contract-specifications): live pairs and per-pool parameters
- [Stop Orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/readme-1/stop-orders): stop-loss / take-profit via the SpotStopOrderRegistry

### Perpetuals (in development)

- [Contract Specifications](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/contract-specifications): perpetual contract details
- [Margin](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/margin): margin modes and sub-accounts
- [Positions & PnL](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/positions-and-pnl): how positions and profits work
- [Funding](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/funding): perpetual funding rate mechanism
- [Liquidations](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/liquidations): liquidation waterfall and safety mechanisms

Previous Roadmap
Next Common
Last updated 15 days ago