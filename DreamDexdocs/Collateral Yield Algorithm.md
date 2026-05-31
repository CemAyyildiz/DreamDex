# Collateral Yield Algorithm

To maintain a highly liquid and efficient Central Limit Order Book (CLOB),
dreamDEX utilizes an algorithmic distribution of yield to reward market makers for
providing order book depth.

## Overview

Unlike traditional "rebate" models that pay per fill, dreamDEX rewards Open Interest (resting orders). This mechanism ensures that liquidity providers are
compensated for their capital commitment and the risk of being filled.

The yield is generated from the underlying collateral strategies: initially
native stablecoin yield, and later expanded to include native token staking and
lending vaults.

## Yield Distribution Principles

The algorithm distributes yield based on three primary factors:

1. Notional Value: The size of the resting order.
2. Time in Book: How long the order has been active and resting.
3. Proximity to Mid-price: How close the order's limit price is to the current market mid-price.

## Proximity Weighting

The core of the algorithm is the Proximity Weighting. Liquidity is most valuable to the exchange when it is near the mid-price, as
this results in tighter spreads for takers.

The weighting follows a Gaussian distribution centered at the mid-price:

W=e−(Porder−Pmid)22𝜎2

Where:

- W: Yield Weight
- P_order: Limit Price of the maker order
- P_mid: Current Mid-price
- σ: Standard deviation, determining how quickly yield rewards drop off as orders
move away from the mid-price.

### Impact of Proximity

- At the Mid-price: Orders earn the maximum base yield rate.
- Deep in the Book: As orders move further from the mid-price, the yield weighting decays,
providing less reward for non-competitive liquidity.

## Yield Accrual and Settlement

- Continuous Calculation: The protocol tracks order book state changes in real-time (i.e. on each
block).
- Automatic Settlement: Yield is periodically settled to the user's margin sub-account.
- Transparency: Market makers can view their historical yield rates via the Developer API or
Trade Interface.

Previous Fees
Next Order Types
Last updated 1 month ago