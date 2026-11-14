# 《不用麻烦她》本地 AI 视频工作流

双击 **启动工作流.cmd**，浏览器会打开本地选片台。也可以访问 http://127.0.0.1:8765 。关闭服务窗口后页面不再更新；后台启动的服务可双击 **停止工作流.cmd** 关闭。

这套流程包含：Seedance 2.5 视频任务 → 保存和整理候选 → 人工选片 → 可调时间线 → FFmpeg 粗剪 MP4 与剪映草稿。

## 先用现有素材

首批演示素材来自你已有的即梦视频，标为“即梦导入”；这些素材不是本次通过 Seedance API 新生成的。E演示素材由两段已有视频本地拼接成10秒，末尾约0.9秒停帧，以验证首尾两段的剪辑交接。其余任务导入原视频，来源记录在 `reports/演示素材来源.json`。演示只验证生产流程，不代表最终镜头选择。

1. 在“镜头选片”播放候选、选用版本。
2. 在“时间线”设置素材截取起点和使用时长。
3. 点击“输出粗剪与剪映草稿”。结果保存在 `exports` 下，每次新建目录。
4. 双击 **安装到剪映.cmd**，将最近一次草稿复制到本机剪映草稿目录。它不会覆盖已有工程。刷新剪映草稿列表后打开，继续精剪并导出。

新即梦素材可以放进 `inbox/E`、`inbox/22`、`inbox/35`、`inbox/24` 对应目录，再点击“扫描导入素材”。原文件保留；工作流会复制到候选目录。

## 接入 Seedance

1. 在火山方舟开通 Seedance 2.5 权限并创建 API Key。开通条件、费用以官方控制台为准。
2. 双击 **配置API.cmd**，在本地终端输入 Key，输入不会显示。Key 存入当前文件夹 `.env`，不出现在网页、任务表或聊天里。
3. 在选片台点击“查看生成计划”，核对任务与素材秒数，再点击“开始生成”。首轮4个任务合计25秒源素材，剪成约20秒。
4. 首轮默认每任务1个候选。需要重抽时，点击该镜头“新增一个候选”。每次是新的付费生成。

默认模型 `doubao-seedance-2-5-260628`，720p、16:9、有声视频。模型ID和参数可在 `project.json` 修改；不要把其他供应商地址直接填入官方地址字段。修改后会记录新的参数版本。

项目累计上限是 **8个API任务、50秒生成素材**，本轮最多新增4个任务。这个限制控制调用数量与素材秒数，不是人民币预算保证；分辨率等参数会影响费用。需要扩展时先查看已生成记录，再调整 `limits`。

网络超时不自动重发创建请求。已取得ID的任务可继续查询；提交结果不确定的候选会标记“需核对任务ID”。到方舟控制台找到对应任务后可关联：

```powershell
python -X utf8 workflow.py attach-task --candidate 候选ID --task-id 方舟任务ID
python -X utf8 workflow.py generate
```

生成失败不会自动重抽。新候选需显式请求。若暂停服务时生成仍在云端执行，下次继续运行首轮会接着查询已记录任务，不会自动取消云端任务。

## 剪辑与声音

E为10秒首尾帧任务，前5秒用于21镜，后5秒用于23镜；22、35、24各生成5秒，粗剪截取3、4、3秒。切点可以调整。

字幕仅为短试片占位，完整台词保留在各任务中。当前没有自动生成角色配音。MP4的字幕另存为SRT，网页预览显示VTT字幕；剪映草稿中包含可编辑字幕轨道。修改片长后需复核字幕。

已有配音或音效可放入本文件夹，例如 `audio/徐月禾.wav`，并在 `project.json` 的 `audio_tracks` 中添加：

```json
{"file":"audio/徐月禾.wav","start":9,"source_start":0,"duration":2.5,"volume":1}
```

环境音来自选中视频。新增音轨会在粗剪中混合、在剪映中单独成轨。此流程不提供自动音频识别或对白对口型。

## 命令行

```powershell
python -X utf8 workflow.py doctor
python -X utf8 workflow.py plan
python -X utf8 workflow.py generate
python -X utf8 workflow.py generate --only 35 --variants 2
python -X utf8 workflow.py import --job 35 --file "D:\素材\镜头35.mp4"
python -X utf8 workflow.py assemble --kind both
```

依赖：本机Python、FFmpeg、FFprobe。剪映草稿库已随项目保存，不需要安装整个社区工具集。当前草稿格式基于社区对新版剪映的适配；实际打开和导出效果需以本机剪映预览为准。可独立输出MP4，不依赖剪映自动导出按钮。

## 来源与验证边界

- 官方接口与图片Base64输入：[创建视频任务](https://docs.volcengine.com/docs/ark/create-video-generation-task-api?lang=zh)
- 官方模型与调用流程：[Seedance 2.5教程](https://docs.volcengine.com/docs/ark/seedance-2-5?lang=zh)
- 草稿库：[jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill)，版本固定在 `32c56928ded4f9e2c2b80e099dc7abb793d2c30b`；底层源于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft)。这里只调用其草稿库，不执行社区的一键安装或UI导出脚本。

实际API调用验证情况见 `reports/验收说明.md`。没有API Key时，测试仅覆盖本地功能和模拟服务器，不证明账户权限或线上模型一定可用。
