"""Manually authored original demo, never a production writing engine."""
import copy

BENCH_TITLE='租房台面挤到转不开？杯子可以向上放'
BENCH=BENCH_TITLE+'\n我和室友共用小厨房，杯子一多就挤。后来添了折叠杯架，示例价19.9元。先量位置，再放杯子。用了7天，台面终于不乱了。这个结论只属于虚构演示作者的叙述，没有实际效果验证。'
PRODUCT='商品是桌面理线夹，售价12.9元，一包6枚，背胶设计。用途是整理桌面充电线的位置。未提供适配线径、适用表面、粘贴强度、耐用测试、真实体验或销量。'

def claim(text,kind='ANALYSIS',ids=None):return {'text':text,'type':kind,'evidence_ids':ids or ['E1','E2']}

def full_case():
    d={'schema_version':'1.0','mode':'standalone','status':'complete','example':True,
       'sources':[{'id':'S1','origin':'BENCHMARK','kind':'text','label':'原创虚拟对标','title':BENCH_TITLE,'content':BENCH},{'id':'S2','origin':'PRODUCT','kind':'text','label':'虚拟商品资料','content':PRODUCT}],
       'evidence':[{'id':'E1','source_id':'S1','location':'标题与正文','quote':BENCH,'observation':'从台面不便进入工具与适配条件，含不可迁移的虚构体验。','clear':True},{'id':'E2','source_id':'S2','location':'商品资料全文','quote':PRODUCT,'observation':'商品名称、价格、数量、用途明确，效果与适配参数缺失。','clear':True}],
       'product':{k:None for k in ['name','purpose','price','spec','audience','scene','pain','benefits','reason','obstacle','trial_cost','visual','showable','proof','forbidden']}}
    for k,v in {'name':'桌面理线夹','purpose':'整理桌面充电线的位置','price':'12.9元','spec':'一包6枚','benefits':'背胶设计','forbidden':'未提供效果、适配参数或真实体验，不能宣称通用、牢固或亲测结果。'}.items():d['product'][k]=claim(v,'PRODUCT_FACT',['E2'])
    dna={'traffic':'把常见空间不便说具体，可能让有同类需求的人停下。','retention':'先呈现使用问题，再给可执行的摆放顺序，维持信息推进。','trust':'适配条件可以让选择更可检查；原作者的体验不能当新商品证据。','conversion':'把工具与自己的使用位置关联，让用户判断是否有必要购买。','formula':'具体使用不便 → 工具与位置匹配 → 可检查条件 → 自主购买判断'}
    d['analysis']={'core':claim('对标用台面拥挤引出具体工具；可迁移的是空间安排和适配判断，而不是原作者的七天效果。'), 'dna':{k:claim(v) for k,v in dna.items()},'fit':{'level':'中','inherit':[claim('继承“具体不便→工具与位置匹配”的问题解决逻辑。')],'modify':[claim('从厨房杯子转到桌面线材，以拟拍的充电位置和选购条件代替原场景。')],'abandon':[claim('放弃室友故事和七天效果；未提供粘贴强度，不承诺牢固或所有桌面适用。')],'opportunity':claim('可以围绕充电位规划、购买前核对和桌面分区做三种信息入口。')}}
    title_texts=['线总往桌下跑？先给充电位定个点','12.9元的理线夹，先看这几件事再下单','桌面收纳别急着堆盒子，线的位置也要安排','工位上的线该放哪？从最常用的接口开始','桌面理线夹怎么选？把使用位置想清楚']
    hooks=['具体不便','价格与判断','信息反差','工位场景','选购搜索']
    reasons=['以找线的不便作为点击入口，检验场景共鸣。','给出价格但保留适配问题，观察购买前咨询。','将注意力从容器转到线材位置，测试规划价值。','用工位任务定位读者，测试场景聚焦程度。','回应选购问题，测试搜索意图与信息需要。']
    d['titles']=[{'id':'T'+str(i+1),'copy':claim(t,'CREATIVE'),'hook':hooks[i],'why':claim(reasons[i])} for i,t in enumerate(title_texts)]
    bodies=[[
        '坐到桌前准备充电，接口却垂在桌沿下面。这样的时刻，最想解决的往往不是整张桌子的收纳，而是让常用的线有个明确位置。',
        '可以先把电脑、插座和手机的使用位置画在同一张草图上，再看看线从哪里经过。别急着把东西贴满桌边，先留出手能拿到、线又不会妨碍操作的位置。',
        '这款桌面理线夹的用途是整理桌面充电线的位置，背胶设计，一包6枚，售价12.9元。它可以作为规划充电位时的一个备选工具；具体线径和桌面是否适用，要先问清楚，不能只凭图片判断。',
        '先看看你最常用的充电接口在哪里。如果使用位置已经明确，再带着线径和表面情况去核对商品信息。'],[
        '12.9元、一包6枚，这款桌面理线夹的信息很直观。但决定要不要买的，不能只有价格。',
        '先列出要整理的线，再核对线径、准备放置的表面和取放方式。商品资料给出了背胶设计，却没有说明所有材质是否适用，也没有粘贴强度的测试结果；这些问题值得放在付款前。',
        '如果只是想整理桌面充电线的位置，可以把它加入备选。反过来，如果你的需求是承重、固定很粗的线或要求长期不脱落，就不能把这些能力当成它已经具备的卖点。',
        '下单前把使用位置拍清楚，向商家确认适配信息；关键问题没有答案，就先别急着买。'],[
        '给桌面添收纳盒之前，也可以先想一想：常用的线从哪里来，又要到哪里去？容器的位置和线材的路径，可以分开规划。',
        '把桌面分成工作区、充电区和暂放区，再按自己的日常动作安排线的位置。这里不需要制造“改造前后一秒变整齐”的效果图，用草图把计划画清楚就够了。',
        '需要整理桌面充电线的位置时，这款背胶设计的桌面理线夹可以列入工具清单。它的适配范围还要核实，布局草图也只是计划，不是商品实际效果的保证。',
        '先保存一张自己的桌面布局草图，再逐项确认哪些位置需要工具、哪些只要调整摆放。']]
    angles=['充电位场景规划','购买前核对清单','桌面分区与线材路径']
    scenes=['坐到工位准备给手机充电','查看商品页决定是否购买','空桌面上用纸笔规划分区']
    structures=['具体动作开场→位置规划→商品备选→适配提醒','价格与规格前置→核对问题→不适用需求→延后决策','规划问题→分区方法→工具清单→保存草图']
    positions=['第三段作为位置规划的工具备选','第一段直接给商品价格与规格','第三段在分区方法之后进入']
    trust=['用充电位草图说明计划，明确尚未核实的适配信息','列出商品资料缺失项，先核实再购买','用拟拍草图展示思考过程，不伪装效果对比']
    benefits=['用途→背胶→数量→价格','价格→数量→背胶→用途','用途→背胶，省略不影响布局的价格']
    cover_heads=['常用的线，准备放哪里？','买之前，先核对适配','先画路径，再挑工具']
    d['plans']=[]
    for i,pid in enumerate('ABC'):
        d['plans'].append({'id':pid,'title_id':'T'+str(i+1),'angle':angles[i],'opening':bodies[i][0],'scene':scenes[i],'structure':structures[i],'product_position':positions[i],'benefit_order':benefits[i],'trust':trust[i],'cta':bodies[i][-1],
         'cover':{'concept':angles[i],'subject':['桌沿与充电线的位置草图','商品与手写适配问题卡','桌面三区布局草图'][i],'person_product':'使用自己的商品照片；不安排虚构体验人物','scene':scenes[i],'headline':cover_heads[i],'composition':['左侧大字，右侧草图，底部留产品位置','上部标题，中部问题卡，下部商品','俯拍纸面布局，文字沿留白排列'][i],'placement':'商品照片置于右下角，保持真实比例与外观','focus':['充电位置问句','需要确认的问题','线材路径示意'][i],'hook':hooks[i],'reason':reasons[i],'production':'自行拍摄或绘制示意；AI辅助画面需标注示意，不生成产品功效证明','boundary':'封面为策划，不是已经拍摄的实物效果；不使用对标原图'},
         'paragraphs':bodies[i],'inherits':['traffic','trust','conversion'],'differences':['更换为自己的商品与拟拍桌面场景','采用'+structures[i]+'，不沿用对标室友故事'],
         'test':{'variable':['测试充电动作的场景共鸣','测试价格前置后的适配咨询','测试布局方法的收藏意愿'][i],'observe':['有曝光数据再看点击口径，同时记录有效场景评论','记录与线径、表面有关的具体咨询；不把咨询视为成交','记录收藏及提问类型；没有曝光口径就不计算点击率'][i],'decision':'观察用户实际问题再修订，不凭一次互动判断销量或保证爆款。'}})
    d['priority']=[{'plan_id':k,'reason':claim(v)} for k,v in [('B','先测购买前核对路线：现有资料能支撑选择条件，不需要补造效果素材。'),('A','其次测试充电位置场景，需要准备真实草图与商品照片。'),('C','最后测试规划方法的内容价值，收藏变化未必代表购买意愿。')]]
    d['fact_uses']=[{'text':v,'field':k} for k,v in [('price','12.9元'),('spec','一包6枚'),('name','桌面理线夹'),('purpose','整理桌面充电线的位置'),('benefits','背胶设计')]]
    d['limitations']=['对标与商品均为原创虚拟演示，不代表真实爆款、价格或交易。','用户实际商品信息需逐条核对；本例没有适配参数、效果或使用体验证据。','标题、封面和正文是内容初稿与拟拍方案，不是效果保证。']
    d['review']={'expression':'五个标题采用位置、选购和规划入口，没有沿用原对标的租房问句与杯子表达。','story':'没有把室友关系或七天使用经历搬给商品；正文使用拟议步骤与条件。','structure':'原文是短体验叙述，新作分别采用动作规划、核对清单和空间分区顺序。','diversity':'三套开头、场景、商品位置、信任机制和CTA不同，封面各自对应正文任务。','facts':'数字只来自商品价格与数量；没有新增线径、牢固程度、销量或真实体验。'}
    return d

def analyzer_case():
    d=full_case();d['mode']='analyzer';s=d['sources'][0];s['origin']='ANALYZER';s['label']='原创上游DNA示例';s['content']='上游DNA：具体使用不便→工具与位置匹配→可检查条件→自主购买判断。上游未提供真实成交验证。';s.pop('title')
    d['evidence'][0].update(quote=s['content'],observation='上游分析而非原文事实',location='DNA段落')
    d['analysis']['core']=claim('沿用上游空间不便与工具适配的机制判断，用自己的商品证据重新审查。')
    d['limitations'].append('未取得上游完整原文，原创性比较不能覆盖未提供的表达。');return d

def screenshot_case(product_image=False):
    d=full_case();index=1 if product_image else 0;s=d['sources'][index]
    s.update(kind='image',inspected=True,file='product.png' if product_image else 'benchmark.png',transcription=s['content']);s.pop('content')
    d['evidence'][index].pop('quote');d['evidence'][index]['observation']=s['transcription'];d['evidence'][index]['location']='原创演示图可见文字'
    return d

def partial_case(missing='product'):
    d=full_case();origin='PRODUCT' if missing=='benchmark' else 'BENCHMARK'
    d['sources']=[s for s in d['sources'] if s['origin']==origin];ids={s['id'] for s in d['sources']};d['evidence']=[e for e in d['evidence'] if e['source_id'] in ids]
    d['status']='needs_input';d['product']={} if missing=='product' else d['product'];d['analysis']={};d['plans']=[];d['titles']=[]
    d['partial']='已清点现有材料；暂不生成完整三套内容，避免虚构缺少的商品或对标DNA。';return d
