from datetime import datetime, timezone
from typing import Any

from src.data_sources.http import PublicAPIClient

BASE = "https://fapi.asterdex.com"
TICKER_ENDPOINT = f"{BASE}/fapi/v3/ticker/24hr"
EXCHANGE_INFO_ENDPOINT = f"{BASE}/fapi/v3/exchangeInfo"


def fetch(client: PublicAPIClient) -> tuple[dict[str, float], dict[str, Any]]:
    exchange_info = client.json("GET", EXCHANGE_INFO_ENDPOINT)
    tickers = client.json("GET", TICKER_ENDPOINT)
    if not isinstance(tickers, list):
        raise ValueError("Unexpected Aster ticker response")
    active = {
        item.get("symbol") for item in exchange_info.get("symbols", [])
        if item.get("status") == "TRADING" and not str(item.get("symbol", "")).startswith("TEST")
    }
    if not active:
        raise ValueError("Aster exchangeInfo returned no active non-TEST symbols")
    usable = [t for t in tickers if t.get("symbol") in active]
    volume = sum(float(t.get("quoteVolume") or 0) for t in usable)
    return {"volume_24h": volume}, {
        "exchange_info": exchange_info,
        "tickers": tickers,
        "included_symbols": len(usable),
        "methodology": "Sum of quoteVolume across active, non-TEST perpetual tickers.",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
