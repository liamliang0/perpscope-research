from src.models import ProtocolSnapshot, Signal


def _change(snapshot: ProtocolSnapshot, metric: str, period: str = "7d") -> float | None:
    return snapshot.changes.get(metric, {}).get(period)


def detect(snapshots: dict[str, ProtocolSnapshot], relative: dict[str, float | None]) -> list[Signal]:
    signals: list[Signal] = []
    for name, item in snapshots.items():
        volume, oi = _change(item, "volume_24h"), _change(item, "open_interest")
        revenue, price = _change(item, "revenue_24h"), _change(item, "token_price")
        if volume is not None and oi is not None and volume - oi >= 25 and volume >= 20:
            signals.append(Signal("watch", name, "Activity is outpacing positioning",
                "Trading activity is increasing faster than persistent positioning; growth quality should be monitored.",
                f"7D change: volume {volume:+.1f}% vs OI {oi:+.1f}%."))
        if volume is not None and revenue is not None and volume >= 20 and volume - revenue >= 20:
            signals.append(Signal("negative", name, "Monetization is lagging activity",
                "Activity growth is not translating proportionally into observable revenue.",
                f"7D change: volume {volume:+.1f}% vs revenue {revenue:+.1f}%."))
        if all(v is not None and v >= 10 for v in (volume, oi, revenue)):
            signals.append(Signal("positive", name, "Broad-based growth",
                "Volume, open interest, and revenue are rising together, indicating broader growth quality.",
                f"7D changes: volume {volume:+.1f}%, OI {oi:+.1f}%, revenue {revenue:+.1f}%."))
        fundamentals = {"volume": volume, "OI": oi, "revenue": revenue}
        known = {label: value for label, value in fundamentals.items() if value is not None}
        if price is not None and known:
            price_faster = {label: value for label, value in known.items() if price - value >= 25}
            fundamentals_faster = {label: value for label, value in known.items() if value - price >= 25}
            evidence = ", ".join(f"{label} {value:+.1f}%" for label, value in known.items())
            if price_faster:
                labels = ", ".join(price_faster)
                signals.append(Signal("watch", name, "Price outpaces selected fundamentals",
                    f"Price increased faster than {labels}; this is a metric-specific divergence, not a claim about all fundamentals.",
                    f"7D price {price:+.1f}%; {evidence}."))
            if fundamentals_faster:
                labels = ", ".join(fundamentals_faster)
                signals.append(Signal("positive", name, "Selected fundamentals outpace price",
                    f"{labels} increased faster than price; other operating metrics may differ.",
                    f"7D price {price:+.1f}%; {evidence}."))
    relative_changes = relative.get("changes", {}) if isinstance(relative, dict) else {}
    for metric, title, interpretation in (
        ("aster_volume_share", "Aster is gaining pairwise volume share",
         "Aster is gaining relative trading activity share against Hyperliquid."),
        ("aster_oi_share", "Aster is gaining pairwise OI share",
         "Aster is gaining relative open-interest share against Hyperliquid."),
    ):
        periods = relative_changes.get(metric, {})
        for period in ("1d", "7d", "30d"):
            delta = periods.get(period)
            if delta is not None and abs(delta) >= 2:
                direction = "gaining" if delta > 0 else "losing"
                level = "positive" if delta > 0 else "watch"
                signals.append(Signal(level, "Aster", title if delta > 0 else title.replace("gaining", "losing"),
                    interpretation if delta > 0 else interpretation.replace("gaining", "losing"),
                    f"Aster pairwise share changed {delta:+.1f} percentage points over {period}."))
                break
    if not signals:
        signals.append(Signal("watch", "Both", "History is still accumulating",
            "No change-based signal has enough local history to pass a rule threshold.",
            "PerpScope requires prior daily snapshots for comparable 1D/7D/30D changes."))
    return signals
