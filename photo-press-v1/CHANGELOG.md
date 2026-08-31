# CHANGELOG

本文件记录 photo-press-v1 的版本与修改历史。版本号与 SKILL.md frontmatter 的 `version` 字段保持一致。

## 1.1.1 — 2026-08-31 数据订正

审查发现已发布数字与 `tests/72-matrix/matrix.csv` 原始数据不一致，全部订正为与矩阵一致：

- 人像 / 黑白源图失败率 **50% → 42%**（5/12，阈值 <0.4 重算；README / SKILL.md / craft-cards / scenarios.json 四处同步）。
- 水墨 ink-wash 失败率 **33% → 17%**（1/6；原 0.33 系边界行 corr=0.40 被误判为失败）。
- risograph / ukiyo-e 视觉判定 **6/6 ✅ → 5/6 ❌ 花**（run2 视觉 s5 花各 1 失败，与 summary.csv / 72-matrix README 一致）。
- 失败判定阈值表述订正：边缘相关 **>0.4 → <0.4** 视为保真失败（README / craft-cards 笔误，与 72-matrix README 一致）。
- `_build_matrix.py` 的 summary fail_rate 改为由 RUN1_MATRIX 计算（corr<0.4），杜绝聚合与原始矩阵再次漂移。

## 1.1.0 — 2026-08-31 可信度与工程化

**可信度（P0）**
- 发布 72 张全量测试原始矩阵：`tests/72-matrix/`（matrix.csv / scores.csv / reviews.jsonl / summary.csv / regression.csv / specs.csv）。数据从 opencode 会话库恢复（2026-08-25 实测），每个实测数字现在可复核。
- 恢复 repro-test 12 张原始数据（review JSONL、QC、result 图）：`tests/repro-test/`。
- 新增可执行回归 runner：`tests/run-repro.py`（读 SKILL.md + 工艺卡 → 生成 → 6 维审查 → 输出矩阵，支持 `--dry-run` 冒烟）。
- 新增场景矩阵：`tests/scenarios.json`（6 类风险场景 × 12 工艺，标注已有数据 / 源图缺口）。
- 通道能力表诚实标注：seedream ✅ 实测；gpt-image / MJ / SD / Nano Banana / Recraft ⚠️ 未实测（勿当结论）。

**工程化（P1）**
- 引入 [VERIFIED] / [ASSUMED] 标注体系（SKILL.md + craft-cards.md），关键断言带数据来源与证伪路径。
- 模型方言由散文改为参数表（行=模型，列=保真句式 / 保真参数区间 / 风格词上限 / 实测状态）。
- 新增会话状态协议：状态文件 `photo-press-state.md`、每步读写契约、步骤②反问中断的恢复流程。
- 版本化：SKILL.md frontmatter 加 `version` 字段；本 CHANGELOG；工艺卡加修改历史。

## 1.0.0 — 2026-08-25/26 首版

- 12 工艺（木刻 / 浮世绘 / 水彩 / 撕纸 / 活字 / 孔版 / 丝网 / 剪纸 / 暗房 / 蓝晒 / 水墨 / 极简）工艺卡注册表。
- 三问读图 + 保真契约（PRESERVE / MAY TRANSFORM / REMOVE）+ 双旋钮 + 双通道 + 返检。
- 72 张全量测试（seedream 通道）+ 视觉模型审查，据此确定各工艺保真上限、主体难度、模型方言。
- letterpress no-text 修复（失败率 83%→17%）；极简 strength 0.7 特例。
- examples/ 13 组真实案例；assets/craft-samples/ 12 张 boring anchor。
