# tests · 可复核测试与数据归档

photo-press-v1 的**可信度资产**：让 SKILL.md / craft-cards.md 里的每个实测数字可复核，并提供可执行回归。

## 结构

| 路径 | 内容 |
|------|------|
| `72-matrix/` | **72 张全量测试原始矩阵**（12 工艺 × 6 源图，2026-08-25 seedream 实测，从会话库恢复）。`matrix.csv` 主矩阵 / `scores.csv` run1 数值 / `reviews.jsonl` run2 视觉审查 / `summary.csv` 每工艺聚合 / `regression.csv` 回归 / `specs.csv` 输入规格 / `README.md` 溯源与诚实标注。 |
| `repro-test/` | **12 工艺复现测试原始归档**（2026-08-26，从 GitHub 提交历史恢复）。review JSONL（6 维评分）+ QC 抽查 + result 图 + 源图。 |
| `run-repro.py` | **可执行回归 runner**：读 SKILL.md + craft-cards + 场景配置 → seedream 生成 → 6 维视觉审查 → 输出 matrix.csv。`--dry-run` 做一致性冒烟（不调 API）。 |
| `scenarios.json` | **场景回归矩阵**：6 类风险场景（人像/黑白源/花·毛发/夜景/文字·logo/产品图）× 12 工艺。标注 ready / needs-source / gap。 |
| `results/` | runner 运行时输出（matrix.csv），不纳入版本管理内容（自动生成）。 |

## 怎么用

```bash
# 冒烟：改完 SKILL.md / craft-cards 后验证配置与输入一致性（无需 API key）
python tests/run-repro.py --scenarios tests/scenarios.json --dry-run

# 真实回归：需要有 ARK_API_KEY（seedream 生成 + 视觉审查）
python tests/run-repro.py --scenarios tests/scenarios.json --out tests/results
```

## 诚实标注（重要）

- **72 张结果图文件未归档**（测试后被清理），数字可复核、图像不可复核；需要目检用 runner 重跑。
- **3 张 picsum 源图未归档**（seed 固定可复现：`picsum.photos/seed/{portrait|flower|city}/1200/800`）。
- **run2 视觉审查中文备注**在恢复时乱码，verdict/craft/subject 为原始 ASCII，备注按会话摘要重建。
- 通道表 ✅/⚠️ 语义：seedream 实测过，其余通道 ⚠️ 未实测（见 SKILL.md 标注体系）。
