import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.models import ProtocolSnapshot


def load_history(directory: Path) -> list[dict]:
    records: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            records.append(data)
        except (OSError, ValueError):
            continue
    return records


def snapshots_for(history: list[dict], protocol: str) -> list[ProtocolSnapshot]:
    found: list[ProtocolSnapshot] = []
    for run in history:
        item = run.get("protocols", {}).get(protocol)
        if item:
            found.append(ProtocolSnapshot.from_dict(item))
    return sorted(found, key=lambda x: x.timestamp)


def percent_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous * 100


HISTORY_TOLERANCE_HOURS = 6


def closest_at_days(items: list[ProtocolSnapshot], days: int,
                    now: datetime) -> ProtocolSnapshot | None:
    """Return a snapshot near the target age, never an arbitrarily older point."""
    eligible = []
    for item in items:
        timestamp = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
        age = (now - timestamp).total_seconds() / 86400
        if abs(age - days) <= HISTORY_TOLERANCE_HOURS / 24:
            eligible.append((abs(age - days), item))
    return min(eligible, key=lambda pair: pair[0])[1] if eligible else None


def enrich_from_history(snapshot: ProtocolSnapshot, items: list[ProtocolSnapshot]) -> None:
    now = datetime.fromisoformat(snapshot.timestamp.replace("Z", "+00:00"))
    for days, label in ((1, "1d"), (7, "7d"), (30, "30d")):
        prior = closest_at_days(items, days, now)
        for metric in ("volume_24h", "open_interest", "tvl", "fees_24h", "revenue_24h", "token_price"):
            snapshot.changes.setdefault(metric, {})[label] = percent_change(
                getattr(snapshot, metric), getattr(prior, metric) if prior else None
            )
    # Sum one daily rolling-volume observation per UTC date only when coverage is complete.
    by_date = {}
    for item in [*items, snapshot]:
        timestamp = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
        by_date[timestamp.astimezone(timezone.utc).date()] = item
    current_date = now.astimezone(timezone.utc).date()
    for days, field in ((7, "volume_7d"), (30, "volume_30d")):
        required_dates = [current_date - timedelta(days=offset) for offset in range(days)]
        recent = [by_date.get(date) for date in required_dates]
        if all(item is not None and item.volume_24h is not None for item in recent):
            setattr(snapshot, field, sum(item.volume_24h for item in recent if item is not None))


def enrich_relative_history(relative: dict, history: list[dict], now: datetime) -> None:
    relative["changes"] = {}
    for metric in ("aster_volume_share", "aster_oi_share"):
        relative["changes"][metric] = {}
        for days, label in ((1, "1d"), (7, "7d"), (30, "30d")):
            candidates = []
            for run in history:
                value = run.get("relative", {}).get(metric)
                timestamp_raw = run.get("generated_at")
                if value is None or not timestamp_raw:
                    continue
                timestamp = datetime.fromisoformat(timestamp_raw.replace("Z", "+00:00"))
                age = (now - timestamp).total_seconds() / 86400
                if abs(age - days) <= HISTORY_TOLERANCE_HOURS / 24:
                    candidates.append((abs(age - days), value))
            prior = min(candidates, key=lambda pair: pair[0])[1] if candidates else None
            current = relative.get(metric)
            # Store percentage-point change, which is easier to interpret for share.
            relative["changes"][metric][label] = (
                (current - prior) * 100 if current is not None and prior is not None else None
            )


def save_history(directory: Path, snapshots: dict[str, ProtocolSnapshot], relative: dict | None = None) -> Path:
    date = datetime.now(timezone.utc).date().isoformat()
    path = directory / f"{date}.json"
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(),
               "protocols": {name: item.to_dict() for name, item in snapshots.items()},
               "relative": relative or {}}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
