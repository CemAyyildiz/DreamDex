#!/usr/bin/env python3
"""Read-only preflight: RPC, balances, order book, one eth_call simulation."""
import argparse
import os
import sys
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv

_repo_root = Path(__file__).resolve().parent.parent
load_dotenv(_repo_root / ".env")

from executor import LiveDreamDexBot, ORDER_IOC  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="DreamDEX Trade Bot preflight")
    parser.add_argument("--config", default="bot/config.yml")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = _repo_root / config_path
    with open(config_path, "r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)

    bot = LiveDreamDexBot(cfg)
    bot._preflight_checks()
    bot._ensure_startup_allowances()

    best_bid, best_ask = bot._best_prices()
    if best_bid is None or best_ask is None:
        print("FAIL: no order book depth")
        return 1

    is_bid = bot._choose_side(best_bid, best_ask)
    if is_bid is None:
        print("FAIL: cannot buy or sell with current balances")
        return 1

    price_raw = bot._price_for_order(is_bid, best_bid, best_ask)
    if is_bid:
        quantity_raw = bot._buy_quantity_from_balance(bot._spendable_quote_balance(), price_raw)
    else:
        quantity_raw = bot._sell_quantity_from_balance(bot._spendable_base_balance())

    if quantity_raw < bot.market.min_quantity:
        print(f"FAIL: quantity {quantity_raw} < min {bot.market.min_quantity}")
        return 1

    side = "buy" if is_bid else "sell"
    print(f"Simulating {side}: qty={quantity_raw} price={price_raw} type=IOC")
    sim = bot.pool.functions.placeTakerOrderWithoutVault(
        is_bid,
        0,
        int(price_raw),
        int(quantity_raw),
        int((time.time() + bot.deadline_sec) * 1e9),
        ORDER_IOC,
        0,
        bot.builder,
        bot.builder_fee_bps_times1k,
    ).call({"from": bot.address, "value": bot._order_value(is_bid, quantity_raw)})

    if not sim[0]:
        print("FAIL: simulation returned success=false")
        return 1

    print("OK: simulation passed — safe to run bot.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
