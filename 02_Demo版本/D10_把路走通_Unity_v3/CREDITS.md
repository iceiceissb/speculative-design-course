# 资产来源与改动

## 本版实际使用的第三方角色

- 作者：Quaternius。
- 原包：[Ultimate Animated Character Pack](https://quaternius.com/packs/ultimatedanimatedcharacter)，2019 年发布。
- 授权：包页面及官方随包 License.txt 均标注 **CC0 1.0 Universal**。
- 下载：2026-10-18，从包页面链接的官方 Google Drive 的 FBX 文件夹下载。
- 使用：Casual_Female.fbx、Casual_Male.fbx、OldClassy_Female.fbx，及文件内 Idle、Walk 动画。原始文件保存在 ThirdParty/Quaternius，游戏导入副本在 UnityProject/Assets/Resources/NPCs。
- 本项目改动：在 Blender 中整理单位和骨骼导出，仅保留 Idle、Walk 两段动画；统一材质、肤色和衣物配色，按实际变形后的网格校正大小与朝向，重新计算平滑法线，使用 Legacy Animation 播放。没有声称这些行人由本项目原创建模。
- 试玩包保留 Build/Licenses/Quaternius-CC0.txt。

## 考察但未用于游戏的资源

[Kenney Mini Characters](https://kenney.nl/assets/mini-characters)，官方免费 CC0 包。已比较预览、模型和授权；头身比例偏积木风，与本轮主角不够一致，未放入游戏。研究副本仅保存在 ThirdParty/KenneyMiniCharacters。

## 原创与沿用资产

轮椅、小女孩主角、房屋、市集、图书馆、共享花园及街道物件由本项目 Blender 脚本制作；v3 在 v2 资产基础上重做主角。河道、桥梁、街区布局、UI、交互和水面着色器由本项目实现。24 个主资产已显式三角化后导入 Unity。

没有调用付费生成服务，没有安装额外插件。
