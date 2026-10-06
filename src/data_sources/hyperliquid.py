from datetime import datetime, timezone
from typing import Any

from src.data_sources.http import PublicAPIClient

ENDPOINT = "https://api.hyperliquid.xyz/info"


def fetch(client: PublicAPIClient) -> tuple[dict[str, float], dict[str, Any]]:
    raw = client.json("POST", ENDPOINT, json={"type": "metaAndAssetCtxs"})
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("Unexpected Hyperliquid metaAndAssetCtxs response")
    meta, contexts = raw
    universe = meta.get("universe", [])
    if len(universe) != len(contexts):
        raise ValueError("Hyperliquid universe/context length mismatch")
    volume = 0.0
    oi = 0.0
    for asset, context in zip(universe, contexts):
        if asset.get("isDelisted"):
            continue
        volume += float(context.get("dayNtlVlm") or 0)
        oi += float(context.get("openInterest") or 0) * float(context.get("markPx") or 0)
    return {"volume_24h": volume, "official_open_interest": oi}, {
        "meta": meta,
        "contexts": contexts,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
