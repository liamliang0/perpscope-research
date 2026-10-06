from src.models import ProtocolSnapshot


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def calculate(snapshot: ProtocolSnapshot) -> None:
    def aligned(numerator: str, denominator: str) -> bool:
        a, b = snapshot.sources.get(numerator), snapshot.sources.get(denominator)
        return bool(a and b and a.scope == b.scope == "perps_specific")

    annual_revenue = snapshot.revenue_30d * 12 if snapshot.revenue_30d is not None else None
    annual_holder = snapshot.holder_revenue_30d * 12 if snapshot.holder_revenue_30d is not None else None
    snapshot.derived.update({
        "volume_oi": safe_ratio(snapshot.volume_24h, snapshot.open_interest),
        "fees_volume": safe_ratio(snapshot.fees_24h, snapshot.volume_24h) if aligned("fees_24h", "volume_24h") else None,
        "revenue_volume": safe_ratio(snapshot.revenue_24h, snapshot.volume_24h) if aligned("revenue_24h", "volume_24h") else None,
        "market_cap_30d_revenue_run_rate": safe_ratio(snapshot.market_cap, annual_revenue),
        "market_cap_30d_holder_revenue_run_rate": safe_ratio(snapshot.market_cap, annual_holder),
    })


def relative_metrics(snapshots: dict[str, ProtocolSnapshot]) -> dict[str, float | None]:
    h, a = snapshots["Hyperliquid"], snapshots["Aster"]
    valid_volume = h.volume_24h is not None and a.volume_24h is not None and h.volume_24h >= 0 and a.volume_24h >= 0
    valid_oi = h.open_interest is not None and a.open_interest is not None and h.open_interest >= 0 and a.open_interest >= 0
    total_volume = (h.volume_24h + a.volume_24h) if valid_volume else None
    total_oi = (h.open_interest + a.open_interest) if valid_oi else None
    return {
        "hyperliquid_volume_share": safe_ratio(h.volume_24h, total_volume) if valid_volume else None,
        "aster_volume_share": safe_ratio(a.volume_24h, total_volume) if valid_volume else None,
        "hyperliquid_oi_share": safe_ratio(h.open_interest, total_oi) if valid_oi else None,
        "aster_oi_share": safe_ratio(a.open_interest, total_oi) if valid_oi else None,
    }
