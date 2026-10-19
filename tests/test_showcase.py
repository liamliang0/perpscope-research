import json
from pathlib import Path
import pytest
from src.showcase import parse_report,build

ROOT=Path(__file__).resolve().parents[1]

def test_actual_sample_keeps_missing_values_and_date():
    data=parse_report((ROOT/'examples/sample_report.md').read_text(encoding='utf-8'))
    assert data['capture_date']=='2026-10-04'
    revenue=next(x for x in data['tables']['perps'] if x['metric']=='Perp 24h Revenue')
    assert revenue['aster']=='N/A'
    assert data['shares']['volume']=={'hyperliquid':74.7,'aster':25.3}
    assert data['shares']['oi']=={'hyperliquid':85.7,'aster':14.3}
    assert len(data['sources'])==11

def test_missing_date_is_not_promoted_to_today():
    text=(ROOT/'examples/sample_report.md').read_text(encoding='utf-8').replace('Date: 2026-10-04','Date: unknown')
    with pytest.raises(ValueError):parse_report(text)

def test_inconsistent_share_is_rejected():
    text=(ROOT/'examples/sample_report.md').read_text(encoding='utf-8').replace('Aster has 25.3%','Aster has 95.3%')
    with pytest.raises(ValueError):parse_report(text)

def test_build_escapes_content_and_provides_downloads(tmp_path):
    data=build(ROOT/'examples/sample_report.md',tmp_path)
    page=(tmp_path/'index.html').read_text(encoding='utf-8')
    assert '__CAPTURE__' not in page
    assert '2026-10-04' in page
    assert '非实时行情' in page
    assert (tmp_path/'sample_report.md').read_bytes()==(ROOT/'examples/sample_report.md').read_bytes()
    assert json.loads((tmp_path/'report-data.json').read_text(encoding='utf-8'))==data
