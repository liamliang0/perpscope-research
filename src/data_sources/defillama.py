from datetime import datetime, timezone
from typing import Any

from src.data_sources.http import PublicAPIClient

BASE = "https://api.llama.fi"
SLUGS = {"Hyperliquid": "hyperliquid", "Aster": "aster"}
PERPS_SLUGS = {"Hyperliquid": "hyperliquid-perps", "Aster": "aster-perps"}
OI_NAMES = {"Hyperliquid": "Hyperliquid Perps", "Aster": "Aster Perps"}


def _latest_tvl(raw: dict[str, Any]) -> float | None:
    points = raw.get("tvl") or []
    return float(points[-1]["totalLiquidityUSD"]) if points else None


def _summary(client: PublicAPIClient, slug: str, data_type: str) -> dict[str, Any]:
    return client.json("GET", f"{BASE}/summary/fees/{slug}", params={"dataType": data_type})


def fetch_protocol(client: PublicAPIClient, protocol: str) -> tuple[dict[str, float | None], dict[str, Any], dict[str, dict[str, str]]]:
    slug = SLUGS[protocol]
    perps_slug = PERPS_SLUGS[protocol]
    raw: dict[str, Any] = {}
    values: dict[str, float | None] = {}
    metadata: dict[str, dict[str, str]] = {}
    protocol_raw = client.json("GET", f"{BASE}/protocol/{slug}")
    raw["protocol"] = protocol_raw
    values["tvl"] = _latest_tvl(protocol_raw)
    metadata["tvl"] = {"endpoint": f"{BASE}/protocol/{slug}", "scope": "parent_protocol",
                       "dataset": slug, "methodology": "Latest parent-protocol TVL reported by DefiLlama."}
    for label, data_type, prefix in (
        ("fees", "dailyFees", "fees"),
        ("revenue", "dailyRevenue", "revenue"),
        ("holder_revenue", "dailyHoldersRevenue", "holder_revenue"),
    ):
        try:
            item = _summary(client, perps_slug, data_type)
            raw[label] = item
            for window, key in (("24h", "total24h"), ("7d", "total7d"), ("30d", "total30d")):
                field = f"{prefix}_{window}"
                values[field] = item.get(key)
                metadata[field] = {"endpoint": f"{BASE}/summary/fees/{perps_slug}?dataType={data_type}",
                    "scope": "perps_specific", "dataset": perps_slug,
                    "methodology": f"DefiLlama {data_type} for the standalone {perps_slug} dataset."}
        except Exception as exc:  # each dataset is independently optional
            raw[f"{label}_error"] = str(exc)
    # Aster exposes holder economics only at combined parent level. Preserve it,
    # but metadata prevents its use in perps operating ratios.
    if values.get("holder_revenue_24h") is None:
        try:
            item = _summary(client, slug, "dailyHoldersRevenue")
            raw["parent_holder_revenue"] = item
            for window, key in (("24h", "total24h"), ("7d", "total7d"), ("30d", "total30d")):
                field = f"holder_revenue_{window}"
                values[field] = item.get(key)
                metadata[field] = {"endpoint": f"{BASE}/summary/fees/{slug}?dataType=dailyHoldersRevenue",
                    "scope": "parent_protocol", "dataset": slug,
                    "methodology": "Combined parent-protocol holder revenue; may include perps and non-perps products."}
        except Exception as exc:
            raw["parent_holder_revenue_error"] = str(exc)
    raw["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return values, raw, metadata


def fetch_open_interest(client: PublicAPIClient) -> tuple[dict[str, float | None], dict[str, Any]]:
    endpoint = f"{BASE}/overview/open-interest"
    raw = client.json("GET", endpoint, params={
        "excludeTotalDataChart": "true",
        "excludeTotalDataChartBreakdown": "true",
    })
    records = {item.get("name"): item for item in raw.get("protocols", [])}
    values = {
        protocol: records.get(name, {}).get("total24h")
        for protocol, name in OI_NAMES.items()
    }
    return values, {"data": raw, "fetched_at": datetime.now(timezone.utc).isoformat()}
