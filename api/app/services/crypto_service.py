"""
Crypto ticker price service.

Abstracted behind get_crypto_prices() so swapping providers later doesn't
touch any router code. Currently:
  - Tries CoinGecko's free public endpoint (no API key required).
  - Falls back to static mock data if the request fails for any reason
    (network blocked, rate-limited, etc.) so the ticker never breaks.
"""

import os
import time
import requests
from typing import List
from ..models import CryptoPrice

_COINGECKO_IDS = {
    "bitcoin": "BTC/USDT",
    "ethereum": "ETH/USDT",
    "solana": "SOL/USDT",
    "ripple": "XRP/USDT",
    "binancecoin": "BNB/USDT",
    "avalanche-2": "AVAX/USDT",
    "chainlink": "LINK/USDT",
}

_MOCK_PRICES: List[CryptoPrice] = [
    CryptoPrice(symbol="BTC/USDT", price="$111,250.00", change="+2.41%", isUp=True),
    CryptoPrice(symbol="ETH/USDT", price="$4,320.50", change="+1.82%", isUp=True),
    CryptoPrice(symbol="SOL/USDT", price="$210.80", change="+3.15%", isUp=True),
    CryptoPrice(symbol="XRP/USDT", price="$2.85", change="+1.42%", isUp=True),
    CryptoPrice(symbol="BNB/USDT", price="$720.10", change="-0.54%", isUp=False),
    CryptoPrice(symbol="AVAX/USDT", price="$42.30", change="+5.10%", isUp=True),
    CryptoPrice(symbol="LINK/USDT", price="$22.40", change="-1.12%", isUp=False),
]


def _fetch_from_coingecko() -> List[CryptoPrice]:
    ids = ",".join(_COINGECKO_IDS.keys())
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    )
    resp = requests.get(url, timeout=4)
    resp.raise_for_status()
    data = resp.json()

    results: List[CryptoPrice] = []
    for coin_id, symbol in _COINGECKO_IDS.items():
        coin_data = data.get(coin_id)
        if not coin_data:
            continue
        price = coin_data.get("usd")
        change = coin_data.get("usd_24h_change", 0) or 0
        is_up = change >= 0
        results.append(
            CryptoPrice(
                symbol=symbol,
                price=f"${price:,.2f}" if price is not None else "--",
                change=f"{'+' if is_up else ''}{change:.2f}%",
                isUp=is_up,
            )
        )
    if not results:
        raise ValueError("CoinGecko returned no usable price data")
    return results


# ---------------------------------------------------------------------------
# In-memory TTL cache (per serverless instance).
# CoinGecko's free API is rate-limited and adds up to ~4s of latency per call —
# caching for 30s means a warm instance answers instantly and stops hammering
# the upstream API. Failures are remembered briefly too, so an outage doesn't
# turn into a request storm against CoinGecko.
# ---------------------------------------------------------------------------
_PRICE_CACHE_TTL = 30.0    # seconds a successful fetch stays fresh
_ERROR_CACHE_TTL = 15.0    # seconds to remember an upstream failure (serve mock)
_cache: dict = {"data": None, "expires": 0.0}


def get_crypto_prices() -> List[CryptoPrice]:
    now = time.monotonic()
    if _cache["data"] is not None and now < _cache["expires"]:
        return _cache["data"]

    # If you have a paid provider key, branch on it here instead.
    if os.environ.get("CRYPTO_PROVIDER_API_KEY"):
        # Placeholder: wire up your paid provider call here and return early.
        pass

    try:
        data = _fetch_from_coingecko()
        _cache["data"] = data
        _cache["expires"] = now + _PRICE_CACHE_TTL
    except Exception:
        # Serve the mock but remember the failure briefly (don't hammer CoinGecko).
        data = _MOCK_PRICES
        _cache["data"] = data
        _cache["expires"] = now + _ERROR_CACHE_TTL
    return data
