from src.models import ProtocolSnapshot
from src.signals import detect


def test_volume_outpaces_oi_signal():
    h = ProtocolSnapshot("Hyperliquid", changes={
        "volume_24h": {"7d": 50}, "open_interest": {"7d": 10},
        "revenue_24h": {"7d": 45}, "token_price": {"7d": 5},
    })
    a = ProtocolSnapshot("Aster")
    signals = detect({"Hyperliquid": h, "Aster": a}, {})
    assert any(s.title == "Activity is outpacing positioning" for s in signals)


def test_missing_data_yields_history_signal():
    items = {name: ProtocolSnapshot(name) for name in ("Hyperliquid", "Aster")}
    assert detect(items, {})[0].title == "History is still accumulating"


def test_relative_share_signals_use_historical_change():
    items = {name: ProtocolSnapshot(name) for name in ("Hyperliquid", "Aster")}
    relative = {"changes": {
        "aster_volume_share": {"1d": None, "7d": 4.0, "30d": None},
        "aster_oi_share": {"1d": 2.5, "7d": None, "30d": None},
    }}
    signals = detect(items, relative)
    assert any(s.title == "Aster is gaining pairwise volume share" for s in signals)
    assert any(s.title == "Aster is gaining pairwise OI share" for s in signals)


def test_price_comparison_is_metric_specific_not_max_based():
    h = ProtocolSnapshot("Hyperliquid", changes={
        "volume_24h": {"7d": 100}, "open_interest": {"7d": 0},
        "revenue_24h": {"7d": 0}, "token_price": {"7d": 60},
    })
    signals = detect({"Hyperliquid": h, "Aster": ProtocolSnapshot("Aster")}, {})
    assert any(s.title == "Price outpaces selected fundamentals" for s in signals)
    assert any(s.title == "Selected fundamentals outpace price" for s in signals)
    assert all("strongest measured fundamental" not in s.evidence for s in signals)
