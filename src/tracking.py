"""Public-series comparisons. Calendar windows are complete UTC days, not 24h extrapolations."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import hashlib
from src.data_sources.http import PublicAPIClient

ROOT = Path(__file__).resolve().parents[1]

def daily_series(points, today):
    result = {}
    for stamp, value in points:
        day = datetime.fromtimestamp(int(stamp), timezone.utc).date()
        if day >= today or value is None:
            continue
        if isinstance(value, dict):
            continue
        number = float(value)
        if number >= 0:
            result[day.isoformat()] = number
    return result

def windows(series, end):
    def total(n, offset=0):
        days = [(end-timedelta(days=i+offset)).isoformat() for i in range(n)]
        return sum(series[d] for d in days) if all(d in series for d in days) else None
    out = {}
    for n in (1, 7, 30):
        current, prior = total(n), total(n, n)
        out[str(n)] = {'current': current, 'previous': prior,
            'change_pct': (current/prior-1)*100 if current is not None and prior not in (None, 0) else None,
            'start': (end-timedelta(days=n-1)).isoformat(), 'end': end.isoformat()}
    return out

def collect_history(root=ROOT):
    today = datetime.now(timezone.utc).date()
    report = {'fetched_at': datetime.now(timezone.utc).isoformat(), 'series': {}, 'comparisons': {}, 'errors': []}
    # Reuse the just-fetched raw responses, never the October sample.
    for protocol in ('Hyperliquid', 'Aster'):
        files = sorted((root/'data/raw').glob('*_defillama_'+protocol.lower()+'.json'))
        raw = json.loads(files[-1].read_text(encoding='utf-8')) if files else {}
        if raw.get('fetched_at','')[:10] != today.isoformat():
            report['errors'].append(protocol+': no current historical-source response')
            raw = {}
        report['series'][protocol] = {}
        for key in ('fees', 'revenue'):
            points = raw.get(key, {}).get('totalDataChart', [])
            report['series'][protocol][key] = daily_series(points, today)
    # Both protocols compare exactly the same completed dates for each metric.
    for key in ('fees', 'revenue'):
        a, b = [report['series'][p][key] for p in ('Hyperliquid', 'Aster')]
        common = sorted(set(a)&set(b))
        end = datetime.fromisoformat(common[-1]).date() if common else today-timedelta(days=1)
        report['comparisons'][key] = {p: windows(report['series'][p][key], end) for p in ('Hyperliquid','Aster')}
    return report

def ecosystem(client):
    endpoint = 'https://api.hyperliquid.xyz/info'
    result = {'fetched_at': datetime.now(timezone.utc).isoformat(), 'endpoint': endpoint, 'dexes': [], 'errors': []}
    try:
        dexes = client.json('POST', endpoint, json={'type': 'perpDexs'})
        for dex in dexes:
            if not dex or not dex.get('name'):
                continue
            name = dex['name']
            try:
                meta, contexts = client.json('POST', endpoint, json={'type': 'metaAndAssetCtxs', 'dex': name})
                usable = [c for m,c in zip(meta['universe'],contexts) if not m.get('isDelisted')]
                result['dexes'].append({'name': name, 'markets':len(usable),
                    'volume_24h':sum(float(c.get('dayNtlVlm') or 0) for c in usable),
                    'open_interest':sum(float(c.get('openInterest') or 0)*float(c.get('markPx') or 0) for c in usable)})
            except Exception as exc:
                result['errors'].append(name+': '+str(exc))
        result['discovered_dexes'] = len([d for d in dexes if d and d.get('name')])
    except Exception as exc:
        result['errors'].append(str(exc))
    return result

def research_changes(client):
    baseline_path=ROOT/'research/source-baseline.json'
    baseline=json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {}
    urls=[
        'https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees.md',
        'https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals.md',
        'https://hyperliquid.gitbook.io/hyperliquid-docs/hyperevm.md',
        'https://docs.asterdex.com/aster-chain/overview.md',
        'https://docs.asterdex.com/usdaster-token/tokenomics.md',
        'https://docs.asterdex.com/overview/roadmap.md',
        'https://docs.asterdex.com/trading/perpetuals/order-types/hidden-order-and-hidden-position.md']
    records=[]
    for url in urls:
        try:
            response=client.session.get(url,timeout=15)
            response.raise_for_status()
            text=response.text
            if not text.strip().startswith(('#','>')) or len(text)<300:
                raise ValueError('Expected nonempty Markdown document')
            digest=hashlib.sha256(text.encode('utf-8')).hexdigest()
            records.append({'url':url,'checked_at':datetime.now(timezone.utc).isoformat(),'sha256':digest,
                'changed_since_review':bool(baseline.get(url) and baseline[url]!=digest),'status':'ok'})
            if url not in baseline:
                baseline[url]=digest
        except Exception as exc:
            records.append({'url':url,'status':'unavailable','error':str(exc)})
    baseline_path.parent.mkdir(exist_ok=True)
    # This file pins the manually reviewed version. Existing hashes are never advanced automatically.
    if not baseline_path.exists():
        baseline_path.write_text(json.dumps(baseline,indent=2)+'\n',encoding='utf-8')
    return records

def run():
    report = collect_history()
    report['ecosystem'] = ecosystem(PublicAPIClient(timeout=15,retries=1))
    report['research_sources'] = research_changes(PublicAPIClient(timeout=15,retries=1))
    (ROOT/'output/tracking.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Completed history and ecosystem collection:', report['fetched_at'])

if __name__ == '__main__':
    run()
