from datetime import datetime, timezone
from typing import Any

from src.models import ProtocolSnapshot, SourceRecord


def merge_values(snapshot: ProtocolSnapshot, values: dict[str, Any], source_name: str,
                 endpoint: str, note: str | None = None, overwrite: bool = True,
                 scope: str = "unknown", dataset: str | None = None,
                 methodology: str | None = None) -> None:
    fetched_at = datetime.now(timezone.utc).isoformat()
    for field_name, value in values.items():
        if not hasattr(snapshot, field_name) or value is None:
            continue
        if overwrite or getattr(snapshot, field_name) is None:
            setattr(snapshot, field_name, float(value))
            snapshot.sources[field_name] = SourceRecord(
                source_name, endpoint, fetched_at, scope=scope, dataset=dataset,
                methodology=methodology, note=note)


def mark_unavailable(snapshot: ProtocolSnapshot, fields: list[str], reason: str) -> None:
    for field_name in fields:
        if getattr(snapshot, field_name, None) is None:
            snapshot.unavailable[field_name] = reason
