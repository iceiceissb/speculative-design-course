# AI 工具使用情况

## 使用范围

Codex 辅助阅读现有案例与课程要求、核对来源、整理叙事、生成讲稿、编写 Three.js 原型及说明 PPT。图片通过原始项目或论文获取，没有把 AI 图像冒写成案例照片。

ImageGen 生成一张网页视觉概念，帮助确定暖白、青绿、陶土色及整体布局。实际场景采用程序化 3D 几何模型，没有将概念图当作可交互画面，也没有生成视频。可视化提交选择四幕分镜，截图来自运行中的网页。

参考用户提供的 laban-workflow-app 的程序建模与动画组织方式，复用其目录中附带的 Three.js r128 库；本项目人物、轮椅、建筑、叙事与状态逻辑另行编写，库的 MIT 许可随原型保留。

## 实现边界

动画和分支是脚本模拟。确认反馈后修改的是会话内规则变量，不是训练模型。未连接实体轮椅，没有实际感知、避障、语音识别或远程消息服务。页面测试不是目标人群用户研究。讲稿及 PPT 明确保留这些边界。

## ImageGen 视觉概念提示词

```text
Create one polished full-screen desktop interface design concept for a Chinese speculative 3D interactive narrative titled “请别替我让路”. This is a design reference only, not a background asset. 1440×1000 landscape composition, full primary screen. Restrained museum-exhibit quality, warm off-white #F7F6F2, charcoal #243431, deep muted teal #316659, small terracotta accents. Clean Chinese sans-serif, aligned controls, generous margins. NO dashboard card grid, no badges, no redundant progress bars.
Layout: header at x64 y35, title 32px left “请别替我让路”, subtitle 15px “轮椅机器人的礼貌，应该由谁付出代价？”. Right navigation “体验” “分镜” “案例与转译”. Beneath header one sentence in bold 24px: “它准备替你让路。” with smaller line “你是林岚。你需要轮椅辅助移动，也想自己决定什么时候退让。”
A LARGE real-time 3D-style stage dominates center, roughly x64 y190 width1312 height540. Orthographic isometric well-lit community center corridor with matte clay architectural models, visible floor plan, subtle shadows, restrained furnishing. Corridor runs horizontally, narrow middle and two wider passing spaces at opposite ends. On left a detailed teal powered wheelchair with large black wheels, silver frame, joystick, footrests carrying a dignified grey-haired elderly woman in teal top and tan trousers. On right three human figures in neutral terracotta/navy/ochre, facing her. Humans have coherent jointed proportions and visible feet, not abstract pawns. Low near wall, higher far wall, clear paths. A few plants and community noticeboard only outside circulation. No floating holograms. Small in-scene labels “林岚” and “对向行人”. Wheelchair is the robot, no unrelated humanoid robot. Camera like a refined procedural Three.js scene that can actually be built.
Below scene a single flat aligned control row: left small “暂停” “俯视 / 乘坐视角”, right compact “重新开始”. Below, two equally sized main actions, “我这次让” and “请对方让”, and smaller text action “先停在这里”. One short consequence sentence below them: “你的选择会改变双方的位置与等待。”
Footer small disclosure “设计虚构 · 3D 脚本模拟，不控制真实轮椅”. All UI text and buttons must be separable code-native in implementation. No extra metrics, icons, widgets, rating scales or new storyline. This full screen is the shared visual system for arrival, movement-stop, consequence and feedback states; downstream states replace the bottom text/actions in the same aligned geometry. On mobile scene stays above stacked controls.
```
