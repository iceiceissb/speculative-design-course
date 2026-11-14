# 存储、恢复与归档范围

## 文件如何存放

| 内容 | GitHub 位置 |
| --- | --- |
| 文档、源码、分镜图、小型办公文件与模型 | 仓库内原编号目录 |
| V01 / V02 成片、设计说明、试玩包、最终提交包 | Release 中可直接下载的独立附件 |
| 原始视频、声音、较大文件、游戏运行依赖、历史二进制资产 | `course-media-*.zip` 附件中的 SHA-256 内容对象 |
| 旧 ZIP 中的内容 | 展开、去重后按上述规则保存；独有文档在 `archive-expanded` |
| 原路径、重复关系、附件位置、字节数和哈希 | `docs/archive/file-manifest.jsonl` |

GitHub 普通 Git 文件有大小限制；Release 适合分发视频和运行包。附件分包保持在单文件限制以内。参考：[大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[Releases 说明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)。本次使用普通仓库和 Release，没有启用付费 LFS 或新增生成任务。

## 恢复原路径

安装 Python 3.10+ 和 GitHub CLI，登录可以访问本仓库的 GitHub 账号。在仓库根目录运行：

```powershell
python scripts/restore_archive.py --download --scope current --output ../course-restored
```

脚本下载所需附件到 `.archive-downloads`，验证 SHA-256，按清单恢复文档、声音、视频和程序的原始相对路径。重复内容会恢复为各原路径的独立文件，方便原 HTML 素材页和剪映工程引用。

- `--scope current`：恢复 00—07 目录，适合继续制作。
- `--scope all`：加上 90、99 和旧 ZIP 的展开内容。
- `--assets-dir <目录>`：使用已经下载的附件；省略 `--download` 可完全离线恢复。
- `--list`：只显示将要恢复的文件数和所需附件。

旧 ZIP 的成员恢复到 `<原压缩包路径>.contents/`，内容和原成员名可追溯；ZIP 容器本身没有重复上传，也不声称复原其原始压缩字节。新生成的完整结课提交包提供即用版本。

剪映草稿保留生成时的材料和路径记录。跨电脑打开时，可能需要在剪映中重新定位素材目录。视频工具的 API 凭据需自行配置，Python / Node 依赖和模型需按原工具说明安装。

## 本次归档处理

工作区原文件未移动或覆盖。发布副本位于工作区的 `06_制作工具/T04_GitHub归档_2026-11-14/repository`。

API 密钥、`.env`、本机数据库、浏览器缓存、虚拟环境、Unity 的 Library / Temp、`node_modules` 和可再生的大型构建中间文件没有上传。具体路径与原因见 [excluded-files.json](archive/excluded-files.json)。如有资料内嵌凭据，发布副本用占位符替换，处理记录见 [sanitization-report.json](archive/sanitization-report.json)。

为便于 GitHub 浏览，Markdown 中指向当前工作区的绝对链接会转换为仓库相对链接；指向大文件的链接会转向 Release 或媒体目录。发生变换的原文也作为内容对象归档，恢复脚本可还原原记录。

外部链接从原文档、代码、数据和 Office 超链接中提取，统一列在 [links.md](links.md)。链接保留原材料的记录时间；没有逐个重新核实外部网页，也不把旧价格或旧模型能力视为当前状态。

## 核对记录

- `archive/summary.json`：文件、内容去重、附件和链接统计。
- `archive/file-manifest.jsonl`：逐文件位置和 SHA-256。
- `archive/expanded-archives.json`：原 ZIP 成员、大小与 CRC。
- `archive/release-assets.json` 与 Release 中的 `SHA256SUMS.txt`：附件大小与 SHA-256。
- `archive/validation.json`：发布前实际执行的完整性与本地恢复检查结果。
