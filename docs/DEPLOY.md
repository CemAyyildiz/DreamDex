# Running the bot 24/7

The bot stops when your machine sleeps, the terminal closes, or the process is killed. For uninterrupted trading, run it on a remote Linux server.

## Options

| Method | When to use |
|--------|-------------|
| **VPS / cloud** (recommended) | Production — always-on execution |
| Mac + `nohup` / `run_forever.sh` | Local testing only; not reliable overnight |
| **systemd** (Linux VPS) | Production — auto-restart on crash |

## 1. Linux VPS (DigitalOcean, Hetzner, AWS EC2, etc.)

```bash
git clone https://github.com/CemAyyildiz/DreamDex.git && cd DreamDex
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp bot/config.yml.example bot/config.yml
# Edit bot/config.yml (market, slippage, volume_mode)
nano .env   # PRIVATE_KEY=0x... (never commit)

chmod +x run_forever.sh
python3 bot/preflight.py --config bot/config.yml
```

### systemd (recommended)

Create `/etc/systemd/system/dreamdex-bot.service`:

```ini
[Unit]
Description=DreamDEX trading bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/DreamDex
EnvironmentFile=/home/ubuntu/DreamDex/.env
ExecStart=/home/ubuntu/DreamDex/.venv/bin/python3 -u bot/bot.py --config bot/config.yml
Restart=always
RestartSec=30
StandardOutput=append:/home/ubuntu/DreamDex/logs/bot.log
StandardError=append:/home/ubuntu/DreamDex/logs/bot.log

[Install]
WantedBy=multi-user.target
```

```bash
mkdir -p logs
sudo systemctl daemon-reload
sudo systemctl enable dreamdex-bot
sudo systemctl start dreamdex-bot
sudo systemctl status dreamdex-bot
journalctl -u dreamdex-bot -f
```

Alternative: `ExecStart=/home/ubuntu/DreamDex/run_forever.sh` (supervisor loop with 30s delay on exit).

## 2. macOS (temporary)

```bash
cd DreamDex
chmod +x run_forever.sh
nohup ./run_forever.sh > logs/supervisor.out 2>&1 &
tail -f logs/bot-forever.log
```

Sleep and closed laptops will stop the bot — use a VPS for multi-day runs.

## 3. Monitoring

```bash
tail -f bot.log              # if using run_bg.sh
tail -f logs/bot-forever.log # if using run_forever.sh
cat metrics.json             # order/error counters
pgrep -fl bot/bot.py         # process running?
```

## 4. Stop conditions

Optional limits in `bot/config.yml`:

- `max_orders` — stop after N successful fills
- `volume_target_quote_raw` — stop at a cumulative notional threshold (high-turnover mode)

Leave both unset for an indefinite run.

## 5. Security on the server

See [SECURITY.md](../SECURITY.md). Summary: protect `.env`, use SSH keys, dedicated trading wallet with limited funds.
