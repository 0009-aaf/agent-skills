"""从 opencode 会话库提取 72 张测试的原始数据（只读）。

数据源：C:\\Users\\fms\\.local\\share\\opencode\\opencode.db
会话：ses_fc6422bd4fferp1Hlvc3iIwoyD（photo-press-v1 开发主会话，2026-08-25~26）

提取内容：
  - specs.csv    72 条测试输入（工艺 × 源图 × 提示词 × strength）
  - scores.csv   第一轮 72 张数值评估（边缘SSIM/相关/灰度SSIM/饱和度/对比度）
  - reviews.jsonl 第二轮 72 张视觉审查（6 维 JSON 判定）
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB = r"C:\Users\fms\.local\share\opencode\opencode.db"
SESSION = "ses_fc6422bd4fferp1Hlvc3iIwoyD"
OUT = Path(__file__).parent


def get_part_data(con, part_id):
    cur = con.cursor()
    cur.execute("SELECT data FROM part WHERE id=?", (part_id,))
    row = cur.fetchone()
    return json.loads(row[0]) if row else None


def find_parts(con, session, needle, limit=50):
    cur = con.cursor()
    cur.execute(
        "SELECT id, time_created, data FROM part WHERE session_id=? AND data LIKE ? "
        "ORDER BY time_created LIMIT ?",
        (session, needle, limit),
    )
    return [(r[0], r[1], json.loads(r[2])) for r in cur.fetchall()]


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # ---- 1) 找到 spec_all / eval_all / vision_review 相关的写入与运行 ----
    for kw in ["spec_all.json", "eval_all.py", "vision_review.py", "seedream_batch.py"]:
        parts = find_parts(con, SESSION, f"%{kw}%", limit=30)
        print(f"--- parts mentioning {kw}: {len(parts)}")
        for pid, ts, data in parts:
            t = data.get("type")
            tool = data.get("tool") if t == "tool" else ""
            inp = data.get("input", {}) if t == "tool" else {}
            summ = ""
            if t == "tool" and tool == "write":
                summ = str(inp.get("filePath", ""))
            elif t == "tool" and tool == "bash":
                summ = str(inp.get("command", ""))[:80]
            print(f"  {pid} {t}/{tool} {summ}")

    con.close()


if __name__ == "__main__":
    main()
