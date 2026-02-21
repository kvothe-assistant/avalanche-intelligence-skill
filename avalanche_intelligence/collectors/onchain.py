"""On-chain data collector using Avalanche RPC."""

import aiohttp
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from .base import BaseCollector


class OnchainCollector(BaseCollector):
    """Collector for Avalanche C-Chain on-chain data."""

    # Avalanche C-Chain RPC endpoints
    MAINNET_RPC = "https://api.avax.network/ext/bc/C/rpc"
    TESTNET_RPC = "https://api.avax-test.network/ext/bc/C/rpc"

    def __init__(self, config):
        super().__init__("onchain", config)
        self.rpc_url = config.rpc_url or self.MAINNET_RPC
        self.rate_limit_per_second = config.rate_limit_per_second
        self._last_call_time = 0

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect on-chain data for the past N hours.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of on-chain events with metadata
        """
        events = []

        # Get current block number
        latest_block = await self._get_latest_block()

        # Calculate starting block (approximate 2s per block)
        blocks_back = (hours * 3600) // 2
        start_block = max(0, latest_block - blocks_back)

        # Fetch blocks
        for block_num in range(start_block, latest_block + 1, 100):  # Batch of 100
            block_events = await self._fetch_block_range(block_num, min(block_num + 100, latest_block + 1))
            events.extend(block_events)

            # Rate limiting
            await asyncio.sleep(0.5)

        return events

    async def _get_latest_block(self) -> int:
        """Get latest block number.

        Returns:
            Latest block number
        """
        await self._rate_limit()

        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }

            async with session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        return int(data["result"], 16)

        return 0

    async def _fetch_block_range(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Fetch data from a range of blocks.

        Args:
            start: Starting block number
            end: Ending block number

        Returns:
            List of on-chain events
        """
        events = []

        for block_num in range(start, end):
            block_data = await self._get_block(block_num)

            if block_data:
                # Parse transactions
                for tx in block_data.get("transactions", []):
                    tx_event = self._parse_transaction(tx, block_data)
                    if tx_event:
                        events.append(tx_event)

        return events

    async def _get_block(self, block_num: int) -> Optional[Dict[str, Any]]:
        """Get block by number.

        Args:
            block_num: Block number

        Returns:
            Block data or None
        """
        await self._rate_limit()

        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_num), True],  # True = include transaction details
                "id": 1
            }

            async with session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        return data["result"]

        return None

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search on-chain data.

        Args:
            query: Search query (address, transaction hash, or contract)

        Returns:
            List of matching items
        """
        results = []

        # Check if query is an address (0x...)
        if query.startswith("0x") and len(query) == 42:
            address_data = await self._get_address_data(query)
            if address_data:
                results.append(address_data)

        # Check if query is a transaction hash
        elif query.startswith("0x") and len(query) == 66:
            tx_data = await self._get_transaction(query)
            if tx_data:
                results.append(tx_data)

        return results

    async def _get_address_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Get data for an address.

        Args:
            address: Ethereum-compatible address

        Returns:
            Address data or None
        """
        # Get balance
        balance = await self._get_balance(address)

        # Get transaction count
        tx_count = await self._get_transaction_count(address)

        return {
            "id": address,
            "source": "onchain",
            "content": f"Address: {address}\nBalance: {balance} AVAX\nTransactions: {tx_count}",
            "timestamp": datetime.now().isoformat(),
            "type": "address",
            "address": address,
            "balance": balance,
            "transaction_count": tx_count,
            "url": f"https://snowtrace.io/address/{address}",
            "collected_at": datetime.now().isoformat(),
        }

    async def _get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash.

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction data or None
        """
        await self._rate_limit()

        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionByHash",
                "params": [tx_hash],
                "id": 1
            }

            async with session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and data["result"]:
                        return self._parse_transaction(data["result"])

        return None

    async def _get_balance(self, address: str) -> str:
        """Get AVAX balance for address.

        Args:
            address: Address to query

        Returns:
            Balance as string (in AVAX)
        """
        await self._rate_limit()

        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }

            async with session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        # Convert wei to AVAX (1e18)
                        balance_wei = int(data["result"], 16)
                        balance_avax = Decimal(balance_wei) / Decimal(10**18)
                        return str(balance_avax)

        return "0"

    async def _get_transaction_count(self, address: str) -> int:
        """Get transaction count for address.

        Args:
            address: Address to query

        Returns:
            Transaction count
        """
        await self._rate_limit()

        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [address, "latest"],
                "id": 1
            }

            async with session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        return int(data["result"], 16)

        return 0

    async def _rate_limit(self):
        """Enforce rate limiting."""
        now = datetime.now().timestamp()

        if now - self._last_call_time < (1.0 / self.rate_limit_per_second):
            wait_time = (1.0 / self.rate_limit_per_second) - (now - self._last_call_time)
            await asyncio.sleep(wait_time)

        self._last_call_time = datetime.now().timestamp()

    def _parse_transaction(self, tx: Dict[str, Any], block: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Parse transaction into standardized format.

        Args:
            tx: Transaction object
            block: Block object (optional)

        Returns:
            Standardized transaction object or None
        """
        if not tx:
            return None

        # Convert hex values
        value = int(tx.get("value", "0x0"), 16)
        gas = int(tx.get("gas", "0x0"), 16)
        gas_price = int(tx.get("gasPrice", "0x0"), 16)
        gas_used = int(tx.get("gas", "0x0"), 16)  # Approximate

        # Calculate value in AVAX
        value_avax = Decimal(value) / Decimal(10**18)

        # Extract timestamp
        timestamp = None
        if block:
            timestamp_hex = block.get("timestamp")
            if timestamp_hex:
                timestamp = datetime.fromtimestamp(int(timestamp_hex, 16)).isoformat()

        # Extract input data (for contract calls)
        input_data = tx.get("input", "0x")
        method_sig = input_data[:10] if len(input_data) >= 10 else ""

        return {
            "id": tx.get("hash"),
            "source": "onchain",
            "content": self._extract_transaction_content(tx, value_avax),
            "timestamp": timestamp,
            "type": "transaction",
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": str(value_avax),
            "gas": gas,
            "gas_price": gas_price,
            "gas_used": gas_used,
            "gas_cost_avax": str(Decimal(gas * gas_price) / Decimal(10**18)),
            "input": method_sig,
            "entities": self._extract_transaction_entities(tx),
            "url": f"https://snowtrace.io/tx/{tx.get('hash')}",
            "collected_at": datetime.now().isoformat(),
        }

    def _extract_transaction_content(self, tx: Dict[str, Any], value_avax: Decimal) -> str:
        """Extract human-readable content from transaction.

        Args:
            tx: Transaction object
            value_avax: Transaction value in AVAX

        Returns:
            Content string
        """
        from_address = tx.get("from", "0x")[:10]
        to_address = tx.get("to", "0x")[:10] if tx.get("to") else "Contract Creation"

        if value_avax > 0:
            return f"Transfer {value_avax:.6f} AVAX from {from_address} to {to_address}"
        else:
            return f"Contract call from {from_address} to {to_address}"

    def _extract_transaction_entities(self, tx: Dict[str, Any]) -> List[str]:
        """Extract entities from transaction.

        Args:
            tx: Transaction object

        Returns:
            List of entity strings
        """
        entities = []

        # Addresses
        if tx.get("from"):
            entities.append(tx["from"][:10])
        if tx.get("to"):
            entities.append(tx["to"][:10])

        # Method signature (for contract calls)
        input_data = tx.get("input", "0x")
        if len(input_data) >= 10:
            method_sig = input_data[:10]
            entities.append(method_sig)

        return entities
