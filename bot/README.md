DreamDex SpotRouter Bot

This bot uses the testnet SpotRouter flow documented by dreamDEX:
- chain ID `50312`
- `quoteMarketExactIn(...)` for live pricing
- `swapExactIn(...)` for taker volume
- one-time operator approval on `OperatorPermissionsRegistry`

Quick start:

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `config.yml.example` to `config.yml` and set the token symbols / router overrides you want.

3. Export credentials (or put into `.env`):

```bash
export DREAMDEX_API_KEY=your_api_key
export WALLET_KEY=0x...
```

4. Run the bot (dry-run recommended first):

```bash
python bot/bot.py --config bot/config.yml
```

What it does
- Discovers the market from the public market-data API.
- Ensures operator approval and ERC-20 allowance when required.
- Quotes each trade before submitting the swap.
- Randomizes input size and delay jitter.
- Tracks volume and order counts in `metrics.json`.

Notes
- For native SOMI, keep `input_is_native: true` and set `router_input_token` to the native sentinel.
- If the market-data quote token differs from the router token, set `router_output_token` explicitly.
- This is a live on-chain bot. Use testnet first.
