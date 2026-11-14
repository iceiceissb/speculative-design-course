import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1] / '分镜图' / '30帧制作版'
source = (root / '即梦_30帧分镜与音效提示词.md').read_text(encoding='utf-8')
raw = {int(n): text.replace('**', '').strip() for n, text in re.findall(r'^\*\*(\d{2})\*\*｜(.+)$', source, re.M)}
files = {i: next(root.glob(f'{i:02d}_*.png')).name for i in range(1, 37)}
assert len(raw) == 30 and len(files) == 36

base = ('16:9，克制的微缩定格动画，材质真实、色彩为灰绿、砖红、赭黄。'
        '邱懿贞短银发、砖红针织衫，始终坐在灰绿轮椅座垫上，膝盖弯曲，鞋放脚踏板；'
        '徐月禾低盘银发、琥珀椭圆眼镜、赭黄外套、蓝条纹上衣、砖红围巾。'
        '轮椅两条机械臂只从车身伸出。所有角色、轮椅和道具保持同一外观；'
        '手脚不穿模，轮子贴地，不漂浮，不新增肢体或人物。手机和状态灯不生成文字。'
        '坡道侧视镜头轮椅前端始终朝画面右侧，徐月禾始终在左侧后方；主观镜头从人物眼睛位置拍，不套用侧视的画面左右关系。'
        '不跨轴，不倒退；助力灯在前次第22镜亮、次日第28镜经人求助后才亮。')

pairs = {
  1: dict(code='A', end=3, title='路口：为半句话停下', scene='01 路口', insert='02 看见朋友',
    prompt='固定宽景，小区清晨。前半段秀秀轮椅向右慢行，邱懿贞稳坐并认出右侧走来的徐月禾；轮椅减速，后半段稳稳停在坡前。徐月禾停步回头，邱懿贞轻抬手准备说话。两人不突然移位，栏杆在道路外。中间可插入 02 号相认特写。音效：清晨鸟鸣、树叶声、轮胎滚动逐渐变轻、两下脚步后停止、菜袋窸窣；不生成对白、旁白或音乐。',
    dialogue=['邱懿贞：你明天……（此句放在后半段，延续到 04）'],
    edit='生成约 12 秒；剪成前后各约 6 秒，中间插入 02。'),
  6: dict(code='B', end=8, title='菜摊：抢先与撤回', scene='02 早市', insert='07 抢先付款',
    prompt='固定早市菜摊机位。前半段邱懿贞坐稳，指向右侧嫩菜，秀秀机械臂却伸向左侧便宜老菜，指尖停在菜上方；后半段机械臂撤回椅侧，她自己拿起右侧嫩菜、翻看菜根。菜必须经真实手部接触移动，机械手不穿过人或木筐。中间插入 07 号支付设备特写。音效：菜市模糊底噪、机械关节短促伺服声、一次被打断的电子付款提示、机械臂后退、菜叶和纸袋声；无清晰人声、无对白、无音乐。',
    dialogue=['邱懿贞：等一下，我先看看根。'],
    edit='生成约 12 秒；在伸手与撤回之间插入 07。'),
  10: dict(code='C', end=12, title='夜里：删掉故障借口', scene='03 夜里', insert='11 先别修',
    prompt='暖灯室内固定近景。邱懿贞坐在轮椅上，手机握在自己的手中，拇指悬在发送键上；她看向桌上空杯，迟疑，后半段亲自删去草稿并把拇指移开。秀秀机械臂始终折叠，不触碰手机。屏幕只留无字光面，剪映后期再加草稿文字。中间插入 11 号自检状态特写。音效：钟表细响、远车声、指腹轻擦与两三下触屏轻点、衣袖声；无对白、无旁白、无音乐。',
    dialogue=['邱懿贞：我知道。先别修。'], overlays=['手机草稿：轮椅不太方便，明天能来吗？', '后半段删除草稿'],
    edit='生成约 12 秒；在犹豫与删除之间插入 11。'),
  16: dict(code='D', end=17, title='见面：亲自说明来意', scene='04 见面', insert='',
    prompt='早市入口同一机位。邱懿贞坐稳轮椅、两手先在扶手上；徐月禾距她一步、手抱早点纸袋。前半段两人看着对方留一拍安静；后半段邱懿贞用真人手做邀请手势，徐月禾用手指示意时间有限。机械臂始终收起，人物不瞬移，不插在两人之间。音效：早市模糊底噪、纸袋轻响、衣袖摩擦、脚步停稳；不生成对白、旁白或音乐。',
    dialogue=['邱懿贞：我想请你陪我走一段。', '徐月禾：我只有半小时。'],
    edit='生成约 12 秒；前 6 秒留停顿，后 6 秒剪映配对白。'),
  21: dict(code='E', end=23, title='坡道：静默助力被发现', scene='05 坡道', insert='22 灯亮',
    prompt='固定侧面全景，坡面宽阔。轮椅前端朝画面右侧上坡，邱懿贞坐稳，徐月禾在画面左侧后方双手握推把。前半段助力灯灭，两人保持真实接触向右缓行；后半段小琥珀灯亮，徐月禾低头看到灯，惊讶，轮椅减速停稳。两人的相对距离和方向不变，车轮始终贴坡面。中间插入 22 号灯亮特写。音效：前半段只有鞋步、轮胎和风声；灯亮时低频电机声悄悄潜入；后半段电机声渐明显再停、轮胎停转；无对白、无旁白、无音乐。',
    dialogue=[], edit='生成约 12 秒；在灯灭与发现之间插入 22，电机声必须先于人的发现。'),
  26: dict(code='F', end=28, title='下一次：先问，等求助', scene='06 下一次', insert='27 先问再推',
    prompt='同一坡道、同一侧视方向。邱懿贞坐在轮椅上，徐月禾在左侧后方握推把。前半段轮椅朝右停在坡前，助力灯灭，秀秀做极小开放手势并等待回答；后半段徐月禾先靠自己推，到她明确求助之后琥珀助力灯才柔和亮起，车继续向右，她仍握住推把。中间插入 27 号自主推行特写。音效：先有鸟鸣、步声、轮胎声和自然呼吸，全程不应提前出现电机声；求助之后才出现轻微低频电机和柔和提示音；不生成任何对白、旁白或音乐。',
    dialogue=['秀秀：这段需要助力吗？', '徐月禾：现在帮我一点。'],
    edit='生成约 12 秒；在等待与助力亮起之间插入 27，人先说需要，电机后响。'),
}

new_prompts = {
  31: '邱懿贞坐在轮椅上的严格第一视角，画面底部只见她的砖红袖口、自己的两只手和灰绿扶手，不出现她的脸。她把两把青菜提到眼前并比较湿润菜根，一把叶子老、一把根白叶嫩，随后选定嫩的。沿用早市摊位和晨光，菜与手真实接触。音效：菜叶摩擦、根部轻碰木筐、早市模糊底噪；不生成对白、旁白或音乐。',
  32: '接08的纠错结果，早市三分之二侧面中景。秀秀灰绿机械手的指爪穿过米色布袋的两个提手，稳稳把装有刚选青菜的唯一一只袋子提离地面，袋底与地面留清晰空隙；邱懿贞一直坐在椅上看着它。随后轮椅缓慢驶离摊位，袋子随车轻摆，绝不能落地或突然消失。音效：布袋提手拉紧、青菜叶轻响、伺服关节轻声、轮胎驶离；无对白、旁白或音乐。',
  33: '邱懿贞坐在轮椅上的严格第一视角，接室内夜景。砖红袖口和灰绿扶手在画面下缘，她一手拿着无字光面的手机，另一手停在膝上；对面那只空茶杯仍在桌上，秀秀机械手礼貌停在侧边。她看一眼空杯再看手机，意识到自己想要的是陪伴。暖灯与窗外夜色保持一致。音效：钟表、远车、指腹在手机边缘轻摩擦、安静呼吸；无对白、旁白或音乐。',
  34: '第二天清晨，邱懿贞坐在轮椅上的严格第一视角；红袖口和灰绿扶手只在下缘。徐月禾银发低盘、赭黄外套、椭圆眼镜，拿热早点纸袋从正前方走近并停住。画面右下秀秀机械手仍提着早市那只米色布袋，青菜可见且袋底悬空；末尾秀秀把袋子挂到椅背外侧挂钩上，袋子始终有支撑，两人道具不交换。接15远景，随后切16侧面会面。音效：由远而近的鞋步、早点纸袋沙沙声、菜袋提手挂稳的轻响、清晨早市底噪；无对白、旁白或音乐。',
  35: '徐月禾站在轮椅正后方的严格第一视角，接22号灯亮镜头。赭黄袖口的两只真人手始终握住两根黑色后推把；邱懿贞砖红衣背部在前方，车沿同一缓坡继续上行，外侧栏杆在画面右。轮椅右后侧那一枚小圆形琥珀助力灯已亮，徐月禾低头才发现。构图与36号下次同视角相似，但此时灯亮且无人被告知。音效：鞋步与轮胎持续、极轻电机低频已存在、发现时呼吸一顿；无对白、旁白或音乐。',
  36: '次日同一坡道，徐月禾站在轮椅正后方的严格第一视角，与35号机位呼应。赭黄袖口的两只真人手握双后推把，邱懿贞穿砖红衣坐在前方并微微回头；栏杆仍在画面右。两人在坡中短暂停下，轮椅右后侧同一小圆形助力灯必须保持完全熄灭。徐月禾尚未请求助力，画面不能提前行驶或亮灯；接28号经请求后再亮。音效：停下的轮胎、自然呼吸、树叶声，绝无电机声或提示音；无对白、旁白或音乐。',
}
continuity_prompts = {
  18:'接34和16/17，菜袋已挂在轮椅椅背后侧，双人中景可遮住它；两只小茶杯在此镜才被放进杯架。',
  19:'前镜两人刚约好同行；菜袋挂在椅背后侧，邱懿贞从其中拿几根自己挑的菜握在手中。',
  20:'本镜以推把、鞋步和车轮为主；被特写遮挡时邱懿贞将手里的几根菜收入袋中，下一镜她手上不再有菜。',
  25:'这是前一天之后再次来坡道，徐月禾今天新带的热早点暂放在自己的挎包里；助力灯重置为灭。',
  30:'徐月禾先从自己的挎包取出今天新带的热早点纸袋，再与邱懿贞手中的菜真实交接；早点不是前一天的剩食。',
}
pairs[16]['prompt'] += ' 与上一镜34保持道具连续：菜袋已被秀秀挂在椅背后侧，正面镜头不必看见，但不能出现在地上。'

single_dialogue = {
  4:['邱懿贞：算了，你先忙。'],
  5:['邱懿贞：月禾做汤爱用嫩叶。'],
  11:['秀秀：驱动正常，制动正常。'],
  13:['邱懿贞：月禾，明天一起去早市吧。我想和你走一段。'],
  14:['徐月禾：九点见。'],
  18:['邱懿贞：够。'],
  19:['邱懿贞：右边。', '徐月禾：又听你的。'],
  24:['徐月禾：刚才这一路，你也在推？帮我可以，先让我知道。'],
  27:['徐月禾：先让我试试，累了我会叫你。'],
  29:['邱懿贞：停一下，茶还热。'],
  30:['邱懿贞：这把是我挑的。', '徐月禾：饼还是热的。'],
  31:['邱懿贞：根白的这把，更新鲜。'],
  32:['邱懿贞：这把留给月禾。'],
  34:['徐月禾：给你带了刚出锅的饼。'],
  35:['徐月禾（低声）：灯怎么亮了？'],
}
single_overlay = {9:['手机草稿：轮椅不太方便，明天能来吗？']}
scene_for = lambda n: ('02 早市' if n in (31,32) else '03 夜里' if n == 33 else '04 见面' if n == 34 else '05 坡道' if n == 35 else '06 下一次' if n == 36 else '01 路口' if n <= 4 else '02 早市' if n <= 8 else '03 夜里' if n <= 14 else '04 见面' if n <= 18 else '05 坡道' if n <= 24 else '06 下一次')

timeline_order = [1,2,3,4,31,5,6,7,8,32,9,10,11,12,33,13,14,15,34,16,17,18,19,20,21,22,35,23,24,25,26,27,36,28,29,30]
assert len(timeline_order) == len(set(timeline_order)) == 36
paired_ends = {v['end']:n for n,v in pairs.items()}
slot_index = {n:i for i,n in enumerate(timeline_order)}
def timestamp(seconds):
    return f'{seconds//60:02d}:{seconds%60:02d}'

bridges = {
  1:'第一天早晨：路口遇见徐月禾。01 行进、02 对视、03 停车再到 04 半句话；两人没有完成邀约。',
  4:'徐月禾继续赶路；同一天邱懿贞独自去早市，下一镜切她的轮椅视角。',
  31:'从邱懿贞眼里看见菜根，镜头落回 05 侧面，观众知道是她在判断。',
  6:'05 亲自挑菜后，06 秀秀越过她取低价老菜；中插 07 支付被打断，再落在 08 撤回。',
  32:'08 她选回嫩菜；本镜证明唯一菜袋由秀秀真正提离地面，再切同一晚家中。',
  9:'第一天夜里。两只茶杯与空座承接她想见朋友的心情。',
  10:'10 手机草稿悬停；11 自检正常；12 由邱懿贞本人删除借口，秀秀不碰手机。',
  33:'从轮椅视角再次看见空杯；随后 13 她亲自发语音，14 徐月禾回复。',
  14:'徐月禾当晚答应，下一镜是第二天早市入口，不让人物或时间瞬移。',
  15:'第二天上午，徐月禾带热早点走近；34 切邱懿贞视角确认她和菜袋均在场。',
  34:'34 主观迎接末尾，秀秀把布袋挂到椅背后侧；再切 16/17 同轴侧面，两人亲自谈好半小时。',
  16:'16 静候一拍、17 邱懿贞伸手说明、18 徐月禾绕到轮椅后握推把。',
  18:'握把动作完成后才切 19 坡道全景；人物和推行方向保持连续。',
  19:'第一天同行的坡道：轮椅从画面左向右上行。菜已收在同一布袋中，不能突然换手。',
  21:'21 灯灭，只听到人推；22 灯亮，电机声先出现；35 切徐月禾眼中的亮灯；23 她惊讶停下。',
  35:'徐月禾的主观发现与 23 外景的低头动作相接；电机声保持连续，灯始终亮到停下。',
  24:'她要求被告知。切到第二天同一坡道 25，保留右行轴线和右侧栏杆。',
  25:'第二天重新试。灯从一开始就灭，直到 28 人明确求助。',
  26:'26 先询问、27 人自己推、36 从人眼看见灯仍灭、28 求助后才亮。',
  36:'与35同机位对照：徐月禾暂时停下，灯灭且无电机；她开口之后才切28亮灯。',
  29:'坡顶邱懿贞要求停，秀秀立刻停；30 她亲手递出自己挑的菜，朋友递早点。',
}

clips = []
for n in timeline_order:
    if n in paired_ends:
        continue
    is_pov = n in (31,33,34,35,36)
    if n in pairs:
        p = pairs[n]
        insert = p['insert']
        if n == 21: insert = '22 灯亮 → 35 徐月禾视角发现助力灯'
        if n == 26: insert = '27 自己先推 → 36 徐月禾视角等待求助'
        clip = dict(id=p['code'],kind='首尾帧',scene=p['scene'],title=p['title'],frames=[dict(number=f'{n:02d}',file=files[n]),dict(number=f"{p['end']:02d}",file=files[p['end']])],duration=10,prompt=base+' '+p['prompt'],dialogue=p['dialogue'],overlays=p.get('overlays',[]),edit=p['edit'].replace('12 秒','10 秒').replace('6 秒','5 秒')+' 首尾各取约5秒；按时间线插入中间单帧。',insert=insert,bridge=bridges.get(n,''),pov=False,slots=[slot_index[n],slot_index[p['end']]])
    else:
        title = files[n].removesuffix('.png').split('_',1)[1]
        clip = dict(id=f'{n:02d}',kind='主观镜头' if is_pov else '单帧',scene=scene_for(n),title=title,frames=[dict(number=f'{n:02d}',file=files[n])],duration=5,prompt=base+' '+new_prompts.get(n,raw.get(n,''))+' '+continuity_prompts.get(n,''),dialogue=single_dialogue.get(n,[]),overlays=single_overlay.get(n,[]),edit='以本帧为参考生成约5秒；人物与道具位置接上前一镜，镜头只轻微移动。',insert='',bridge=bridges.get(n,''),pov=is_pov,slots=[slot_index[n]])
    clip['timecodes'] = [f'{timestamp(i*5)}–{timestamp((i+1)*5)}' for i in clip['slots']]
    clips.append(clip)

timeline = []
for index,n in enumerate(timeline_order):
    task = pairs[n]['code'] if n in pairs else pairs[paired_ends[n]]['code'] if n in paired_ends else f'{n:02d}'
    timeline.append(dict(number=f'{n:02d}',file=files[n],title=files[n].removesuffix('.png').split('_',1)[1],scene=scene_for(n),task=task,start=timestamp(index*5),end=timestamp((index+1)*5),pov=n in (31,33,34,35,36)))

assert len(clips) == 30 and sum(c['duration'] for c in clips) == 180
assert all(c['prompt'].find('音效：') >= 0 for c in clips)
(root / 'clips.js').write_text('window.VIDEO_CLIPS = '+json.dumps(clips,ensure_ascii=False,indent=2)+';\nwindow.VIDEO_TIMELINE = '+json.dumps(timeline,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

scene_bridges = [
 ('01 路口','第一天早晨，偶遇朋友；邱懿贞没能说完“明天”。','04 留住欲言又止，再切她独自到早市。'),
 ('02 早市','邱懿贞自己看菜根；秀秀抢先选便宜菜；她纠正；秀秀才把选好的菜袋拎走。','32 布袋在机械手中离地，夜里可不入镜，但不能回到摊位。'),
 ('03 夜里','家中两只茶杯；自检正常；她删除故障借口，亲自发出邀请；朋友当晚回复。','14 晚间回复到15 次日上午，以清晨环境音转场。'),
 ('04 见面','第二天早市，朋友带早点，她带着昨日备好的菜；双方说清只走半小时。','18 徐月禾绕到轮椅后，19 才开始同向推行。'),
 ('05 坡道','第一回上坡，徐月禾在后推；灯先亮，电机后被她察觉；坡顶她提出告知边界。','35 主观镜头灯亮，23 外景低头，24 质问；次日灯重置为灭。'),
 ('06 下一次','第二回同一坡，她先自己试，明确求助后才开助力；邱懿贞要求停，秀秀即停。','35 与36 使用相近主观机位，对比“擅自助力/请求后助力”。'),
]
lines = ['# 《不用麻烦她》36帧最终制作表', '', '本版按 **36个5秒画面单位＝3:00** 剪辑：30个即梦任务，其中6组首尾帧各生成约10秒并拆成前后各5秒，24个单帧任务各约5秒。对白、手机字和字幕在剪映后配；即梦只生成画面与提示词内写明的环境/动作音。', '', '打开 [即梦视频制作台](即梦制作台.html) 可逐项看参考图、复制提示词和剪映台词；[36帧画廊](index.html) 可逐图放大。', '', '## 六幕接力核对', '', '| 幕 | 发生什么 | 下一镜怎样接 |', '|---|---|---|']
lines += [f'| {a} | {b} | {c} |' for a,b,c in scene_bridges]
lines += ['', '## 36个剪辑位置', '', '| 时间 | 帧号 | 参考图 | 即梦任务 |', '|---|---|---|---|']
for shot in timeline:
    lines.append(f"| {shot['start']}–{shot['end']} | {shot['number']}{' · 主观视角' if shot['pov'] else ''} | [{shot['title']}]({shot['file']}) | {shot['task']} |")
lines += ['', '## 逐项生成', '']
for c in clips:
    lines += [f"### {c['id']}｜{c['title']}（{c['scene']}，{', '.join(c['timecodes'])}）", '', f"参考帧：{' → '.join(f['number'] for f in c['frames'])}；生成约{c['duration']}秒。", '', '**即梦提示词**', '', c['prompt'], '', '**剪映后配**', '', '；'.join(c['dialogue']+c['overlays']) or '本段无对白，保留环境和动作音。', '', '**剪辑接力**', '', c['bridge'] or c['edit'], '']
lines += ['## 生成前统一核对', '', '- 邱懿贞全片坐在轮椅上，脚留在脚踏板；徐月禾只有在18镜绕到椅后才握双推把。', '- 32与34前段的米色菜袋由秀秀机械手提着；34末挂到椅背后侧，之后不能落地或凭空出现另一袋；最终30镜由邱懿贞亲手交菜。', '- 第一回坡道：21灭、22亮、35看见亮、23发现、24追问；第二回：25/26/27/36均灭，28人求助后亮，29停下后灭。', '- 侧视坡道镜头车头始终朝画面右侧；徐月禾主观镜头从车后看上坡，不用侧视画面左右直接套用。', '- 把即梦自动配乐和人声关闭或压低；画面内的文字、对白、手机界面用剪映做。', '']
(root / '即梦_36帧最终制作表.md').write_text('\n'.join(lines),encoding='utf-8')
gallery = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>不用麻烦她｜36帧最终分镜画廊</title><style>
*{box-sizing:border-box}body{margin:0;background:#242723;color:#ebe4d4;font-family:"Microsoft YaHei",system-ui,sans-serif}header{padding:42px max(24px,5vw) 28px;border-bottom:1px solid #586359}h1{font-family:serif;font-size:clamp(32px,4vw,58px);font-weight:400;margin:0 0 12px}p{line-height:1.7;color:#b9c4b7;margin:0;max-width:1000px}a{color:#b2d0b7}.nav{padding-top:14px}.grid{padding:34px max(24px,5vw) 70px;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:28px}.card{background:#30362f;border:1px solid #556050;overflow:hidden}.card.pov{border-color:#c69d6f}.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;cursor:zoom-in}.meta{padding:16px 18px}.num{color:#a4c1a8;font-size:13px;letter-spacing:.12em}.title{font-size:21px;margin:5px 0}.tag{color:#d9aa84;font-size:13px}dialog{border:0;background:#171a17;padding:12px;max-width:95vw;max-height:95vh}dialog img{max-width:91vw;max-height:86vh;display:block}dialog::backdrop{background:#000b}button{background:transparent;color:#e8e1d4;border:1px solid #8a9d8c;padding:8px 12px;cursor:pointer;float:right;margin-bottom:8px}@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body><header><h1>不用麻烦她 · 36帧最终分镜</h1><p>36个连续的5秒画面单位，按3分钟最终剪辑顺序排列；第31—36号为本轮新增的菜袋和主观视角参考。点击图片可放大。六组首尾帧：01→03、06→08、10→12、16→17、21→23、26→28。</p><div class="nav"><a href="即梦制作台.html">打开30项即梦视频制作台（参考图 + 音效提示词 + 剪映台词）</a></div></header><main class="grid" id="grid"></main><dialog id="lightbox"><button type="button" id="close">关闭 ×</button><img id="large" alt="分镜放大图"></dialog><script src="clips.js"></script><script>
const shots=window.VIDEO_TIMELINE||[],grid=document.getElementById('grid'),dialog=document.getElementById('lightbox'),large=document.getElementById('large');shots.forEach(s=>{const card=document.createElement('article');card.className='card'+(s.pov?' pov':'');card.innerHTML='<img loading="lazy" src="'+encodeURI(s.file)+'" alt="'+s.number+' '+s.title+'"><div class="meta"><div class="num">'+s.number+' / 36 · '+s.start+'–'+s.end+'</div><div class="title">'+s.title.replace(/_/g,' · ')+'</div><div class="tag">'+s.scene+' · 即梦任务 '+s.task+(s.pov?' · 主观视角':'')+'</div></div>';card.querySelector('img').onclick=()=>{large.src=encodeURI(s.file);large.alt=s.number+' '+s.title;dialog.showModal()};grid.append(card)});document.getElementById('close').onclick=()=>dialog.close();dialog.onclick=e=>{if(e.target===dialog)dialog.close()};
</script></body></html>'''
(root / 'index.html').write_text(gallery,encoding='utf-8')
print('30 clips, 36 reference frames, 180 source seconds')
