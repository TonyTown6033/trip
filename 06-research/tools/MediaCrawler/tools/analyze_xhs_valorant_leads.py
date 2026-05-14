# -*- coding: utf-8 -*-
"""Analyze XHS crawled data and export Valorant lead sheets."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "xhs" / "jsonl"
OUTPUT_DIR = ROOT / "data" / "analysis"
OUTPUT_XLSX = OUTPUT_DIR / "xhs_valorant_customer_leads.xlsx"
OUTPUT_CSV = OUTPUT_DIR / "xhs_valorant_customer_leads.csv"


GAME_RE = re.compile(r"无畏契约|瓦罗兰特|valorant|VALORANT|打瓦|端瓦|瓦陪|瓦店|瓦赋能|无畏")
RANK_RE = re.compile(r"黑铁|青铜|白银|黄金|铂金|白金|钻石|下三|低段|低分段|晋级赛")
NEED_RE = re.compile(
    r"求带|找人带|有人带|带我|谁带|谁打|有人打|有吗|还有吗|现在.*(打|带|有)|"
    r"可以带吗|能带吗|可以吗|接吗|还接吗|还能进吗|怎么找|推荐吗|"
    r"多少钱|价格|怎么收费|收费|带价|包赢|想找|想点|想上分|上不去|打不上去|卡段位|卡在|太菜|不会玩|新手"
)
SERVICE_RE = re.compile(r"代练|代打|上分|陪玩|陪练|赋能|纯绿|手打|老板|点陪|陪陪|教学|私教")
SUPPLY_RE = re.compile(
    r"接单|接瓦|接陪|接老板|打手|工作室|陪玩店|电竞|俱乐部|招新|招人|招打手|"
    r"下单|欢迎咨询|主页|私我|私信|可接|可带|可陪|包结|输结|赢照常|"
    r"价格表|价目表|纯绿手打|大学生纯绿|老板来|组队等你|GZR|考核|店|"
    r"可教学|可玩|试音|技术陪|包c|包C|包赢|客反|老板反馈|国服当前|"
    r"神话|超凡|赋能|代打个单子|欢迎来问|白菜|钻石以下|情绪价值|"
    r"\d+\s*[rR]\s*(一小时|/h|每小时|一把|/把)|\d+\s*/h|价格[:：]"
)
OTHER_GAME_RE = re.compile(r"蛋仔|王者|洛克王国|明日方舟|三角洲|永劫|和平精英|英雄联盟|LOL|金铲铲")
EXCLUDED_SOURCE_KEYWORDS = {"远程工作"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def compact_text(value: Any, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def ts_to_dt(value: Any) -> str:
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return ""
    if ts > 10_000_000_000:
        ts = ts // 1000
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def note_text(note: dict[str, Any]) -> str:
    return " ".join(
        str(note.get(k, ""))
        for k in ("title", "desc", "tag_list", "nickname")
    )


def comment_text(comment: dict[str, Any]) -> str:
    return " ".join(str(comment.get(k, "")) for k in ("content", "nickname"))


def classify_note(note: dict[str, Any]) -> str:
    text = note_text(note)
    if GAME_RE.search(text) and SUPPLY_RE.search(text):
        return "同行/服务供给笔记"
    if GAME_RE.search(text):
        return "游戏相关笔记"
    if OTHER_GAME_RE.search(text):
        return "其他游戏噪声"
    return "弱相关/噪声"


def score_comment(comment: dict[str, Any], note: dict[str, Any] | None) -> tuple[int, list[str], str]:
    ctext = comment_text(comment)
    ntext = note_text(note or {})
    combined = f"{ctext} {ntext}"
    reasons: list[str] = []
    score = 0

    if not GAME_RE.search(combined):
        return -100, ["缺少无畏契约/瓦上下文"], "噪声"

    if NEED_RE.search(ctext):
        score += 45
        reasons.append("评论有明确需求/询价/求带")
    if RANK_RE.search(ctext):
        score += 25
        reasons.append("评论提到目标段位")
    if GAME_RE.search(ctext):
        score += 20
        reasons.append("评论明确提到无畏契约/瓦")
    elif GAME_RE.search(ntext):
        score += 10
        reasons.append("所在笔记为无畏契约/瓦相关")
    if SERVICE_RE.search(ctext):
        score += 15
        reasons.append("评论提到上分/陪玩/代练服务")
    if re.search(r"现在|今天|今晚|马上|还能|还有|有人", ctext):
        score += 10
        reasons.append("有即时需求信号")

    if SUPPLY_RE.search(ctext):
        score -= 55
        reasons.append("疑似同行/供给方")
    if OTHER_GAME_RE.search(combined) and not GAME_RE.search(combined):
        score -= 40
        reasons.append("非无畏契约游戏")

    if score >= 75:
        level = "高意向客户"
    elif score >= 50:
        level = "中意向客户"
    elif score >= 25:
        level = "低意向线索"
    elif SUPPLY_RE.search(ctext):
        level = "同行/供给方"
    else:
        level = "噪声"
    return score, reasons, level


def score_note_author(note: dict[str, Any]) -> tuple[int, list[str], str]:
    text = note_text(note)
    reasons: list[str] = []
    score = 0
    if not GAME_RE.search(text):
        return -100, ["缺少无畏契约/瓦上下文"], "噪声"
    if GAME_RE.search(text):
        score += 20
        reasons.append("笔记为无畏契约/瓦相关")
    if NEED_RE.search(text):
        score += 35
        reasons.append("笔记正文有需求/询价/求带")
    if RANK_RE.search(text):
        score += 20
        reasons.append("笔记提到段位痛点")
    if SERVICE_RE.search(text):
        score += 10
        reasons.append("笔记提到服务场景")
    if SUPPLY_RE.search(text):
        score -= 45
        reasons.append("笔记作者疑似同行/供给方")
    if OTHER_GAME_RE.search(text) and not GAME_RE.search(text):
        score -= 40
        reasons.append("非无畏契约游戏")

    if score >= 55:
        level = "高意向客户"
    elif score >= 35:
        level = "中意向客户"
    elif SUPPLY_RE.search(text):
        level = "同行/供给方"
    else:
        level = "噪声"
    return score, reasons, level


def build_rows() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_notes = read_jsonl(DATA_DIR / "search_contents_2026-05-06.jsonl")
    raw_comments = read_jsonl(DATA_DIR / "search_comments_2026-05-06.jsonl")
    notes = list({n.get("note_id"): n for n in raw_notes if n.get("note_id")}.values())
    comments = list({c.get("comment_id"): c for c in raw_comments if c.get("comment_id")}.values())
    note_by_id = {n.get("note_id"): n for n in notes}

    rows: list[dict[str, Any]] = []
    for comment in comments:
        note = note_by_id.get(comment.get("note_id"), {})
        if note.get("source_keyword") in EXCLUDED_SOURCE_KEYWORDS:
            continue
        score, reasons, level = score_comment(comment, note)
        if level == "噪声" and score < 25:
            continue
        rows.append(
            {
                "线索等级": level,
                "意向分": score,
                "线索来源": "评论用户",
                "用户昵称": comment.get("nickname", ""),
                "用户ID": comment.get("user_id", ""),
                "IP属地": comment.get("ip_location", ""),
                "评论时间": ts_to_dt(comment.get("create_time")),
                "评论内容": compact_text(comment.get("content"), 500),
                "命中原因": "；".join(reasons),
                "来源关键词": note.get("source_keyword", ""),
                "笔记标题": compact_text(note.get("title"), 180),
                "笔记作者": note.get("nickname", ""),
                "笔记分类": classify_note(note),
                "笔记链接": note.get("note_url", ""),
                "note_id": comment.get("note_id", ""),
                "comment_id": comment.get("comment_id", ""),
                "like_count": comment.get("like_count", ""),
                "sub_comment_count": comment.get("sub_comment_count", ""),
            }
        )

    for note in notes:
        if note.get("source_keyword") in EXCLUDED_SOURCE_KEYWORDS:
            continue
        score, reasons, level = score_note_author(note)
        if level not in {"高意向客户", "中意向客户"}:
            continue
        rows.append(
            {
                "线索等级": level,
                "意向分": score,
                "线索来源": "笔记作者",
                "用户昵称": note.get("nickname", ""),
                "用户ID": note.get("user_id", ""),
                "IP属地": note.get("ip_location", ""),
                "评论时间": ts_to_dt(note.get("time")),
                "评论内容": compact_text(f"{note.get('title', '')} {note.get('desc', '')}", 500),
                "命中原因": "；".join(reasons),
                "来源关键词": note.get("source_keyword", ""),
                "笔记标题": compact_text(note.get("title"), 180),
                "笔记作者": note.get("nickname", ""),
                "笔记分类": classify_note(note),
                "笔记链接": note.get("note_url", ""),
                "note_id": note.get("note_id", ""),
                "comment_id": "",
                "like_count": note.get("liked_count", ""),
                "sub_comment_count": note.get("comment_count", ""),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        level_rank = {"高意向客户": 0, "中意向客户": 1, "低意向线索": 2, "同行/供给方": 3, "噪声": 4}
        df["_rank"] = df["线索等级"].map(level_rank).fillna(9)
        df = df.sort_values(["_rank", "意向分", "评论时间"], ascending=[True, False, False])
        df = df.drop(columns=["_rank"])

    summary_rows = [
        {"指标": "笔记总数", "数量": len(notes)},
        {"指标": "评论总数", "数量": len(comments)},
    ]
    if not df.empty:
        for key, count in Counter(df["线索等级"]).items():
            summary_rows.append({"指标": key, "数量": count})
        for key, count in Counter(df["线索来源"]).items():
            summary_rows.append({"指标": key, "数量": count})
    summary = pd.DataFrame(summary_rows)

    by_keyword = []
    if not df.empty:
        grouped = df[df["线索等级"].isin(["高意向客户", "中意向客户"])].groupby("来源关键词")
        for keyword, group in grouped:
            by_keyword.append(
                {
                    "来源关键词": keyword,
                    "高意向客户": int((group["线索等级"] == "高意向客户").sum()),
                    "中意向客户": int((group["线索等级"] == "中意向客户").sum()),
                    "线索合计": int(len(group)),
                    "平均意向分": round(float(group["意向分"].mean()), 1),
                }
            )
    keyword_df = pd.DataFrame(by_keyword).sort_values("线索合计", ascending=False) if by_keyword else pd.DataFrame()
    return df, summary, keyword_df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    leads, summary, keyword_df = build_rows()
    customer_leads = leads[leads["线索等级"].isin(["高意向客户", "中意向客户"])].copy()
    supply_leads = leads[leads["线索等级"].eq("同行/供给方")].copy()
    low_leads = leads[leads["线索等级"].eq("低意向线索")].copy()

    customer_leads.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        customer_leads.to_excel(writer, index=False, sheet_name="客户线索")
        supply_leads.to_excel(writer, index=False, sheet_name="同行供给方")
        low_leads.to_excel(writer, index=False, sheet_name="低意向线索")
        leads.to_excel(writer, index=False, sheet_name="全部命中")
        summary.to_excel(writer, index=False, sheet_name="汇总")
        keyword_df.to_excel(writer, index=False, sheet_name="关键词效果")
    print(f"customer_leads={len(customer_leads)}")
    print(f"all_hits={len(leads)}")
    print(f"xlsx={OUTPUT_XLSX}")
    print(f"csv={OUTPUT_CSV}")


if __name__ == "__main__":
    main()
