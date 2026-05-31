# Why dreamDEX

Work in Progress. Content evolves with the protocol.

The endgame DEX. CEX-grade execution. DEX-grade decentralisation. Zero fees. A fully on-chain
CLOB where the book pays its own makers and the protocol takes nothing off the
top.

## Why another DEX?

In Q1 2026, on-chain venues cleared $760bn of spot and $2.43 trillion of perpetuals (DefiLlama). Despite that volume, no existing venue meets the bar professional
capital, institutions, and agentic systems need to commit flow on-chain at
scale:

- AMM-based DEXs force liquidity providers into slippage, impermanent loss, MEV exploitation,
and capital inefficiency.
- Existing CLOB DEXs still charge fees on at least one side, run centralised matching engines or
sequencers the operator controls, and (on perpetuals) rely on opaque, discretionary
risk management.

Most other venues force a compromise: fees, a centralised matching engine, or a
sequencer the operator controls. dreamDEX gives up none of them.

## What we refused to compromise on

### Transparency

Every rule governing spot is encoded on-chain and enforced algorithmically:
order matching, the (zero) fee schedule, yield allocation, settlement. The same
discipline carries into perps when they launch. Margin thresholds, liquidation
stages, and ADL conditions are all published in advance, with no discretionary
intervention.

### Credible neutrality

The order book lives at the smart contract level on Somnia and clears at
validator level. No centralised matching engine. No private sequencer that throttles
flow. No 'forced API' gating.

A $10 retail order and a $10m institutional fill take the same code path. Market
makers earn yield for posting tight quotes, but anyone can become one: acquire
SOMI, start quoting.

### Zero-fee, by design

Zero maker, zero taker, every pair. SOMI and stablecoin pairs go further: the
protocol sponsors gas on the core assets of the Somnia economy.

dreamDEX is built to be Somnia's on-chain liquidity layer, not a venue that taxes flow. Third-party apps can rebase onto our book and keep the spread or the user
relationship for themselves.

### An agents-first future

Autonomous agents and LLMs are first-class participants alongside humans through
our skills library:

- Native MCP server
- `SKILL.md` / `AGENTS.md` for auto-discoverable agent contracts
- CCXT-compatible bindings, so every existing trading bot works out of the box
- Clean REST and WebSocket endpoints

### Reactivity as a base primitive

Every other chain forces agents to poll. Somnia pushes book events to your
agents the instant they fire. When a price level, fill, or order update happens on
Somnia, your strategy reacts in the same block, with deterministic intra-block
execution. This is the substrate agentic and algorithmic trading is actually built
on. No centralised venue or polling-based chain can offer it.

### Performance

Real serial transactions, not speculatively parallel. dreamDEX runs on Somnia's
EVM, an L1 capable of up to 1M TPS with sub-second finality.

## How dreamDEX compares

| Property | dreamDEX | Major CEX | AMM DEX | Other CLOB DEX |
| --- | --- | --- | --- | --- |

## The pitch, by audience

Institutions want trust and credible neutrality. Every rule is on-chain. There is no
operator with discretion over your liquidation.

Market makers want yield on resting capital and predictable execution. USDso yield is
redistributed to active makers each period, weighted by proximity to mid-price.

Agentic and algorithmic desks want reactive primitives and first-class access. Native MCP, CCXT, AGENTS.md,
on a chain that lets contracts react in the same block.

Builders want infrastructure they can compose on without ceding margin. dreamDEX is
liquidity, not a fee-taking destination. Route flow through us and keep the spread.

Retail wants the same fills the pros get, on the same book. Zero fees. Same code path.

## Summary

One venue. One book. No compromises.

- Best prices, driven by the tightest spreads in DeFi.
- Zero protocol fees, funded by yield on resting capital, not by taxing flow.
- Credible neutrality: same code path for everyone, no centralised matching engine, no private
sequencer.
- Yield-subsidised market making: makers earn the USDso yield stream by quoting close to mid.
- Safety in speed: sub-10ms matching (on the roadmap) and Somnia's deterministic intra-block
execution reduce adverse selection and liquidation risk.
- Agents-first by design: MCP, CCXT, AGENTS.md, reactivity, all native.

Previous Quick Start
Next Roadmap
Last updated 15 days ago