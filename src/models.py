from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


MONEY_FIELDS = (
    "volume_24h", "volume_7d", "volume_30d", "open_interest", "tvl",
    "fees_24h", "fees_7d", "fees_30d", "revenue_24h", "revenue_7d",
    "revenue_30d", "holder_revenue_24h", "holder_revenue_7d", "holder_revenue_30d",
    "official_open_interest",
    "token_price", "market_cap", "fdv",
)


@dataclass
class SourceRecord:
    provider: str
    endpoint: str
    fetched_at: str
    scope: str = "unknown"
    dataset: str | None = None
    methodology: str | None = None
    status: str = "ok"
    note: str | None = None


@dataclass
class ProtocolSnapshot:
    protocol: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    volume_24h: float | None = None
    volume_7d: float | None = None
    volume_30d: float | None = None
    open_interest: float | None = None
    official_open_interest: float | None = None
    tvl: float | None = None
    fees_24h: float | None = None
    fees_7d: float | None = None
    fees_30d: float | None = None
    revenue_24h: float | None = None
    revenue_7d: float | None = None
    revenue_30d: float | None = None
    holder_revenue_24h: float | None = None
    holder_revenue_7d: float | None = None
    holder_revenue_30d: float | None = None
    token_price: float | None = None
    market_cap: float | None = None
    fdv: float | None = None
    changes: dict[str, dict[str, float | None]] = field(default_factory=dict)
    derived: dict[str, float | None] = field(default_factory=dict)
    sources: dict[str, SourceRecord] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unavailable: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        for name in MONEY_FIELDS:
            value = getattr(self, name)
            if value is not None and value < 0:
                self.warnings.append(f"Rejected negative {name}: {value}")
                setattr(self, name, None)
        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError:
            self.warnings.append("Invalid source timestamp; replaced with current UTC time.")
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.volume_24h and self.volume_24h > 1e14:
            self.warnings.append("24h volume exceeds $100T; verify the upstream source.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProtocolSnapshot":
        copy = dict(data)
        normalized = {}
        for key, value in copy.get("sources", {}).items():
            value = dict(value)
            if "source" in value and "provider" not in value:
                value["provider"] = value.pop("source")
            normalized[key] = SourceRecord(**value)
        copy["sources"] = normalized
        return cls(**copy)


@dataclass
class Signal:
    level: str
    protocol: str
    title: str
    interpretation: str
    evidence: str
