"""提取 photo-press 72 张测试的回归数据（letterpress 修复 / woodcut 具体描述）。
只读 opencode 会话库，输出到 stdout。"""

import json
import sqlite3
import sys

DB = r"C:\Users\fms\.local\share\opencode\opencode.db"
SESSION = "ses_fc6422bd4fferp1Hlvc3iIwoyD"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()
cur.execute(
    "SELECT id, time_created, data FROM part WHERE session_id=? AND data LIKE ? "
    "AND time_created BETWEEN ? AND ? ORDER BY time_created",
    (SESSION, '%"tool":"bash"%', 1787712844000, 1787713560000),
)
for r in cur.fetchall():
    d = json.loads(r[2])
    out = d.get("state", {}).get("output", "")
    cmd = d.get("state", {}).get("input", {}).get("command", "")
    print("=" * 20, r[0], r[1])
    print("CMD:", cmd[:120])
    print(out[:2000])
