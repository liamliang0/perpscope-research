from src.analysis.rules import thesis_status
from src.models import ProtocolSnapshot, SourceRecord


def test_insufficient_history_is_not_stable():
    item = ProtocolSnapshot("Aster", volume_24h=100, open_interest=50, revenue_24h=1)
    status, _ = thesis_status(item)
    assert status == "Baseline Established"
    assert status != "Stable"


def test_scope_metadata_round_trip():
    item = ProtocolSnapshot("Aster", sources={
        "holder_revenue_24h": SourceRecord(
            "DefiLlama", "https://example.test", "2026-01-01T00:00:00+00:00",
            scope="parent_protocol", dataset="aster", methodology="Combined parent dataset")
    })
    restored = ProtocolSnapshot.from_dict(item.to_dict())
    source = restored.sources["holder_revenue_24h"]
    assert source.provider == "DefiLlama"
    assert source.scope == "parent_protocol"
    assert source.dataset == "aster"
    assert source.methodology == "Combined parent dataset"
