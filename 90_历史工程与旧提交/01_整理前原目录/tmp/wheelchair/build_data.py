from pathlib import Path
import json,csv,shutil,collections
ROOT=Path('D:/课/大四上/思辨设计')
OUT=ROOT/'output/作业一_智能轮椅';OUT.mkdir(exist_ok=True)
DB=ROOT/'output/机器人自我修养数据库'
DATE='2026-09-18'
def writecsv(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base=json.loads((DB/'机器人自我修养数据库.json').read_text(encoding='utf-8'))
lookup={r['id']:r for r in base['records']}
new=[
 ('RC261','LUCI：可覆盖的轮椅辅助与使用者控制','真实产品与事件','纪实／产品','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf','辅助减速、避障，并提供临时Override、参数设置及数据分享控制。','厂商手册证明功能说明；不是独立效果试验，不能声称系统从每次覆盖中自动学习。'),
 ('RC262','CoNav Chair: Development and Evaluation of a Shared Control-based Wheelchair for the Built Environment','研究与技术','实证／技术','https://arxiv.org/abs/2507.11716','整合自主导航与摇杆纠正，比较手动、共享和自主三种模式。','21名无相关功能障碍的成年人；2025年预印本，未证明目标残障使用者的长期效果。'),
 ('RC263','NavChair: Adaptive Shared Control for an Intelligent Power Wheelchair','研究与技术','实证／技术','https://cdn.aaai.org/AAAI/1996/AAAI96-222.pdf','已开发穿门、沿墙及基于环境线索的模式适应模块；讨论自动选择模式的负担。','1996年单页研究报告；贝叶斯适应方法和评价属于拟开展内容，无完整用户试验结果。'),
 ('RC264','Shirley Ryan AbilityLab Smart Wheelchair','研究与技术','项目／技术','https://www.sralab.org/research/projects/smart-wheelchair','共享自主轮椅面向个人需要与偏好，开发门洞、坡面、落差和停靠感知。','机构项目页提及脊髓损伤志愿者研究，但未列样本量和效果数值；不据此声称优势显著。'),
 ('RC265','WHILL Autonomous Service','真实产品与事件','纪实／产品','https://whill.inc/au/mobility-service/how-it-works/autonomous-drive','使用者选择目的地，设备自主行驶，提供暂停与紧急停止。','官方服务说明；特定设施服务，不能推断可适配所有残障者、场景或可长期学习。'),
 ('RC266','Low cost sensor network for obstacle avoidance in share-controlled smart wheelchairs under daily scenarios','研究与技术','实证／技术','https://www.sciencedirect.com/science/article/abs/pii/S0026271418301082','2018年多传感器共享控制轮椅，摘要报告告警、避障及问卷。','本轮只有检索返回的摘要，原文未取得，不纳入核心行为比较。'),
 ('RC267','Blending User Intent and Obstacle Avoidance Through Artificial Potential Fields: An Experimental Validation on Smart Walker','研究与技术','实证／技术','https://www.iris.unict.it/handle/20.500.11769/729611','2026年智能助行器共享控制研究，以人工势场协调人类意图与避障。','本轮机构记录无法打开；仅摘要，不纳入核心行为比较。'),
 ('RC268','Ethics at the Intersection of Intelligent Assistive Technology, Ageing, and the Home Environment: A Scoping Review','理论与综述','概念／综述','https://link.springer.com/article/10.1007/s11673-025-10479-8','2025年居家智能辅具与老龄伦理范围综述。','综述用于问题背景，不作为一例已实现机器人行为。'),
]
for ident,title,kind,nature,url,summary,boundary in new:
 lookup[ident]={'id':ident,'legacy_ids':[],'aliases':[],'title':title,'record_role':'理论／方法' if ident=='RC268' else '案例','material_type':kind,'evidence_nature':nature,'summary':summary,'evidence_boundary':boundary,'research_question':'辅助系统如何尊重使用者的行动自主，并允许纠正其判断？','cultivation_capabilities':['尊重意愿','承认局限','反馈修正'],'debate_axes':['同意与自主','所有权与控制','学习与纠错'],'scenario_domains':['辅助出行','轮椅与助行'],'search_terms':['wheelchair','shared control','user autonomy','assistive technology'],'primary_url':url,'source_urls':[url],'source_quality':'本轮按具体来源类型说明，未作统一质量评分','review_status':'来源核查；见2026-09-18专题台账','provenance_rounds':['智能轮椅专题补充检索2026-09-18'],'added_on':DATE}

# Per-case fields are human-readable research extraction, not inferred from keywords.
cases=[]
def case(code,id,title,cat,year,source,scene,behavior,trait,feedback,boundary,locator,url=None):
 cases.append(dict(案例编号=code,主库编号=id,案例名称=title,分类=cat,年份或版本=year,来源类型=source,场景与对象=scene,具体行为=behavior,修养特点_本作业解释=trait,反馈与改进证据=feedback,证据边界=boundary,核查位置=locator,来源链接=url or lookup[id]['primary_url'],核查日期=DATE))
case('W01','RC262','CoNav Chair','A 共享行动决定','2025','研究预印本','室内走廊导航；21名无相关功能障碍的成年人。','自主导航中接收摇杆输入，允许使用者修正行驶；比较手动、共享与自主模式。','人的意图能够进入执行过程，辅助不必等于完全接管。','F1：摇杆改变当前行动。研究提供模式比较，未证明个人偏好被长期学习。','不能把这21人的结果推广为老人或残障使用者的验证结论。','摘要；§III-D；§IV-C；图2与图7')
case('W02','RC263','NavChair','A 共享行动决定','1996','会议研究短文','电动轮椅穿门、沿墙；目标是减少使用者频繁切换模式的负担。','报告已开发穿门、沿墙和基于环境线索的行为适应模块。','让辅助随情境变化，减少手动操作负担；也引出谁决定切换的问题。','F0：有环境响应机制，但无用户反馈导致后续学习的证据。','贝叶斯适应与评价在该文中仍是计划；不得写成已完成实验。','单页报告，第1370页，末段与研究计划')
case('W03','RC264','AbilityLab Smart Wheelchair','A 共享行动决定','项目页2017','研究机构项目页','共享自主轮椅；项目提及脊髓损伤志愿者参与。','按个体需要和偏好设计辅助，开发门洞、坡面、落差及停靠感知。','辅助程度与操控接口应适配个人，不用统一能力假设代替使用者。','F0：项目记录了参与者评价，但页面未给出反馈如何改变策略的细节。','未公开样本量或效果数值；个性化目标不等于已验证的自动学习。','项目页正文第1—3段')
case('W04','RC265','WHILL Autonomous Service','A 共享行动决定','官网核查2026-09-18','官方产品服务说明','机场等设施内的自主代步服务。','使用者选择目的地；可在屏幕暂停，也有紧急停止按钮。','把可中止性放进行程，避免启动自动服务就失去退出机会。','F1：目的地选择与暂停影响本次服务；未找到跨行程学习证据。','官方说明不等于独立效果评估；设施服务不等于个人日常轮椅。','Autonomous Service Device Features')
case('W05','RC007','KnowNo / Robots That Ask For Help','B 承认局限并澄清','2023','CoRL研究项目页','物品操作等任务中，语言指令有多个合理解释。','当预测集合有多个选项时请求人类帮助，再收窄行动选择。','明确不知道什么，避免把猜测直接变成行动。','F1：人类帮助改变当次计划；方法不要求模型微调。','统计保证依赖校准与帮助等条件；不能视为任意环境中的安全承诺。','Abstract；Goal；Approach')
case('W06','RC008','CLARA','B 承认局限并澄清','2024','RA-L研究项目页','桌面递物；对象、接收者或要求不明确。','区分清楚、含糊与不可行命令；追问或停止。公开失败例中把Redbull认作Coca-Cola。','把理由说出来，让人能够发现“拒绝也可能有错”。','F1：澄清改变当次行动；官网未展示误识别后的持续修复。','不可行判断依赖感知与场景描述，不等于可靠的伦理判断。','Demonstrations；Failure Cases')
case('W07','RC261','LUCI轮椅辅助','C 尊重身体与信息边界','User Guide Rev F；官网','官方用户手册与产品说明','日常驾驶、近距离停靠、转移等辅助轮椅场景。','辅助减速避障；允许暂时覆盖；提供参数设置与分项数据分享。','保护应可理解、可调整，不能假设设备比使用者永远更懂情境。','F1：覆盖与设置改变辅助状态。手册记载用户反馈影响侧向靠近设置；不等于每次覆盖自动学习。','覆盖会暂时停用相关辅助；厂商说明并非独立临床验证。','Rev F印刷页7、10、16、18、22—23；Judging Smart网页','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf')
case('W08','RC232','HuggieBot 2.0 / Six Hug Commandments','C 尊重身体与信息边界','2021','HRI论文','机器人拥抱；线下32人，每人8次拥抱。','依据视觉和触觉适配拥抱，感知使用者退出信号并释放。','同意持续存在于身体动作中，开始互动不等于同意无限持续。','F1：触觉反馈改变当前拥抱。另有117人观看视频研究，不与线下人数相加。','这里是2.0，不是旧库误写的3.0；拥抱感知不能直接当作轮椅操控方案。','摘要；系统设计；线下实验','https://arxiv.org/abs/2101.07679')
case('W09','RC060','What should a robot disclose about me?','C 尊重身体与信息边界','2023','在线情境研究','机器人向他人透露用户信息的书面情境；有效样本155人。','研究比较直接、抽象、非语言和不披露等表达选项。','帮助他人不应自动获得披露全部个人信息的权限。','F0：收集人的隐私判断；没有机器人据此实时学习的证据。','真实研究中的书面情境，不是已部署的自主隐私决策系统。','§4研究设计；§5.1样本；§5.2结果')
case('W10','RC010','ICREATe','D 接受纠正并验证改变','2023','期刊研究','非专业使用者通过纠正或评价教机器人执行任务。','联合考虑知识不足和反馈歧义，按需询问并用反馈更新学习。','承认教师也可能出错，区分有效纠正与有歧义的要求。','F2：反馈进入数据与策略更新，含实验及用户研究。','把没有纠正作为隐含正反馈是方法假设；不能转译成默认同意出行或数据分享。','摘要；方法§3；反馈处理','https://link.springer.com/article/10.1007/s00521-022-08118-z')
case('W11','RC106','ARMAR-6增量行为学习','D 接受纠正并验证改变','2024','期刊研究','日常操作任务，例如协助清洁时补充缺少的工具。','根据自然语言纠正调整行为；保存改进的互动，供语义相近任务检索。','“改过”需要体现在后续行动中，并能追到哪条反馈。','F2：论文报告记忆更新和后续检索机制；有模拟定量评价及实体定性演示。','学习的是高层行为；不能据此声称新轮椅完成动力学适配或获得意识。','摘要；图1；§3；§5')
case('W12','RC154','Corrective Shared Autonomy','D 接受纠正并验证改变','2021','机器人研究论文','制造任务；6名20—27岁参与者，包含抛光、装配与铺贴。','机器人执行基准动作，人对关键任务变量进行有限纠正。','留出可控纠错通道，不必让使用者接管全部动作。','F1：人实时修正当前执行。论文说明基准行为与纠正尺度由人工设定。','没有自动学习这些尺度的结果；制造任务只能提供跨场景机制参照。','§IV-G；§V实验；§VI讨论')

seed_ids=['RC007','RC008','RC010','RC036','RC060','RC086','RC089','RC095','RC101','RC106','RC154','RC166','RC187','RC232']
excluded={
 'RC101':('初筛排除','E1 理论或综述','自传体记忆理论与综述；可作概念背景，不计核心行为案例。'),
 'RC166':('初筛排除','E1 理论或综述','伦理分析用于尊严与自主背景；本轮不作为可提取反馈闭环的核心案例。'),
 'RC187':('初筛排除','E1 理论或综述','重新学习框架，不是本次所需的已验证具体行为案例。'),
 'RC268':('初筛排除','E1 理论或综述','智能辅具伦理范围综述，列背景而非重复计入原始案例。'),
 'RC266':('未取得足够原文','U 来源不足','检索摘要可见，原文获取失败；无法核对完整方法与反馈。'),
 'RC267':('未取得足够原文','U 来源不足','机构记录打开失败；仅摘要不足以核对具体过程。'),
 'RC036':('评估后排除','E2 仅人的评价','信任修复研究讨论人的评价；本次聚焦实际控制和纠正机制。'),
 'RC086':('评估后排除','E2 事件偏离','停服与数据迁移是背景事件；缺乏本次轮椅行动协商机制。'),
 'RC089':('评估后排除','E2 事件偏离','维修与仪式主要是人的实践，不是机器人可观察的修养行为。'),
 'RC095':('评估后排除','E2 操作偏离','重置操作可说明删除机制，但不提供本次行动协商与修正行为。'),
}
audits=[]
for id in seed_ids+[r[0] for r in new]:
 c=next((c for c in cases if c['主库编号']==id),None)
 st,reason,note=excluded.get(id,('纳入','I 核心案例','具有可比较的具体行为，来源可核查；证据限制另列。'))
 audits.append(dict(主库编号=id,候选名称=lookup[id]['title'],进入途径='既有库目的性选种' if id in seed_ids else '本轮补充检索',筛选结果=st,排除代码=reason,决定理由=note,对应案例=c['案例编号'] if c else '',来源链接=lookup[id]['primary_url']))
supp=[
 ('RC261','Q03','LUCI Judging Smart','https://www.luci.com/smart'),
 ('RC261','Q03→官方导航','LUCI User Guide Rev F','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf'),
 ('RC261','Q03','LUCI Safety Report 2021（历史缓存）','https://luci.com/wp-content/uploads/2021/07/LUCI-Safety-Report.pdf'),
 ('RC262','Q01/Q02','CoNav 2025年1月设计报告','https://arxiv.org/abs/2501.09680'),
 ('RC262','Q01/Q02','CoNav 2025年7月评价报告','https://arxiv.org/abs/2507.11716'),
 ('RC263','Q02/Q09','NavChair 1996','https://cdn.aaai.org/AAAI/1996/AAAI96-222.pdf'),
 ('RC264','Q02/Q07','AbilityLab Smart Wheelchair','https://www.sralab.org/research/projects/smart-wheelchair'),
 ('RC265','Q04/Q05','WHILL Autonomous Service','https://whill.inc/au/mobility-service/how-it-works/autonomous-drive'),
 ('RC266','Q01','低成本共享控制轮椅','https://www.sciencedirect.com/science/article/abs/pii/S0026271418301082'),
 ('RC267','Q02','人工势场智能助行器','https://www.iris.unict.it/handle/20.500.11769/729611'),
 ('RC268','Q06','智能辅具伦理范围综述','https://link.springer.com/article/10.1007/s11673-025-10479-8'),
]
sources=[]
for i,id in enumerate(seed_ids,1):sources.append(dict(来源编号=f'S{i:02}',主库编号=id,来源名称=lookup[id]['title'],进入方式='目的性选种',归并说明='主记录',链接=lookup[id]['primary_url']))
seen=set()
for i,(id,q,title,url) in enumerate(supp,15):
 merge='同项目追加来源，不新增案例' if id in seen else '主记录';seen.add(id)
 sources.append(dict(来源编号=f'S{i:02}',主库编号=id,来源名称=title,进入方式=q,归并说明=merge,链接=url))
queries=[
 'smart wheelchair shared control user autonomy obstacle avoidance user study wheelchair users',
 'intelligent wheelchair shared control learning user preferences correction assistive navigation',
 'LUCI wheelchair override collision avoidance user control official',
 'WHILL autonomous wheelchair user stop destination official',
 'site.whill.inc autonomous service wheelchair stop button destination',
 'smart wheelchair ethics autonomy shared control review',
 'site.sralab.org "Smart Wheelchair" "volunteers"',
 '"HuggieBot" "six" "commandments" 2021',
 '"Adaptive Shared Control" "NavChair" Simpson Levine 1996 pdf',
]
qrows=[dict(查询编号=f'Q{i:02}',执行日期=DATE,检索入口='公开Web搜索',实际查询=q,用途='补充候选发现' if i<=7 else '原文定位与版本核查',记录口径='保存相关命名来源；未导出搜索引擎全部命中') for i,q in enumerate(queries,1)]

# Versioned snapshot before appending to the user-authorized master database.
backup=OUT/'研究底稿';backup.mkdir(exist_ok=True)
for file in ['机器人自我修养数据库.json','机器人自我修养数据库.csv']:
 dest=backup/('更新前260条_'+file)
 if not dest.exists():shutil.copy2(DB/file,dest)
for c in cases:
 r=lookup[c['主库编号']]
 r['wheelchair_review_2026_09_18']=c
 r['review_status']='2026-09-18核查核心来源与对应方法／演示；详见智能轮椅专题提取表'
 if c['主库编号']=='RC232':
  r['title']='The Six Hug Commandments: HuggieBot 2.0';r['summary']=c['具体行为'];r['evidence_boundary']=c['证据边界'];r['primary_url']=c['来源链接']
 if c['主库编号']=='RC154':r['summary']=c['具体行为'];r['evidence_boundary']=c['证据边界']
 if c['主库编号']=='RC106':r['evidence_boundary']=c['证据边界']
 if c['主库编号']=='RC060':r['evidence_nature']='实证／在线情境研究';r['summary']=c['具体行为'];r['evidence_boundary']=c['证据边界']
 if c['主库编号']=='RC010':r['primary_url']=c['来源链接']
for id in ['RC101','RC166','RC187']:
 lookup[id]['wheelchair_screening_note']=excluded[id][2]
 if id=='RC101':lookup[id]['evidence_nature']='理论／研究综述';lookup[id]['material_type']='理论与综述';lookup[id]['record_role']='理论／方法'
base['records']=list(lookup.values())
base['meta']['version']='0.2';base['meta']['updated']=DATE;base['meta']['total_unique_records']=len(base['records'])
for key,field in [('counts_by_role','record_role'),('counts_by_material_type','material_type'),('counts_by_source_quality','source_quality')]:base['meta'][key]=dict(collections.Counter(r[field] for r in base['records']))
base['meta']['provenance_mentions']['智能轮椅专题补充检索2026-09-18']=8
base['meta']['latest_update_note']='新增8项候选，专题纳入12例；纠正HuggieBot型号、隐私研究性质与反馈证据。其余旧记录未在本轮重新验证。'
(DB/'机器人自我修养数据库.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf-8')
fields=list(next(csv.DictReader((DB/'机器人自我修养数据库.csv').open(encoding='utf-8-sig'))))
flat=[{k:'；'.join(r.get(k,[])) if isinstance(r.get(k),list) else r.get(k,'') for k in fields} for r in base['records']]
writecsv(DB/'机器人自我修养数据库.csv',flat)
(DB/'机器人自我修养数据库_可读索引.md').write_text('# 机器人自我修养数据库\n\n更新：2026-09-18；268条。新专题核查不代表全库均已全文验证。\n\n'+'\n\n'.join(f"## {r['id']} {r['title']}\n\n{r['summary']}\n\n证据边界：{r['evidence_boundary']}\n\n来源：{r['primary_url']}" for r in base['records']),encoding='utf-8')
with (DB/'数据库说明与检索进度.md').open('a',encoding='utf-8') as f:f.write('\n\n## 2026-09-18 智能轮椅专题更新\n\n主库新增RC261—RC268，共268条。专题从原260条中目的性选取14条种子，另保存11条补充来源，按项目归并为8个新候选。专题共22个候选，12例纳入。该流程不是对全部268条的系统筛选。详细检索、来源归并和筛选决定见output/作业一_智能轮椅。旧260条快照已保留。\n')
writecsv(OUT/'01_核心案例提取表.csv',cases);writecsv(OUT/'02_22项筛选台账.csv',audits);writecsv(OUT/'03_25条来源与归并.csv',sources);writecsv(OUT/'04_实际检索记录.csv',qrows)
data=dict(cases=cases,audits=audits,sources=sources,queries=qrows,new_records=[lookup[x[0]] for x in new],counts={'来源记录':25,'完全重复':0,'同项目归并':3,'候选':22,'初筛排除':4,'拟核查':18,'未获足够原文':2,'完成评估':16,'评估后排除':4,'纳入案例':12,'纳入来源记录':15},date=DATE)
(OUT/'研究底稿/专题数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'tmp/wheelchair/web_search_capture.json',OUT/'研究底稿/检索工具原始返回.json')
assert len(cases)==12 and len(audits)==22 and len(sources)==25 and len(base['records'])==268
assert collections.Counter(a['筛选结果'] for a in audits)=={'纳入':12,'初筛排除':4,'未取得足够原文':2,'评估后排除':4}
print(json.dumps(data['counts'],ensure_ascii=False))
