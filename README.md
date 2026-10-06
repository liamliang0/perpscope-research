# PerpScope

An AI-assisted intelligence engine for tracking Perpetual DEX fundamentals and competitive dynamics.

PerpScope is a Python CLI that collects public data for Hyperliquid and Aster, preserves raw responses, normalizes the metrics, calculates comparable KPIs, detects transparent rule-based signals, and writes a daily research memo.

## My role and AI assistance

I initiated PerpScope while researching whether the competitive position and token value capture of Hyperliquid and Aster could support an investment thesis.

I owned the research question, metric framework, scope rules, validation criteria, and iteration decisions. I used OpenAI Codex to help implement the data collectors, calculations, report generator, and tests. I reviewed the outputs against source definitions and kept missing or non-comparable data explicit rather than forcing a conclusion.

This repository is therefore best understood as an **AI-assisted research system**, not as a claim that I independently engineered every line of the software.

## Simple Windows setup

First time: double-click `setup_perpscope.bat`.

Every day after that: double-click `run_perpscope.bat`.

The daily launcher runs PerpScope and opens `output/daily_report.md` automatically.

## Why I built this

Perp DEX activity changes quickly, but raw volume alone can be misleading.

For example, `Volume +80% / OI +10% / Revenue +8%` describes a different quality of growth from `Volume +80% / OI +70% / Revenue +75%`. The first may reflect short-lived turnover; the second is more consistent with activity, persistent positioning, and monetization expanding together.

PerpScope turns raw protocol data into structured, auditable research signals. It is designed as research support—not a price-prediction system or financial advice.

## What it tracks

- Protocol activity: 24h volume, locally accumulated 7d/30d volume, and open interest
- Capital and monetization: TVL/deposited capital, fees, protocol revenue, and holder revenue when explicitly reported
- Token data: price, circulating market cap, FDV, and price changes
- Derived KPIs: Volume/OI, Fees/Volume, Revenue/Volume, Market Cap / 30D Revenue Run-Rate, and scope-labeled holder-revenue run-rate multiples
- Competitive position: Hyperliquid versus Aster volume and OI shares (two-protocol share, not total market share)
- Changes: 1d, 7d, and 30d comparisons when a comparable source or sufficient local history exists

Every populated metric has a source record with an endpoint and fetch timestamp. Missing or failed metrics remain `N/A`; sample numbers are never inserted into the live report.

**Metric comparability matters as much as metric availability.** PerpScope classifies each source as perps-specific, parent-protocol, token-level, or unknown. Perps operating metrics are kept separate from parent-protocol and token value-capture metrics, and ratios are withheld when their scopes do not align.

## Research philosophy

PerpScope follows a simple causal lens:

**Attention → Flow → Liquidity → Fundamentals**

Attention can create flow, but volume alone does not prove high-quality growth. Open interest helps show whether positioning persists, while fees and revenue test whether activity monetizes. Retention, incentive cost, and participant quality are additional checks—but they are not assumed when public APIs cannot measure them.

Two distinctions matter throughout the report:

- **Volume alone ≠ high-quality growth.** Activity is stronger evidence when volume, OI, and revenue rise together.
- **Protocol success ≠ token value capture.** A successful venue may not transfer equivalent economics to token holders. Holder revenue therefore remains separate from protocol revenue.
- **Pairwise share ≠ global market share.** Relative shares in the report compare only Hyperliquid and Aster unless a true market-wide dataset is explicitly available.

## Architecture

```text
Official APIs / DefiLlama / CoinGecko
                 ↓
        raw timestamped JSON
                 ↓
        normalized snapshots
                 ↓
    history + derived metrics
                 ↓
     transparent signal rules
                 ↓
 deterministic memo (+ optional LLM)
```

Key modules:

- `src/data_sources/`: independently failing API adapters
- `src/models.py`: common `ProtocolSnapshot` schema and source records
- `src/history.py`: daily snapshots and comparable-period calculations
- `src/metrics.py`: derived KPI calculations
- `src/signals.py`: editable, threshold-based research rules
- `src/analysis/`: deterministic thesis logic and constrained optional LLM layer
- `src/report.py`: Markdown rendering

Data is stored under `data/raw`, `data/processed`, and `data/history`. Running more than once on the same UTC day replaces that day's history point. Rolling 7d/30d volume requires complete consecutive UTC calendar-day coverage; a missing day keeps the result N/A. Historical changes use a ±6-hour tolerance around the target lookback and otherwise remain N/A.

## Data sources and methodology

| Dataset | Preferred source | Method |
|---|---|---|
| Hyperliquid 24h volume and official OI cross-check | Hyperliquid official API | `metaAndAssetCtxs` without `dex` covers the default/first perp dex only. Sum asset `dayNtlVlm`; official OI is `openInterest × markPx`. HIP-3 builder-deployed perp dexes are not aggregated. |
| Aster 24h volume | Aster official Futures V3 API | Sum active, non-TEST ticker `quoteVolume`; activity status comes from `exchangeInfo` |
| Comparable OI for both protocols | DefiLlama | One standardized open-interest dataset is used for both pairwise shares |
| Perp fees and revenue | DefiLlama | Standalone `hyperliquid-perps` and `aster-perps` datasets; unavailable fields remain N/A |
| TVL and parent value capture | DefiLlama | Parent-protocol datasets, explicitly separated from perp operations |
| Token price, market cap, FDV | CoinGecko | Coin market endpoint using IDs `hyperliquid` and `aster-2` |
| 7d/30d volume | Local history | Sum one official 24h observation per UTC day only after complete coverage |

The code does not silently fall back to estimated data. A source failure affects its own fields, not the complete run.

## Example output

Recruiters and researchers can inspect a complete real-data example without running the project: [examples/sample_report.md](examples/sample_report.md).

```markdown
## Relative Position

- Hyperliquid has 84.2% of combined Hyperliquid+Aster 24h volume.
- Aster has 15.8% of combined Hyperliquid+Aster 24h volume.
- These are two-protocol relative shares, not total perp-DEX market share.

## Key Signals

- 🟡 Watch — History is still accumulating. No change-based signal has enough local history.
```

Actual values are fetched at runtime and written to `output/daily_report.md`.

## How to run

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Run tests with:

```bash
pytest -q
```

The default deterministic mode needs no API key. Copy `.env.example` to `.env` only if you want to change settings.

## Optional LLM analysis

Rule-based analysis always works and is the default:

```dotenv
LLM_PROVIDER=none
```

For an OpenAI-compatible endpoint:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

For Ollama:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

The LLM receives only structured metrics, calculated changes, signals, and declared data gaps. Its prompt requires separate **Facts**, **Interpretation**, and **Unknowns** sections. If it fails, the deterministic report is still generated. Never commit `.env`; it is ignored by Git.

## Limitations

- Aster's official API does not provide a practical aggregate OI endpoint. Pairwise OI therefore uses DefiLlama for both protocols; official Hyperliquid OI remains a separate cross-check.
- DefiLlama's derivatives-volume API requires paid access; PerpScope uses official 24h exchange volume and accumulates longer windows locally.
- Official Hyperliquid and Aster volume fields have aligned perps-only scope but provider-specific calculation. The report discloses this limitation.
- Aster Perps currently exposes fees but not protocol or holder revenue through the tested public summary endpoints. Parent-level holder revenue is labeled separately and never treated as perp revenue.
- A fresh installation cannot make valid local 7d/30d comparisons. The report explicitly says when history is insufficient.
- User retention, incentive/subsidy expenditure, privacy/hidden-order adoption, whale or professional-trader adoption, and Binance/YZi distribution support may require manual or first-party research.
- TVL definitions can differ across protocol architectures and should not be treated as perfectly comparable.
- API definitions and endpoints can change. Raw payload retention makes methodology changes auditable.
- PerpScope supports research; it does not provide financial advice.

## Project structure

```text
perpscope/
├── main.py
├── config/settings.py
├── src/
│   ├── data_sources/
│   ├── analysis/
│   ├── models.py
│   ├── history.py
│   ├── metrics.py
│   ├── signals.py
│   ├── report.py
│   └── pipeline.py
├── data/{raw,processed,history}/
├── output/
└── tests/
```
