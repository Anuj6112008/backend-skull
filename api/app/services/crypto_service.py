"""
Crypto ticker price service.

Abstracted behind get_crypto_prices() so swapping providers later doesn't
touch any router code. Currently:
  - Tries CoinGecko's free public endpoint (no API key required).
  - Falls back to static mock data if the request fails for any reason
    (network blocked, rate-limited, etc.) so the ticker never breaks.
"""

import os
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


def get_crypto_prices() -> List[CryptoPrice]:
    # If you have a paid provider key, branch on it here instead.
    if os.environ.get("CRYPTO_PROVIDER_API_KEY"):
        # Placeholder: wire up your paid provider call here and return early.
        pass

    try:
        return _fetch_from_coingecko()
    except Exception:
        return _MOCK_PRICES
