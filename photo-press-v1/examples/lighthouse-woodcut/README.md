# 灯塔木刻 · Lighthouse Woodcut

**工艺：木刻版画（woodcut）**
**Skill：`photo-press-v1`**
**通道：Agent Plan doubao-seedream-5.0-lite（图生图，reference_strength=0.9，中文直白保真锚定模板）**

| 原始照片 | 最终作品 |
| :---: | :---: |
| <img src="source.jpg" alt="Cape May 灯塔原始照片" width="440"> | <img src="result.jpg" alt="灯塔木刻最终作品" width="440"> |

## 三问读图

- **是什么**：白色灯塔（红顶）立在天空与绿地之间，主体竖立、轮廓清晰。
- **为什么值得**：灯塔在地标意义下是"孤立的存在"——一座塔对着整片天。
- **怎么做**：木刻黑白硬边，用大块黑剪影放大这种孤立感。

## 保真契约

- **PRESERVE**：灯塔形状、位置、轮廓、长宽比例。
- **MAY TRANSFORM**：天空、绿地、环境（刀刻纹样化）。
- **保真旋钮**：3（紧）→ reference_strength 0.95。

## 返检结果

| 指标 | 数值 | 判定 |
|------|------|------|
| 饱和度 | 0.345 → 0.028 | ✅ 黑白化达成 |
| 边缘结构相似度 | 0.255 | ⚠️ 部分保留 |
| 边缘相关性 | 0.555 | ⚠️ 主体轮廓部分保留 |

- 说明：木刻是强风格化工艺，seedream 在黑白化时对构图做了重新组织，主体保留不彻底（这是工艺的保真上限）。提示词模板经批量测试选优：对强风格化工艺，**"中文直白保真锚定"（严格保持构图不变，只改变媒介）优于英文 Preserve/Change 模板与风格堆叠**（后者会诱发更激进的风格化重绘，边缘相关性从 0.555 降到 0.419）。
- 对比历史：弱模型文生图 SSIM 0.216（参考被忽略，彻底重绘）→ 程序化保真 SSIM 0.628（算法级但无艺术感）→ seedream 高清 + 部分艺术化重绘（本版为批量测试最优）。

> 白塔被刻成黑与白，孤立感留在了纸面。

---
源照片：Wikimedia Commons [Cape May Lighthouse September 2020 002.jpg](https://commons.wikimedia.org/wiki/File:Cape_May_Lighthouse_September_2020_002.jpg)
