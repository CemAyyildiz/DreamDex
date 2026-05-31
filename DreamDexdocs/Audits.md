# Audits

dreamDEX prioritizes the security of user funds above all else. Our security strategy includes rigorous internal testing, comprehensive external audits, and an ongoing bug bounty program.

## Built on Somnia

dreamDEX is built on the [Somnia blockchain](https://somnia.network/), a high-performance Layer 1 designed for real-time applications. By building on Somnia, dreamDEX inherits the robust security practices and infrastructure of the Somnia network.

### Inherited Security Practices

Somnia follows industry-leading security standards, including:

- Smart Contract Security: Comprehensive guidelines for secure smart contract development
- Audit Processes: Rigorous audit checklists and verification procedures
- Infrastructure Security: Battle-tested node and infrastructure security protocols
- Responsible Disclosure: Clear policies for reporting vulnerabilities

For more information on Somnia's security practices, see the [Somnia Security Documentation](https://docs.somnia.network/developer/security).

## Audit Status of dreamDEX Smart Contracts

Current Status: The dreamDEX spot protocol has completed external audit with Hacken. The final report is pending Hacken's review of the protocol team's remediations and will be published here once available.

### Spot Protocol — Hacken (April 2026)

| Item | Details |
| --- | --- |
| Firm | [Hacken](https://hacken.io) |
| Engagement | April 2026 |
| Scope | Spot DEX core contracts: `OrderBook`, `SpotPool`, `SpotStopOrderRegistry`, `ERC20Vault`, and supporting libraries (`PriorityIndex`, `OrderIndexManager`, `PerUserOrderIndex`, `LinkedList`, `Common`). |
| Status | Audit complete; final report pending Hacken's review of remediations |
| Report | Published here once finalized |

The audit covered the matching engine, order lifecycle, vault accounting (including native token support), fee model, mark-price emission, and the on-chain reactivity integration that powers stop orders. Remediations to the findings raised during the engagement have been delivered to Hacken and are currently under re-review.

### USDso Swap Contract — Sherlock

USDso, the stablecoin used as the quote token across dreamDEX spot markets, is backed 1:1 by FraxUSD via LayerZero. The USDso swap contract is being audited by [Sherlock](https://sherlock.xyz/) as a separate engagement. See the [Roadmap](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/welcome/roadmap) for context on how USDso fits into v1.0.

### Future Audits

Additional audits will be commissioned ahead of v2.0 (perpetuals) and any major protocol upgrade. Audit firms and scopes will be listed here once engagements are finalized.

## Bug Bounty

A dreamDEX bug bounty program will launch alongside v1.0. Details (scope, severity tiers, payout ranges, disclosure process) will be published on this page when the program goes live. In the meantime, please disclose any suspected vulnerabilities via Somnia's [responsible disclosure process](https://docs.somnia.network/developer/security).

Previous Risks
Next Audits
Last updated 17 days ago