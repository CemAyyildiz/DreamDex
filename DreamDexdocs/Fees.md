# Fees

Work in Progress - This section is currently being developed. Content may be incomplete or
subject to change.

dreamDEX pioneers a yield-subsidized fee model that offers zero trading fees while maintaining protocol sustainability and
rewarding liquidity providers.

## Trading Fees

dreamDEX charges 0% maker and taker fees. Unlike traditional exchanges that extract value from every trade, dreamDEX
monetizes the time-value of collateral.

| Fee Type | Rate |
| --- | --- |
| Maker Fee | 0% |
| Taker Fee | 0% |

## Gas Fees

While trading fees are zero, users still pay small gas fees to the Somnia
network for on-chain execution. These fees are paid in SOMI, the native token of the Somnia blockchain, and are negligible compared to the 2–10 basis point fees charged by traditional DEXs and CEXs.

### Estimated Gas Costs (SOMI)

| Action | Estimated SOMI Cost | Est. USD Value | Comparison (Traditional 5bps) |
| --- | --- | --- | --- |
| Place Limit Order | [TODO] SOMI | [TODO] | $50.00 (on $100k) |
| Cancel Order | [TODO] SOMI | [TODO] | $0.00 |
| Market Order (Fill) | [TODO] SOMI | [TODO] | $50.00 (on $100k) |
| Deposit / Withdrawal | [TODO] SOMI | [TODO] | $1.00 - $10.00 |

Note: Estimates based on standard network congestion and a hypothetical SOMI
price for illustration.

## Maker Rewards: Collateral Yield

Makers do not receive traditional "rebates." Instead, they earn Collateral Yield on their resting liquidity.

When you place a maker limit order, your margin remains in your control on-chain
while being automatically eligible for yield generation. This rewards market
makers for providing book depth and maintaining tight spreads.

### How it Works

The protocol provides yield to all open interest on the books. To encourage
liquidity where it's needed most:

- Proximity Weighting: Orders closer to the mid-price receive a higher weight in the yield distribution.
- Continuous Accrual: Yield is earned for as long as the order remains open on the book.
- Payment: Yield is paid out in USDso to the maker's wallet. [TODO: Add methodology]

For a technical breakdown of how yield is calculated and distributed, see the [Collateral Yield Algorithm](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/common/yield-algorithm).

## Other Costs

- Funding Rates: Peer-to-peer payments between longs and shorts to keep mark price pegged to index (see [Funding](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/perpetuals/funding)).
- Liquidation Clearing Fee: [TODO]

Previous Common
Next Collateral Yield Algorithm
Last updated 1 month ago