# PerpScope Daily

Date: 2026-10-29

> Research support only. This report does not provide financial advice. N/A means the metric was not reliably available; it is never silently estimated.

## Executive Summary

- Hyperliquid: 4/4 core snapshot metrics are currently verified.
- Aster: 3/4 core snapshot metrics are currently verified.
- Aster: Aster is gaining relative trading activity share against Hyperliquid.

## Perp Market Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
| 24h Volume | $4.23B | $1.64B |
| 7d Volume | $31.70B | $9.99B |
| 30d Volume | N/A | N/A |
| Standardized OI | $7.82B | $1.45B |
| Official API OI | $11.48B | N/A |
| Perp 24h Fees | $2.82M | $128.25K |
| Perp 24h Revenue | $1.96M | N/A |

7d/30d volume is a daily-sampled estimate requiring one official rolling-24h observation for every consecutive UTC date. Sampling times may differ; it is not an exact calendar-volume reconstruction. Any missing day keeps the metric N/A.

## Token / Value Capture Snapshot

| Metric | Hyperliquid | Aster |
|---|---:|---:|
| Parent-protocol TVL | $8.26B | $779.50M |
| Perps-linked Holder Revenue (24h) | $1.96M | N/A |
| Parent/Token Holder Revenue (24h) | N/A | $62.52K |
| Token Price | $80.12 | $0.70 |
| Market Cap | $19.18B | $1.76B |
| FDV | $76.24B | $5.47B |

Holder revenue is a value-capture metric, not a perp operating-margin metric. Aster's available value is parent-protocol scope and may include non-perp products.
Hyperliquid and Aster holder-revenue multiples have different scopes and should not be compared directly.

## Relative Position

- **Scope: Pairwise comparison between Hyperliquid and Aster—not global Perp DEX market share.**
- Hyperliquid has 72.1% of combined Hyperliquid+Aster 24h volume; Aster has 27.9%.
- Hyperliquid has 84.3% of combined measured OI; Aster has 15.7%.
- OI share uses the same standardized DefiLlama open-interest dataset for both protocols. Official Hyperliquid OI is shown only as a cross-check.

## Hyperliquid Thesis Update

### Growth
**Fact:** Perp 24h volume is $4.23B. 7d volume is $31.70B; 30d volume is N/A (Insufficient historical data for 30D comparison.).

### Liquidity / OI
**Fact:** Standardized perp OI is $7.82B; Volume/OI is 0.54x.

### Monetization
**Fact:** Perp 24h fees are $2.82M and perp protocol revenue is $1.96M. Fees/Volume is 0.067%.

### Token Value Capture
**Fact:** Market cap is $19.18B. Market Cap / 30D Revenue Run-Rate is 25.88x; Market Cap / 30D Perps-linked Holder Revenue Run-Rate is 25.88x.

**Unknown:** A run-rate is not trailing-twelve-month revenue and does not establish durable token value capture.

### Competitive Position
Competitive share is limited to the two-protocol comparison in this report; it is not whole-market share.

### Growth Quality
**Interpretation:** Growth quality is stronger when volume, OI, and monetization move together. No trend claim is made without comparable history.

### Key Risks
API methodology changes, incentive-driven activity, incomplete value-capture disclosure, and limited retention/participant-quality data.

### Thesis Status: Weakening
At least two core fundamentals declined by more than 10% over the comparable period.

## Aster Thesis Update

### Growth
**Fact:** Perp 24h volume is $1.64B. 7d volume is $9.99B; 30d volume is N/A (Insufficient historical data for 30D comparison.).

### Liquidity / OI
**Fact:** Standardized perp OI is $1.45B; Volume/OI is 1.12x.

### Monetization
**Fact:** Perp 24h fees are $128.25K and perp protocol revenue is N/A. Fees/Volume is 0.008%.

### Token Value Capture
**Fact:** Market cap is $1.76B. Market Cap / 30D Revenue Run-Rate is N/A; Market Cap / 30D Parent/Token Holder Revenue Run-Rate is 58.27x.

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

- **🟢 Positive — Aster: Aster is gaining pairwise volume share.** **Fact:** Aster pairwise share changed +2.6 percentage points over 7d. **Interpretation:** Aster is gaining relative trading activity share against Hyperliquid.

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

- Hyperliquid official OI differs from standardized OI by +46.7%. The standardized figure is used only for pairwise share; the discrepancy is not silently reconciled.

## What To Watch Next

1. Whether Aster's official 24h volume and open interest rise together.
2. Whether fees and protocol revenue keep pace with activity for both protocols.
3. Whether Aster gains combined two-protocol volume and OI share.
4. Whether token-price changes diverge materially from observable fundamentals.
5. Retention, incentive cost, hidden-order usage, and professional-trader adoption from primary disclosures.

## Sources

- **Hyperliquid official API** — scope: `perps_specific`; dataset: `metaAndAssetCtxs`; fetched 2026-10-29T01:21:17.224540+00:00. Used for: Hyperliquid.volume_24h, Hyperliquid.official_open_interest. Endpoint: `https://api.hyperliquid.xyz/info`. Method: Default/first Hyperliquid perp dex only (no dex parameter). 24h notional volume is summed across its active assets; official OI is openInterest × markPx. HIP-3 builder-deployed perp dexes are not aggregated.
- **DefiLlama** — scope: `parent_protocol`; dataset: `hyperliquid`; fetched 2026-10-29T01:21:18.995145+00:00. Used for: Hyperliquid.tvl. Endpoint: `https://api.llama.fi/protocol/hyperliquid`. Method: Latest parent-protocol TVL reported by DefiLlama.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-29T01:21:18.995173+00:00. Used for: Hyperliquid.fees_24h, Hyperliquid.fees_7d, Hyperliquid.fees_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees`. Method: DefiLlama dailyFees for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-29T01:21:18.995191+00:00. Used for: Hyperliquid.revenue_24h, Hyperliquid.revenue_7d, Hyperliquid.revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyRevenue`. Method: DefiLlama dailyRevenue for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `hyperliquid-perps`; fetched 2026-10-29T01:21:18.995208+00:00. Used for: Hyperliquid.holder_revenue_24h, Hyperliquid.holder_revenue_7d, Hyperliquid.holder_revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyHoldersRevenue`. Method: DefiLlama dailyHoldersRevenue for the standalone hyperliquid-perps dataset.
- **DefiLlama** — scope: `perps_specific`; dataset: `open-interest`; fetched 2026-10-29T01:21:23.315496+00:00. Used for: Hyperliquid.open_interest, Aster.open_interest. Endpoint: `https://api.llama.fi/overview/open-interest`. Method: Standardized provider dataset used for cross-protocol OI comparison.
- **CoinGecko** — scope: `token_level`; dataset: `coins/markets`; fetched 2026-10-29T01:21:23.591194+00:00. Used for: Hyperliquid.token_price, Hyperliquid.market_cap, Hyperliquid.fdv, Aster.token_price, Aster.market_cap, Aster.fdv. Endpoint: `https://api.coingecko.com/api/v3/coins/markets`. Method: USD token market data using the configured CoinGecko coin ID.
- **Aster official API** — scope: `perps_specific`; dataset: `Futures V3 24hr ticker`; fetched 2026-10-29T01:21:17.714339+00:00. Used for: Aster.volume_24h. Endpoint: `https://fapi.asterdex.com/fapi/v3/ticker/24hr`. Method: 24h quote volume summed across active, non-TEST perpetual markets.
- **DefiLlama** — scope: `parent_protocol`; dataset: `aster`; fetched 2026-10-29T01:21:23.268753+00:00. Used for: Aster.tvl. Endpoint: `https://api.llama.fi/protocol/aster`. Method: Latest parent-protocol TVL reported by DefiLlama.
- **DefiLlama** — scope: `perps_specific`; dataset: `aster-perps`; fetched 2026-10-29T01:21:23.268788+00:00. Used for: Aster.fees_24h, Aster.fees_7d, Aster.fees_30d. Endpoint: `https://api.llama.fi/summary/fees/aster-perps?dataType=dailyFees`. Method: DefiLlama dailyFees for the standalone aster-perps dataset.
- **DefiLlama** — scope: `parent_protocol`; dataset: `aster`; fetched 2026-10-29T01:21:23.268805+00:00. Used for: Aster.holder_revenue_24h, Aster.holder_revenue_7d, Aster.holder_revenue_30d. Endpoint: `https://api.llama.fi/summary/fees/aster?dataType=dailyHoldersRevenue`. Method: Combined parent-protocol holder revenue; may include perps and non-perps products.

## Methodology Notes

- Hyperliquid's `metaAndAssetCtxs` request omits `dex`, so it covers only the default/first Hyperliquid perp dex. It does not automatically aggregate builder-deployed/HIP-3 perp dexes. Within that scope, 24h notional volume and official cross-check OI are summed across active assets; official OI is `openInterest × markPx`.
- Aster 24h volume is the sum of `quoteVolume` across official active, non-TEST perpetual tickers; active status is checked with `exchangeInfo`.
- Cross-protocol OI share uses DefiLlama's standardized dataset for both protocols.
- Perp fees and revenue use DefiLlama's standalone perps datasets. Parent TVL and parent-level value capture remain separately labeled.
- Missing values remain N/A. Signals require explicit thresholds in `src/signals.py`.
