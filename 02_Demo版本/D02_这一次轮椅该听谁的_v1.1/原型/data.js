window.STUDY = {
  "sources": [
    {
      "id": "W07 / RC261",
      "name": "LUCI — 用户可以覆盖一次保护判断",
      "type": "官方用户手册，Rev F",
      "where": "印刷页 16：It’s okay to override sometimes；页 18：隐私；页 22–23：设置。",
      "fact": "手册承认靠近物体、转移与推门等情境可能需要 override；已有可配置设置与共享权限。",
      "method": "产品操作与功能说明，非本作业开展的用户试验。",
      "limit": "不证明机器人理解自主权，也不证明系统会自动从异议中学习。本文不把已有 override 当作新发明。",
      "translation": "已有覆盖功能说明控制存在选择空间；本次比较谁发起确认，并允许对服务规则提出异议。",
      "url": "https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf"
    },
    {
      "id": "W01 / RC262",
      "name": "CoNav Chair — 操作可以进入共享控制",
      "type": "Xu 等，2025，研究预印本",
      "where": "摘要；§III-D；§IV-C；图 2、图 7。",
      "fact": "比较手动、共享与自主导航；共享模式接受使用者摇杆输入修正当前行动。",
      "method": "室内任务比较，21 名无相关功能障碍的成年人。",
      "limit": "尚不能推广为老年或残障轮椅使用者的验证结果；即时修正不等于长期偏好学习。",
      "translation": "人的操作可以介入控制；进一步追问是否默认使用者始终愿意、能够主动解释。",
      "url": "https://arxiv.org/abs/2507.11716"
    },
    {
      "id": "W06 / RC008",
      "name": "CLARA — 拒绝可能来自错误理解",
      "type": "Park 等，2024，RA-L / 官方项目页",
      "where": "Proposed method；Failure Cases：Redbull 被识别为 Coca-Cola。",
      "fact": "区分清楚、模糊、不可执行的指令；项目失败例中，视觉误识别导致任务被判定无法完成。",
      "method": "指令分类数据集、桌面仿真与实机交接演示。",
      "limit": "并非轮椅导航系统；停止不能自动证明风险确实存在；并未展示对该错误的长期自主修正。",
      "translation": "在“保护性暂停”旁边保留解释、提出异议和复核通道。",
      "url": "https://clararobot.github.io/"
    },
    {
      "id": "W11 / RC106",
      "name": "ARMAR-6 — 纠正影响后续高层行为",
      "type": "Bärmann 等，2024，Frontiers in Robotics and AI",
      "where": "交互式纠正、增量学习和实验评估章节。",
      "fact": "以语言交互纠正高层任务行为，并保存改进后的交互供相似任务使用。",
      "method": "仿真定量评估与真实机器人定性演示。",
      "limit": "高层行为修正不证明不同底盘间的运动能力迁移；没有本原型的身体版本绑定与撤销权限设计。",
      "translation": "让反馈改变后续提问规则，同时给现场记录设置身体与地点边界；这不是在网页内实现学习模型。",
      "url": "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full"
    }
  ]
};
