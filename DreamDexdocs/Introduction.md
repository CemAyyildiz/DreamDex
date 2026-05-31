# Introduction

Work in Progress. This documentation tracks dreamDEX as it ships. Sections may change as the protocol evolves.

dreamDEX is the endgame DEX: CEX performance, DEX decentralisation, zero fees. A fully on-chain CLOB where the book pays its own makers and the protocol takes nothing off the top. Powered by Somnia, the Agentic L1.

## The DEX vs CEX trade-off is over

Most on-chain venues still ask you to compromise: pay fees, route through a centralised matching engine, or trust an opaque sequencer. dreamDEX gives up none of them. The same code path serves a $10 retail order and a $10m institutional fill. Market makers earn yield for posting tight quotes, and anyone can become one.

This is one venue, one book, designed to win on every axis (execution quality, decentralisation, and cost) for institutions, market makers, algorithmic desks, autonomous agents, and retail.

## What's live at launch

- Fully on-chain spot CLOB. Order book lives at the smart contract level on Somnia and clears at validator level. Auditable end-to-end.
- Zero maker / zero taker fees. Every pair, every order. Funded by yield on resting capital, not by taxing flow.
- Gas sponsorship on SOMI and stablecoin pairs. The protocol sponsors gas on the core assets of the Somnia economy. Elsewhere, gas fees are still paid by users in the native SOMI token, but are negligible compared to fees charged by alternative DEXs/CEXs.
- Yield-bearing CLOB. USDso yield is redistributed to active makers each period, weighted by proximity to mid-price.
- USDso-native settlement. Frax-backed stablecoin makes zero fees economically viable.
- Native agent and algo access. MCP server, AGENTS.md / SKILL.md, CCXT-compatible bindings, REST and WebSocket endpoints. Existing bot infrastructure works without modification.

## Values

- Transparency. Every rule governing the venue — matching, fees, yield allocation, settlement — is encoded on-chain and enforced algorithmically.
- Credible neutrality. No private matching engine. No 'forced API' gating. The same code path runs whether you're posting $10 or $10m.
- Zero-fee, by design. dreamDEX is Somnia's on-chain liquidity layer, not a fee-taking destination. Third-party apps can rebase onto our book and keep the spread for themselves.
- Agents-first. Autonomous agents and LLMs are first-class participants alongside humans through our skills library.
- Reactivity as a primitive. Data is pushed to your agents in real time. When a price level, fill, or book event happens on Somnia, your strategy reacts in the same block, no polling required.
- Performance. Real serial transactions on an L1 capable of up to 1M TPS with sub-second finality.

## Build on dreamDEX

dreamDEX is liquidity infrastructure. Frontends, DEXs, vaults, aggregators, structured-product issuers, and agent apps can route order flow through dreamDEX and keep the spread, the rebate, or the user relationship for themselves. Get in touch via the dreamDEX builder desk at [dreamdex.io](https://dreamdex.io/).

## Quick Links

- [Why dreamDEX](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/why-dreamdex): the values, the trade-offs we refused to make, and how we compare
- [Quick Start](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/quick-start): connect, fund, and place your first order
- [Roadmap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/roadmap): foundations now, the gap-closers next
- [Trading](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/trading/trading): how the book works, how fees work (they don't), how yield flows
- [Developers](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/developers): APIs, contracts, libraries, MCP, AGENTS.md

## License

Copyright (c) 2026 DreamDEX S.A. (Panama). See [LICENSE.md](https://github.com/somnia-chain/somnia-dex-docs/blob/main/LICENSE.md).

Next Quick Start
Last updated 15 days ago