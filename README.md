# Agent Skills 集合

个人 Agent Skills 仓库。每个 skill 是一个自包含的目录，可直接安装到 `~/.claude/skills`、`~/.agents/skills` 或 `~/.config/opencode/skills`。

## 已收录

### [photo-press-v1](photo-press-v1/)

把一张照片送进印坊，选一种真实印刷工艺，印成一件印刷品。风格不是滤镜，是工艺。

- **12 种工艺**：木刻、浮世绘、水彩、撕纸、活字、孔版、丝网、剪纸、暗房、蓝晒、水墨、极简，每种工艺有材料 / 工具 / 工序 / 痕迹 / 保真上限。
- **三问读图**：是什么 / 为什么值得 / 怎么做。第二问答不出，就不生成。
- **保真契约**：PRESERVE / MAY TRANSFORM / REMOVE 三分类清单；保真上限由工艺决定，越界先换工艺不硬调。
- **风格词路由**：说"复古 / 清新 / 波普"等大白话也能自动匹配工艺。
- **模型无关**：通道能力检查把保真旋钮映射到任意生图模型（seedream / gpt-image / Midjourney / SD-Flux…）。
- **实测驱动**：72 张全量测试 + 视觉模型审查，工艺参数都有数据支撑。
- 许可：MIT

## 安装

把某个 skill 目录复制到你的 skills 目录即可，例如：

```bash
cp -r photo-press-v1 ~/.claude/skills/
```

## 许可

[MIT](LICENSE)
