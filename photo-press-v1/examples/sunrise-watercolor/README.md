# 日出水彩 · Sunrise Watercolor

**工艺：水彩（watercolor）**
**Skill：`photo-press-v1`**
**通道：Agent Plan doubao-seedream-5.0-lite（图生图，reference_strength=0.9，中文直白保真锚定模板）**

| 原始照片 | 最终作品 |
| :---: | :---: |
| <img src="source.jpg" alt="日出山脉原始照片" width="440"> | <img src="result.jpg" alt="日出水彩最终作品" width="440"> |

## 三问读图

- **是什么**：日出时的山脉、河流与天空，柔和光线。
- **为什么值得**：晨曦的静，光刚从山后起来的那一小段。
- **怎么做**：水彩水洗——让柔和的东西更柔。

## 保真契约

- **PRESERVE**：山脉剪影、河流走向、天空位置。
- **MAY TRANSFORM**：色彩处理（水洗降饱和）、细节软化。
- **保真旋钮**：2（标准）→ reference_strength 0.8。

## 返检结果

| 指标 | 数值 | 判定 |
|------|------|------|
| 饱和度 | 0.347 → 0.186 | ✅ 水洗降饱和 |
| 边缘结构相似度 | 0.736 | ✅ 结构高度保留 |
| 边缘相关性 | 0.589 | ✅ |

- 说明：seedream 高清输出（2656×1632），水洗降饱和 + 结构保真同时达成，是三个案例中保真与艺术感平衡最好的。提示词用中文直白保真锚定模板（严格保持构图不变，只改变媒介）。
- 对比历史：弱模型文生图 SSIM 0.452（降饱和被理解成鲜艳水彩）→ 程序化保真 SSIM 0.883（结构好但无艺术感）→ 本版 seedream 高清 + 真水彩晕染。

> 晨光被水洗过一遍，山脉还在原处。

---
源照片：Wikimedia Commons [Sunrise in Pieniny, Poland 02.jpg](https://commons.wikimedia.org/wiki/File:Sunrise_in_Pieniny,_Poland_02.jpg)
