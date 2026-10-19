"""Publish current observations, dated research and reproducible historical comparisons."""
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from src.models import ProtocolSnapshot
from src.report import money
from src.showcase import ROOT, LABELS, table

def esc(x):
    return html.escape(str(x), quote=True)

def percent(x):
    return 'N/A' if x is None else f'{x:+.1f}%'

def data_model(payload, tracking):
    snapshots = payload['snapshots']
    for name in ('Hyperliquid','Aster'):
        s = snapshots[name]
        if not any(s.get(k) is not None for k in ('volume_24h','fees_24h')):
            raise ValueError('Refusing to replace published observations: no operating data for '+name)
        if datetime.fromisoformat(s['timestamp']).date() != datetime.now(timezone.utc).date():
            raise ValueError('Refusing to relabel an old snapshot as current')
    rows = {'perps': [], 'token': []}
    fields = [('24h Volume','volume_24h'),('7d Volume','volume_7d'),('30d Volume','volume_30d'),
              ('Standardized OI','open_interest'),('Official API OI','official_open_interest'),
              ('Perp 24h Fees','fees_24h'),('Perp 24h Revenue','revenue_24h'),
              ('Parent-protocol TVL','tvl'),('Token Price','token_price'),('Market Cap','market_cap'),('FDV','fdv')]
    for label, field in fields:
        row = {'metric':label,'label':LABELS[label]}
        if field in ('volume_7d','volume_30d'):
            row['label']+='（日采样估算）'
        for name,key in [('Hyperliquid','hyperliquid'),('Aster','aster')]:
            row[key] = money(snapshots[name].get(field))
        rows['perps' if field in ('volume_24h','volume_7d','volume_30d','open_interest','official_open_interest','fees_24h','revenue_24h') else 'token'].append(row)
    sources = []
    for name,s in snapshots.items():
        grouped = {}
        for field, source in s.get('sources',{}).items():
            key=(source['endpoint'],source['scope'])
            if key not in grouped:
                grouped[key] = {**source, 'used_for':name+': '+field}
            else:
                grouped[key]['used_for'] += ', '+field
        sources.extend(grouped.values())
    shares={}
    for key,field in [('volume','volume_24h'),('oi','open_interest')]:
        h,a=[snapshots[p].get(field) for p in ('Hyperliquid','Aster')]
        shares[key]={'hyperliquid':h/(h+a)*100,'aster':a/(h+a)*100} if h is not None and a is not None and h+a>0 else {'hyperliquid':None,'aster':None}
    return {'capture_date': snapshots['Hyperliquid']['timestamp'][:10], 'captured_at':snapshots['Hyperliquid']['timestamp'],
            'tables':rows,'shares':shares,'sources':sources,'tracking':tracking,'snapshots':snapshots,
            'provenance':'Live public-API collection. Historical daily series supplied by DefiLlama; local snapshots are separately recorded. Research notes have their own review date.'}

def trend_table(data):
    out=['<h2>一天、一周、一个月：增长有没有兑现？</h2><p>费用/收入：最近完整 UTC 日、7 日、30 日，分别对比前一个等长周期；不纳入未结束的当天。价格：CoinGecko 滚动变化率。两类窗口不同，不混算。</p>']
    for key,label in [('fees','永续业务费用'),('revenue','永续业务收入')]:
        comp=data['tracking']['comparisons'][key]
        out.append('<h3>'+label+'</h3><div class="table-wrap"><table><thead><tr><th>周期 / 截止日期</th><th>Hyperliquid 本期 / 环比</th><th>Aster 本期 / 环比</th></tr></thead><tbody>')
        for n,labeln in [('1','1日'),('7','7日'),('30','30日')]:
            h,a=[comp[p][n] for p in ('Hyperliquid','Aster')]
            out.append('<tr><th>'+labeln+'<small>'+esc(h['start']+' → '+h['end'])+'</small></th><td>'+money(h['current'])+'<small>'+percent(h['change_pct'])+'</small></td><td>'+money(a['current'])+'<small>'+percent(a['change_pct'])+'</small></td></tr>')
        out.append('</tbody></table></div>')
    out.append('<h3>Token 价格变化</h3><div class="table-wrap"><table><thead><tr><th>滚动周期</th><th>HYPE</th><th>ASTER</th></tr></thead><tbody>')
    for n,labeln in [('1d','24小时'),('7d','7日'),('30d','30日')]:
        vals=[percent(data['snapshots'][p].get('changes',{}).get('token_price',{}).get(n)) for p in ('Hyperliquid','Aster')]
        out.append('<tr><th>'+labeln+'</th><td>'+vals[0]+'</td><td>'+vals[1]+'</td></tr>')
    out.append('</tbody></table></div><p class="note">7/30日成交量：付费历史端点未接入；连续每日官方快照积累后才显示日采样估算，并明确标记。费用/收入历史来自其独立数据集，不反推成交量。OI变化等待同口径本地观测。</p>')
    out.append('<h3>最近60个完整日的费用轨迹</h3><div class="review-grid">')
    for protocol in ('Hyperliquid','Aster'):
        series=data['tracking']['series'][protocol]['fees']; days=sorted(series)[-60:]
        if not days:
            out.append('<div><h3>'+protocol+'</h3><p>N/A：历史序列未取得</p></div>');continue
        maximum=max(series[d] for d in days) or 1
        bars=''.join(f'<rect x="{i*5}" y="{80-series[d]/maximum*74:.2f}" width="4" height="{series[d]/maximum*74:.2f}"><title>{d}: {money(series[d])}</title></rect>' for i,d in enumerate(days))
        out.append('<div><h3>'+protocol+'</h3><svg class="spark" viewBox="0 0 300 84" role="img" aria-label="'+protocol+'每日费用">'+bars+'</svg><small>'+days[0]+' → '+days[-1]+'；独立纵轴峰值 '+money(maximum)+'</small></div>')
    return ''.join(out)+'</div>'

def narrative(data):
    eco=data['tracking']['ecosystem']; dexes=eco['dexes']
    complete=not eco['errors'] and len(dexes)==eco.get('discovered_dexes')
    active=[d for d in dexes if d['volume_24h']>0]
    volume=sum(d['volume_24h'] for d in dexes);oi=sum(d['open_interest'] for d in dexes)
    default=data['snapshots']['Hyperliquid'].get('volume_24h')
    share=f'{volume/(volume+default)*100:.1f}%' if complete and default and volume else 'N/A'
    counts=f'{len(active)} / {len(dexes)}' if complete else 'N/A（采集不完整）'
    src='https://hyperliquid.gitbook.io/hyperliquid-docs/'
    reviewed=data['tracking'].get('research_sources',[])
    changed=[r for r in reviewed if r.get('changed_since_review')]
    failed=[r for r in reviewed if r['status']!='ok']
    notice='<p class="note">官方资料监测：'+str(len(reviewed)-len(failed))+'/'+str(len(reviewed))+' 页检查成功；'+str(len(changed))+' 页较研究基线变化。'+('有变化或未完成检查，请先复核对应来源，下面仍为原复核日期的判断。' if changed or failed else '未发现正文哈希变化。哈希监测不等于自动完成新研究。')+'</p>'
    out=f'''<h2>未来增长点，走到哪一步了？</h2>{notice}
<p>研究复核：2026-10-19。以下是基于公开证据的研究判断，不是项目方承诺。指标定时更新，路线和机制需要另行复核。</p>
<div class="theses"><article><h3>HYPE：从交易场所扩展为金融基础设施</h3><p>优先验证 HIP-3 外部市场带来的增量交易、HyperEVM 应用对流动性的复用，以及这些活动最终贡献的净费用。生态扩张是增长路径；“项目多”本身不是代币价值。</p>
<p><a href="{src}hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals">HIP-3 官方机制</a> · <a href="{src}hyperevm">HyperEVM 官方说明</a></p>
<dl><dt>有实际成交的 HIP-3 部署 / 发现总数</dt><dd>{counts}</dd><dt>HIP-3 24h 成交额 / 官方持仓</dt><dd>{money(volume) if complete else 'N/A'} / {money(oi) if complete else 'N/A'}</dd><dt>HIP-3 占默认市场 + HIP-3 成交额</dt><dd>{share}</dd></dl>
<p class="note">来源：官方 info API，perpDexs → 逐 dex 的 metaAndAssetCtxs。采集于 {esc(eco['fetched_at'])}。该份额只在 Hyperliquid 内部计算；不加入上方默认市场的双协议成交量份额。部署存在不等于采用；零成交不会计为活跃。HIP-3 收入占比、HyperEVM 非重复 TVL和留存：N/A。</p>
<p><b>前景判断：</b>已有外部部署与实际成交支撑，验证下一步是持续性和净收入贡献。增长模式减费、部署者分成可能让交易额扩张快于 HYPE 回购需求；不能按成交量等比例估算收益。</p></article>
<article><h3>ASTER：隐私交易差异化，加上自有链和市场扩展</h3><p>隐私是较明确的产品差异，但不是唯一增长点；Aster Chain、开放上币和 TradFi 市场也在扩展交易品类与分发。这里优先检验：隐私是否吸引可留存、愿意付费的增量交易者。</p>
<p><a href="https://docs.asterdex.com/trading/perpetuals/order-types/hidden-order-and-hidden-position">Hidden Order / Position</a> · <a href="https://docs.asterdex.com/aster-chain/overview">链与隐私机制</a> · <a href="https://docs.asterdex.com/overview/roadmap">官方路线</a></p>
<dl><dt>产品功能证据</dt><dd>官方机制说明与操作教程</dd><dt>隐私成交占比 / 隐私用户30日留存</dt><dd>N/A / N/A</dd><dt>隐私增量收入 / 补贴后净贡献</dt><dd>N/A / N/A</dd></dl>
<p class="note">未接入可审计的隐私采用聚合数据；N/A 不等于没有用户。协议总费用可观察，但不能归因给隐私。链文档列出阶段性验证者参与和核心组件开源限制；机制描述不等于独立安全证明。路线中的 ETA 不直接记为已上线。</p>
<p><b>前景判断：</b>解决公开持仓暴露的需求有逻辑基础；商业兑现仍待验证。优先跟踪隐私用户的留存、收入贡献和激励退出后的表现，而不是用 TPS、活动奖励或总交易量证明隐私成功。</p></article></div>
<h3>如何判断“发展程度”，而不是凭感觉打分</h3><div class="table-wrap"><table><thead><tr><th>证据层</th><th>HYPE 生态扩张</th><th>ASTER 隐私增长</th></tr></thead><tbody>
<tr><th>机制与产品</th><td>官方架构 + API 部署记录</td><td>官方机制 + 使用教程；独立验证仍需补充</td></tr>
<tr><th>实际采用</th><td>可量化外部市场成交、OI和集中度</td><td>未取得隐私专属采用数据，不能量化完成度</td></tr>
<tr><th>可持续增量经济利益</th><td>HIP-3 净费用与回购贡献待拆分</td><td>隐私增量收入、成本及留存待拆分</td></tr></tbody></table></div>'''
    if complete and volume:
        top=max(dexes,key=lambda d:d['volume_24h'])
        out+=f'<p class="note">集中度检查：{esc(top["name"])} 占本次 HIP-3 成交额 {top["volume_24h"]/volume*100:.1f}%。外部市场增长仍可能依赖少数部署，不能直接认定生态已充分多元化。</p>'
    return out

def valuation(data):
    out=['<h2>落到代币：好业务是否已经是好价格？</h2><p>排序标准：经营兑现的证据、估值负担、增长可选性。以下是条件性研究判断；不把叙事强弱直接转成目标价或收益概率。</p><div class="table-wrap"><table><thead><tr><th>观察项</th><th>HYPE</th><th>ASTER</th></tr></thead><tbody>']
    labels=[('token_price','现价'),('market_cap','流通市值'),('fdv','FDV'),('holder_revenue_30d','近30日持有人收益：范围不同')]
    for field,label in labels:
        out.append('<tr><th>'+label+'</th>'+''.join('<td>'+money(data['snapshots'][p].get(field))+'</td>' for p in ('Hyperliquid','Aster'))+'</tr>')
    for key,label in [('market_cap','近30日持有人收益 ×12 / 流通市值'),('fdv','近30日持有人收益 ×12 / FDV')]:
        cells=[]
        for p in ('Hyperliquid','Aster'):
            s=data['snapshots'][p];v=s.get('holder_revenue_30d');den=s.get(key)
            cells.append(f'{v*12/den*100:.2f}%' if v is not None and den else 'N/A')
        out.append('<tr><th>'+label+'</th><td>'+cells[0]+'</td><td>'+cells[1]+'</td></tr>')
    out.append('<tr><th>指标范围</th><td>Hyperliquid Perps-linked</td><td>Aster parent / token</td></tr></tbody></table></div><p class="note">年化仅为最近30日重复12次的诊断，不是 APY、现金分红或可直接比较的 PE。两边范围不同，不能据此说投资价值相差某个倍数。市值/FDV差距不等于未来12个月解锁量；净新增流通、回购和销毁需另外核对。</p>')
    fees=data['tracking']['comparisons']['fees']
    out.append('<h3>本期可验证的经营比较</h3><p>相同完整周期内，7日费用环比：HYPE '+percent(fees['Hyperliquid']['7']['change_pct'])+'，ASTER '+percent(fees['Aster']['7']['change_pct'])+'；30日费用环比：'+percent(fees['Hyperliquid']['30']['change_pct'])+' / '+percent(fees['Aster']['30']['change_pct'])+'。这是总业务变动，不能直接归因于某一个叙事。</p>')
    out.append('''<div class="theses"><article><h3>HYPE：兑现证据更容易核验，价格仍要过关</h3><p>Assistance Fund 将相关费用兑换为 HYPE 并销毁；费用并非全部归该基金，部署者和 HLP 也参与分配。生态交易扩张是否提高净回购，需要结合费率与分成验证。</p><p><a href="https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees">费用与销毁机制</a></p><p><b>更有吸引力的条件：</b>新增市场持续贡献净费用、收入增长超过估值扩张、销毁与解锁后的净供应改善。</p><p><b>推翻条件：</b>外部交易高度集中且收入转化持续走弱，或者当前价格已隐含过高增长。</p></article>
<article><h3>ASTER：追赶空间存在，隐私溢价需要兑现</h3><p>官方规则为每日平台费用的99%用于回购，回购代币分配给 veASTER，储备等量销毁。普通现货持有人与锁仓者的经济利益不同；激励发行也可能抵消供应收缩。</p><p><a href="https://docs.asterdex.com/usdaster-token/tokenomics">回购、分配与供应规则</a></p><p><b>更有吸引力的条件：</b>隐私采用与留存可核实，费用在激励退出后仍增长，净流通供应改善且价格未先行透支。</p><p><b>推翻条件：</b>采用不能转化为可持续收入，或回购叙事掩盖更大的新增流通。</p></article></div>
<p class="verdict"><b>研究结论：</b>当前更容易核验的是 HYPE 的生态采用与经济兑现；ASTER 的隐私具有产品差异，但采用归因仍有缺口。这支持“兑现证据优先看 HYPE、增量验证重点看 ASTER”，不等于当前价格下必然应买 HYPE。缺少净解锁预测、未来现金利益情景和风险预算，本页不伪造便宜程度、胜率或统一目标价。</p>''')
    return ''.join(out)

def build():
    processed=sorted((ROOT/'data/processed').glob('*.json'))[-1]
    payload=json.loads(processed.read_text(encoding='utf-8'))
    tracking=json.loads((ROOT/'output/tracking.json').read_text(encoding='utf-8'))
    data=data_model(payload,tracking)
    page=(ROOT/'web/template.html').read_text(encoding='utf-8')
    source_rows=''.join('<tr><th>'+esc(s['provider'])+'</th><td>'+esc(s['scope'])+'<br>'+esc(s['used_for'])+'</td><td>'+esc(s['fetched_at'])+'<br><a href="'+esc(s['endpoint'])+'">原始接口</a></td></tr>' for s in data['sources'])
    values={'CAPTURE':esc(datetime.fromisoformat(data['captured_at']).strftime('%Y-%m-%d %H:%M UTC')), 'PERPS':table(data['tables']['perps']), 'TOKEN':table(data['tables']['token']),
            'SOURCES':source_rows,'STYLE':(ROOT/'web/style.css').read_text(encoding='utf-8'),
            'SCRIPT':(ROOT/'web/app.js').read_text(encoding='utf-8'),'TRENDS':trend_table(data),
            'NARRATIVE':narrative(data),'VALUATION':valuation(data),
            'DATA':json.dumps(data,ensure_ascii=False).replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')}
    for key,value in values.items():
        page=page.replace('__'+key+'__',value)
    if re.search(r'__[A-Z]+__',page):
        raise ValueError('Unresolved template placeholder')
    for name in ('招聘者友好','recruiter-friendly'):
        if name in page:
            raise ValueError('Internal design wording leaked into the page')
    docs=ROOT/'docs';docs.mkdir(exist_ok=True)
    (docs/'index.html').write_text(page,encoding='utf-8')
    (docs/'report-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (docs/'latest-snapshot.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(ROOT/'output/daily_report.md',docs/'sample_report.md')
    (docs/'.nojekyll').touch()
    print('Published observations:',data['captured_at'])

if __name__=='__main__':
    build()
