# PerpScope Daily

Date: 2026-10-30

> Research support only. This report does not provide financial advice. N/A means the metric was not reliably available; it is never silently estimated.

## Executive Summary

- Hyperliquid: 4/4 core snapshot metrics are currently verified.
- Aster: 3/4 core snapshot metrics are currently verified.
- Hyperliquid: Trading activity is increasing faster than persistent positioning; growth quality should be monitored.
- Hyperliquid: Activity growth is not translating proportionally into observable revenue.
- Hyperliquid: Price increased faster than revenue; this is a metric-specific divergence, not a claim about all fundamentals.

## Perp Market Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
| 24h Volume | $14.77B | $2.87B |
| 7d Volume | $39.75B | $10.95B |
| 30d Volume | N/A | N/A |
| Standardized OI | $7.87B | $1.39B |
| Official API OI | $11B | N/A |
| Perp 24h Fees | $2.82M | $204.76K |
| Perp 24h Revenue | $1.96M | N/A |

7d/30d volume is a daily-sampled estimate requiring one official rolling-24h observation for every consecutive UTC date. Sampling times may differ; it is not an exact calendar-volume reconstruction. Any missing day keeps the metric N/A.

## Token / Value Capture Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
| Parent-protocol TVL | $8.36B | $746.03M |
| Perps-linked Holder Revenue (24h) | $1.96M | N/A |
| Parent/Token Holder Revenue (24h) | N/A | $64.87K |
| Token Price | $89.80 | $0.67 |
| Market Cap | $21.50B | $1.69B |
| FDV | $85.47B | $5.25B |

Holder revenue is a value-capture metric, not a perp operating-margin metric. Aster's available value is parent-protocol scope and may include non-perp products.
Hyperliquid and Aster holder-revenue multiples have different scopes and should not be compared directly.

## Relative Position

- **Scope: Pairwise comparison between Hyperliquid and Aster—not global Perp DEX market share.**
- Hyperliquid has 83.8% of combined Hyperliquid+Aster 24h volume; Aster has 16.2%.
- Hyperliquid has 85.0% of combined measured OI; Aster has 15.0%.
- OI share uses the same standardized DefiLlama open-interest dataset for both protocols. Official Hyperliquid OI is shown only as a cross-check.

## Hyperliquid Thesis Update

### Growth
**Fact:** Perp 24h volume is $14.77B. 7d volume is $39.75B; 30d volume is N/A (Insufficient historical data for 30D comparison.).

### Liquidity / OI
**Fact:** Standardized perp OI is $7.87B; Volume/OI is 1.88x.

### Monetization
**Fact:** Perp 24h fees are $2.82M and perp protocol revenue is $1.96M. Fees/Volume is 0.019%.

### Token Value Capture
**Fact:** Market cap is $21.50B. Market Cap / 30D Revenue Run-Rate is 30.18x; Market Cap / 30D Perps-linked Holder Revenue Run-Rate is 30.18x.

**Unknown:** A run-rate is not trailing-twelve-month revenue and does not establish durable token value capture.

### Competitive Position
Competitive share is limited to the two-protocol comparison in this report; it is not whole-market share.

### Growth Quality
**Interpretation:** Growth quality is stronger when volume, OI, and monetization move together. No trend claim is made without comparable history.

### Key Risks
API methodology changes, incentive-driven activity, incomplete value-capture disclosure, and limited retention/participant-quality data.

### Thesis Status: Stable
The available core metrics do not show a broad directional move.

## Aster Thesis Update

### Growth
**Fact:** Perp 24h volume is $2.87B. 7d volume is $10.95B; 30d volume is N/A (Insufficient historical data for 30D comparison.).

### Liquidity / OI
**Fact:** Standardized perp OI is $1.39B; Volume/OI is 2.07x.

### Monetization
**Fact:** Perp 24h fees are $204.76K and perp protocol revenue is N/A. Fees/Volume is 0.007%.

### Token Value Capture
**Fact:** Market cap is $1.69B. Market Cap / 30D Revenue Run-Rate is N/A; Market Cap / 30D Parent/Token Holder Revenue Run-Rate is 56.52x.

**Unknown:** A run-rate is not trailing-twelve-month revenue and does not establish durable token value capture.

### Competitive Position
Competitive share is limited to the two-protocol comparison in this report; it is not whole-market share.

### Growth Quality
**Interpretation:** Growth quality is stronger when volume, OI, and monetization move together. No trend claim is made without comparable history.

### Key Risks
API methodology changes, incentive-driven activity, incomplete value-capture disclosure, and limited retention/participant-quality data.

### Thesis Status: Stable
The available core metrics do not show a broad directional move.

## Key Signals

- **🟡 Watch — Hyperliquid: Activity is outpacing positioning.** **Fact:** 7D change: volume +119.8% vs OI -0.6%. **Interpretation:** Trading activity is increasing faster than persistent positioning; growth quality should be monitored.
- **🔴 Negative — Hyperliquid: Monetization is lagging activity.** **Fact:** 7D change: volume +119.8% vs revenue -27.3%. **Interpretation:** Activity growth is not translating proportionally into observable revenue.
- **🟡 Watch — Hyperliquid: Price outpaces selected fundamentals.** **Fact:** 7D price +18.3%; volume +119.8%, OI -0.6%, revenue -27.3%. **Interpretation:** Price increased faster than revenue; this is a metric-specific divergence, not a claim about all fundamentals.
- **🟢 Positive — Hyperliquid: Selected fundamentals outpace price.** **Fact:** 7D price +18.3%; volume +119.8%, OI -0.6%, revenue -27.3%. **Interpretation:** volume increased faster than price; other operating metrics may differ.
- **🟡 Watch — Aster: Activity is outpacing positioning.** **Fact:** 7D change: volume +50.0% vs OI +3.8%. **Interpretation:** Trading activity is increasing faster than persistent positioning; growth quality should be monitored.
- **🟢 Positive — Aster: Selected fundamentals outpace price.** **Fact:** 7D price -2.1%; volume +50.0%, OI +3.8%. **Interpretation:** volume increased faster than price; other operating metrics may differ.
- **🟡 Watch — Aster: Aster is losing pairwise volume share.** **Fact:** Aster pairwise share changed -11.7 percentage points over 1d. **Interpretation:** Aster is losing relative trading activity share against Hyperliquid.

## Data Gaps

- **Hyperliquid / volume_30d:** Insufficient historical data for 30D comparison.
- **Aster / revenue_24h:** Source/API unavailable or did not return this metric.
- **Aster / volume_30d:** Insufficient historical data for 30D comparison.
- Aster D30 retention and cohort quality require user-level or first-party data.
- Incentive/subsidy expenditure is not reliably exposed by the selected APIs.
- Privacy/hidden-order adoption and whale/professional adoption require first-party or manual research.
- Binance/YZi distribution support is qualitative and requires manual research.
- Protocol TVL definitions are not perfectly comparable across architectures.

## Data Quality / Scope Notes

- DefiLlama's public derivatives-volume API currently returns HTTP 402. Pairwise volume uses official perps-only 24h notional/quote-volume fields with aligned product scope but provider-specific calculation.
- Perp fees/revenue use standalone `hyperliquid-perps` and `aster-perps` datasets, not parent-protocol fee totals.
- Revenue/holder datasets may be missing independently. Any combined parent holder revenue is labeled parent-protocol scope and is not silently substituted for perp protocol revenue.
- Missing one side of a comparison makes both pairwise shares N/A; missing values are never treated as zero.
- Run-rate annualization assumes the recent 30D period repeats and is not equivalent to trailing twelve-month revenue.

- Hyperliquid official OI differs from standardized OI by +39.8%. The standardized figure is used only for pairwise share; the discrepancy is not silently reconciled.

## What To Watch Next

1. Whether Aster's official 24h volume and open interest rise together.
2. Whether fees and protocol revenue keep pace with activity for both protocols.
3. Whether Aster gains combined two-protocol volume and OI share.
4. Whether token-price changes diverge materially from observable fundamentals.
5. Retention, incentive cost, hidden-order usage, and professional-trader adoption from primary disclosures.

## Sources

- **Hyperliquid official API** — scope: `perps_specific`; dataset: `metaAndAssetCtxs`; fetched 2026-10-30T01:24:27.150813+00:00. Used for: Hyperliquid.volume_24h, Hyperliquid.official_open_interest. Endpoint: `https://api.hyperliquid.xyz/info`. Method: Default/first Hyperliquid perp dex only (no dex parameter). 24h notional volume is summed across its active assets; official OI is openInterest × markPx. HIP-3 builder-deployed perp dexes are not aggregated.
- **DefiLlama** — scope: `parent_protocol`; dataset: `hyperliquid`; fetched 2026-10-30T01:24:29.902976+00:00. Used for: Hyperliquid.tvl. Endpoint: `https://api.llama.fi/protocol/hyperliquid`. Method: Latest parent-protocol TVL reported by DefiLlama.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-30T01:24:29.903001+00:00. Used for: Hyperliquid.fees_24h, Hyperliquid.fees_7d, Hyperliquid.fees_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees`. Method: DefiLlama dailyFees for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-30T01:24:29.903041+00:00. Used for: Hyperliquid.revenue_24h, Hyperliquid.revenue_7d, Hyperliquid.revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyRevenue`. Method: DefiLlama dailyRevenue for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-30T01:24:29.903060+00:00. Used for: Hyperliquid.holder_revenue_24h, Hyperliquid.holder_revenue_7d, Hyperliquid.holder_revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyHoldersRevenue`. Method: DefiLlama dailyHoldersRevenue for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `open-interest`; fetched 2026-10-30T01:24:35.203637+00:00. Used for: Hyperliquid.open_interest, Aster.open_interest. Endpoint: `https://api.llama.fi/overview/open-interest`. Method: Standardized provider dataset used for cross-protocol OI comparison.
- **CoinGecko** — scope: `token_level`; dataset: `coins/markets`; fetched 2026-10-30T01:24:35.520445+00:00. Used for: Hyperliquid.token_price, Hyperliquid.market_cap, Hyperliquid.fdv, Aster.token_price, Aster.market_cap, Aster.fdv. Endpoint: `https://api.coingecko.com/api/v3/coins/markets`. Method: USD token market data using the configured CoinGecko coin ID.
- **Aster official API** — scope: `perps_specific`; dataset: `Futures V3 24hr ticker`; fetched 2026-10-30T01:24:27.895816+00:00. Used for: Aster.volume_24h. Endpoint: `https://fapi.asterdex.com/fapi/v3/ticker/24hr`. Method: 24h quote volume summed across active, non-TEST perpetual markets.
- **DefiLlama** — scope: `parent_protocol`; dataset: `aster`; fetched 2026-10-30T01:24:35.135871+00:00. Used for: Aster.tvl. Endpoint: `https://api.llama.fi/protocol/aster`. Method: Latest parent-protocol TVL reported by DefiLlama.
- **DefiLlama** — scope: `perps_specific`; dataset: `aster-perps`; fetched 2026-10-30T01:24:35.135894+00:00. Used for: Aster.fees_24h, Aster.fees_7d, Aster.fees_30d. Endpoint: `https://api.llama.fi/summary/fees/aster-perps?dataType=dailyFees`. Method: DefiLlama dailyFees for the standalone aster-perps dataset.
- **DefiLlama** — scope: `parent_protocol`; dataset: `aster`; fetched 2026-10-30T01:24:35.135911+00:00. Used for: Aster.holder_revenue_24h, Aster.holder_revenue_7d, Aster.holder_revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/aster?dataType=dailyHoldersRevenue`. Method: Combined parent-protocol holder revenue; may include perps and non-perps products.

## Methodology Notes

- Hyperliquid's `metaAndAssetCtxs` request omits `dex`, so it covers only the default/first Hyperliquid perp dex. It does not automatically aggregate builder-deployed/HIP-3 perp dexes. Within that scope, 24h notional volume and official cross-check OI are summed across active assets; official OI is `openInterest × markPx`.
- Aster 24h volume is the sum of `quoteVolume` across official active, non-TEST perpetual tickers; active status is checked with `exchangeInfo`.
- Cross-protocol OI share uses DefiLlama's standardized dataset for both protocols.
- Perp fees and revenue use DefiLlama's standalone perps datasets. Parent TVL and parent-level value capture remain separately labeled.
- Missing values remain N/A. Signals require explicit thresholds in `src/signals.py`.
