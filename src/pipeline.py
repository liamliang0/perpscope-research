import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from config.settings import Settings
from src.analysis.llm import enhance
from src.data_sources import aster, defillama, hyperliquid, market_data
from src.data_sources.http import PublicAPIClient
from src.history import enrich_from_history, enrich_relative_history, load_history, save_history, snapshots_for
from src.metrics import calculate, relative_metrics
from src.models import ProtocolSnapshot
from src.normalize import mark_unavailable, merge_values
from src.report import render, write_report
from src.signals import detect

log = logging.getLogger(__name__)


def _save_raw(directory: Path, name: str, payload: Any) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (directory / f"{stamp}_{name}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _try(label: str, function: Callable[[], Any]) -> Any | None:
    try:
        return function()
    except Exception as exc:
        log.warning("%s unavailable: %s", label, exc)
        return None


def run() -> int:
    settings = Settings()
    settings.ensure_directories()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                        format="%(levelname)s %(name)s: %(message)s")
    client = PublicAPIClient(settings.request_timeout, settings.request_retries)
    snapshots = {name: ProtocolSnapshot(name) for name in ("Hyperliquid", "Aster")}
    coingecko_changes: dict[str, dict[str, float | None]] = {}

    result = _try("Hyperliquid official API", lambda: hyperliquid.fetch(client))
    if result:
        values, raw = result
        _save_raw(settings.raw_dir, "hyperliquid", raw)
        merge_values(snapshots["Hyperliquid"], values, "Hyperliquid official API", hyperliquid.ENDPOINT,
                     scope="perps_specific", dataset="metaAndAssetCtxs",
                     methodology="Default/first Hyperliquid perp dex only (no dex parameter). 24h notional volume is summed across its active assets; official OI is openInterest × markPx. HIP-3 builder-deployed perp dexes are not aggregated.")

    result = _try("Aster official API", lambda: aster.fetch(client))
    if result:
        values, raw = result
        _save_raw(settings.raw_dir, "aster", raw)
        merge_values(snapshots["Aster"], values, "Aster official API", aster.TICKER_ENDPOINT,
                     "Active symbols verified via /fapi/v3/exchangeInfo; sum of ticker quoteVolume.",
                     scope="perps_specific", dataset="Futures V3 24hr ticker",
                     methodology="24h quote volume summed across active, non-TEST perpetual markets.")

    for protocol in snapshots:
        result = _try(f"DefiLlama {protocol}", lambda p=protocol: defillama.fetch_protocol(client, p))
        if result:
            values, raw, metadata = result
            _save_raw(settings.raw_dir, f"defillama_{protocol.lower()}", raw)
            for field, value in values.items():
                meta = metadata.get(field, {})
                merge_values(snapshots[protocol], {field: value}, "DefiLlama", meta.get("endpoint", ""),
                             scope=meta.get("scope", "unknown"), dataset=meta.get("dataset"),
                             methodology=meta.get("methodology"))

    result = _try("DefiLlama open interest", lambda: defillama.fetch_open_interest(client))
    if result:
        values, raw = result
        _save_raw(settings.raw_dir, "defillama_open_interest", raw)
        # Standardized DefiLlama OI is mandatory for both sides of relative share.
        for protocol, value in values.items():
            merge_values(snapshots[protocol], {"open_interest": value}, "DefiLlama",
                         f"{defillama.BASE}/overview/open-interest", overwrite=True,
                         scope="perps_specific", dataset="open-interest",
                         methodology="Standardized provider dataset used for cross-protocol OI comparison.")

    result = _try("CoinGecko market data", lambda: market_data.fetch(client))
    if result:
        values, raw = result
        _save_raw(settings.raw_dir, "coingecko", raw)
        for protocol, fields in values.items():
            price_changes = {k: v for k, v in fields.items() if k.startswith("price_change_")}
            market_fields = {k: v for k, v in fields.items() if not k.startswith("price_change_")}
            merge_values(snapshots[protocol], market_fields, "CoinGecko", market_data.ENDPOINT,
                         scope="token_level", dataset="coins/markets",
                         methodology="USD token market data using the configured CoinGecko coin ID.")
            coingecko_changes[protocol] = {
                key.removeprefix("price_change_"): value for key, value in price_changes.items()
            }

    history = load_history(settings.history_dir)
    for protocol, snapshot in snapshots.items():
        enrich_from_history(snapshot, snapshots_for(history, protocol))
        # CoinGecko price changes are available immediately; restore them after local-history enrichment.
        for period, value in coingecko_changes.get(protocol, {}).items():
            if value is not None:
                snapshot.changes.setdefault("token_price", {})[period] = value
        mark_unavailable(snapshot, ["volume_7d"], "Insufficient historical data for 7D comparison.")
        mark_unavailable(snapshot, ["volume_30d"], "Insufficient historical data for 30D comparison.")
        mark_unavailable(snapshot, ["holder_revenue_24h", "holder_revenue_7d", "holder_revenue_30d"],
                         "No reliable holder-revenue value was returned by the selected source.")
        mark_unavailable(snapshot, ["open_interest", "tvl", "fees_24h", "revenue_24h",
                                    "token_price", "market_cap", "fdv"],
                         "Source/API unavailable or did not return this metric.")
        snapshot.validate()
        calculate(snapshot)

    relative = relative_metrics(snapshots)
    enrich_relative_history(relative, history, datetime.now(timezone.utc))
    signals = detect(snapshots, relative)
    llm_payload = {"snapshots": {k: v.to_dict() for k, v in snapshots.items()},
                   "relative": relative, "signals": [vars(s) for s in signals],
                   "known_data_gaps": {k: v.unavailable for k, v in snapshots.items()}}
    llm_text = enhance(settings, llm_payload)
    processed_path = settings.processed_dir / f"{datetime.now(timezone.utc).date().isoformat()}.json"
    processed_path.write_text(json.dumps(llm_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    save_history(settings.history_dir, snapshots, relative)
    report_path = settings.output_dir / "daily_report.md"
    write_report(report_path, render(snapshots, relative, signals, llm_text))
    log.info("Report written to %s", report_path)
    return 0
