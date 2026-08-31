"""从 opencode 会话库提取的 72 张测试原始输出 → 结构化矩阵。

数据来源（2026-08-25 会话 ses_fc6422bd4 中实跑，已从会话库提取到本地 dump）：
  - run1 数值评估：eval_all.py 输出（12 工艺 × 6 源图 边缘相关矩阵 + 每工艺聚合）
  - run2 视觉审查：vision_review.py 输出（72 张 verdict/craft/subject 判定）
  - 回归：eval_regression.py 输出（letterpress 修复、woodcut 具体描述对比）

生成：
  - scores.csv       run1 数值（每张边缘相关 + 每工艺聚合）
  - reviews.jsonl    run2 视觉审查（72 张判定）
  - specs.csv        测试输入规格（工艺 × 源图 × strength × 模板）
  - matrix.csv       合并矩阵（工艺 × 源图 × 数值 × 判定 × 失败原因）
"""

import csv
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).parent

# ---------------- 源图定义 ----------------
SOURCES = {
    "s1": {
        "file": "s1-source-test.jpg",
        "name": "灯塔 lighthouse",
        "note": "Wikimedia 公有领域（Cape May 灯塔）",
    },
    "s2": {
        "file": "s2-source-watercolor.jpg",
        "name": "日出 sunrise",
        "note": "Wikimedia 公有领域（层叠山峦日出）",
    },
    "s3": {
        "file": "s3-source-ukiyo.jpg",
        "name": "浪 wave",
        "note": "Wikimedia 公有领域（海浪）",
    },
    "s4": {
        "file": "p_portrait.jpg",
        "name": "黑白人像 portrait",
        "note": "picsum seed=portrait（源图文件未归档，可复现下载）",
    },
    "s5": {
        "file": "p_flower.jpg",
        "name": "彩色花 flower",
        "note": "picsum seed=flower（源图文件未归档，可复现下载）",
    },
    "s6": {
        "file": "p_city.jpg",
        "name": "城市街道 city",
        "note": "picsum seed=city（源图文件未归档，可复现下载）",
    },
}

CRAFTS = [
    "cyanotype",
    "darkroom",
    "ink-wash",
    "letterpress",
    "minimalist",
    "paper-cut",
    "risograph",
    "silkscreen",
    "torn-paper",
    "ukiyo-e",
    "watercolor",
    "woodcut",
]

# ---------------- run1 数值矩阵（eval_all.py 输出，原始数据） ----------------
# 每工艺 × 6 源图的边缘相关（<0.4 视为保真失败）
RUN1_MATRIX = {
    "cyanotype": [0.71, 0.68, 0.69, 0.67, 0.74, 0.87],
    "darkroom": [0.86, 0.64, 0.72, 0.60, 0.72, 0.86],
    "ink-wash": [0.63, 0.55, 0.63, 0.40, 0.34, 0.70],
    "letterpress": [0.39, 0.31, 0.55, 0.32, 0.31, 0.32],
    "minimalist": [0.69, 0.50, 0.33, 0.37, 0.37, 0.42],
    "paper-cut": [0.46, 0.36, 0.52, 0.23, 0.45, 0.42],
    "risograph": [0.72, 0.49, 0.69, 0.41, 0.52, 0.74],
    "silkscreen": [0.69, 0.53, 0.69, 0.34, 0.46, 0.75],
    "torn-paper": [0.65, 0.46, 0.59, 0.44, 0.49, 0.61],
    "ukiyo-e": [0.62, 0.67, 0.65, 0.43, 0.40, 0.55],
    "watercolor": [0.74, 0.57, 0.68, 0.41, 0.58, 0.78],
    "woodcut": [0.57, 0.52, 0.58, 0.38, 0.35, 0.58],
}

# 每工艺聚合（eval_all.py 输出的聚合行）
RUN1_AGG = {
    "cyanotype": {
        "n": 6,
        "ssim_avg": 0.658,
        "ssim_min": 0.584,
        "corr_avg": 0.726,
        "corr_min": 0.673,
        "fail_rate": 0.0,
        "sat": "0.22->0.48",
    },
    "darkroom": {
        "n": 6,
        "ssim_avg": 0.781,
        "ssim_min": 0.690,
        "corr_avg": 0.734,
        "corr_min": 0.597,
        "fail_rate": 0.0,
        "sat": "0.22->0.06",
    },
    "ink-wash": {
        "n": 6,
        "ssim_avg": 0.699,
        "ssim_min": 0.541,
        "corr_avg": 0.541,
        "corr_min": 0.343,
        "fail_rate": 0.33,
        "sat": "0.22->0.11",
    },
    "letterpress": {
        "n": 6,
        "ssim_avg": 0.440,
        "ssim_min": 0.296,
        "corr_avg": 0.367,
        "corr_min": 0.307,
        "fail_rate": 0.83,
        "sat": "0.22->0.20",
    },
    "minimalist": {
        "n": 6,
        "ssim_avg": 0.677,
        "ssim_min": 0.526,
        "corr_avg": 0.446,
        "corr_min": 0.329,
        "fail_rate": 0.5,
        "sat": "0.22->0.26",
    },
    "paper-cut": {
        "n": 6,
        "ssim_avg": 0.570,
        "ssim_min": 0.395,
        "corr_avg": 0.406,
        "corr_min": 0.230,
        "fail_rate": 0.33,
        "sat": "0.22->0.23",
    },
    "risograph": {
        "n": 6,
        "ssim_avg": 0.601,
        "ssim_min": 0.522,
        "corr_avg": 0.596,
        "corr_min": 0.412,
        "fail_rate": 0.0,
        "sat": "0.22->0.26",
    },
    "silkscreen": {
        "n": 6,
        "ssim_avg": 0.586,
        "ssim_min": 0.375,
        "corr_avg": 0.576,
        "corr_min": 0.337,
        "fail_rate": 0.17,
        "sat": "0.22->0.24",
    },
    "torn-paper": {
        "n": 6,
        "ssim_avg": 0.692,
        "ssim_min": 0.575,
        "corr_avg": 0.540,
        "corr_min": 0.441,
        "fail_rate": 0.0,
        "sat": "0.22->0.19",
    },
    "ukiyo-e": {
        "n": 6,
        "ssim_avg": 0.558,
        "ssim_min": 0.365,
        "corr_avg": 0.554,
        "corr_min": 0.402,
        "fail_rate": 0.0,
        "sat": "0.22->0.27",
    },
    "watercolor": {
        "n": 6,
        "ssim_avg": 0.779,
        "ssim_min": 0.636,
        "corr_avg": 0.630,
        "corr_min": 0.414,
        "fail_rate": 0.0,
        "sat": "0.22->0.16",
    },
    "woodcut": {
        "n": 6,
        "ssim_avg": 0.323,
        "ssim_min": 0.193,
        "corr_avg": 0.497,
        "corr_min": 0.354,
        "fail_rate": 0.33,
        "sat": "0.22->0.13",
    },
}

# ---------------- run2 视觉审查（vision_review.py 输出，72 行） ----------------
# 每行: {cid}-s{n}: verdict=X craft=Y subject=Z | note
# 原始中文备注在提取时乱码丢失，verdict/craft/subject 为干净 ASCII，直接使用；
# 逐行无法解析处（risograph-s5 字段乱码）用汇总区（每工艺 x/6）兜底。
RUN2_LINES = """cyanotype-s1: verdict=pass craft=pass subject=pass
cyanotype-s2: verdict=pass craft=pass subject=pass
cyanotype-s3: verdict=pass craft=pass subject=pass
cyanotype-s4: verdict=pass craft=pass subject=pass
cyanotype-s5: verdict=pass craft=pass subject=pass
cyanotype-s6: verdict=pass craft=pass subject=pass
darkroom-s1: verdict=pass craft=pass subject=pass
darkroom-s2: verdict=pass craft=pass subject=pass
darkroom-s3: verdict=pass craft=pass subject=pass
darkroom-s4: verdict=pass craft=pass subject=pass
darkroom-s5: verdict=pass craft=pass subject=pass
darkroom-s6: verdict=pass craft=pass subject=pass
ink-wash-s1: verdict=pass craft=pass subject=pass
ink-wash-s2: verdict=pass craft=pass subject=pass
ink-wash-s3: verdict=pass craft=pass subject=pass
ink-wash-s4: verdict=pass craft=pass subject=pass
ink-wash-s5: verdict=pass craft=pass subject=pass
ink-wash-s6: verdict=pass craft=pass subject=pass
letterpress-s1: verdict=pass craft=pass subject=pass
letterpress-s2: verdict=pass craft=pass subject=pass
letterpress-s3: verdict=pass craft=pass subject=pass
letterpress-s4: verdict=pass craft=pass subject=pass
letterpress-s5: verdict=pass craft=pass subject=pass
letterpress-s6: verdict=pass craft=pass subject=pass
minimalist-s1: verdict=pass craft=pass subject=pass
minimalist-s2: verdict=pass craft=pass subject=pass
minimalist-s3: verdict=pass craft=pass subject=pass
minimalist-s4: verdict=pass craft=pass subject=pass
minimalist-s5: verdict=pass craft=pass subject=pass
minimalist-s6: verdict=pass craft=pass subject=pass
paper-cut-s1: verdict=pass craft=pass subject=pass
paper-cut-s2: verdict=pass craft=pass subject=pass
paper-cut-s3: verdict=pass craft=pass subject=pass
paper-cut-s4: verdict=pass craft=pass subject=pass
paper-cut-s5: verdict=fail craft=pass subject=fail
paper-cut-s6: verdict=pass craft=pass subject=pass
risograph-s1: verdict=pass craft=pass subject=pass
risograph-s2: verdict=pass craft=pass subject=pass
risograph-s3: verdict=pass craft=pass subject=pass
risograph-s4: verdict=pass craft=pass subject=pass
risograph-s5: verdict=fail craft=fail subject=fail
risograph-s6: verdict=pass craft=pass subject=pass
silkscreen-s1: verdict=pass craft=pass subject=pass
silkscreen-s2: verdict=pass craft=pass subject=pass
silkscreen-s3: verdict=pass craft=pass subject=pass
silkscreen-s4: verdict=pass craft=pass subject=pass
silkscreen-s5: verdict=pass craft=pass subject=pass
silkscreen-s6: verdict=pass craft=pass subject=pass
torn-paper-s1: verdict=pass craft=pass subject=pass
torn-paper-s2: verdict=pass craft=pass subject=pass
torn-paper-s3: verdict=pass craft=pass subject=pass
torn-paper-s4: verdict=pass craft=pass subject=pass
torn-paper-s5: verdict=pass craft=pass subject=pass
torn-paper-s6: verdict=pass craft=pass subject=pass
ukiyo-e-s1: verdict=pass craft=pass subject=pass
ukiyo-e-s2: verdict=pass craft=pass subject=pass
ukiyo-e-s3: verdict=pass craft=pass subject=pass
ukiyo-e-s4: verdict=pass craft=pass subject=pass
ukiyo-e-s5: verdict=fail craft=pass subject=pass
ukiyo-e-s6: verdict=pass craft=pass subject=pass
watercolor-s1: verdict=pass craft=pass subject=pass
watercolor-s2: verdict=pass craft=pass subject=pass
watercolor-s3: verdict=pass craft=pass subject=pass
watercolor-s4: verdict=pass craft=pass subject=pass
watercolor-s5: verdict=pass craft=pass subject=pass
watercolor-s6: verdict=pass craft=pass subject=pass
woodcut-s1: verdict=pass craft=pass subject=pass
woodcut-s2: verdict=pass craft=pass subject=pass
woodcut-s3: verdict=pass craft=pass subject=pass
woodcut-s4: verdict=pass craft=pass subject=pass
woodcut-s5: verdict=pass craft=pass subject=pass
woodcut-s6: verdict=pass craft=pass subject=pass""".splitlines()

# 视觉审查备注（汇总区乱码丢失的中文内容，按会话摘要重建；仅用于记录失败/异常原因）
VISION_NOTES = {
    (
        "paper-cut",
        "s5",
    ): "花主体被破坏性重绘（无花朵结构，全是源图没有的元素）；具体花朵描述也无法救回",
    ("risograph", "s5"): "花主体被重绘/替换为源图没有的无关元素",
    ("ukiyo-e", "s5"): "花朵主体被替换为源图没有的无关元素（编织物/花盆等）",
    ("letterpress", "s5"): "异常：右下角多出源图没有的元素（verdict=pass）",
    ("minimalist", "s4"): "异常：画面多出额外的几何形/拼贴色块（verdict=pass）",
    ("torn-paper", "s2"): "异常：背景多出源图没有的浅色雪山元素（verdict=pass）",
    ("ukiyo-e", "s4"): "异常：原图形态被替换为无关元素（verdict=pass）",
    ("risograph", "s6"): "异常：岩石旁多出额外的红色装饰元素（verdict=pass）",
}

# ---------------- 回归数据（eval_regression.py 输出） ----------------
LETTERPRESS_REGRESSION = {
    "corr": {
        "s1": 0.591,
        "s2": 0.425,
        "s3": 0.697,
        "s4": 0.457,
        "s5": 0.325,
        "s6": 0.694,
    },
    "corr_avg_after": 0.531,
    "corr_avg_before": 0.367,
    "fail_rate_after": 0.17,
    "fail_rate_before": 0.83,
}
WOODCUT_DETAIL = {
    "s1": {"general": 0.568, "specific": 0.612},
    "s2": {"general": 0.518, "specific": 0.462},
    "s3": {"general": 0.578, "specific": 0.607},
    "s4": {"general": 0.382, "specific": 0.395},
    "s5": {"general": 0.354, "specific": 0.414},
    "s6": {"general": 0.583, "specific": 0.581},
    "avg": {"general": 0.497, "specific": 0.512},
}


# strength 规则（来自 SKILL.md 第七步）：印刷工艺 0.9，极简特例 0.7
def strength_for(craft):
    return 0.7 if craft == "minimalist" else 0.9


def main():
    # ---- specs.csv ----
    with open(HERE / "specs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cid", "sid", "source_name", "strength", "prompt_template", "refs"])
        for craft in CRAFTS:
            for sid in sorted(SOURCES):
                w.writerow(
                    [
                        f"{craft}-{sid}",
                        sid,
                        SOURCES[sid]["name"],
                        strength_for(craft),
                        "D 模板：中文直白保真锚定 + 工艺语言片段（见 SKILL.md §6 与 craft-cards）",
                        f"[源图 {sid}, anchor {craft}.jpg]",
                    ]
                )

    # ---- scores.csv（run1 数值）----
    with open(HERE / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cid", "sid", "edge_corr", "corr<0.4=FAIL", "note"])
        for craft in CRAFTS:
            for i, sid in enumerate(sorted(SOURCES)):
                corr = RUN1_MATRIX[craft][i]
                w.writerow([craft, sid, corr, "FAIL" if corr < 0.4 else "pass", ""])

    # ---- reviews.jsonl（run2 视觉审查）----
    parsed = {}
    pat = re.compile(
        r"^([a-z-]+)-s([1-6]):\s*verdict=(\w+)\s+craft=(\w+)\s+subject=(\w+)"
    )
    for line in RUN2_LINES:
        m = pat.match(line.strip())
        if not m:
            print(f"WARN unparsed line: {line[:60]}")
            continue
        cid, sid, verdict, craft, subject = m.groups()
        parsed[(cid, f"s{sid}")] = {
            "verdict": verdict,
            "craft": craft,
            "subject": subject,
        }
    with open(HERE / "reviews.jsonl", "w", encoding="utf-8") as f:
        for craft in CRAFTS:
            for sid in sorted(SOURCES):
                rec = parsed.get((craft, sid))
                if rec is None:
                    # 用 run2 汇总兜底：paper-cut/risograph/ukiyo-e 仅 s5 一个 fail
                    fail = (
                        craft in ("paper-cut", "risograph", "ukiyo-e") and sid == "s5"
                    )
                    rec = {
                        "verdict": "fail" if fail else "pass",
                        "craft": "pass",
                        "subject": "fail" if fail else "pass",
                    }
                note = VISION_NOTES.get((craft, sid), "")
                json.dump(
                    {"cid": craft, "sid": sid, **rec, "note": note},
                    f,
                    ensure_ascii=False,
                )
                f.write("\n")

    # ---- matrix.csv（合并）----
    # final_status 反映当前 skill 状态（run2 视觉 = 修复后最新提示词）。
    # run1_verdict 是历史数值判定（letterpress 为修复前状态，见 regression.csv）。
    with open(HERE / "matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cid",
                "sid",
                "source",
                "strength",
                "edge_corr_run1",
                "run1_verdict",
                "vision_run2",
                "vision_craft",
                "vision_subject",
                "final_status",
                "failure_reason",
            ]
        )
        for craft in CRAFTS:
            for i, sid in enumerate(sorted(SOURCES)):
                corr = RUN1_MATRIX[craft][i]
                run1_v = "FAIL" if corr < 0.4 else "pass"
                rec = parsed.get((craft, sid))
                if rec is None:
                    fail = (
                        craft in ("paper-cut", "risograph", "ukiyo-e") and sid == "s5"
                    )
                    rec = {
                        "verdict": "fail" if fail else "pass",
                        "craft": "pass",
                        "subject": "fail" if fail else "pass",
                    }
                note = VISION_NOTES.get((craft, sid), "")
                if craft == "letterpress":
                    note = (
                        "[run1 为修复前状态：强制加文字导致 83% 失败，见 regression.csv] "
                        + note
                    ).strip()
                w.writerow(
                    [
                        craft,
                        sid,
                        SOURCES[sid]["name"],
                        strength_for(craft),
                        corr,
                        run1_v,
                        rec["verdict"],
                        rec["craft"],
                        rec["subject"],
                        "FAIL" if rec["verdict"] == "fail" else "PASS",
                        note,
                    ]
                )

    # ---- summary.csv（每工艺聚合：与 craft-cards 汇总表一一对应）----
    with open(HERE / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cid",
                "n",
                "ssim_avg",
                "ssim_min",
                "corr_avg",
                "corr_min",
                "fail_rate_run1",
                "sat_change",
                "vision_pass_rate",
                "notes",
            ]
        )
        for craft in CRAFTS:
            agg = RUN1_AGG[craft]
            vision_fails = sum(
                1
                for sid in sorted(SOURCES)
                if (parsed.get((craft, sid)) or {}).get("verdict") == "fail"
            )
            note = ""
            if craft == "letterpress":
                note = "run1 为修复前；修复后 corr_avg=0.531, fail=0.17（见 regression.csv）"
            elif craft == "minimalist":
                note = "run1 数值失败为减法风格预期（边缘结构天然降低）；run2 视觉 6/6 pass"
            w.writerow(
                [
                    craft,
                    agg["n"],
                    agg["ssim_avg"],
                    agg["ssim_min"],
                    agg["corr_avg"],
                    agg["corr_min"],
                    agg["fail_rate"],
                    agg["sat"],
                    f"{6 - vision_fails}/6",
                    note,
                ]
            )

    # ---- regression.csv（回归重测：letterpress 修复 + woodcut 具体描述）----
    with open(HERE / "regression.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["test", "sid", "metric", "value"])
        for sid, v in LETTERPRESS_REGRESSION["corr"].items():
            w.writerow(["letterpress-no-text-fix", sid, "edge_corr_after_fix", v])
        w.writerow(
            [
                "letterpress-no-text-fix",
                "all",
                "corr_avg_after",
                LETTERPRESS_REGRESSION["corr_avg_after"],
            ]
        )
        w.writerow(
            [
                "letterpress-no-text-fix",
                "all",
                "corr_avg_before",
                LETTERPRESS_REGRESSION["corr_avg_before"],
            ]
        )
        w.writerow(
            [
                "letterpress-no-text-fix",
                "all",
                "fail_rate_after",
                LETTERPRESS_REGRESSION["fail_rate_after"],
            ]
        )
        w.writerow(
            [
                "letterpress-no-text-fix",
                "all",
                "fail_rate_before",
                LETTERPRESS_REGRESSION["fail_rate_before"],
            ]
        )
        for sid, v in WOODCUT_DETAIL.items():
            if sid == "avg":
                continue
            w.writerow(
                ["woodcut-specific-subject", sid, "edge_corr_general", v["general"]]
            )
            w.writerow(
                ["woodcut-specific-subject", sid, "edge_corr_specific", v["specific"]]
            )
        w.writerow(
            [
                "woodcut-specific-subject",
                "avg",
                "edge_corr_general",
                WOODCUT_DETAIL["avg"]["general"],
            ]
        )
        w.writerow(
            [
                "woodcut-specific-subject",
                "avg",
                "edge_corr_specific",
                WOODCUT_DETAIL["avg"]["specific"],
            ]
        )

    # ---- 汇总统计 ----
    print("生成完成:")
    for p in [
        "specs.csv",
        "scores.csv",
        "reviews.jsonl",
        "matrix.csv",
        "summary.csv",
        "regression.csv",
    ]:
        print(f"  {p}: {(HERE / p).stat().st_size} bytes")
    total = 12 * 6
    fails = sum(
        1
        for c in CRAFTS
        for s in sorted(SOURCES)
        if (parsed.get((c, s)) or {}).get("verdict") == "fail"
    )
    print(f"  合计 {total} 条；run2 视觉最终 FAIL = {fails} 条（全部集中在 s5 彩色花）")


if __name__ == "__main__":
    main()
