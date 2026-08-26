# 浪 · 浮世绘 · Wave Ukiyo-e

**工艺：浮世绘多色套版（ukiyo-e）**
**Skill：`photo-press-v1`**
**通道：Agent Plan doubao-seedream-5.0-lite（图生图，reference_strength=0.9，中文直白保真锚定模板）**

| 原始照片 | 最终作品 |
| :---: | :---: |
| <img src="source.jpg" alt="海浪原始照片" width="440"> | <img src="result.jpg" alt="海浪浮世绘最终作品" width="440"> |

## 三问读图

- **是什么**：一道卷曲的海浪，浪头正在翻落。
- **为什么值得**：浪的动势——被定格在将要破碎的那一刻（《神奈川冲浪里》同一类张力）。
- **怎么做**：浮世绘套色，靛蓝浪纹 + 传统色，用纹样节奏放大动势。

## 保真契约

- **PRESERVE**：浪的形态、卷曲方向、动势。
- **MAY TRANSFORM**：颜色（转传统色域）、背景。
- **保真旋钮**：2（标准）→ reference_strength 0.8。

## 返检结果

| 指标 | 数值 | 判定 |
|------|------|------|
| 饱和度 | 0.153 → 0.260 | ✅ 传统色域（靛蓝套色） |
| 边缘结构相似度 | 0.761 | ✅ 结构高度保留 |
| 边缘相关性 | 0.676 | ✅ |

- 说明：seedream 高清输出（2560×1600），浪的形态与动势保留良好，靛蓝套色到位。提示词用中文直白保真锚定模板（严格保持构图不变，只改变媒介）。
- 对比历史：弱模型文生图 SSIM 0.390（浪被重绘）→ 程序化保真 SSIM 0.918（结构好但色块生硬）→ 本版 seedream 高清 + 真浮世绘套色质感。

> 浪被刻成靛蓝的纹样，动势留在版上。

---
源照片：Wikimedia Commons [Ocean wave in Narragansett, Rhode Island.jpg](https://commons.wikimedia.org/wiki/File:Ocean_wave_in_Narragansett,_Rhode_Island.jpg)
