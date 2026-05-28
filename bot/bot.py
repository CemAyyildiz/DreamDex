#!/usr/bin/env python3
import argparse
import asyncio
from pathlib import Path

import yaml

from executor import LiveDreamDexBot


def load_config(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


async def main():
    parser = argparse.ArgumentParser(description="DreamDex SpotPool bot")
    parser.add_argument("--config", default="bot/config.yml", help="Path to YAML config")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = load_config(str(config_path))

    bot = LiveDreamDexBot(cfg)

    print("Starting live bot — press Ctrl+C to stop")
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
