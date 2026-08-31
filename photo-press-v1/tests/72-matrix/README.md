# 72 张全量测试矩阵 · 72-Matrix

> 本目录是 SKILL.md / craft-cards.md 中所有"实测数字"的原始数据归档，让每个数字可复核。
> **数据恢复自 opencode 会话库**（`~/.local/share/opencode/opencode.db`，会话 `ses_fc6422bd4`，2026-08-25~26 开发主会话）。原始生成图与临时脚本在 2026-08-25 晚被清理删除，但评估输出完整保留在会话库中，已提取归档于此。

## 测试方法（如实还原）

**通道**：doubao-seedream-5.0-lite（Agent Plan，`reference_strength` 0.9，极简 0.7）
**提示词模板**：D 模板（中文直白保真锚定 + 工艺语言片段，即 SKILL.md §6 现行模板）

测试分**两轮**，数据含义不同：

| 轮次 | 时间 | 内容 | 归档文件 |
|------|------|------|---------|
| run1 数值 | 08-25 | 12 工艺 × 6 源图 = 72 张，skimage 数值评估（边缘SSIM / 边缘相关 / 饱和度） | `scores.csv`、`matrix.csv`（edge_corr_run1 列） |
| run2 视觉 | 08-25（修复后） | 72 张重新生成（含 letterpress no-text 修复、极简 strength 0.7），doubao-seed-2.0-lite 逐张 6 维审查 | `reviews.jsonl`、`matrix.csv`（vision_run2 列） |
| 回归 | 08-25 | letterpress no-text 修复重测 6 张；woodcut 具体主体描述对比 6 张 | `regression.csv` |

**判定阈值**：边缘相关 < 0.4 视为保真失败（run1 数值判定）；视觉审查 verdict=fail 为失败（run2）。

## 文件清单

| 文件 | 内容 |
|------|------|
| `matrix.csv` | **主矩阵**：72 条 = 工艺 × 源图 × strength × run1 数值 × run2 视觉 × 最终状态 × 失败原因 |
| `specs.csv` | 72 条测试输入规格（工艺 × 源图 × strength × 提示词模板引用） |
| `scores.csv` | run1 每张边缘相关值 |
| `reviews.jsonl` | run2 每张视觉审查判定（verdict/craft/subject + 重建备注） |
| `summary.csv` | 每工艺聚合（与 craft-cards 汇总表一一对应） |
| `regression.csv` | letterpress 修复 / woodcut 具体描述回归数据 |
| `sources/` | 6 张源图（3 张 Wikimedia 现成 + 3 张 picsum，见下） |
| `_build_matrix.py` | 数据构建脚本（从提取输出重建全部 CSV） |

## 与 craft-cards / SKILL.md 数字的对应（可复核）

**每工艺聚合（`summary.csv` → craft-cards 汇总表）**：

| 工艺 | craft-cards 平均相关 | 实测 corr_avg (run1) | craft-cards 失败率 | 实测 fail_rate (run1) |
|------|--------------------|---------------------|-------------------|----------------------|
| darkroom 暗房 | 0.73 | 0.734 | 0% | 0.0 |
| cyanotype 蓝晒 | 0.73 | 0.726 | 0% | 0.0 |
| watercolor 水彩 | 0.63 | 0.630 | 0% | 0.0 |
| risograph 孔版 | 0.60 | 0.596 | 0% | 0.0 |
| silkscreen 丝网 | 0.58 | 0.576 | 17% | 0.17 |
| ukiyo-e 浮世绘 | 0.55 | 0.554 | 0% | 0.0 |
| ink-wash 水墨 | 0.54 | 0.541 | 33% | 0.33 |
| torn-paper 撕纸 | 0.54 | 0.540 | 0% | 0.0 |
| woodcut 木刻 | 0.50 | 0.497 | 33% | 0.33 |
| minimalist 极简 | 0.45 | 0.446 | 50% | 0.5 |
| paper-cut 剪纸 | 0.41 | 0.406 | 33% | 0.33 |
| letterpress 活字 | 0.53（修复后） | 修复前 0.367 → 修复后 0.531 | 17%（修复后） | 修复前 0.83 → 修复后 0.17 |

**主体难度（run1 每源图聚合）**：人像 0.50、花 0.33、日出 0.17、灯塔/浪/城市 0.08 —— 与 craft-cards「主体难度」一致。

**run2 视觉结论**：9/12 工艺 6/6 全 pass；3 个工艺各 1 个失败，**全部集中在 s5 彩色花**（paper-cut / risograph / ukiyo-e）——与 SKILL.md「花主体对硬边类工艺不适用」一致。

**回归（`regression.csv`）**：
- letterpress 改默认 no-text 后：平均相关 0.367→0.531，失败率 0.83→0.17
- woodcut 具体主体描述：人像 0.382→0.395、花 0.354→0.414、平均 0.497→0.512（对应 SKILL.md 数字）

## 诚实标注（已知限制）

1. **72 张结果图文件未归档**：`batch_all/` 在测试后被清理，只有评估输出保留。数字可复核，图像不可复核。需要目检时用 runner（`../run-repro.py`）重跑。
2. **3 张 picsum 源图未归档**：`p_portrait / p_flower / p_city`（`https://picsum.photos/seed/{seed}/1200/800`，seed 固定可复现下载，网络恢复后可补齐至 `sources/`）。本机下载时 picsum 服务不可达（503/连接拒绝）。
3. **run2 视觉审查的中文备注乱码**：提取时原 bash 输出为 GBK 且已损坏，verdict/craft/subject 字段为干净 ASCII 直接使用；失败/异常备注按会话摘要重建（已在 `reviews.jsonl` 标注）。
4. **run1 与 run2 提示词有差异**：run2 使用修复后最新提示词（letterpress no-text、极简 strength 0.7），因此 letterpress/minimalist 的 run1 数值落后于 craft-cards 最终值。matrix.csv 中两列并列，最终状态以 run2 视觉为准。

## 重新生成（当有 API key 时）

```bash
# 用 runner 按场景矩阵重跑并对比（本矩阵为 2026-08-25 实测基线）
python ../run-repro.py --scenarios ../scenarios.json --out ../results
```
