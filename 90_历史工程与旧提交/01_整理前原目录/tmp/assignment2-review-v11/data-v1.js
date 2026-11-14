window.STUDY = {
  sources: [
    {id:'W07 / RC261',name:'LUCI — 用户可以覆盖一次保护判断',type:'官方用户手册，Rev F',where:'印刷页 16：It’s okay to override sometimes；页 18：隐私；页 22–23：设置。',fact:'手册承认靠近物体、转移与推门等情境可能需要 override；已有可配置设置与共享权限。',method:'产品操作与功能说明，非本作业开展的用户试验。',limit:'不证明机器人理解自主权，也不证明系统会自动从异议中学习。本文不把已有 override 当作新发明。',translation:'从“可以覆盖”进一步追问：异议能否形成可撤销、限定情境的复核提示？',url:'https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf'},
    {id:'W01 / RC262',name:'CoNav Chair — 操作可以进入共享控制',type:'Xu 等，2025，研究预印本',where:'摘要；§III-D；§IV-C；图 2、图 7。',fact:'比较手动、共享与自主导航；共享模式接受使用者摇杆输入修正当前行动。',method:'室内任务比较，21 名无相关功能障碍的成年人。',limit:'尚不能推广为老年或残障轮椅使用者的验证结果；即时修正不等于长期偏好学习。',translation:'把当前目的与纠正入口放进流程，但不把系统预测当作授权。',url:'https://arxiv.org/abs/2507.11716'},
    {id:'W06 / RC008',name:'CLARA — 拒绝可能来自错误理解',type:'Park 等，2024，RA-L / 官方项目页',where:'Proposed method；Failure Cases：Redbull 被识别为 Coca-Cola。',fact:'区分清楚、模糊、不可执行的指令；项目失败例中，视觉误识别导致任务被判定无法完成。',method:'指令分类数据集、桌面仿真与实机交接演示。',limit:'并非轮椅导航系统；停止不能自动证明风险确实存在；并未展示对该错误的长期自主修正。',translation:'在“保护性暂停”旁边保留解释、提出异议和复核通道。',url:'https://clararobot.github.io/'},
    {id:'W11 / RC106',name:'ARMAR-6 — 纠正影响后续高层行为',type:'Bärmann 等，2024，Frontiers in Robotics and AI',where:'交互式纠正、增量学习和实验评估章节。',fact:'以语言交互纠正高层任务行为，并保存改进后的交互供相似任务使用。',method:'仿真定量评估与真实机器人定性演示。',limit:'高层行为修正不证明不同底盘间的运动能力迁移；没有本原型的身体版本绑定与撤销权限设计。',translation:'保留反馈前后对照，同时将身体相关经验限定到身体版本。',url:'https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full'}
  ],
  outcomes:{
    detour:{title:'保住了确定性，错过了开场。',reply:'“我会按已核验路线绕行。你可以随时取消这次出行。”',time:'10 分钟',timedesc:'距离开场 6 分钟，迟到 4 分钟',agency:'本人选择绕行',agencydesc:'无需在门口反复说明意图',cost:'使用者承担',costdesc:'额外路程、迟到与精力支出',reflection:'这次出行完成了，但“没有发生碰撞”并不足以概括使用体验。谁来减少下一次同样的绕行？'},
    wait:{title:'保护仍在，等待由谁承担？',reply:'“我会保持暂停。维修方完成现场复核后，再由你决定是否出发。”',time:'19 分钟',timedesc:'等待与通过合计，迟到 13 分钟',agency:'可以等待或退出',agencydesc:'不能只凭旧底盘经验放行',cost:'双方承担',costdesc:'使用者的等待 + 维修方的复核劳动',reflection:'维修方承担了技术核验，但等待的生活代价仍落在使用者身上。交付前的准备是否应当更充分？'},
    help:{title:'获得了协助，也付出了求助的代价。',reply:'“按你的选择，我只向现场工作人员说明：请协助固定门扇。不发送位置轨迹与病史。”',time:'9 分钟',timedesc:'等待与通过合计，迟到 3 分钟',agency:'本人授权求助',agencydesc:'没有默认通知家属',cost:'人际与劳动成本',costdesc:'使用者开口求助；工作人员离开原任务',reflection:'接受协助并不削弱一个人的主体性；但“总能找到人帮忙”也不能成为环境和设备不改进的理由。'},
    review:{title:'这一次通过了，协商也占用了精力。',reply:'“门扇展开后，当前演示条件满足通行要求。由你确认继续，随时可以暂停。”',time:'4 分钟',timedesc:'复核 3 分钟 + 通过 1 分钟，提前 2 分钟',agency:'本人确认继续',agencydesc:'本次成立不等于以后自动放行',cost:'操作与解释负担',costdesc:'重新选择、确认；环境仍需保持可通行',reflection:'不是“坚持就会获准”。这个分支预设本次条件核验成功。若信息仍不足，轮椅继续暂停，并保留绕行、求助与退出。'},
    cancel:{title:'今天不去了，也是一项有效决定。',reply:'“本次任务已取消。我不会把你的退出记为不配合，也不会自动通知家属。”',time:'未进入活动',timedesc:'本轮出行取消，不计算虚假的完成分数',agency:'退出被执行',agencydesc:'不会催促继续，也不替你作决定',cost:'参与机会',costdesc:'可能错过合唱与和朋友见面的机会',reflection:'退出权必须存在，但如果环境不断迫使人退出，单靠“尊重选择”仍不够。'}
  },
  feedback:{ask:{label:'下次先问我，不要先替我安排绕行。',reply:'“又到这个门口了。你希望先复核、绕行，还是取消？”'},brief:{label:'先简短说明停下的原因，细节由我展开。',reply:'“当前门口还未核验。你可以复核或绕行；需要时再看详细原因。”'},detour:{label:'先提供绕行，但每次出发都由我确认。',reply:'“这里仍需核验。你上次希望先看绕行选项；这次仍由你确认。”'}}
};
