#!/usr/bin/env python3
"""photo-press-v1 可执行回归 runner。

读 SKILL.md + references/craft-cards.md + 场景配置 → 调生成通道（seedream）
→ 6 维评分（视觉模型）→ 输出 results matrix（工艺 × 场景 × 分数 × 状态）。

用法:
  python run-repro.py --scenarios scenarios.json --out results/            # 真实执行
  python run-repro.py --scenarios scenarios.json --dry-run                 # 冒烟：只校验配置与输入

说明:
  - API key 优先读环境变量 ARK_API_KEY；缺失时回退读 ~/.config/opencode/opencode.json
    （provider.volcengine-coding-plan.options.apiKey）。两者都缺则报错退出。
  - 生成通道：Agent Plan seedream（doubao-seedream-5.0-lite）。
  - 双参考生成：源图（内容通道）+ 工艺 anchor（质感通道），与 72-matrix 基线对齐（specs.csv refs=[源图, anchor]）。
  - 6 维评分：doubao-seed-2.0-lite（subject/space/light/craft/color/text，各 1-5 分）。
  - 每次运行追加写入 <out>/matrix.csv；--dry-run 不调用任何 API。
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
CRAFT_CARDS = SKILL_ROOT / "references" / "craft-cards.md"
ANCHORS = SKILL_ROOT / "assets" / "craft-samples"
ENDPOINT = "https://ark.cn-beijing.volces.com/api/plan/v3/images/generations"
GENERATION_MODEL = "doubao-seedream-5.0-lite"
REVIEW_MODEL = "doubao-seed-2.0-lite"

# 默认 strength（SKILL.md §7：印刷工艺 0.9，极简特例 0.7）
DEFAULT_STRENGTH = 0.9
MINIMALIST_STRENGTH = 0.7

FAIL_THRESHOLD = 0.4  # 数值边缘相关 < 0.4 视为保真失败


# ---------------- 配置与输入 ----------------


def _load_api_key() -> str:
    """入口判空：环境变量优先，回退 opencode.json；都没有则明确报错。"""
    key = os.environ.get("ARK_API_KEY", "").strip()
    if key:
        return key
    cfg_path = Path(os.path.expanduser("~/.config/opencode/opencode.json"))
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            key = (
                cfg.get("provider", {})
                .get("volcengine-coding-plan", {})
                .get("options", {})
                .get("apiKey", "")
            )
            if key:
                return key
        except (json.JSONDecodeError, OSError) as e:
            raise RuntimeError(f"opencode.json 读取失败: {e}") from e
    raise RuntimeError(
        "缺少 API key：请设置环境变量 ARK_API_KEY，或确保 ~/.config/opencode/opencode.json "
        "含 provider.volcengine-coding-plan.options.apiKey"
    )


def load_scenarios(path: Path) -> list[dict]:
    """读取场景配置（JSON）。空数组视为配置错误。"""
    if not path.exists():
        raise FileNotFoundError(f"场景配置不存在: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", data) if isinstance(data, dict) else data
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError(f"场景配置为空或格式错误: {path}")
    return scenarios


def parse_craft_fragments(cards_text: str) -> dict[str, str]:
    """从 craft-cards.md 解析每个工艺的「工艺语言片段」（第 5 模块注入用）。"""
    fragments: dict[str, str] = {}
    # 匹配 "## N. <cid> — 中文名" 与后续 "**工艺语言片段**：" 代码块
    for m in re.finditer(r"^##\s+\d+\.\s+([a-z-]+)\s+—", cards_text, re.M):
        cid = m.group(1)
        rest = cards_text[m.end() :]
        fm = re.search(r"\*\*工艺语言片段\*\*：\s*```(.*?)```", rest, re.S)
        if fm:
            fragments[cid] = fm.group(1).strip()
    return fragments


def compile_prompt(craft: str, source_desc: str, cards_text: str) -> str:
    """按 SKILL.md §6 D 模板编译提示词：中文直白保真锚定 + 工艺语言片段。"""
    frag = parse_craft_fragments(cards_text).get(craft, "")
    if not frag:
        raise ValueError(f"工艺卡中未找到「{craft}」的工艺语言片段（craft-cards.md）")
    return (
        "严格保持原图构图不变：主体、位置、大小、轮廓、比例、地平线、光线方向全部与原图一致。\n"
        f"只改变媒介：把照片变成 {craft} 质感。{frag}\n"
        "不重新构图，不添加原图没有的元素。"
    )


def to_ref(path: str) -> str:
    """图片 → data URL（base64 本地传，URL 会超时）。"""
    if path.startswith(("http://", "https://")):
        return path
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"参考图不存在: {p}")
    ext = p.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(
        ext, "jpeg"
    )
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/{mime};base64,{b64}"


# ---------------- 通道调用 ----------------


def call_generate(
    key: str, prompt: str, refs: list[str], strength: float, size: str = "2k"
) -> str:
    """调 seedream 生成，返回结果图下载后的本地路径。失败显式抛错（不吞）。"""
    body = {
        "model": GENERATION_MODEL,
        "prompt": prompt,
        "size": size,
        "response_format": "url",
        "watermark": False,
        "output_format": "jpeg",
        "stream": False,
    }
    if refs:
        data_refs = [to_ref(r) for r in refs]
        body["image"] = data_refs[0] if len(data_refs) == 1 else data_refs
        body["reference_strength"] = strength
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"生成 HTTP {e.code}: {detail[:300]}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"生成网络错误: {e}") from e
    items = (data or {}).get("data") or []
    if not items:
        raise RuntimeError(f"生成响应无 data: {str(data)[:200]}")
    url = items[0].get("url")
    if not url:
        raise RuntimeError(f"生成响应无图片 URL: {str(items[0])[:200]}")
    out = (
        Path(os.environ.get("TEMP", "/tmp")) / f"pp_repro_{int(time.time() * 1000)}.jpg"
    )
    out.parent.mkdir(parents=True, exist_ok=True)  # TEMP 可能指向未创建目录（实测踩过）
    try:
        urllib.request.urlretrieve(url, out)
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(f"结果图下载失败: {e}") from e
    return str(out)


def call_review(key: str, source_path: str, result_path: str) -> dict:
    """调视觉模型对源图 vs 结果图做 6 维评分（doubao-seed-2.0-lite）。"""
    prompt = (
        "请对比源照片与风格转换结果，按 6 个维度评分（每维 1-5 分，5=完全达标），"
        '输出 JSON：{"subject":{"score":n,"pass":bool,"note":"..."},'
        '"space":{...},"light":{...},"craft":{...},"color":{...},"text":{...},'
        '"verdict":"pass|fail","summary":"..."}。'
        "维度：subject=主体识别（核心主体是否与源图同一主体且可识别）；space=空间关系；"
        "light=光线方向；craft=工艺质感是否符合该工艺；color=色彩规则；text=文字/乱码。"
    )
    body = {
        "model": REVIEW_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": to_ref(source_path)}},
                    {"type": "image_url", "image_url": {"url": to_ref(result_path)}},
                ],
            }
        ],
    }
    # 视觉聊天走同域 v3 端点
    url = ENDPOINT.rsplit("/images/", 1)[0] + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"审查 HTTP {e.code}: {detail[:300]}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"审查网络错误: {e}") from e
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError(f"审查响应无内容: {str(data)[:200]}")
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        raise RuntimeError(f"审查响应非 JSON: {content[:300]}")
    return json.loads(m.group(0))


# ---------------- 主流程 ----------------


def run(
    scenarios: list[dict],
    out_dir: Path,
    dry_run: bool,
    key: str | None,
    base_dir: Path | None = None,
) -> None:
    cards_text = CRAFT_CARDS.read_text(encoding="utf-8") if CRAFT_CARDS.exists() else ""
    if not cards_text:
        raise FileNotFoundError(f"工艺卡不存在: {CRAFT_CARDS}")
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = out_dir / "matrix.csv"
    header = [
        "cid",
        "scene",
        "source",
        "strength",
        "edge_guard",
        "subject",
        "space",
        "light",
        "craft",
        "color",
        "text",
        "verdict",
        "status",
    ]
    new_file = not matrix_path.exists()
    f = open(matrix_path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if new_file:
        w.writerow(header)

    try:
        for item in scenarios:
            cid = str(item.get("craft", "")).strip()
            scene = str(item.get("scene", "")).strip()
            source = str(item.get("source", "")).strip()
            strength = float(item.get("strength", DEFAULT_STRENGTH))
            refs = list(item.get("refs") or [])  # 入口判空
            # gap 项（无源图，未测试）：记录跳过，不阻断
            if not source:
                print(f"SKIP {scene or cid or '?'}: 无源图（gap），未测试")
                continue
            if not cid or not scene:
                raise ValueError(f"场景条目缺字段（需 craft/scene/source）: {item}")
            prompt = str(item.get("prompt", "")).strip() or compile_prompt(
                cid, scene, cards_text
            )
            # 相对路径解析：源图相对场景文件目录，refs 相对 skill 根
            src_path = (
                Path(source) if not source.startswith(("http://", "https://")) else None
            )
            if src_path is not None and not src_path.is_absolute():
                src_path = (base_dir or Path(".")) / src_path
                source = str(src_path)
            if src_path is not None and not src_path.exists():
                if str(item.get("status", "")) == "needs-source":
                    # 已知缺口：源图未归档（picsum seed 可复现），跳过不报错
                    print(f"SKIP {cid} × {scene}: 源图未归档（{source}），seed 可复现")
                    continue
                raise FileNotFoundError(f"源图不存在: {source}")
            # refs 解析为绝对路径（与 source 同待遇）：to_ref/call_generate 不感知 SKILL_ROOT，
            # 相对路径会在 CWD 下解析失败（2026-08-31 首次真实回归暴露）。
            resolved_refs: list[str] = []
            for r in refs:
                if r.startswith(("http://", "https://")):
                    resolved_refs.append(r)
                    continue
                rp = Path(r)
                if not rp.is_absolute():
                    rp = SKILL_ROOT / rp
                if not rp.exists():
                    raise FileNotFoundError(f"参考图不存在: {r}")
                resolved_refs.append(str(rp))
            refs = resolved_refs

            if dry_run:
                row = [
                    cid,
                    scene,
                    source,
                    strength,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "DRY-RUN",
                ]
            else:
                if key is None:  # 异常不吞：非 dry-run 必须有 key
                    raise RuntimeError("缺少 API key")
                # 双参考：源图（内容通道）+ 工艺 anchor（质感通道）。
                # 与 72-matrix 基线对齐（specs.csv refs=[源图 s{n}, anchor {craft}.jpg]，SKILL.md §6 双通道协议）。
                refs_with_source = [source] + refs
                result = call_generate(key, prompt, refs_with_source, strength)
                try:
                    review = call_review(key, source, result)
                except Exception as e:
                    # 审查失败不吞静默：记录原因，verdict 置 fail 由人工复核
                    print(f"WARN 审查失败 {cid}×{scene}: {e}")
                    review = {}
                dims = {
                    k: (
                        review.get(k, {}).get("score")
                        if isinstance(review.get(k), dict)
                        else None
                    )
                    for k in ["subject", "space", "light", "craft", "color", "text"]
                }
                verdict = review.get("verdict", "fail")
                row = [
                    cid,
                    scene,
                    source,
                    strength,
                    "-",
                    dims["subject"],
                    dims["space"],
                    dims["light"],
                    dims["craft"],
                    dims["color"],
                    dims["text"],
                    verdict,
                    verdict,
                ]
            w.writerow(row)
            f.flush()
            print(f"{'DRY' if dry_run else 'RUN'} {cid} × {scene} → {row[-1]}")
    finally:
        f.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenarios", required=True, help="场景配置 JSON")
    ap.add_argument("--out", default="results", help="输出目录（matrix.csv）")
    ap.add_argument("--dry-run", action="store_true", help="只校验配置与输入，不调 API")
    args = ap.parse_args()

    try:
        scenarios_path = Path(args.scenarios)
        scenarios = load_scenarios(scenarios_path)
        key = None if args.dry_run else _load_api_key()
        if not args.dry_run and not key:
            raise RuntimeError("非 dry-run 模式必须提供 API key")
        run(scenarios, Path(args.out), args.dry_run, key, scenarios_path.parent)
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
