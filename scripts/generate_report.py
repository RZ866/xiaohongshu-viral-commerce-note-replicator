"""Validate and render host-authored creative work. No model/network/OCR calls."""
import argparse
import base64
import difflib
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'BENCHMARK_FACT':'对标原文事实','PRODUCT_FACT':'用户商品事实','ANALYSIS':'分析判断','CREATIVE':'原创创作'}
FIELDS = {'name':'商品','purpose':'用途','price':'价格','spec':'规格','audience':'人群','scene':'场景','pain':'痛点','benefits':'卖点','reason':'购买理由','obstacle':'购买阻力','trial_cost':'试错成本','visual':'视觉特点','showable':'可展示内容','proof':'已有证明','forbidden':'不能宣称'}
DNA = {'traffic':'流量DNA','retention':'停留DNA','trust':'信任DNA','conversion':'购买考虑DNA','formula':'DNA总公式'}
DIMENSIONS = {'angle':'切入点','opening':'开头','scene':'拟拍场景','structure':'正文结构','product_position':'商品出现','benefit_order':'卖点顺序','trust':'信任方式','cta':'CTA'}
COVER = {'concept':'核心概念','subject':'主体','person_product':'人物/产品','scene':'场景','headline':'封面大字','composition':'构图','placement':'商品位置','focus':'第一焦点','hook':'视觉钩子','reason':'点击理由','production':'拍摄/生成建议','boundary':'证据边界'}
RISK = re.compile(r'亲测|回购|我(?:妈|爸|奶奶|外婆|朋友)|用了[一二三四五六七八九十\d]+[天周月年]|有效率|治愈|治疗|检测报告|认证|销量|售出|除菌|杀菌|无毒|零甲醛|百分百|100%|真的有效|真没了')

class ReportError(ValueError):
    pass

def need(ok, message):
    if not ok: raise ReportError(message)

def txt(s, label, limit=20000):
    need(isinstance(s,str) and s.strip() and len(s)<=limit,label)
    return s

def ident(s):
    need(isinstance(s,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',s),'identifier')

def normalized(s):
    return ''.join(c for c in unicodedata.normalize('NFKC',s).lower() if c.isalnum())

def overlap(a,b):
    a,b=normalized(a),normalized(b)
    m=difflib.SequenceMatcher(None,a,b,autojunk=False)
    return m.ratio(),m.find_longest_match(0,len(a),0,len(b)).size

def readiness(sources, product):
    if not any(s.get('origin') in ('BENCHMARK','ANALYZER') for s in sources):
        return '请提供一篇对标的截图、文字或已有DNA，作为本次迁移依据。'
    if not any(s.get('origin')=='PRODUCT' for s in sources) or not product.get('name') or not product.get('purpose'):
        return '你自己的商品是什么，主要用来解决什么问题？一句话即可。'
    return None

def validate(d):
    need(isinstance(d,dict) and d.get('schema_version')=='1.0','schema_version')
    need(d.get('mode') in ('standalone','analyzer'),'mode')
    need(d.get('status') in ('complete','needs_input'),'status')
    need(type(d.get('example',False)) is bool,'example')
    sources=d.get('sources');need(isinstance(sources,list) and 0<len(sources)<=30,'sources')
    sm={}
    for s in sources:
        ident(s.get('id'));need(s['id'] not in sm,'duplicate source')
        need(s.get('origin') in ('BENCHMARK','PRODUCT','ANALYZER'),'source origin')
        need(s.get('kind') in ('text','image'),'source kind');txt(s.get('label'),'label',200)
        if s['kind']=='text':txt(s.get('content'),'source content',80000)
        else:need(type(s.get('inspected')) is bool,'inspected')
        sm[s['id']]=s
    if d['mode']=='analyzer':need(any(s['origin']=='ANALYZER' for s in sources),'analyzer input missing')
    evidence=d.get('evidence',[]);need(isinstance(evidence,list) and len(evidence)<=200,'evidence')
    em={}
    for e in evidence:
        ident(e.get('id'));need(e['id'] not in em and e.get('source_id') in sm,'evidence source')
        txt(e.get('location'),'location',300);txt(e.get('observation'),'observation',4000)
        need(type(e.get('clear')) is bool,'clear');s=sm[e['source_id']]
        if s['kind']=='text':
            txt(e.get('quote'),'quote',4000);need(e['quote'] in s['content'],'quote not in source')
        else:need(s['inspected'],'unseen image')
        em[e['id']]=e
    def statement(c, allowed=None):
        need(isinstance(c,dict),'statement object');txt(c.get('text'),'statement text',6000)
        kind=c.get('type');need(kind in TYPES and (not allowed or kind in allowed),'statement type')
        refs=c.get('evidence_ids');need(isinstance(refs,list) and refs and all(x in em for x in refs),'statement evidence')
        origins={sm[em[x]['source_id']]['origin'] for x in refs}
        if kind in ('PRODUCT_FACT','BENCHMARK_FACT'):
            need(all(em[x]['clear'] for x in refs),'unclear fact')
            need(origins==({'PRODUCT'} if kind=='PRODUCT_FACT' else {'BENCHMARK'}),'fact provenance')
    def walk(value):
        if isinstance(value,dict):
            if 'type' in value and 'text' in value:statement(value)
            for v in value.values():walk(v)
        elif isinstance(value,list):
            for v in value:walk(v)
    walk(d.get('analysis',{}))
    product=d.get('product',{});need(isinstance(product,dict) and set(product)<=set(FIELDS),'product fields')
    for c in product.values():
        if c is not None:statement(c,{'PRODUCT_FACT'})
    question=readiness(sources,product)
    if d['status']=='needs_input':
        need(question is not None,'unnecessary blocked status')
        need(not d.get('plans') and not d.get('titles'),'cannot invent complete work without inputs')
        txt(d.get('partial'),'partial work');return {'sources':sm,'evidence':em,'question':question}
    need(question is None,'missing core input')
    analysis=d.get('analysis');need(isinstance(analysis,dict),'analysis')
    statement(analysis.get('core'),{'ANALYSIS'})
    dna=analysis.get('dna');need(isinstance(dna,dict) and set(dna)==set(DNA),'dna keys')
    for k,c in dna.items():
        if k=='formula':need(c is not None,'formula missing')
        if c is not None:statement(c,{'ANALYSIS'})
    fit=analysis.get('fit');need(isinstance(fit,dict) and fit.get('level') in ('高','中','低'),'fit level')
    for key in ('inherit','modify','abandon'):
        need(isinstance(fit.get(key),list) and fit[key],'fit decisions')
        for c in fit[key]:statement(c,{'ANALYSIS'})
    statement(fit.get('opportunity'),{'ANALYSIS'})
    titles=d.get('titles');need(isinstance(titles,list) and len(titles)==5,'five titles required')
    tm={}
    for t in titles:
        ident(t.get('id'));need(t['id'] not in tm,'duplicate title');tm[t['id']]=t
        statement(t.get('copy'),{'CREATIVE'});txt(t.get('hook'),'title hook',300);statement(t.get('why'),{'ANALYSIS'})
    plans=d.get('plans');need(isinstance(plans,list) and len(plans)==3,'three plans required')
    need([p.get('id') for p in plans]==['A','B','C'],'plan order')
    need(len({p.get('title_id') for p in plans})==3 and all(p.get('title_id') in tm for p in plans),'title mapping')
    allcopy=[]
    for p in plans:
        for k in DIMENSIONS:txt(p.get(k),k,3000)
        cover=p.get('cover');need(isinstance(cover,dict) and set(cover)==set(COVER),'cover fields')
        for v in cover.values():txt(v,'cover value',1500)
        paras=p.get('paragraphs');need(isinstance(paras,list) and 2<=len(paras)<=16,'complete paragraphs')
        for para in paras:txt(para,'paragraph',8000)
        body='\n'.join(paras);need(len(normalized(body))>=80,'body too short')
        need(p['opening']==paras[0] and p['cta']==paras[-1],'opening/CTA must match actual copy')
        need(isinstance(p.get('inherits'),list) and p['inherits'] and all(x in dna and dna[x] is not None for x in p['inherits']),'DNA inheritance')
        need(isinstance(p.get('differences'),list) and len(p['differences'])>=2,'original changes')
        for v in p['differences']:txt(v,'difference')
        for k in ('variable','observe','decision'):txt(p.get('test',{}).get(k),'test '+k)
        allcopy.extend(paras);allcopy.extend(cover.values())
    allcopy.extend(t['copy']['text'] for t in titles)
    uses=d.get('fact_uses');need(isinstance(uses,list),'fact uses')
    for u in uses:
        txt(u.get('text'),'fact-use phrase',2000)
        need(u.get('field') in product and product[u['field']] is not None,'fact-use target')
        need(any(u['text'] in c for c in allcopy),'fact use not in copy')
    # Numbers and common high-risk phrases require a source-bound phrase containing that occurrence.
    for copy in allcopy:
        for match in list(RISK.finditer(copy))+list(re.finditer(r'\d+(?:\.\d+)?',copy)):
            covered=False
            for u in uses:
                start=copy.find(u['text'])
                while start>=0:
                    if start<=match.start() and start+len(u['text'])>=match.end() and match.group() in product[u['field']]['text']:covered=True
                    start=copy.find(u['text'],start+1)
            need(covered,'unsupported risky phrase or number in creative copy: '+match.group())
    priority=d.get('priority');need(isinstance(priority,list) and len(priority)==3 and {x.get('plan_id') for x in priority}=={'A','B','C'},'priority')
    for x in priority:statement(x.get('reason'),{'ANALYSIS'})
    limits=d.get('limitations');need(isinstance(limits,list) and limits,'limitations')
    for v in limits:txt(v,'limitation')
    review=d.get('review');need(isinstance(review,dict),'semantic review')
    for key in ('expression','story','structure','diversity','facts'):need(len(txt(review.get(key),'review '+key))>=12,'review requires concrete explanation')
    findings=originality(d)
    need(not findings,'originality/difference review failed: '+'; '.join(findings))
    return {'sources':sm,'evidence':em,'question':None}

def originality(d):
    findings=[]
    benchmarks=[s for s in d['sources'] if s['origin']=='BENCHMARK']
    titles=[t['copy']['text'] for t in d['titles']]
    for i,a in enumerate(titles):
        for b in titles[:i]:
            if overlap(a,b)[0]>.70:findings.append('candidate titles too similar')
        for s in benchmarks:
            # For screenshots the host supplies a faithfully transcribed title/text; no OCR claim.
            if s.get('title'):
                ratio,longest=overlap(a,s['title'])
                if ratio>=.62 or longest>=10:findings.append('benchmark title reuse')
    bodies=['\n'.join(p['paragraphs']) for p in d['plans']]
    for i,p in enumerate(d['plans']):
        for s in benchmarks:
            original=s.get('content',s.get('transcription',''))
            if original and overlap(bodies[i],original)[1]>=24:findings.append('long benchmark expression reuse')
        for j,other in enumerate(d['plans'][:i]):
            if overlap(bodies[i],bodies[j])[0]>=.68:findings.append('plan bodies too similar')
            changed=sum(overlap(p[k],other[k])[0]<.72 for k in DIMENSIONS)
            if changed<3:findings.append('insufficient strategy differences')
            if p['structure']==other['structure'] and p['product_position']==other['product_position'] and p['trust']==other['trust']:
                findings.append('same structure/placement/trust')
    return sorted(set(findings))

def image_uri(source,root,budget):
    value=source.get('file')
    if not value:return None,'未获取到可嵌入图片'
    need(isinstance(value,str) and not any(c in value for c in (':','\\')),'unsafe image path')
    rel=Path(value);need(not rel.is_absolute() and '..' not in rel.parts,'unsafe image path')
    base=Path(root).resolve();p=(base/rel).resolve()
    need(p.is_relative_to(base),'image escapes media root')
    cursor=base
    for part in rel.parts:
        cursor/=part;need(not cursor.is_symlink(),'image symlink')
    if not p.is_file():return None,'图片不可读取，保留素材编号'
    size=p.stat().st_size
    if size>12*1024*1024 or budget[0]+size>40*1024*1024:return None,'图片超过嵌入上限'
    raw=p.read_bytes();mime=None
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):mime='image/png'
    elif raw.startswith(b'\xff\xd8\xff'):mime='image/jpeg'
    elif raw[:4]==b'RIFF' and raw[8:12]==b'WEBP':mime='image/webp'
    if not mime:return None,'不支持的图片格式'
    budget[0]+=len(raw)
    return 'data:'+mime+';base64,'+base64.b64encode(raw).decode(),'用户提供的原素材；不是新封面成品'

def render(d,media_root=None):
    ctx=validate(d);esc=lambda s:html.escape(str(s),quote=True)
    def statement(c):
        if c is None:return '<p class="unknown">未知／未获取到对应材料</p>'
        excerpts=[]
        for eid in c['evidence_ids']:
            e=ctx['evidence'][eid];s=ctx['sources'][e['source_id']]
            excerpts.append('<li>'+esc(eid+' · '+s['label']+' · '+e['location']+'：'+e.get('quote',e['observation']))+'</li>')
        return '<span class="badge">【'+TYPES[c['type']]+'】</span><p>'+esc(c['text'])+'</p><details><summary>查看依据</summary><ul>'+''.join(excerpts)+'</ul></details>'
    def section(title,body,id=''):
        return '<section'+(' id="'+esc(id)+'"' if id else '')+'><h2>'+esc(title)+'</h2>'+body+'</section>'
    if d['status']=='needs_input':
        content=section('可以先做的部分','<p>'+esc(d['partial'])+'</p>')+section('只需补充这一点','<p>'+esc(ctx['question'])+'</p>')
        name='等待关键素材';summary=d['partial']+'\n\n'+ctx['question'];notes='尚未生成完整方案。'
    else:
        a=d['analysis'];fit=a['fit'];name=d['product']['name']['text'];tm={t['id']:t for t in d['titles']}
        first=d['priority'][0]['plan_id']
        cards=[('原对标核心',statement(a['core'])),('适配度：'+fit['level'],statement(fit['opportunity'])),('最值得继承',statement(fit['inherit'][0])),('必须改造',statement(fit['modify'][0]))]
        content=section('本次复刻核心结论','<div class="grid">'+''.join('<article><h3>'+esc(k)+'</h3>'+v+'</article>' for k,v in cards)+'</div><p class="lead">第一优先测试：方案 '+first+' · '+esc(next(p['angle'] for p in d['plans'] if p['id']==first))+'</p>')
        content+=section('DNA Migration Map','<div class="migration"><div>原对标<br><strong>'+esc(a['core']['text'])+'</strong></div><b>→</b><div>抽象机制<br><strong>'+esc(a['dna']['formula']['text'])+'</strong></div><b>→</b><div>适配判断<br><strong>'+fit['level']+' · 改造证据与场景</strong></div><b>→</b><div>原创路线<br>'+''.join('<a href="#plan-'+p['id']+'">'+p['id']+' · '+esc(p['angle'])+'</a>' for p in d['plans'])+'</div></div><p>机制解释与测试假设，不是已验证的成交因果。</p>')
        content+=section('爆款 DNA','<div class="grid">'+''.join('<article><h3>'+v+'</h3>'+statement(a['dna'][k])+'</article>' for k,v in DNA.items())+'</div>')
        content+=section('你的商品：只采用自己的资料','<p>以下来自用户提供的商品材料，未独立核验；未知项不补写。</p><div class="grid compact">'+''.join('<article><h3>'+label+'</h3>'+statement(d['product'].get(k))+'</article>' for k,label in FIELDS.items())+'</div>')
        content+=section('哪些迁移，哪些放弃','<div class="grid three">'+''.join('<article><h3>'+label+'</h3>'+''.join(statement(c) for c in fit[key])+'</article>' for key,label in [('inherit','可直接继承'),('modify','改造后迁移'),('abandon','应当放弃')])+'</div>')
        content+=section('5 个原创标题','<div class="title-list">'+''.join('<article><span class="eyebrow">'+esc(t['id']+' · '+t['hook'])+'</span>'+statement(t['copy'])+statement(t['why'])+'</article>' for t in d['titles'])+'</div>')
        notes='# 三套原创带货笔记\n\n以下为内容初稿，发布前核对商品事实与素材授权。\n'
        for p in d['plans']:
            title=tm[p['title_id']]['copy']['text']
            body='<header class="plan-head"><span>ORIGINAL PLAN '+p['id']+'</span><h3>'+esc(title)+'</h3><p>'+esc(p['angle'])+'</p></header>'
            body+='<div class="plan-grid"><article class="cover"><h3>封面'+p['id']+' · 拍摄方案</h3><div class="cover-type">'+esc(p['cover']['headline'])+'</div><dl>'+''.join('<dt>'+label+'</dt><dd>'+esc(p['cover'][key])+'</dd>' for key,label in COVER.items())+'</dl></article>'
            body+='<article class="copy"><span class="badge">【原创创作】</span><h3>完整正文 · 可选择复制</h3>'+''.join('<p>'+esc(v)+'</p>' for v in p['paragraphs'])+'</article></div>'
            body+='<div class="grid three"><article><h3>继承什么</h3><p>'+esc(' / '.join(DNA[k] for k in p['inherits']))+'</p><h3>原创变化</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in p['differences'])+'</ul></article><article><h3>内容策略</h3><dl>'+''.join('<dt>'+DIMENSIONS[k]+'</dt><dd>'+esc(p[k])+'</dd>' for k in ('scene','structure','product_position','benefit_order','trust','cta'))+'</dl></article><article><h3>内容测试建议</h3>'+''.join('<p>'+esc(p['test'][k])+'</p>' for k in ('variable','observe','decision'))+'</article></div>'
            content+=section('方案 '+p['id'],body,'plan-'+p['id']);notes+='\n## '+p['id']+'｜'+title+'\n\n'+'\n\n'.join(p['paragraphs'])+'\n'
        used={p['title_id'] for p in d['plans']}
        content+=section('2 个备用标题',''.join(statement(t['copy']) for t in d['titles'] if t['id'] not in used))
        content+=section('发布测试优先级','<ol>'+''.join('<li><h3>方案 '+x['plan_id']+'</h3>'+statement(x['reason'])+'</li>' for x in d['priority'])+'</ol><p>这些是内容测试建议，不是严格控制变量的科学实验，也不保证成功。</p>')
        content+=section('事实与原创复核','<details><summary>查看本次复核说明与商品断言绑定</summary>'+''.join('<p>'+esc(v)+'</p>' for v in d['review'].values())+'<ul>'+''.join('<li>'+esc(u['text']+' → '+FIELDS[u['field']])+'</li>' for u in d['fact_uses'])+'</ul></details><ul>'+''.join('<li>'+esc(x)+'</li>' for x in d['limitations'])+'</ul>')
        summary='本次复刻核心结论\n\n原对标核心：'+a['core']['text']+'\n适配度：'+fit['level']+'\n继承：'+fit['inherit'][0]['text']+'\n放弃：'+fit['abandon'][0]['text']+'\n'+ '\n'.join(p['id']+'：'+p['angle'] for p in d['plans'])+'\n第一优先测试：'+first+'。完整方案见HTML；正文另存original-notes.md。'
    budget=[0];materials=[]
    for s in d['sources']:
        source_type={'BENCHMARK':'【对标原文事实】材料中的宣称，未独立核验','PRODUCT':'【用户商品事实】用户提供，未独立核验','ANALYZER':'【分析判断】上游输入，仍需复核'}[s['origin']]
        body='<span class="badge">'+source_type+'</span><p>'+esc(s['label'])+'</p>'
        if s['kind']=='image':
            uri,msg=image_uri(s,media_root or ROOT,budget)
            if uri:body+='<img src="'+uri+'" alt="'+esc(s['label'])+'" loading="lazy">'
            body+='<p>'+esc(msg)+'</p>'
        else:body+='<details><summary>查看提供的文字</summary><p class="source-text">'+esc(s['content'])+'</p></details>'
        materials.append('<article>'+body+'</article>')
    content+=section('素材与来源','<div class="grid">'+''.join(materials)+'</div>')
    template=(ROOT/'assets/report.html').read_text(encoding='utf-8')
    nav=''.join('<a href="#plan-'+p['id']+'">'+p['id']+' · '+esc(p['angle'])+'</a>' for p in d.get('plans',[]))
    values={'TITLE':'小红书爆款带货笔记原创复刻方案','DATE':date.today().isoformat(),'PRODUCT':esc(name),'COUNT':str(len(d['sources'])),'EXAMPLE':'原创合成演示 · 非真实爆款或效果证明' if d.get('example') else '基于用户提供材料 · 原创内容初稿','CONTENT':content,'NAV':nav}
    # Single pass: user text that happens to look like a marker is never re-evaluated.
    result=re.sub(r'@@([A-Z]+)@@',lambda m:values[m.group(1)],template)
    return result,summary,notes

def write_report(d,output,media_root=None):
    output=Path(output);report,summary,notes=render(d,media_root)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(report,encoding='utf-8');(output.parent/'chat-summary.md').write_text(summary,encoding='utf-8');(output.parent/'original-notes.md').write_text(notes,encoding='utf-8')
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--output',required=True);p.add_argument('--media-root');p.add_argument('--debug',action='store_true');a=p.parse_args()
    try:
        f=Path(a.input);need(f.stat().st_size<=5*1024*1024,'input too large')
        write_report(json.loads(f.read_text(encoding='utf-8-sig')),a.output,a.media_root)
        print('Report generated.');return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('报告未生成：输入或证据检查未通过。'+(' '+str(exc) if a.debug else ''),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
