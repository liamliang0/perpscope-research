from src.metrics import calculate, safe_ratio
from src.models import ProtocolSnapshot, SourceRecord


def test_safe_ratio_handles_missing_and_zero():
    assert safe_ratio(10, 2) == 5
    assert safe_ratio(None, 2) is None
    assert safe_ratio(10, 0) is None


def test_derived_metrics():
    item = ProtocolSnapshot("Test", volume_24h=1000, open_interest=500,
                            fees_24h=2, revenue_24h=1, revenue_30d=30,
                            market_cap=3600)
    source = SourceRecord("Test", "endpoint", "2026-01-01T00:00:00+00:00", scope="perps_specific")
    item.sources.update({"volume_24h": source, "fees_24h": source, "revenue_24h": source,
                         "revenue_30d": source})
    calculate(item)
    assert item.derived["volume_oi"] == 2
    assert item.derived["fees_volume"] == 0.002
    assert item.derived["market_cap_30d_revenue_run_rate"] == 10


def test_pairwise_share_requires_both_values():
    from src.metrics import relative_metrics

    items = {"Hyperliquid": ProtocolSnapshot("Hyperliquid", volume_24h=100, open_interest=50),
             "Aster": ProtocolSnapshot("Aster")}
    result = relative_metrics(items)
    assert result["hyperliquid_volume_share"] is None
    assert result["aster_volume_share"] is None
    assert result["hyperliquid_oi_share"] is None
    assert result["aster_oi_share"] is None

    items = {"Hyperliquid": ProtocolSnapshot("Hyperliquid"),
             "Aster": ProtocolSnapshot("Aster", volume_24h=100, open_interest=50)}
    result = relative_metrics(items)
    assert all(value is None for value in result.values())


def test_pairwise_share_with_both_valid_values():
    from src.metrics import relative_metrics

    items = {"Hyperliquid": ProtocolSnapshot("Hyperliquid", volume_24h=300, open_interest=75),
             "Aster": ProtocolSnapshot("Aster", volume_24h=100, open_interest=25)}
    result = relative_metrics(items)
    assert result["aster_volume_share"] == 0.25
    assert result["hyperliquid_oi_share"] == 0.75
