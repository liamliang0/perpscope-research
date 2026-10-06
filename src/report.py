from datetime import datetime
from pathlib import Path

from src.analysis.rules import executive_summary, thesis_status
from src.models import ProtocolSnapshot, Signal


def money(value: float | None) -> str:
    if value is None:
        return "N/A"
    absolute = abs(value)
    for divisor, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if absolute >= divisor:
            return f"${value / divisor:,.2f}{suffix}".replace(".00", "")
    return f"${value:,.2f}"


def pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.1f}%"


def ratio(value: float | None, percentage: bool = False) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.3f}%" if percentage else f"{value:.2f}x"


def _metric_note(item: ProtocolSnapshot, field: str) -> str:
    reason = item.unavailable.get(field)
    return f" ({reason})" if reason else ""


def _thesis(item: ProtocolSnapshot) -> str:
    status, reason = thesis_status(item)
    holder_source = item.sources.get("holder_revenue_30d")
    holder_scope = holder_source.scope if holder_source else "unknown"
    holder_label = {
        "perps_specific": "Market Cap / 30D Perps-linked Holder Revenue Run-Rate",
        "parent_protocol": "Market Cap / 30D Parent/Token Holder Revenue Run-Rate",
        "token_level": "Market Cap / 30D Token Holder Revenue Run-Rate",
    }.get(holder_scope, "Market Cap / 30D Holder Revenue Run-Rate (scope unavailable)")
    return f"""### Growth
**Fact:** Perp 24h volume is {money(item.volume_24h)}. 7d volume is {money(item.volume_7d)}{_metric_note(item, 'volume_7d')}; 30d volume is {money(item.volume_30d)}{_metric_note(item, 'volume_30d')}.

### Liquidity / OI
**Fact:** Standardized perp OI is {money(item.open_interest)}; Volume/OI is {ratio(item.derived.get('volume_oi'))}.

### Monetization
**Fact:** Perp 24h fees are {money(item.fees_24h)} and perp protocol revenue is {money(item.revenue_24h)}. Fees/Volume is {ratio(item.derived.get('fees_volume'), True)}.

### Token Value Capture
**Fact:** Market cap is {money(item.market_cap)}. Market Cap / 30D Revenue Run-Rate is {ratio(item.derived.get('market_cap_30d_revenue_run_rate'))}; {holder_label} is {ratio(item.derived.get('market_cap_30d_holder_revenue_run_rate'))}.

**Unknown:** A run-rate is not trailing-twelve-month revenue and does not establish durable token value capture.

### Competitive Position
Competitive share is limited to the two-protocol comparison in this report; it is not whole-market share.

### Growth Quality
**Interpretation:** Growth quality is stronger when volume, OI, and monetization move together. No trend claim is made without comparable history.

### Key Risks
API methodology changes, incentive-driven activity, incomplete value-capture disclosure, and limited retention/participant-quality data.

### Thesis Status: {status}
{reason}
"""


def render(snapshots: dict[str, ProtocolSnapshot], relative: dict[str, float | None],
           signals: list[Signal], llm_text: str | None = None) -> str:
    h, a = snapshots["Hyperliquid"], snapshots["Aster"]
    def scoped_value(item: ProtocolSnapshot, field: str, scope: str) -> float | None:
        source = item.sources.get(field)
        return getattr(item, field) if source and source.scope == scope else None

    perp_rows = [
        ("24h Volume", h.volume_24h, a.volume_24h), ("7d Volume", h.volume_7d, a.volume_7d),
        ("30d Volume", h.volume_30d, a.volume_30d), ("Standardized OI", h.open_interest, a.open_interest),
        ("Official API OI", h.official_open_interest, a.official_open_interest),
        ("Perp 24h Fees", h.fees_24h, a.fees_24h),
        ("Perp 24h Revenue", h.revenue_24h, a.revenue_24h),
    ]
    value_rows = [
        ("Parent-protocol TVL", h.tvl, a.tvl),
        ("Perps-linked Holder Revenue (24h)", scoped_value(h, "holder_revenue_24h", "perps_specific"),
         scoped_value(a, "holder_revenue_24h", "perps_specific")),
        ("Parent/Token Holder Revenue (24h)", scoped_value(h, "holder_revenue_24h", "parent_protocol"),
         scoped_value(a, "holder_revenue_24h", "parent_protocol")),
        ("Token Price", h.token_price, a.token_price), ("Market Cap", h.market_cap, a.market_cap),
        ("FDV", h.fdv, a.fdv),
    ]
    perp_table = "\n".join(f"| {label} | {money(hv)} | {money(av)} |" for label, hv, av in perp_rows)
    value_table = "\n".join(f"| {label} | {money(hv)} | {money(av)} |" for label, hv, av in value_rows)
    signal_icons = {"positive": "🟢 Positive", "watch": "🟡 Watch", "negative": "🔴 Negative"}
    signal_text = "\n".join(
        f"- **{signal_icons[s.level]} — {s.protocol}: {s.title}.** **Fact:** {s.evidence} **Interpretation:** {s.interpretation}"
        for s in signals
    )
    grouped_sources: dict[tuple[str, str, str, str, str], dict[str, list[str] | str]] = {}
    for item in snapshots.values():
        for field, source in item.sources.items():
            key = (source.provider, source.endpoint, source.scope,
                   source.dataset or "", source.methodology or "")
            group = grouped_sources.setdefault(key, {"fields": [], "fetched_at": source.fetched_at})
            group["fields"].append(f"{item.protocol}.{field}")
    source_lines = [
        f"- **{provider}** — scope: `{scope}`; dataset: `{dataset or 'N/A'}`; fetched {fetched_at}. "
        f"Used for: {', '.join(fields)}. Endpoint: `{endpoint}`. Method: {methodology or 'Not specified.'}"
        for (provider, endpoint, scope, dataset, methodology), group in grouped_sources.items()
        for fetched_at, fields in [(group["fetched_at"], group["fields"])]
    ]
    oi_quality_note = ""
    if h.official_open_interest is not None and h.open_interest not in (None, 0):
        difference = (h.official_open_interest / h.open_interest - 1) * 100
        if abs(difference) >= 10:
            oi_quality_note = (
                f"\n- Hyperliquid official OI differs from standardized OI by {difference:+.1f}%. "
                "The standardized figure is used only for pairwise share; the discrepancy is not silently reconciled."
            )
    unavailable = []
    for item in snapshots.values():
        for field, reason in sorted(item.unavailable.items()):
            unavailable.append(f"- **{item.protocol} / {field}:** {reason}")
    summary = "\n".join(f"- {line}" for line in executive_summary(snapshots, signals))
    llm_section = f"\n## Optional LLM Commentary\n\n{llm_text}\n" if llm_text else ""
    return f"""# PerpScope Daily

Date: {datetime.now().date().isoformat()}

> Research support only. This report does not provide financial advice. N/A means the metric was not reliably available; it is never silently estimated.

## Executive Summary

{summary}

## Perp Market Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
{perp_table}

7d/30d volume requires one official 24h-volume snapshot for every consecutive UTC calendar day in the window. Any missing day keeps the metric N/A.

## Token / Value Capture Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
{value_table}

Holder revenue is a value-capture metric, not a perp operating-margin metric. Aster's available value is parent-protocol scope and may include non-perp products.
Hyperliquid and Aster holder-revenue multiples have different scopes and should not be compared directly.

## Relative Position

- **Scope: Pairwise comparison between Hyperliquid and Aster—not global Perp DEX market share.**
- Hyperliquid has {pct(relative.get('hyperliquid_volume_share'))} of combined Hyperliquid+Aster 24h volume; Aster has {pct(relative.get('aster_volume_share'))}.
- Hyperliquid has {pct(relative.get('hyperliquid_oi_share'))} of combined measured OI; Aster has {pct(relative.get('aster_oi_share'))}.
- OI share uses the same standardized DefiLlama open-interest dataset for both protocols. Official Hyperliquid OI is shown only as a cross-check.

## Hyperliquid Thesis Update

{_thesis(h)}
## Aster Thesis Update

{_thesis(a)}
## Key Signals

{signal_text}

## Data Gaps

{chr(10).join(unavailable) if unavailable else '- No automatically detected field-level gaps.'}
- Aster D30 retention and cohort quality require user-level or first-party data.
- Incentive/subsidy expenditure is not reliably exposed by the selected APIs.
- Privacy/hidden-order adoption and whale/professional adoption require first-party or manual research.
- Binance/YZi distribution support is qualitative and requires manual research.
- Protocol TVL definitions are not perfectly comparable across architectures.

## Data Quality / Scope Notes

- DefiLlama's public derivatives-volume API currently returns HTTP 402. Pairwise volume uses official perps-only 24h notional/quote-volume fields with aligned product scope but provider-specific calculation.
- Perp fees/revenue use standalone `hyperliquid-perps` and `aster-perps` datasets, not parent-protocol fee totals.
- Aster Perps does not expose protocol revenue or holder revenue through the tested public summary endpoint; combined Aster holder revenue is labeled parent-protocol scope.
- Missing one side of a comparison makes both pairwise shares N/A; missing values are never treated as zero.
- Run-rate annualization assumes the recent 30D period repeats and is not equivalent to trailing twelve-month revenue.
{oi_quality_note}

## What To Watch Next

1. Whether Aster's official 24h volume and open interest rise together.
2. Whether fees and protocol revenue keep pace with activity for both protocols.
3. Whether Aster gains combined two-protocol volume and OI share.
4. Whether token-price changes diverge materially from observable fundamentals.
5. Retention, incentive cost, hidden-order usage, and professional-trader adoption from primary disclosures.
{llm_section}
## Sources

{chr(10).join(source_lines) if source_lines else '- No source completed successfully.'}

## Methodology Notes

- Hyperliquid's `metaAndAssetCtxs` request omits `dex`, so it covers only the default/first Hyperliquid perp dex. It does not automatically aggregate builder-deployed/HIP-3 perp dexes. Within that scope, 24h notional volume and official cross-check OI are summed across active assets; official OI is `openInterest × markPx`.
- Aster 24h volume is the sum of `quoteVolume` across official active, non-TEST perpetual tickers; active status is checked with `exchangeInfo`.
- Cross-protocol OI share uses DefiLlama's standardized dataset for both protocols.
- Perp fees and revenue use DefiLlama's standalone perps datasets. Parent TVL and parent-level value capture remain separately labeled.
- Missing values remain N/A. Signals require explicit thresholds in `src/signals.py`.
"""


def write_report(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
