# Cursor、OpenCode、GitHub Copilot

核对日期：2026-10-17。三个产品都可覆盖多种入口，本篇按各自最值得研究的工作方式展开。

## 一、先抓住三种产品重心

| 产品 | 研究时最值得抓住的主线 | 对用户的价值假设 |
| --- | --- | --- |
| Cursor | 编辑过程、Agent 执行、云端任务和审查的衔接 | 减少开发者在理解、修改和验证间的切换 |
| OpenCode | 可配置的 Agent、模型与客户端／服务端 | 让用户或团队控制执行方式和集成方式 |
| GitHub Copilot | 从 IDE、终端到仓库和 PR 的团队工作流 | 在现有协作过程中委托、审查和交付 |

这是基于官方功能的产品分析，不是说某种能力只属于一家。

---

## 二、Cursor

### 2.1 产品结构

| 部分 | 接管的任务跨度 | 用户主要怎样检查 |
| --- | --- | --- |
| Tab | 正在进行的局部编辑与后续修改 | 立即接受、部分接受或继续输入 |
| Agent | 一个需要探索、编辑和运行的任务 | 对话、文件改动与运行结果 |
| Cloud Agents | 可异步委托的工程任务 | 运行记录、PR 和成果证据 |
| Bugbot | 代码审查与相关修复 | 审查意见、修改和后续验证 |

Tab 基于近期编辑、周围代码及错误信息提供补全；Agent 可使用搜索、编辑和终端等工具。Cloud Agents 在云端独立环境运行，官方注明其旧称是 Background Agents。[Tab](https://cursor.com/docs/tab/overview)、[Agent](https://cursor.com/docs/agent/overview)、[Cloud](https://cursor.com/docs/cloud-agent)

### 2.2 为什么 Tab 是一个独立的产品问题

用户正在输入时，不需要每次停下来解释任务。建议必须足够快、足够贴近意图，并且容易拒绝。

**产品判断：**Tab 应研究接受后的保留程度，而非只看接受次数。用户先接受再大量删除，可能只是为了跳过当前建议。

可衡量：建议接受、后续撤销／重写、错误引入、用户被打断的程度。低延迟与更强推理之间需要按场景权衡。

### 2.3 Agent 为什么需要代码上下文

Agent 的官方结构包含指令、工具和模型，产品会为不同模型调整执行方式。当前文档也有协调 Agent 组织较大项目的入口。[Agent 结构](https://cursor.com/docs/agent/overview)

**产品判断：**用户选中的代码表达当下注意力，仓库搜索提供关联信息，两者都重要。读全仓库会增加成本；只看选区又可能漏掉调用方和测试。

适合追问：系统怎样解释为什么要改这几个文件？用户能否限制改动范围，并在执行中纠正方向？

### 2.4 云端 Agent 改变了审查方式

官方文档描述了截图、视频和日志等成果证据，以及远程桌面接管。它们让用户可以直接体验修改后的软件，而不只阅读总结。[Cloud Agents](https://cursor.com/docs/cloud-agent)

**产品判断：**异步委托减少了实时指导，却增加了环境准备和结果核验的责任。对 UI 修改，可操作预览通常比一句“已完成”提供更多信息，但仍需覆盖错误与边界状态。

### 2.5 权限：别把新版本仍讲成只有“逐步批准或全部放行”

当前官方 Run Modes 包括 Auto-review、Allowlist、Run Everything 等，分别组合允许规则、沙箱或分类审核。云环境的执行政策又有不同。[运行模式](https://cursor.com/docs/agent/security/run-modes)

**产品判断：**设计上应区分“这次动作被策略允许”“风险分类器认为可行”和“用户明确选择了这个后果”。三者提供的保证不同。

### 2.6 Bugbot 的独立价值

Bugbot 把审查放进代码变更过程；Autofix 可以启动 Cloud Agent 处理发现的问题。[Bugbot](https://cursor.com/docs/bugbot)

**产品判断：**审查意见只有被理解、值得处理并实际改善代码，才产生价值。需要检查误报、重复意见、修复是否引入新问题，以及审查成本。

### 2.7 分发与商业化

编辑器里的高频小操作可帮助形成习惯，更长任务和云执行扩大使用范围。Cloud 的官方说明涉及模型使用与支出控制；实际套餐和计费规则应核对当期页面。[Cloud 计费说明](https://cursor.com/docs/cloud-agent)

**分析重点：**从个人输入效率扩展到任务交付时，付费价值能否同时覆盖环境、审查和团队协作，而不是只累加模型调用。

### 2.8 面试值得问的改进题

用户正在做小改动时，系统怎样避免升级为大规模重构？建议可显示本次预期范围、超出范围的原因和可选方案，然后验证范围误判与返工是否下降。

---

## 三、OpenCode

### 3.1 定位：研究可配置的执行方式

这里指 `anomalyco/opencode`，官方仓库将其定义为开源 Coding Agent，不与其他同名项目混用。[官方仓库](https://github.com/anomalyco/opencode)

OpenCode 的文档提供 Agent、模型、工具和权限配置，并有 TUI 与服务端的分工。[概览](https://opencode.ai/docs/)、[Agent](https://opencode.ai/docs/agents/)、[Server](https://opencode.ai/docs/server/)

**产品判断：**对重视可配置性与集成的人，价值来自模型、执行流程和界面之间能够组合。配置空间增加的同时，也会增加环境准备和排错负担。

### 3.2 主 Agent 和子 Agent

当前文档区分 primary agent 与 subagent；Build、Plan 是不同权限和工作方式的主入口，专门子任务可以交给子 Agent。[Agent 类型](https://opencode.ai/docs/agents/)

**产品判断：**这里可以研究“角色和模型”和“权限”怎样组合。Plan 有怎样的边界，应由具体配置决定，不应只从名字推断。

### 3.3 模型可换，体验不一定相同

官方模型配置支持不同 provider、模型及参数，并允许按 Agent 覆盖设置。[模型配置](https://opencode.ai/docs/models/)

**产品判断：**更换模型会影响工具调用、指令遵循、上下文处理、速度和成本。兼容 API 只是接口层的一部分，不能证明所有模型在相同 Harness 下表现一致。

如果准备 DeepSeek 相关面试，可以设计“相同任务、不同模型”与“相同模型、不同执行方式”两类实验，分别观察能力和 Harness 的作用。

### 3.4 权限配置

`allow`、`ask`、`deny` 分别表示自动执行、询问与阻断。当前自动批准模式也仍保留显式 deny 的作用。[权限](https://opencode.ai/docs/permissions/)

**产品判断：**权限配置越灵活，越需要说明最后生效的规则。PM 可以关注用户能否解释“为什么这次被允许、那次被阻断”，而非只看是否存在配置项。

### 3.5 客户端／服务端结构

`opencode serve` 提供 HTTP 服务，TUI 也是连接服务端的客户端，文档提供程序化接口与认证配置。[Server](https://opencode.ai/docs/server/)

**产品判断：**交互界面和执行循环分开后，可以接不同客户端，但会引入连接、认证、事件同步、会话恢复和部署管理等问题。

它和 MCP 的区别：客户端／服务端接口用于控制 Agent；MCP 用于给 Agent 连接工具与信息。两层可以同时存在。

### 3.6 成本和维护责任

研究总成本时，应包含模型／工具调用、运行环境、部署和人工维护，不能只看客户端是否收费。不同 provider 的账号和使用条款也应分别核对。

**面试问题：**哪些默认设置能让新用户快速完成第一个任务，同时不削弱高级用户的配置能力？

### 3.7 适合你的验证任务

在一个单独的小项目中，要求它理解代码、做一处反馈状态修改、运行检查，再解释修改范围。记录配置步骤、工具失败、人工介入和最终结果。无需把所有模型都跑一遍才开始学习。

---

## 四、GitHub Copilot

### 4.1 产品已经超过代码补全插件

截至核对，GitHub 官方列出 Copilot app、CLI、IDE、GitHub 上的异步 Agent 等入口，也描述第三方 Agent 与自动化工作流。面试时不宜停留在早期补全产品的理解。[产品入口](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents)

### 4.2 按用户阶段拆

| 阶段 | 典型能力 | PM 要验证什么 |
| --- | --- | --- |
| 边写边改 | 补全、对话、IDE Agent | 建议是否符合项目，是否被大量返工 |
| 委托任务 | CLI、桌面或云端 Agent | 输入、环境与任务边界是否充分 |
| 团队交付 | 分支、PR、代码审查 | 变更是否容易理解、验证和合并 |
| 持续维护 | 事件触发或定时自动化 | 是否减少积压，也是否制造噪声 |

这些不是所有入口完全相同的功能清单。组织策略、编辑器支持和配置会影响实际体验。

### 4.3 IDE Agent 与云端 Agent

IDE Agent 可以选择相关文件、修改、运行命令并响应用户的中途反馈；当前文档说明命令批准与自动执行会受配置影响。[IDE Agent](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-agent-mode)

GitHub 上可把任务异步交给云端 Agent，在云环境研究、计划、修改分支并提交 PR 供审查。[GitHub 入口](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)

**产品判断：**前者更接近共同操作，后者更接近委托和验收。相同的需求，用户需要付出的实时指导和事后审查工作不同。

### 4.4 为什么 GitHub 工作流有分发优势

这是基于入口位置的分析：任务、代码、讨论、检查和审查原本就在仓库协作中。把 Agent 放在这些节点，可以减少重新输入背景和迁移结果的负担。

同时，团队仍要维护好 Issue 质量、测试、仓库指导和审查责任。平台能接收一个任务，不代表任务已经可执行。

### 4.5 多 Agent 入口的治理问题

官方描述支持把工作交给第三方 Coding Agent，并通过 PR 流程返回变更。[Agent 入口说明](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents)

**产品判断：**当同一协作平台容纳多个 Agent，选择、权限一致性、结果格式和费用解释会成为平台问题。用户可能不希望先理解每家底层执行细节，才有能力提出一个小修改。

### 4.6 指标应该深入到团队交付

建议观察：任务被接受后实际完成的比例、PR 审查时间、修改请求次数、合并后的缺陷和回滚，以及人工维护负担。

不能只统计打开了多少个 PR。大量无人愿意审查的变更也可能增加团队积压。

### 4.7 商业化观察

团队分发和治理是重要付费场景；AI 使用还有额度与成本管理。当前 IDE 文档使用 GitHub AI Credits 的表述，具体计划与账单应以当期官方页面为准。[使用与额度说明](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-agent-mode)

---

## 五、三者与 Codex、Claude Code 怎样比较

| 观察角度 | 适合重点研究的对象 | 比较时别漏掉什么 |
| --- | --- | --- |
| 人正在编辑时的细颗粒体验 | Cursor Tab、Copilot 的编辑器能力 | 接受后的重写与错误成本 |
| 从自然语言推进工程任务 | Codex、Claude Code、Cursor Agent、OpenCode、Copilot Agent | 环境、权限、上下文和最终审查 |
| 客户端与执行系统的集成 | Codex app-server、OpenCode Server 等 | 连接、身份、事件与恢复 |
| 从 Issue 到 PR 的团队协作 | Copilot、各家的仓库／云端能力 | 输入质量、审查负担和平台政策 |
| 异步交付与可体验证据 | 各家的 Cloud Agent | 预览、测试、人工接管和成本 |

**值得形成的判断：**产品入口正在重叠；具体任务中谁更好用，需要在相同输入、执行条件和验收标准下验证。主要工作方式的差别仍能帮助解释设计取舍。
