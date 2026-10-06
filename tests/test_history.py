from datetime import datetime, timedelta, timezone

from src.history import enrich_from_history, enrich_relative_history, percent_change
from src.models import ProtocolSnapshot


def test_percent_change_missing_and_values():
    assert percent_change(120, 100) == 20
    assert percent_change(10, None) is None
    assert percent_change(10, 0) is None


def test_history_change_and_insufficient_30d():
    now = datetime.now(timezone.utc)
    prior = ProtocolSnapshot("Aster", timestamp=(now - timedelta(days=7)).isoformat(), volume_24h=100)
    current = ProtocolSnapshot("Aster", timestamp=now.isoformat(), volume_24h=150)
    enrich_from_history(current, [prior])
    assert current.changes["volume_24h"]["7d"] == 50
    assert current.changes["volume_24h"]["30d"] is None
    assert current.volume_30d is None


def test_missing_calendar_day_prevents_7d_volume():
    now = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    # Seven observations exist, but October 7 is missing; October 1 is outside
    # the required October 2-8 consecutive window.
    days = [7, 6, 5, 4, 3, 2]
    history = [ProtocolSnapshot("Aster", timestamp=(now - timedelta(days=day)).isoformat(),
                                volume_24h=100) for day in days]
    current = ProtocolSnapshot("Aster", timestamp=now.isoformat(), volume_24h=100)
    enrich_from_history(current, history)
    assert current.volume_7d is None


def test_consecutive_calendar_days_produce_7d_volume():
    now = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    history = [ProtocolSnapshot("Aster", timestamp=(now - timedelta(days=day)).isoformat(),
                                volume_24h=100) for day in range(1, 7)]
    current = ProtocolSnapshot("Aster", timestamp=now.isoformat(), volume_24h=100)
    enrich_from_history(current, history)
    assert current.volume_7d == 700


def test_far_snapshot_is_not_used_for_7d_change():
    now = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    far = ProtocolSnapshot("Aster", timestamp=(now - timedelta(days=9)).isoformat(), volume_24h=100)
    current = ProtocolSnapshot("Aster", timestamp=now.isoformat(), volume_24h=150)
    enrich_from_history(current, [far])
    assert current.changes["volume_24h"]["7d"] is None


def test_relative_history_uses_same_target_tolerance():
    now = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    history = [{"generated_at": (now - timedelta(days=9)).isoformat(),
                "relative": {"aster_volume_share": 0.20, "aster_oi_share": 0.10}}]
    relative = {"aster_volume_share": 0.30, "aster_oi_share": 0.15}
    enrich_relative_history(relative, history, now)
    assert relative["changes"]["aster_volume_share"]["7d"] is None
