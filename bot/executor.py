import asyncio
import json
import logging
import os
import random
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import requests
from eth_account import Account
from web3 import Web3
from web3.exceptions import ContractCustomError

logger = logging.getLogger(__name__)


NATIVE_TOKEN = Web3.to_checksum_address("0x28f34DeFd2b4CB48d9eE6d89f2Be4Bc601694c00")
ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")


POOL_ABI = [
    {
        "inputs": [
            {"internalType": "bool", "name": "isBid", "type": "bool"},
            {"internalType": "uint64", "name": "userData", "type": "uint64"},
            {"internalType": "uint256", "name": "price", "type": "uint256"},
            {"internalType": "uint256", "name": "quantity", "type": "uint256"},
            {"internalType": "uint64", "name": "expireTimestampNs", "type": "uint64"},
            {"internalType": "uint8", "name": "orderType", "type": "uint8"},
            {"internalType": "uint8", "name": "selfMatchingOption", "type": "uint8"},
            {"internalType": "address", "name": "builder", "type": "address"},
            {"internalType": "uint96", "name": "builderFeeBpsTimes1k", "type": "uint96"},
        ],
        "name": "placeTakerOrderWithoutVault",
        "outputs": [
            {"internalType": "bool", "name": "success", "type": "bool"},
            {"internalType": "uint128", "name": "orderId", "type": "uint128"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getPoolParams",
        "outputs": [
            {"internalType": "address", "name": "baseToken_", "type": "address"},
            {"internalType": "address", "name": "quoteToken_", "type": "address"},
            {"internalType": "uint256", "name": "makerFeeBpsTimes1k_", "type": "uint256"},
            {"internalType": "uint256", "name": "takerFeeBpsTimes1k_", "type": "uint256"},
            {"internalType": "uint256", "name": "tickSize_", "type": "uint256"},
            {"internalType": "uint256", "name": "minQuantity_", "type": "uint256"},
            {"internalType": "uint256", "name": "lotSize_", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bool", "name": "isBid", "type": "bool"},
            {"internalType": "uint64", "name": "numLevels", "type": "uint64"},
        ],
        "name": "getBookLevels",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "uint256", "name": "quantity", "type": "uint256"},
                ],
                "internalType": "struct OrderBookLevel[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "baseQuantity", "type": "uint256"},
            {"internalType": "uint256", "name": "priceQuote", "type": "uint256"},
        ],
        "name": "convertToQuoteAtPriceCeil",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "tuple[]", "name": "route", "type": "tuple[]"},
            {"internalType": "address", "name": "inputToken", "type": "address"},
            {"internalType": "uint256", "name": "inputAmount", "type": "uint256"},
        ],
        "name": "quoteMarketExactIn",
        "outputs": [
            {"internalType": "bool", "name": "ok", "type": "bool"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "tuple[]", "name": "legs", "type": "tuple[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "tuple[]", "name": "route", "type": "tuple[]"},
            {"internalType": "address", "name": "inputToken", "type": "address"},
            {"internalType": "address", "name": "outputToken", "type": "address"},
            {"internalType": "uint256", "name": "outputAmount", "type": "uint256"},
        ],
        "name": "quoteExactOut",
        "outputs": [
            {"internalType": "bool", "name": "ok", "type": "bool"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "tuple[]", "name": "legs", "type": "tuple[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "inputToken", "type": "address"},
                    {"internalType": "uint256", "name": "inputAmount", "type": "uint256"},
                    {"internalType": "address", "name": "outputToken", "type": "address"},
                    {"internalType": "uint256", "name": "minOutputAmount", "type": "uint256"},
                    {"internalType": "tuple[]", "name": "route", "type": "tuple[]"},
                    {"internalType": "uint64", "name": "deadlineNs", "type": "uint64"},
                ],
                "internalType": "struct ISpotRouter.SwapExactInParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "swapExactIn",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint256", "name": "amountInUsed", "type": "uint256"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "inputToken", "type": "address"},
                    {"internalType": "uint256", "name": "maxInputAmount", "type": "uint256"},
                    {"internalType": "address", "name": "outputToken", "type": "address"},
                    {"internalType": "uint256", "name": "outputAmount", "type": "uint256"},
                    {"internalType": "tuple[]", "name": "route", "type": "tuple[]"},
                    {"internalType": "uint64", "name": "deadlineNs", "type": "uint64"},
                ],
                "internalType": "struct ISpotRouter.SwapExactOutParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "swapExactOut",
        "outputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutReceived", "type": "uint256"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
]


ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


@dataclass
class Market:
    symbol: str
    pool: str
    base: str
    quote: str
    base_decimals: int
    quote_decimals: int
    tick_size: int
    min_quantity: int
    lot_size: int
    base_is_native: bool
    quote_is_native: bool


class LiveDreamDexBot:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.rpc_url = cfg["rpc_url"]
        self.market_data_base = cfg.get("market_data_base", "https://api.dreamdex.io")
        self.private_key = os.getenv(cfg.get("private_key_env", "PRIVATE_KEY"))
        if not self.private_key:
            raise ValueError("Missing private key environment variable")

        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={"timeout": 30}))
        if not self.web3.is_connected():
            raise RuntimeError(f"Cannot connect to RPC: {self.rpc_url}")

        self.native_token = Web3.to_checksum_address(cfg.get("native_token", NATIVE_TOKEN))
        self.pool_address_override = cfg.get("pool_address")
        self.max_orders = cfg.get("max_orders")
        self.min_input = Decimal(str(cfg.get("min_input", "0.01")))
        self.max_input = Decimal(str(cfg.get("max_input", "0.05")))
        # Bulk/volume strategy: when enabled, increase per-order size to raise
        # volume while keeping transaction count low. Can use FOK to avoid
        # partial fills if desired.
        self.bulk_mode = bool(cfg.get("bulk_mode", False))
        self.bulk_multiplier = int(cfg.get("bulk_multiplier", 5))
        self.use_fok_for_bulk = bool(cfg.get("use_fok_for_bulk", True))
        self.freq_sec = float(cfg.get("freq_sec", 10))
        self.slippage_bps = int(cfg.get("slippage_bps", 50))
        self.deadline_sec = int(cfg.get("deadline_sec", 120))
        self.only_buy = bool(cfg.get("only_buy", False))
        self.only_sell = bool(cfg.get("only_sell", False))
        self.metrics_path = cfg.get("metrics_path", "metrics.json")
        self.state_path = cfg.get("state_path", "bot_state.json")
        self.max_approval = int(cfg.get("max_approval", 2**256 - 1))
        self.priority_fee_gwei = cfg.get("priority_fee_gwei", 1)
        # Builder codes not supported in v1.0 - must be zero
        self.builder = ZERO_ADDRESS
        self.builder_fee_bps_times1k = 0

        self.metrics = {"orders": 0, "volume_in_raw": 0, "volume_out_raw": 0, "errors": 0}
        self.market = self._load_market()
        self.pool = self.web3.eth.contract(address=self.market.pool, abi=POOL_ABI)
        # Router configuration (optional)
        self.use_router = bool(cfg.get("use_router", False))
        self.router_address = cfg.get("router_address")
        self.router = None
        if self.use_router:
            if not self.router_address:
                raise RuntimeError("use_router is true but router_address not set in config")
            self.router = self.web3.eth.contract(address=Web3.to_checksum_address(self.router_address), abi=ROUTER_ABI)
        self.base_token_contract = None if self.market.base_is_native else self.web3.eth.contract(
            address=self.market.base, abi=ERC20_ABI
        )
        self.quote_token_contract = None if self.market.quote_is_native else self.web3.eth.contract(
            address=self.market.quote, abi=ERC20_ABI
        )

        if self.market.base_is_native and self.web3.eth.get_balance(self.address) == 0:
            raise RuntimeError(f"Wallet {self.address} has zero native balance; cannot trade native market")
        
        logger.info(f"Bot initialized: wallet={self.address}, market={self.market.symbol}")

    def _fetch_json(self, path: str) -> Dict[str, Any]:
        url = f"{self.market_data_base.rstrip('/')}{path}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def _load_market(self) -> Market:
        markets = self._fetch_json("/v0/markets").get("markets", [])
        desired_symbol = self.cfg.get("market_symbol", "SOMI:USDso").upper()

        market = None
        if self.pool_address_override:
            desired_pool = Web3.to_checksum_address(self.pool_address_override)
            for item in markets:
                if Web3.to_checksum_address(item["contract"]) == desired_pool:
                    market = item
                    break

        if market is None:
            for item in markets:
                if item.get("symbol", "").upper() == desired_symbol:
                    market = item
                    break

        if market is None:
            raise RuntimeError(f"Market not found for {desired_symbol}")

        pool = Web3.to_checksum_address(market["contract"])
        pool_contract = self.web3.eth.contract(address=pool, abi=POOL_ABI)
        params = pool_contract.functions.getPoolParams().call()
        base_token = Web3.to_checksum_address(params[0])
        quote_token = Web3.to_checksum_address(params[1])
        tick_size = int(params[4])
        min_quantity = int(params[5])
        lot_size = int(params[6])

        return Market(
            symbol=market["symbol"],
            pool=pool,
            base=base_token,
            quote=quote_token,
            base_decimals=int(market["baseDecimals"]),
            quote_decimals=int(market["quoteDecimals"]),
            tick_size=tick_size,
            min_quantity=min_quantity,
            lot_size=lot_size,
            base_is_native=base_token == self.native_token,
            quote_is_native=quote_token == self.native_token,
        )

    def _build_base_tx(self) -> Dict[str, Any]:
        tx: Dict[str, Any] = {
            "from": self.address,
            "nonce": self.web3.eth.get_transaction_count(self.address),
            "chainId": int(self.cfg.get("chain_id", 5031)),
        }
        latest_block = self.web3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas")
        if base_fee is not None:
            priority = self.web3.to_wei(self.priority_fee_gwei, "gwei")
            tx["maxPriorityFeePerGas"] = int(priority)
            tx["maxFeePerGas"] = int(base_fee * 2 + priority)
            tx["type"] = 2
        else:
            tx["gasPrice"] = self.web3.eth.gas_price
        # Prefill a conservative gas limit to avoid web3 auto-estimating during build
        tx["gas"] = int(self.cfg.get("fallback_gas", 300000))
        return tx

    def _sign_and_send(self, tx: Dict[str, Any]) -> str:
        signed = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()

    def _token_balance(self, token: str) -> int:
        if token == self.native_token:
            return self.web3.eth.get_balance(self.address)
        contract = self.web3.eth.contract(address=token, abi=ERC20_ABI)
        return int(contract.functions.balanceOf(self.address).call())

    def _approve_token(self, token: str) -> Optional[str]:
        if token == self.native_token:
            return None

        contract = self.web3.eth.contract(address=token, abi=ERC20_ABI)
        allowance = int(contract.functions.allowance(self.address, self.market.pool).call())
        if allowance >= self.max_approval // 2:
            return None

        tx = contract.functions.approve(self.market.pool, self.max_approval).build_transaction(
            self._build_base_tx()
        )
        tx["gas"] = self.web3.eth.estimate_gas(tx)
        tx_hash = self._sign_and_send(tx)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash

    def ensure_allowances(self) -> List[str]:
        approvals: List[str] = []
        for token in {self.market.base, self.market.quote}:
            try:
                tx_hash = self._approve_token(token)
                if tx_hash:
                    approvals.append(tx_hash)
            except Exception as exc:
                logger.warning(f"Approval failed for {token}: {exc}")
        return approvals

    def _align_to_lot(self, quantity_raw: int) -> int:
        lot = max(1, self.market.lot_size)
        aligned = (quantity_raw // lot) * lot
        if aligned == 0:
            aligned = lot
        return max(aligned, self.market.min_quantity)

    def _random_quantity(self) -> int:
        decimals = self.market.base_decimals
        low = int(Decimal(str(self.min_input)) * (Decimal(10) ** decimals))
        high = int(Decimal(str(self.max_input)) * (Decimal(10) ** decimals))
        if self.bulk_mode:
            # scale up both low and high bounds to create larger orders
            low = int(low * self.bulk_multiplier)
            high = int(high * self.bulk_multiplier)
        low = max(low, self.market.min_quantity)
        high = max(high, low)
        raw = random.randint(low, high)
        return self._align_to_lot(raw)

    def _best_prices(self) -> Tuple[Optional[int], Optional[int]]:
        asks = self.pool.functions.getBookLevels(False, 1).call()
        bids = self.pool.functions.getBookLevels(True, 1).call()
        best_ask = int(asks[0][0]) if asks else None
        best_bid = int(bids[0][0]) if bids else None
        return best_bid, best_ask

    def _align_price(self, price_raw: int, is_bid: bool) -> int:
        tick = max(1, self.market.tick_size)
        remainder = price_raw % tick
        if remainder == 0:
            return price_raw
        if is_bid:
            return price_raw + (tick - remainder)
        return max(tick, price_raw - remainder)

    def _price_for_order(self, is_bid: bool, best_bid: int, best_ask: int) -> int:
        if is_bid:
            aggressive = (best_ask * (10_000 + self.slippage_bps)) // 10_000
            return self._align_price(aggressive, True)
        aggressive = (best_bid * (10_000 - self.slippage_bps)) // 10_000
        return self._align_price(aggressive, False)

    def _can_afford(self, is_bid: bool, quantity_raw: int, price_raw: int) -> bool:
        if is_bid:
            quote_cost = self._quote_cost(quantity_raw, price_raw)
            return self._token_balance(self.market.quote) >= quote_cost
        return self._token_balance(self.market.base) >= quantity_raw

    def _quote_cost(self, quantity_raw: int, price_raw: int) -> int:
        return int(self.pool.functions.convertToQuoteAtPriceCeil(quantity_raw, price_raw).call())

    def _choose_side(self, quantity_raw: int, best_bid: int, best_ask: int) -> Optional[bool]:
        can_buy = self._can_afford(True, quantity_raw, self._price_for_order(True, best_bid, best_ask))
        can_sell = self._can_afford(False, quantity_raw, self._price_for_order(False, best_bid, best_ask))
        
        logger.debug(f"Side decision: can_buy={can_buy}, can_sell={can_sell}, orders={self.metrics['orders']}, qty={quantity_raw}")

        if self.only_buy:
            return True if can_buy else None
        if self.only_sell:
            return False if can_sell else None

        # Bidirectional trading - alternate between buy and sell for maximum volume
        if can_buy and can_sell:
            # Alternate based on order count for maximum volume
            side = (self.metrics["orders"] % 2) == 0
            logger.debug(f"Alternating side: {'buy' if side else 'sell'}")
            return side
        if can_buy:
            logger.debug("Only buy possible")
            return True
        if can_sell:
            logger.debug("Only sell possible")
            return False
        logger.warning("Neither buy nor sell possible")
        return None

    def _order_value(self, is_bid: bool, quantity_raw: int) -> int:
        # Native input must be attached as msg.value for both buy and sell flows.
        if is_bid and self.market.quote_is_native:
            return quantity_raw
        if not is_bid and self.market.base_is_native:
            return quantity_raw
        return 0

    def _tick_align_away(self, price: int, is_bid: bool) -> int:
        # Round price away from user's interest then align to tick
        # For bids (user pays more), round up; for asks (user receives less), round down.
        return self._align_price(price, is_bid)

    def _swap_via_router(self, is_bid: bool, quantity_raw: int) -> str:
        if not self.router:
            raise RuntimeError("Router not configured")

        # Single-leg route using the market's pool
        leg = (self.market.pool, 0, 0)  # (pool, priceLimit, quantity)
        route = [leg]

        # Sell (is_bid=False): input = base -> output = quote, use swapExactIn
        if not is_bid:
            input_token = self.market.base if not self.market.base_is_native else NATIVE_TOKEN
            output_token = self.market.quote
            # Quote what we'd get for exact input
            try:
                q = self.router.functions.quoteMarketExactIn(route, input_token, int(quantity_raw)).call()
            except Exception as exc:
                logger.warning(f"router quoteMarketExactIn failed: {exc}")
                raise
            ok = q[0]
            amount_out = int(q[2])
            if not ok and amount_out == 0:
                raise RuntimeError("Router quote indicates no liquidity for this sell size")
            min_output = (amount_out * (10_000 - self.slippage_bps)) // 10_000

            # Build live route with priceLimit based on worstFillPrice
            worst = int(q[3][0][3]) if q[3] and len(q[3]) > 0 and len(q[3][0]) > 3 else 0
            price_limit = self._tick_align_away(int(worst * (10_000 - self.slippage_bps) // 10_000), False)
            live_route = [(self.market.pool, int(price_limit), 0)]

            params = (
                input_token,
                int(quantity_raw),
                output_token,
                int(min_output),
                [(r[0], r[1], r[2]) for r in live_route],
                int((time.time() + self.deadline_sec) * 1e9),
            )

            # Build and send tx
            tx = self.router.functions.swapExactIn(params).build_transaction(self._build_base_tx())
            # For native input, attach msg.value
            if input_token == NATIVE_TOKEN:
                tx["value"] = int(quantity_raw)
            try:
                tx["gas"] = self.web3.eth.estimate_gas(tx)
            except Exception as exc:
                logger.warning(f"estimate_gas reverted during router swapExactIn: {exc}")
                tx["gas"] = int(self.cfg.get("fallback_gas", 300000))
            tx_hash = self._sign_and_send(tx)
            return tx_hash

        # Buy (is_bid=True): want exact base output -> use quoteExactOut + swapExactOut
        input_token = self.market.quote if not self.market.quote_is_native else NATIVE_TOKEN
        output_token = self.market.base
        try:
            q = self.router.functions.quoteExactOut(route, input_token, output_token, int(quantity_raw)).call()
        except Exception as exc:
            logger.warning(f"router quoteExactOut failed: {exc}")
            raise
        ok = q[0]
        amount_in = int(q[1])
        if not ok and amount_in == 0:
            raise RuntimeError("Router quoteExactOut indicates no liquidity for this buy size")

        # max input allowed with slippage cushion
        max_input = (amount_in * (10_000 + self.slippage_bps)) // 10_000
        # Align live route: set quantity to desired exact output (lot-aligned)
        qty = self._align_to_lot(int(quantity_raw))
        worst = int(q[3][0][3]) if q[3] and len(q[3]) > 0 and len(q[3][0]) > 3 else 0
        price_limit = self._tick_align_away(int(worst * (10_000 + self.slippage_bps) // 10_000), True)
        live_route = [(self.market.pool, int(price_limit), int(qty))]

        params = (
            input_token,
            int(max_input),
            output_token,
            int(qty),
            [(r[0], r[1], r[2]) for r in live_route],
            int((time.time() + self.deadline_sec) * 1e9),
        )

        tx = self.router.functions.swapExactOut(params).build_transaction(self._build_base_tx())
        # Native input must set msg.value
        if input_token == NATIVE_TOKEN:
            tx["value"] = int(max_input)
        try:
            tx["gas"] = self.web3.eth.estimate_gas(tx)
        except Exception as exc:
            logger.warning(f"estimate_gas reverted during router swapExactOut: {exc}")
            tx["gas"] = int(self.cfg.get("fallback_gas", 300000))
        tx_hash = self._sign_and_send(tx)
        return tx_hash

    def _submit_order(self, is_bid: bool, quantity_raw: int, price_raw: int) -> str:
        expire_timestamp_ns = int((time.time() + self.deadline_sec) * 1e9)
        # orderType: 0=GTC, 1=PostOnly, 2=IOC, 3=FOK
        # Select order type. Default IOC for taker orders so triggered
        # sells don't revert; when bulk_mode enabled we may prefer FOK
        # to avoid partial fills and reduce tx churn.
        order_type = 2
        if self.bulk_mode and self.use_fok_for_bulk:
            order_type = 3
        # Prevent web3 from auto-calling estimate_gas during build_transaction by
        # passing a conservative gas limit first, then attempt an explicit estimate.
        # Prefill a conservative gas in base tx so build_transaction does not
        # call estimate_gas (which can revert when simulating failing txn).
        base_tx = self._build_base_tx()
        base_tx["gas"] = int(self.cfg.get("fallback_gas", 300000))

        if self.use_router:
            return self._swap_via_router(is_bid, quantity_raw)

        tx = self.pool.functions.placeTakerOrderWithoutVault(
            is_bid,
            0,
            int(price_raw),
            int(quantity_raw),
            int(expire_timestamp_ns),
            order_type,
            0,
            self.builder,
            self.builder_fee_bps_times1k,
        ).build_transaction(base_tx)

        tx["value"] = self._order_value(is_bid, quantity_raw)

        # Try a fresh estimate now that build_transaction won't trigger it.
        try:
            estimated = self.web3.eth.estimate_gas(tx)
            tx["gas"] = int(estimated)
        except Exception as exc:
            logger.warning(f"estimate_gas reverted: {exc}")
            # Log contextual info to help debug sell-side reverts
            try:
                native_bal = self.web3.eth.get_balance(self.address)
            except Exception:
                native_bal = None
            try:
                base_bal = self._token_balance(self.market.base)
            except Exception:
                base_bal = None
            try:
                quote_bal = self._token_balance(self.market.quote)
            except Exception:
                quote_bal = None
            logger.debug(
                f"estimate_gas context: is_bid={is_bid} qty={quantity_raw} price={price_raw} "
                f"native_bal={native_bal} base_bal={base_bal} quote_bal={quote_bal}"
            )
            # Keep the prefilled fallback gas
        tx_hash = self._sign_and_send(tx)
        return tx_hash

    def _save_metrics(self) -> None:
        with open(self.metrics_path, "w", encoding="utf-8") as handle:
            json.dump(self.metrics, handle)

    def _save_state(self, last_tx: str) -> None:
        state = {
            "wallet": self.address,
            "market": self.market.symbol,
            "pool": self.market.pool,
            "last_tx": last_tx,
            "updated_at": int(time.time()),
        }
        with open(self.state_path, "w", encoding="utf-8") as handle:
            json.dump(state, handle)

    async def run(self) -> None:
        logger.info(f"Connected wallet: {self.address}")
        logger.info(f"Market: {self.market.symbol} | pool={self.market.pool}")
        logger.info(f"Chain ID: {self.cfg.get('chain_id', 5031)}")
        logger.info(f"Base token: {self.market.base} | Quote token: {self.market.quote}")

        approvals = self.ensure_allowances()
        for approval_tx in approvals:
            logger.info(f"Approval submitted: {approval_tx}")

        order_count = 0
        logger.info("Starting trading loop...")
        while True:
            if self.max_orders is not None and order_count >= int(self.max_orders):
                logger.info("Reached max_orders; stopping.")
                break

            best_bid, best_ask = self._best_prices()
            if best_bid is None or best_ask is None:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("No book depth yet; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            quantity_raw = self._random_quantity()
            is_bid = self._choose_side(quantity_raw, best_bid, best_ask)
            if is_bid is None:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("Insufficient wallet balance for either side; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            price_raw = self._price_for_order(is_bid, best_bid, best_ask)
            if not self._can_afford(is_bid, quantity_raw, price_raw):
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("Balance check failed after pricing; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            try:
                # Select order type for simulation. Default IOC; use FOK
                # for bulk-mode if configured.
                order_type = 2
                if self.bulk_mode and self.use_fok_for_bulk:
                    order_type = 3
                sim_result = self.pool.functions.placeTakerOrderWithoutVault(
                    is_bid,
                    0,
                    int(price_raw),
                    int(quantity_raw),
                    int((time.time() + self.deadline_sec) * 1e9),
                    order_type,
                    0,
                    self.builder,
                    self.builder_fee_bps_times1k,
                ).call({"from": self.address, "value": self._order_value(is_bid, quantity_raw)})

                if not sim_result[0]:
                    self.metrics["errors"] += 1
                    self._save_metrics()
                    logger.warning("Order simulation rejected; skipping this round.")
                    await asyncio.sleep(self.freq_sec)
                    continue

                tx_hash = self._submit_order(is_bid, quantity_raw, price_raw)
                receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt.status != 1:
                    raise RuntimeError(f"Order failed: {tx_hash}")

                self.metrics["orders"] += 1
                if is_bid:
                    self.metrics["volume_in_raw"] += self._quote_cost(quantity_raw, price_raw)
                    self.metrics["volume_out_raw"] += int(quantity_raw)
                else:
                    self.metrics["volume_in_raw"] += int(quantity_raw)
                    self.metrics["volume_out_raw"] += self._quote_cost(quantity_raw, price_raw)
                order_count += 1
                self._save_metrics()
                self._save_state(tx_hash)
                side = "buy" if is_bid else "sell"
                logger.info(f"order ok side={side} tx={tx_hash} qty={quantity_raw} price={price_raw}")
            except Exception as exc:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.error(f"order error: {exc}", exc_info=True)

            await asyncio.sleep(max(0.5, random.uniform(self.freq_sec * 0.8, self.freq_sec * 1.2)))
