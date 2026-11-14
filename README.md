# 不用麻烦她 · 把路走通

思辨设计课程项目：从“轮椅该听谁的”出发，讨论智能辅助、人的自主性、信息授权，以及无障碍环境由谁持续改善。

本仓库保存课程调研、早期构想、35 版剧本、10 版交互 Demo、角色与分镜、AI 视频制作过程、成片和结课材料。归档日期：2026-11-14。

![《不用麻烦她》影片封面](05_汇报与成片/V02_不用麻烦她_动作与声音修订_2026-10-19/封面.jpg)

## 先看作品

| 内容 | 入口 |
| --- | --- |
| 《不用麻烦她》V02 成片 | [下载 1080p 字幕版，4 分 37 秒](https://github.com/iceiceissb/speculative-design-course/releases/download/course-archive-2026-11-14/film-v02-1080p-subtitled.mp4) |
| 设计说明 | [5 页 PDF](https://github.com/iceiceissb/speculative-design-course/releases/download/course-archive-2026-11-14/design-brief.pdf) |
| 最终汇报 | [21 页 PowerPoint](05_汇报与成片/04_最终提交作业/不用麻烦她_最终结课汇报.pptx) |
| 《把路走通 · 晴溪两岸》v3 | [Windows 试玩包](https://github.com/iceiceissb/speculative-design-course/releases/download/course-archive-2026-11-14/sunny-path-v3-windows.zip) · [玩法、按键与工程说明](02_Demo版本/D10_把路走通_Unity_v3/README.md) |
| 完整结课提交 | [影片、PDF、PPT 和可玩 Demo 一起下载](https://github.com/iceiceissb/speculative-design-course/releases/download/course-archive-2026-11-14/final-submission-2026-10-23.zip) |
| 课程要求与作品对应 | [作业要求对照与试玩指引](05_汇报与成片/04_最终提交作业/01_作业要求对照与试玩指引.md) |
| 全部视频与过程资产 | [Releases](https://github.com/iceiceissb/speculative-design-course/releases/tag/course-archive-2026-11-14) · [逐项文件目录](docs/media-catalog.md) |

试玩包解压后运行其中的启动脚本；分享时保留完整文件夹。程序为 Windows 64 位本地原型，无需安装 Unity 或 Blender。

## 从构想到作品

1. [研究入口](04_研究资料/资料入口.md)：课程要求、作业一、机器人案例库、论文与参考作品。
2. [讨论与构想](00_当前创作/01_讨论共识与待定问题.md)：人物、故事冲突、反馈和设计选择。
3. [剧本版本索引 S01—S35](01_剧本版本/00_版本顺序.md)：轮椅、医院与让行、城市礼仪、两位老友四个阶段。
4. [《不用麻烦她》v9 完整剧本](01_剧本版本/04_两位老友/S35_不用麻烦她_v9/不用麻烦她_v9_完整剧本.md)与 [F11 的 72 镜分镜计划](03_分镜与角色/F11_不用麻烦她_v9_视频生成分镜/00_先看这里.md)。
5. [Demo 版本索引 D01—D10](02_Demo版本/00_版本顺序.md)：网页原型到 Unity 双视角街区。
6. [影片 V02 交付说明](05_汇报与成片/V02_不用麻烦她_动作与声音修订_2026-10-19/00_交付说明.md)：动作、对白、环境声、配乐与剪映工程。
7. [AI 视频完整工作流与产品研究](04_研究资料/06_AI视频工作流与产品研究_2026-11-14/00_先看这里.md)：制作流程、可复制提示词、成本与产品分析。

## 目录

保留原项目的编号和版本命名，使剧本、素材、代码与制作记录可以相互对照。根目录补充 README、归档文档和恢复脚本。

```text
00_当前创作/             讨论、早期构想、制作决策与交付记录
01_剧本版本/             S01—S35，含早期稿和定稿
02_Demo版本/             D01—D10，网页及 Unity / Blender 源文件
03_分镜与角色/           F01—F11、角色候选、分镜图与提示词
04_研究资料/             课程要求、案例库、论文、产品与工作流研究
05_汇报与成片/           汇报、提交文档、影片索引与剪辑工程描述
06_制作工具/             AI 视频工作流、Bodystorming Agent、核对脚本
07_面试准备/             项目复盘与产品研究表达
90_历史工程与旧提交/     早期过程、旧原型与工具快照
99_备份与整理记录/       整理说明、迁移清单与版本核对
archive-expanded/        旧压缩包中独有的可浏览文档
docs/                    链接、媒体目录、存储说明与校验清单
scripts/                 下载与恢复脚本
```

## 下载与继续制作

文档、源码、分镜图和适合直接浏览的材料保存在 Git；大型视频、音频和运行文件保存在同仓库的 Release 附件。每个原文件都有路径和 SHA-256 记录，重复内容共用一份附件。

只看作品可下载上面的成片或完整提交包。需要原始镜头、剪映素材和可运行工程时，先克隆仓库，再运行：

```powershell
python scripts/restore_archive.py --download --scope current --output ../course-restored
```

私有仓库使用已登录的 GitHub CLI 下载。`--scope all` 同时恢复历史材料和旧压缩包展开内容；脚本会先验证附件校验值，再恢复原文件名。详情见[存储、恢复与归档范围](docs/ARCHIVE.md)。

## 工具、链接与来源

- [所有外部链接及原出处](docs/links.md)
- [案例来源、AI 工具使用与证据边界](05_汇报与成片/04_最终提交作业/02_案例来源与AI工具使用.md)
- [AI 视频工作流源码](06_制作工具/T01_AI视频工作流/README_先看这里.md)
- [场外 · Bodystorming Agent](06_制作工具/T02_Bodystorming_Agent/README.md) · [可运行分享包](https://github.com/iceiceissb/speculative-design-course/releases/download/course-archive-2026-11-14/bodystorming-workbench.zip)
- [归档统计](docs/archive/summary.json)、[逐文件清单](docs/archive/file-manifest.jsonl)与[旧压缩包目录](docs/archive/zip-catalog.md)

影片和分镜属于 AI 辅助生成的设计虚构；Unity 中的维修、受理和反馈由程序规则模拟。项目未连接实体轮椅或真实政务系统。第三方素材、论文和软件保留各自来源与授权，见 [NOTICE.md](NOTICE.md)。
