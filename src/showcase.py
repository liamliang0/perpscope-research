"""Render the existing dated Markdown report as a readable static artifact."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
LABELS={
 '24h Volume':'24小时成交量','7d Volume':'7日成交量','30d Volume':'30日成交量',
 'Standardized OI':'同源持仓量 OI','Official API OI':'官方持仓量（仅交叉核对）',
 'Perp 24h Fees':'永续业务24小时费用','Perp 24h Revenue':'永续业务24小时收入',
 'Parent-protocol TVL':'母协议TVL','Perps-linked Holder Revenue (24h)':'永续业务持有人收益（24h）',
 'Parent/Token Holder Revenue (24h)':'母协议/Token持有人收益（24h）','Token Price':'Token价格',
 'Market Cap':'流通市值','FDV':'完全稀释估值 FDV'}

def parse_report(text):
    date_match=re.search(r'^Date: (\d{4}-\d{2}-\d{2})$',text,re.M)
    if not date_match:raise ValueError('A real capture date is required')
    tables={}
    for heading,key in [('Perp Market Snapshot','perps'),('Token / Value Capture Snapshot','token')]:
        section=text.split('## '+heading+'\n',1)[1].split('\n## ',1)[0]
        rows=[]
        for line in section.splitlines():
            if not line.startswith('|'):continue
            cells=[c.strip() for c in line.strip('|').split('|')]
            if len(cells)!=3 or cells[0] in ('Metric','---') or cells[0].startswith('-'):continue
            if cells[0] not in LABELS:raise ValueError('Unmapped report metric: '+cells[0])
            rows.append(dict(metric=cells[0],label=LABELS[cells[0]],hyperliquid=cells[1],aster=cells[2]))
        tables[key]=rows
    shares={}
    for key,pattern in [('volume',r'Hyperliquid has ([\d.]+)% of combined Hyperliquid\+Aster 24h volume; Aster has ([\d.]+)%'),('oi',r'Hyperliquid has ([\d.]+)% of combined measured OI; Aster has ([\d.]+)%')]:
        match=re.search(pattern,text)
        if not match:raise ValueError('Missing measured pairwise shares: '+key)
        h,a=map(float,match.groups())
        if not 0<=h<=100 or not 0<=a<=100 or abs(h+a-100)>.11:raise ValueError('Invalid pairwise share')
        shares[key]=dict(hyperliquid=h,aster=a)
    sources=[]
    section=text.split('## Sources\n',1)[1].split('\n## ',1)[0]
    for line in section.splitlines():
        if not line.startswith('- **'):continue
        provider=re.search(r'^- \*\*(.+?)\*\*',line).group(1)
        endpoint=re.search(r'Endpoint: `([^`]+)`',line).group(1)
        if not endpoint.startswith('https://'):raise ValueError('Source endpoint must use HTTPS')
        scope=re.search(r'scope: `([^`]+)`',line).group(1)
        fetched=line.split('fetched ',1)[1].split('. Used for:',1)[0]
        used=line.split('Used for: ',1)[1].split('. Endpoint:',1)[0]
        sources.append(dict(provider=provider,endpoint=endpoint,scope=scope,fetched_at=fetched,used_for=used))
    if len(sources)<2:raise ValueError('Sources are required')
    return dict(capture_date=date_match.group(1),tables=tables,shares=shares,sources=sources,
                provenance='Values and shares are parsed from the dated sample report. Display values retain the original rounding; they are not reconstructed raw API precision.')

def table(rows):
    return ''.join('<tr><th>'+html.escape(r['label'])+'</th><td>'+html.escape(r['hyperliquid'])+'</td><td>'+html.escape(r['aster'])+'</td></tr>' for r in rows)

def build(report_path,output):
    report_path=Path(report_path);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    text=report_path.read_text(encoding='utf-8');data=parse_report(text)
    page=(ROOT/'web/template.html').read_text(encoding='utf-8')
    source_rows=''.join('<tr><th>'+html.escape(s['provider'])+'</th><td><code>'+html.escape(s['scope'])+'</code><br>'+html.escape(s['used_for'])+'</td><td>'+html.escape(s['fetched_at'])+'<br><a target="_blank" rel="noopener noreferrer" href="'+html.escape(s['endpoint'],quote=True)+'">原始接口</a></td></tr>' for s in data['sources'])
    replacements={'__CAPTURE__':html.escape(data['capture_date']),'__PERPS__':table(data['tables']['perps']),'__TOKEN__':table(data['tables']['token']),
                  '__SOURCES__':source_rows,'__STYLE__':(ROOT/'web/style.css').read_text(encoding='utf-8'),'__SCRIPT__':(ROOT/'web/app.js').read_text(encoding='utf-8'),
                  '__DATA__':json.dumps(data,ensure_ascii=False).replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')}
    for key in ('NARRATIVE','TRENDS','VALUATION'): replacements['__'+key+'__']='历史归档：此页只保留原始快照，不回填当前研究。'
    for key,value in replacements.items():page=page.replace(key,value)
    if re.search(r'__(CAPTURE|PERPS|TOKEN|SOURCES|STYLE|SCRIPT|DATA)__',page):raise ValueError('Unresolved report placeholder')
    (output/'index.html').write_text(page,encoding='utf-8')
    (output/'report-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'sample_report.md').write_text(text,encoding='utf-8')
    (output/'.nojekyll').touch()
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'examples/sample_report.md')
    parser.add_argument('--output',type=Path,default=ROOT/'docs')
    args=parser.parse_args()
    data=build(args.report,args.output)
    print(f"Built dated report {data['capture_date']}; {len(data['sources'])} source records. {args.output/'index.html'}")
