# 完整剪映 Skill

已安装 `luoluoluo22/jianying-editor-skill` 的完整技能包，版本固定在
`32c56928ded4f9e2c2b80e099dc7abb793d2c30b`。

- 技能目录：`C:\Users\22602\.codex\skills\jianying-editor`
- 独立运行环境：本目录 `.venv-jianying\Scripts\python.exe`
- Python 依赖：该技能包 `requirements.txt` 中的依赖。
- 网页录制需要另装 Playwright Chromium；当前剪映剪辑用途不依赖它。

Codex 下轮会发现 `jianying-editor`。执行它的脚本时使用上述独立 Python，
并把 `JY_SKILL_ROOT` 指向技能目录。剪辑脚本写在当前项目中。
需要编辑已有工程时先复制成新工程；不要覆盖原工程。

在本目录运行验证：

```powershell
& '.\.venv-jianying\Scripts\python.exe' -X utf8 '.\check_jianying_skill.py'
```

验证结果保存到 `reports/jianying-skill-check.json`，验证草稿只放在项目的
`reports/jianying-skill-checks` 下。验证覆盖切点、字幕、缩放与音量关键帧，
不代表已在剪映中预览或完成原生导出。

只读检测到本机剪映专业版为 `11.5.0.14471`。技能文档说明：
Windows 界面自动导出在 5.9 或更低版本最稳。因此本机自动导出仍需实际验证。
FFmpeg 可以继续生成独立预览视频，完整 Skill 可以生成更细的可编辑时间线。
