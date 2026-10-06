from src.models import ProtocolSnapshot, Signal


def thesis_status(snapshot: ProtocolSnapshot) -> tuple[str, str]:
    available = [snapshot.volume_24h, snapshot.open_interest, snapshot.revenue_24h]
    if sum(value is not None for value in available) < 2:
        return "Insufficient Data", "Too few core operating metrics are available for a directional view."
    changes = [snapshot.changes.get(metric, {}).get("7d") for metric in
               ("volume_24h", "open_interest", "revenue_24h")]
    known = [value for value in changes if value is not None]
    if not known:
        return "Baseline Established", "A current operating baseline exists, but no comparable historical period is available yet."
    if len(known) < 2:
        return "Insufficient Trend Data", "Fewer than two comparable core operating trends are available; no directional status is assigned."
    if sum(v > 10 for v in known) >= 2:
        return "Improving", "At least two core fundamentals increased by more than 10% over the comparable period."
    if sum(v < -10 for v in known) >= 2:
        return "Weakening", "At least two core fundamentals declined by more than 10% over the comparable period."
    return "Stable", "The available core metrics do not show a broad directional move."


def executive_summary(snapshots: dict[str, ProtocolSnapshot], signals: list[Signal]) -> list[str]:
    lines = []
    h, a = snapshots["Hyperliquid"], snapshots["Aster"]
    for item in (h, a):
        known = sum(getattr(item, x) is not None for x in ("volume_24h", "open_interest", "tvl", "revenue_24h"))
        lines.append(f"{item.protocol}: {known}/4 core snapshot metrics are currently verified.")
    lines.extend(f"{s.protocol}: {s.interpretation}" for s in signals[:3])
    return lines[:6]
