from src.metrics import calculate, relative_metrics
from src.models import ProtocolSnapshot, Signal, SourceRecord
from src.report import render


def test_report_handles_missing_data():
    items = {
        "Hyperliquid": ProtocolSnapshot("Hyperliquid", volume_24h=100, open_interest=50),
        "Aster": ProtocolSnapshot("Aster", unavailable={"volume_7d": "Insufficient historical data."}),
    }
    for item in items.values():
        calculate(item)
    output = render(items, relative_metrics(items), [Signal("watch", "Both", "Test", "Interpretation", "Evidence")])
    assert "# PerpScope Daily" in output
    assert "N/A" in output
    assert "Insufficient historical data" in output
    assert "financial advice" in output


def test_parent_holder_revenue_is_not_presented_as_perp_revenue():
    source = SourceRecord("DefiLlama", "endpoint", "2026-01-01T00:00:00+00:00",
                          scope="parent_protocol", dataset="aster")
    items = {"Hyperliquid": ProtocolSnapshot("Hyperliquid"),
             "Aster": ProtocolSnapshot("Aster", holder_revenue_24h=100,
                                       sources={"holder_revenue_24h": source})}
    output = render(items, relative_metrics(items), [Signal("watch", "Both", "Test", "I", "F")])
    assert "Parent/Token Holder Revenue (24h)" in output
    assert "Aster's available value is parent-protocol scope" in output
    assert "Perp 24h Revenue | N/A | N/A" in output


def test_holder_revenue_multiple_labels_follow_scope():
    timestamp = "2026-01-01T00:00:00+00:00"
    perps = SourceRecord("DefiLlama", "perps", timestamp, scope="perps_specific")
    parent = SourceRecord("DefiLlama", "parent", timestamp, scope="parent_protocol")
    items = {
        "Hyperliquid": ProtocolSnapshot("Hyperliquid", market_cap=1200, holder_revenue_30d=10,
            sources={"holder_revenue_30d": perps}),
        "Aster": ProtocolSnapshot("Aster", market_cap=1200, holder_revenue_30d=10,
            sources={"holder_revenue_30d": parent}),
    }
    for item in items.values():
        calculate(item)
    output = render(items, relative_metrics(items), [Signal("watch", "Both", "Test", "I", "F")])
    assert "Market Cap / 30D Perps-linked Holder Revenue Run-Rate is 10.00x" in output
    assert "Market Cap / 30D Parent/Token Holder Revenue Run-Rate is 10.00x" in output
    assert "should not be compared directly" in output
