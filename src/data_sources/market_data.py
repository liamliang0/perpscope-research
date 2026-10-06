from datetime import datetime, timezone
from typing import Any

from src.data_sources.http import PublicAPIClient

ENDPOINT = "https://api.coingecko.com/api/v3/coins/markets"
IDS = {"Hyperliquid": "hyperliquid", "Aster": "aster-2"}


def fetch(client: PublicAPIClient) -> tuple[dict[str, dict[str, float | None]], Any]:
    raw = client.json("GET", ENDPOINT, params={
        "vs_currency": "usd",
        "ids": ",".join(IDS.values()),
        "price_change_percentage": "24h,7d,30d",
    })
    by_id = {item["id"]: item for item in raw}
    result: dict[str, dict[str, float | None]] = {}
    for protocol, coin_id in IDS.items():
        item = by_id.get(coin_id, {})
        result[protocol] = {
            "token_price": item.get("current_price"),
            "market_cap": item.get("market_cap"),
            "fdv": item.get("fully_diluted_valuation"),
            "price_change_1d": item.get("price_change_percentage_24h_in_currency"),
            "price_change_7d": item.get("price_change_percentage_7d_in_currency"),
            "price_change_30d": item.get("price_change_percentage_30d_in_currency"),
        }
    return result, {"data": raw, "fetched_at": datetime.now(timezone.utc).isoformat()}
