# Risks

Trading involves significant risk. You should only trade with funds you can afford to lose. dreamDEX is a decentralized protocol and its use involves technical and market risks.

dreamDEX provides a high-performance, non-custodial trading environment, but users should be aware of the inherent risks associated with decentralized finance (DeFi).

## Technical Risks

### Smart Contract Vulnerabilities

All deposits, order matching, and settlement occur via smart contracts on the Somnia blockchain. While these contracts undergo rigorous internal testing and external audits, they may contain undiscovered bugs or vulnerabilities that could lead to loss of funds. See [Audits](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/security/audits) for the current audit status.

### Blockchain Infrastructure

As an on-chain protocol, dreamDEX depends on the Somnia blockchain. Network downtime, congestion, or consensus failures could prevent users from placing, cancelling, or filling orders.

### Upgradeable Contracts

The spot DEX contracts (`SpotPool`, `SpotStopOrderRegistry`) are deployed behind upgradeable beacons. Upgrades are controlled by the protocol owner and are designed to ship security fixes and improvements, but any upgrade introduces the risk of unintended changes in behavior. See [Audits](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/security/audits) for how upgrades are validated.

## Market Risks

### Liquidity Risk

While dreamDEX aims to attract deep liquidity through its yield-bearing collateral model, certain markets or extreme conditions may experience wider spreads or reduced liquidity, making it difficult to execute large orders at desired prices.

### Price Risk

Spot trades execute at the price determined by the order book at the time of fill. Market orders and aggressive limit orders may fill across multiple price levels, resulting in an average fill price worse than the top of book. Use limit orders to control your worst acceptable price.

## Protocol Risks

### Protocol Upgrades

As an evolving protocol, dreamDEX may undergo upgrades. While these are designed to improve the system, changes to parameters or logic could impact trading strategies.

### Parameter Changes

Configurable parameters — including order book constraints (tick size, lot size, minimum quantity), stop-order registry settings, and fee rates — can be updated by the protocol owner via on-chain transactions. Material changes will be announced ahead of time where possible.

Previous Errors
Next Audits
Last updated 17 days ago