# 照片印坊 · Photo Press

把一张照片送进印坊，选一种真实印刷工艺，印成一件印刷品。风格不是滤镜，是工艺。

## 这是什么

一个图片风格转换 skill：用户给一张照片 + 一个风格词（"复古"、"清新"、"波普"……或直接说工艺名），它按真实印刷工艺（木刻、水彩、浮世绘、撕纸、活字、孔版、丝网、剪纸、暗房、蓝晒、水墨、极简）的工序还原成海报。

## 核心机制

- **三问读图**：是什么 / 为什么值得 / 怎么做。第二问答不出，就不生成。
- **保真契约**：PRESERVE / MAY TRANSFORM / REMOVE 三分类清单。
- **保真上限由工艺决定**：木刻保不了细节，是工艺选错了，越界先换工艺不硬调。
- **双通道参考**：原图（内容通道）+ 工艺样张（质感通道，boring anchor）。
- **模型无关**：通道能力检查把保真旋钮映射到任意生图模型（seedream / gpt-image / Midjourney / SD-Flux…）。
- **实测驱动**：72 张全量测试 + 视觉模型审查，工艺参数（strength 甜点、保真上限、适用限制）都有数据支撑。

## 灵感来源

- [Zeejay0/gathered-scenes-zine-skill](https://github.com/Zeejay0/gathered-scenes-zine-skill)（意象提取 / 语义最小集方法，MIT）
- 同类参考：[jas0nh/zine-poster-skill](https://github.com/jas0nh/zine-poster-skill)、[LiamGvchi/gc-minimal-zine-poster](https://github.com/LiamGvchi/gc-minimal-zine-poster)

## 许可

[MIT](LICENSE)
