import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.exceptions import ContractCustomError

logger = logging.getLogger(__name__)


NATIVE_TOKEN = Web3.to_checksum_address("0x28f34DeFd2b4CB48d9eE6d89f2Be4Bc601694c00")
ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

# On-chain OrderType enum (wallet taker: IOC or FOK only)
ORDER_FOK = 1
ORDER_IOC = 2


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
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
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
    base_code: str
    quote_code: str
    base_decimals: int
    quote_decimals: int
    taker_fee_bps_times1k: int
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
        self.volume_mode = bool(cfg.get("volume_mode", False))
        self.bulk_mode = bool(cfg.get("bulk_mode", False))
        self.bulk_multiplier = int(cfg.get("bulk_multiplier", 5))
        self.use_fok_for_bulk = bool(cfg.get("use_fok_for_bulk", False))
        self.trade_fraction = float(cfg.get("trade_fraction", 0.90))
        self.reserve_quote_fraction = float(cfg.get("reserve_quote_fraction", 0.05))
        self.reserve_native_wei = int(cfg.get("reserve_native_wei", 50_000_000_000_000_000))
        self.volume_target_quote_raw = cfg.get("volume_target_quote_raw")
        self.freq_sec = float(cfg.get("freq_sec", 18 if self.volume_mode else 10))
        self.min_loop_sec = float(cfg.get("min_loop_sec", 3 if self.volume_mode else self.freq_sec))
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
        self._api_token: Optional[str] = None
        self._api_token_expires_at_ms: int = 0

        self.metrics = {"orders": 0, "volume_in_raw": 0, "volume_out_raw": 0, "errors": 0}
        self._load_metrics()
        self.market = self._load_market()
        self.pool = self.web3.eth.contract(address=self.market.pool, abi=POOL_ABI)
        if cfg.get("use_router"):
            raise RuntimeError("Router flow is disabled; this bot uses direct pool taker orders only")
        self.base_token_contract = None if self.market.base_is_native else self.web3.eth.contract(
            address=self.market.base, abi=ERC20_ABI
        )
        self.quote_token_contract = None if self.market.quote_is_native else self.web3.eth.contract(
            address=self.market.quote, abi=ERC20_ABI
        )

        native_balance = self.web3.eth.get_balance(self.address)
        if self.market.base_is_native and native_balance == 0:
            raise RuntimeError(f"Wallet {self.address} has zero native balance; cannot trade native market")
        if native_balance < self.reserve_native_wei:
            logger.warning(
                f"Low native (gas) balance: {native_balance} wei "
                f"(reserve {self.reserve_native_wei})"
            )

        mode = "volume" if self.volume_mode else "standard"
        logger.info(
            f"Bot initialized: wallet={self.address}, market={self.market.symbol}, mode={mode}"
        )

    def _fetch_json(self, path: str) -> Dict[str, Any]:
        url = f"{self.market_data_base.rstrip('/')}{path}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def _api_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, auth: bool = True) -> Any:
        url = f"{self.market_data_base.rstrip('/')}{path}"
        headers = {"Accept": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self._get_api_token()}"
        if body is not None:
            headers["Content-Type"] = "application/json"

        response = requests.request(method, url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        if not response.content:
            return None
        return response.json()

    def _get_api_token(self) -> str:
        now_ms = int(time.time() * 1000)
        if self._api_token and self._api_token_expires_at_ms > now_ms + 60_000:
            return self._api_token

        nonce_response = self._api_request("GET", "/v0/auth/nonce", auth=False)
        nonce = nonce_response["nonce"]
        issued_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        message = (
            f"api.dreamdex.io wants you to sign in with your Ethereum account:\n{self.address}\n\n"
            f"Sign in to dreamDEX\n\n"
            f"URI: https://api.dreamdex.io\n"
            f"Version: 1\n"
            f"Chain ID: {int(self.cfg.get('chain_id', 5031))}\n"
            f"Nonce: {nonce}\n"
            f"Issued At: {issued_at}"
        )
        signature = self.account.sign_message(encode_defunct(text=message)).signature.hex()
        login_response = self._api_request(
            "POST",
            "/v0/auth/login",
            body={"message": message, "signature": f"0x{signature}"},
            auth=False,
        )
        self._api_token = login_response["token"]
        self._api_token_expires_at_ms = int(login_response.get("expiresAt", 0))
        return self._api_token

    def _decimal_string(self, raw_value: int, decimals: int) -> str:
        value = Decimal(raw_value) / (Decimal(10) ** decimals)
        normalized = format(value, "f")
        return normalized.rstrip("0").rstrip(".") if "." in normalized else normalized

    def _prepared_tx_to_web3_tx(self, prepared: Dict[str, Any]) -> Dict[str, Any]:
        tx = self._build_base_tx()
        tx["to"] = Web3.to_checksum_address(prepared["to"])
        tx["data"] = prepared["data"]
        tx["value"] = int(prepared.get("value", "0"))
        tx["chainId"] = int(prepared["chainId"])
        gas_limit = prepared.get("gasLimit")
        if gas_limit is not None:
            tx["gas"] = int(gas_limit)
        self._apply_gas_estimate(tx)
        return tx

    def _apply_gas_estimate(self, tx: Dict[str, Any]) -> None:
        estimate_fields = {
            "from": tx["from"],
            "to": tx["to"],
            "data": tx.get("data", "0x"),
            "value": tx.get("value", 0),
        }
        try:
            estimated = int(self.web3.eth.estimate_gas(estimate_fields))
            tx["gas"] = max(int(tx.get("gas", 0)), int(estimated * 1.2))
        except Exception as exc:
            logger.warning(f"Gas estimate failed, using fallback: {exc}")
            tx["gas"] = int(self.cfg.get("fallback_gas", 2_000_000))

    def _broadcast_prepared_tx(self, prepared: Dict[str, Any]) -> str:
        tx = self._prepared_tx_to_web3_tx(prepared)
        tx_hash = self._sign_and_send(tx)
        return tx_hash

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
        taker_fee_bps_times1k = int(params[3])
        currency_codes: Dict[str, str] = {}
        for currency in self._fetch_json("/v0/currencies").get("currencies", []):
            currency_id = currency.get("id")
            currency_code = currency.get("code")
            if currency_id and currency_code:
                currency_codes[Web3.to_checksum_address(currency_id)] = str(currency_code)

        base_code = currency_codes.get(base_token, market.get("baseCode") or market.get("baseCurrency") or "")
        quote_code = currency_codes.get(quote_token, market.get("quoteCode") or market.get("quoteCurrency") or "")

        return Market(
            symbol=market["symbol"],
            pool=pool,
            base=base_token,
            quote=quote_token,
            base_code=str(base_code),
            quote_code=str(quote_code),
            base_decimals=int(market["baseDecimals"]),
            quote_decimals=int(market["quoteDecimals"]),
            taker_fee_bps_times1k=taker_fee_bps_times1k,
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
        tx["gas"] = int(self.cfg.get("fallback_gas", 2_000_000))
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

    def _token_decimals(self, token: str) -> int:
        checksum_token = Web3.to_checksum_address(token)
        if checksum_token == self.market.base:
            return int(self.market.base_decimals)
        if checksum_token == self.market.quote:
            return int(self.market.quote_decimals)
        contract = self.web3.eth.contract(address=checksum_token, abi=ERC20_ABI)
        return int(contract.functions.decimals().call())

    def _approval_amount(self, is_bid: bool, quantity_raw: int, price_raw: int) -> int:
        if is_bid:
            principal = self._quote_cost(quantity_raw, price_raw)
        else:
            principal = int(quantity_raw)

        fee_overhead = (principal * int(self.market.taker_fee_bps_times1k) + 999_999) // 1_000_000
        return principal + fee_overhead

    def _currency_code_for_token(self, token: str) -> str:
        checksum = Web3.to_checksum_address(token)
        if checksum == self.market.base:
            return self.market.base_code or "BASE"
        if checksum == self.market.quote:
            return self.market.quote_code or "QUOTE"
        raise ValueError(f"Unknown token for market: {token}")

    def _approve_via_api(self, token: str, amount_needed: int) -> Optional[str]:
        decimals = self._token_decimals(token)
        if amount_needed >= 10 ** (decimals + 12):
            amount_human = "1000000"
        else:
            amount_human = self._decimal_string(amount_needed, decimals)
        body = {
            "walletAddress": self.address,
            "currency": self._currency_code_for_token(token),
            "amount": amount_human,
        }
        prepared = self._api_request(
            "POST",
            f"/v0/markets/{self.market.symbol}/vault/approve",
            body=body,
        )
        if prepared is None:
            return None
        tx_hash = self._broadcast_prepared_tx(prepared)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise RuntimeError(f"API approve failed: {tx_hash}")
        return tx_hash

    def _approve_token(self, token: str, amount_needed: int) -> Optional[str]:
        if token == self.native_token:
            return None

        contract = self.web3.eth.contract(address=token, abi=ERC20_ABI)
        allowance = int(contract.functions.allowance(self.address, self.market.pool).call())
        if allowance >= amount_needed:
            return None

        try:
            if allowance > 0:
                zero_tx = contract.functions.approve(self.market.pool, 0).build_transaction(
                    self._build_base_tx()
                )
                zero_tx["gas"] = self.web3.eth.estimate_gas(zero_tx)
                zero_hash = self._sign_and_send(zero_tx)
                self.web3.eth.wait_for_transaction_receipt(zero_hash)

            tx = contract.functions.approve(self.market.pool, amount_needed).build_transaction(
                self._build_base_tx()
            )
            tx["gas"] = self.web3.eth.estimate_gas(tx)
            tx_hash = self._sign_and_send(tx)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                return tx_hash
        except Exception as exc:
            logger.warning(f"Direct approve failed for {token}: {exc}")

        return self._approve_via_api(token, amount_needed)

    def _ensure_order_allowance(self, is_bid: bool, quantity_raw: int, price_raw: int) -> Optional[str]:
        token = self.market.quote if is_bid else self.market.base
        if token == self.native_token:
            return None
        amount_needed = self._approval_amount(is_bid, quantity_raw, price_raw)
        contract = self.web3.eth.contract(address=token, abi=ERC20_ABI)
        allowance = int(contract.functions.allowance(self.address, self.market.pool).call())
        if allowance >= amount_needed:
            return None
        return self._approve_token(token, amount_needed)

    def _load_metrics(self) -> None:
        try:
            with open(self.metrics_path, "r", encoding="utf-8") as handle:
                saved = json.load(handle)
            for key in self.metrics:
                if key in saved:
                    self.metrics[key] = saved[key]
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Could not load metrics from {self.metrics_path}: {exc}")

    def _order_type_on_chain(self) -> int:
        if self.volume_mode:
            return ORDER_IOC
        if self.bulk_mode and self.use_fok_for_bulk:
            return ORDER_FOK
        return ORDER_IOC

    def _order_type_for_api(self) -> str:
        if self._order_type_on_chain() == ORDER_FOK:
            return "fillOrKill"
        return "immediateOrCancel"

    def _spendable_quote_balance(self) -> int:
        balance = self._token_balance(self.market.quote)
        if not self.volume_mode:
            return balance
        reserve = int(balance * self.reserve_quote_fraction)
        spendable = max(0, balance - reserve)
        return int(spendable * self.trade_fraction)

    def _spendable_base_balance(self) -> int:
        balance = self._token_balance(self.market.base)
        if not self.volume_mode:
            return balance
        if self.market.base_is_native:
            balance = max(0, balance - self.reserve_native_wei)
        return int(balance * self.trade_fraction)

    def _cumulative_volume_quote_raw(self) -> int:
        return int(self.metrics["volume_in_raw"]) + int(self.metrics["volume_out_raw"])

    def _ensure_startup_allowances(self) -> None:
        # Approve both sides up front so the first sell after a buy does not fail simulation.
        for token in (self.market.quote, self.market.base):
            if token == self.native_token:
                continue
            try:
                tx_hash = self._approve_token(token, self.max_approval)
                if tx_hash:
                    logger.info(f"Startup approval for {token}: {tx_hash}")
                else:
                    logger.info(f"Startup approval already sufficient for {token}")
            except Exception as exc:
                logger.warning(f"Startup approval skipped for {token}: {exc}")

    def _preflight_checks(self) -> None:
        best_bid, best_ask = self._best_prices()
        quote_bal = self._token_balance(self.market.quote)
        base_bal = self._token_balance(self.market.base)
        native_bal = self.web3.eth.get_balance(self.address)
        logger.info(
            f"Preflight: bid={best_bid} ask={best_ask} "
            f"quote_bal={quote_bal} base_bal={base_bal} native={native_bal}"
        )
        if best_bid is None or best_ask is None:
            logger.warning("Preflight: order book has no depth yet")
        spendable_quote = self._spendable_quote_balance()
        buy_price = self._price_for_order(True, best_bid or 0, best_ask or 1)
        max_buy_qty = self._buy_quantity_from_balance(spendable_quote, buy_price)
        logger.info(
            f"Preflight: spendable_quote={spendable_quote} max_buy_qty={max_buy_qty} "
            f"min_qty={self.market.min_quantity}"
        )
        if max_buy_qty < self.market.min_quantity and self._spendable_base_balance() < self.market.min_quantity:
            logger.warning("Preflight: balances may be too small for min order size")

    def _align_to_lot(self, quantity_raw: int) -> int:
        lot = max(1, self.market.lot_size)
        aligned = (quantity_raw // lot) * lot
        if aligned == 0:
            aligned = lot
        return max(aligned, self.market.min_quantity)

    def _sell_quantity_from_balance(self, base_balance_raw: int) -> int:
        return self._align_to_lot(base_balance_raw)

    def _buy_quantity_from_balance(self, quote_balance_raw: int, price_raw: int) -> int:
        lot = max(1, self.market.lot_size)
        price_raw = max(1, int(price_raw))
        approx = int((Decimal(quote_balance_raw) * (Decimal(10) ** self.market.base_decimals)) / Decimal(price_raw))
        upper_steps = max(1, self._align_to_lot(max(approx, self.market.min_quantity)) // lot)
        low_steps = 0
        high_steps = upper_steps
        best_steps = 0

        while low_steps <= high_steps:
            mid_steps = (low_steps + high_steps) // 2
            quantity_raw = max(lot, mid_steps * lot)
            if quantity_raw < self.market.min_quantity:
                quantity_raw = self._align_to_lot(self.market.min_quantity)
            if self._quote_cost(quantity_raw, price_raw) <= quote_balance_raw:
                best_steps = mid_steps
                low_steps = mid_steps + 1
            else:
                high_steps = mid_steps - 1

        return max(best_steps * lot, 0)

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

    def _choose_side(self, best_bid: int, best_ask: int) -> Optional[bool]:
        buy_price = self._price_for_order(True, best_bid, best_ask)
        can_buy = (
            self._buy_quantity_from_balance(self._spendable_quote_balance(), buy_price)
            >= self.market.min_quantity
        )
        can_sell = (
            self._sell_quantity_from_balance(self._spendable_base_balance())
            >= self.market.min_quantity
        )

        logger.debug(f"Side decision: can_buy={can_buy}, can_sell={can_sell}, orders={self.metrics['orders']}")

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

    def _prepare_order(self, is_bid: bool, quantity_raw: int, price_raw: int) -> Dict[str, Any]:
        side = "buy" if is_bid else "sell"
        amount = self._decimal_string(quantity_raw, self.market.base_decimals)
        price = self._decimal_string(price_raw, self.market.quote_decimals)
        body = {
            "type": "limit",
            "side": side,
            "price": price,
            "amount": amount,
            "walletAddress": self.address,
            "fundingSource": "wallet",
            "orderType": self._order_type_for_api(),
        }
        return self._api_request("POST", f"/v0/markets/{self.market.symbol}/orders", body=body, auth=True)

    def _prepare_approval(self, approval: Dict[str, Any]) -> Optional[str]:
        token = approval.get("token")
        amount = approval.get("amount")
        if not token or not amount:
            return None

        token = Web3.to_checksum_address(token)
        if token == self.native_token:
            return None

        approval_amount_raw = int(Decimal(str(amount)) * (Decimal(10) ** self._token_decimals(token)))
        return self._approve_token(token, approval_amount_raw)

    def _submit_order(self, is_bid: bool, quantity_raw: int, price_raw: int) -> str:
        prepared_order = self._prepare_order(is_bid, quantity_raw, price_raw)
        approval = prepared_order.get("approval")
        if approval:
            approval_tx_hash = self._prepare_approval(approval)
            if approval_tx_hash:
                logger.info(f"Approval submitted: {approval_tx_hash}")

        return self._broadcast_prepared_tx(prepared_order)

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
        if self.volume_mode:
            logger.info(
                f"Volume mode: trade_fraction={self.trade_fraction} "
                f"freq_sec={self.freq_sec} order_type=IOC"
            )
            if self.volume_target_quote_raw is not None:
                logger.info(f"Volume target (quote raw): {self.volume_target_quote_raw}")

        self._preflight_checks()
        self._ensure_startup_allowances()

        order_count = 0
        logger.info(
            f"Starting trading loop (freq_sec={self.freq_sec}, min_loop_sec={self.min_loop_sec})..."
        )
        while True:
            loop_sleep = self.freq_sec
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

            is_bid = self._choose_side(best_bid, best_ask)
            if is_bid is None:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("Insufficient wallet balance for either side; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            price_raw = self._price_for_order(is_bid, best_bid, best_ask)
            if is_bid:
                quantity_raw = self._buy_quantity_from_balance(self._spendable_quote_balance(), price_raw)
            else:
                quantity_raw = self._sell_quantity_from_balance(self._spendable_base_balance())

            if quantity_raw < self.market.min_quantity:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("Computed trade size was below market minimum; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            if not self._can_afford(is_bid, quantity_raw, price_raw):
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.warning("Balance check failed after pricing; retrying later.")
                await asyncio.sleep(self.freq_sec)
                continue

            try:
                approval_tx = self._ensure_order_allowance(is_bid, quantity_raw, price_raw)
                if approval_tx:
                    logger.info(f"Allowance tx: {approval_tx}")

                order_type = self._order_type_on_chain()
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
                vol_quote = self._cumulative_volume_quote_raw() / (10 ** self.market.quote_decimals)
                logger.info(
                    f"order ok side={side} tx={tx_hash} qty={quantity_raw} price={price_raw} "
                    f"cumulative_volume_quote≈{vol_quote:.2f}"
                )
                if (
                    self.volume_target_quote_raw is not None
                    and self._cumulative_volume_quote_raw() >= int(self.volume_target_quote_raw)
                ):
                    logger.info("Volume target reached; stopping.")
                    break
                loop_sleep = self.min_loop_sec
            except Exception as exc:
                self.metrics["errors"] += 1
                self._save_metrics()
                logger.error(f"order error: {exc}", exc_info=True)
                if "Connection" in type(exc).__name__ or "Connection" in str(exc):
                    logger.warning("RPC connection issue; backing off 60s")
                    await asyncio.sleep(60)
                    continue
                loop_sleep = self.freq_sec

            await asyncio.sleep(max(0.5, random.uniform(loop_sleep * 0.85, loop_sleep * 1.15)))
