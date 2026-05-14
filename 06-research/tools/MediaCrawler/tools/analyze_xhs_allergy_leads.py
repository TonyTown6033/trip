# -*- coding: utf-8 -*-
"""Analyze XHS crawled data and export allergy testing customer lead sheets."""

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
OUTPUT_XLSX = OUTPUT_DIR / "xhs_allergy_customer_profiles.xlsx"
OUTPUT_CSV = OUTPUT_DIR / "xhs_allergy_customer_profiles.csv"

ALLOWED_SOURCE_KEYWORDS = {
    "过敏原检测",
    "过敏源检测",
    "查过敏原",
    "查过敏源",
    "过敏检测",
    "过敏体质检测",
    "食物过敏检测",
    "食物不耐受检测",
    "IgE检测",
    "ige过敏检测",
    "儿童过敏原检测",
    "宝宝过敏原检测",
    "湿疹查过敏原",
    "荨麻疹查过敏原",
    "鼻炎查过敏原",
    "尘螨过敏检测",
    "花粉过敏检测",
    "宠物过敏检测",
    "皮肤点刺试验",
    "过敏原检测多少钱",
}


ALLERGY_CONTEXT_RE = re.compile(
    r"过敏|过敏原|过敏源|IgE|ige|IGE|湿疹|荨麻疹|鼻炎|哮喘|尘螨|螨虫|花粉|"
    r"食物不耐受|食物过敏|皮肤点刺|点刺试验|猫毛|狗毛|宠物过敏|乳糖不耐|特应性皮炎"
)
DETECTION_NEED_RE = re.compile(
    r"检测|检查|查|测|抽血|报告|结果|指标|套餐|项目|多少钱|价格|费用|医院|机构|"
    r"哪里|去哪|怎么查|怎么测|有必要|准不准|靠谱吗|推荐|挂什么科|ige高|IgE高|IGE高"
)
SYMPTOM_RE = re.compile(
    r"湿疹|荨麻疹|鼻炎|鼻塞|流鼻涕|打喷嚏|咳嗽|哮喘|喘|皮炎|红疹|瘙痒|痒|"
    r"起疹|红肿|腹泻|拉肚子|呕吐|眼痒|流泪|喉咙|过敏反应"
)
CHILD_RE = re.compile(r"宝宝|孩子|小孩|儿童|婴儿|幼儿|娃|儿子|女儿|宝妈|妈妈|家长")
PET_RE = re.compile(r"猫|狗|宠物|猫毛|狗毛|养猫|养狗|吸猫|铲屎官")
FOOD_RE = re.compile(r"食物|牛奶|鸡蛋|蛋白|海鲜|虾|蟹|花生|坚果|小麦|乳糖|不耐受")
URGENT_RE = re.compile(r"现在|最近|一直|反复|严重|急|怎么办|求|有没有|帮忙|崩溃|难受|影响")
PERSONAL_NEED_RE = re.compile(
    r"我|我家|本人|自己|宝宝|孩子|小孩|儿子|女儿|妈妈|家里|最近|一直|反复|"
    r"怎么办|想|需要|求|有没有|哪里|多少钱|检测|检查|查|测|报告"
)
SUPPLY_RE = re.compile(
    r"广告|推广|福利|团购|优惠|下单|购买|私信|主页|链接|领取|咨询我|扫码|客服|"
    r"代理|招商|合作|品牌|厂家|测评|种草|好物|抗过敏蛋片|鼎伴|益生菌|产品"
)
PROVIDER_ACCOUNT_RE = re.compile(
    r"体检中心|检测中心|医院|门诊|诊所|医生|医师|主任|护士|营养师|营养|健康管理|"
    r"皮肤科|儿科|过敏科|官方|旗舰店|专营店|科普|老师"
)
NOISE_RE = re.compile(r"无畏契约|瓦罗兰特|蛋仔|王者荣耀|英雄联盟|LOL|代练|陪玩|上分")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def compact_text(value: Any, limit: int = 360) -> str:
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
    return " ".join(str(note.get(k, "")) for k in ("title", "desc", "tag_list", "nickname"))


def comment_text(comment: dict[str, Any]) -> str:
    return " ".join(str(comment.get(k, "")) for k in ("content", "nickname"))


def all_jsonl(kind: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(DATA_DIR.glob(f"search_{kind}_*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def lead_tags(text: str) -> list[str]:
    tags: list[str] = []
    if CHILD_RE.search(text):
        tags.append("儿童/家长")
    if PET_RE.search(text):
        tags.append("宠物过敏")
    if FOOD_RE.search(text):
        tags.append("食物相关")
    if SYMPTOM_RE.search(text):
        tags.append("症状明显")
    if DETECTION_NEED_RE.search(text):
        tags.append("检测咨询")
    if URGENT_RE.search(text):
        tags.append("近期/急迫")
    if SUPPLY_RE.search(text):
        tags.append("疑似广告/供给")
    return tags


def classify_note(note: dict[str, Any]) -> str:
    text = note_text(note)
    if NOISE_RE.search(text) and not ALLERGY_CONTEXT_RE.search(text):
        return "非过敏噪声"
    if SUPPLY_RE.search(text):
        return "广告/产品/供给内容"
    if DETECTION_NEED_RE.search(text) and SYMPTOM_RE.search(text):
        return "检测需求笔记"
    if ALLERGY_CONTEXT_RE.search(text):
        return "过敏相关笔记"
    return "弱相关/噪声"


def score_text(primary_text: str, context_text: str, source: str) -> tuple[int, list[str], str]:
    reasons: list[str] = []
    score = 0
    combined = f"{primary_text} {context_text}"

    if NOISE_RE.search(combined) and not ALLERGY_CONTEXT_RE.search(combined):
        return -100, ["非过敏检测上下文"], "噪声"
    if not ALLERGY_CONTEXT_RE.search(combined):
        return -80, ["缺少过敏/检测上下文"], "噪声"

    if ALLERGY_CONTEXT_RE.search(primary_text):
        score += 20
        reasons.append("自身内容有过敏/IgE/症状上下文")
    else:
        score += 8
        reasons.append("所在笔记有过敏上下文")

    if DETECTION_NEED_RE.search(primary_text):
        score += 35
        reasons.append("出现检测/报告/费用/机构等咨询信号")
    if SYMPTOM_RE.search(primary_text):
        score += 25
        reasons.append("出现明确症状痛点")
    if CHILD_RE.search(primary_text):
        score += 15
        reasons.append("儿童/家长场景")
    if FOOD_RE.search(primary_text):
        score += 10
        reasons.append("食物过敏或不耐受场景")
    if PET_RE.search(primary_text):
        score += 10
        reasons.append("宠物过敏场景")
    if URGENT_RE.search(primary_text):
        score += 10
        reasons.append("近期或急迫表达")
    if source == "评论用户":
        score += 8
        reasons.append("评论用户可作为互动线索")
        if not PERSONAL_NEED_RE.search(primary_text):
            score -= 25
            reasons.append("评论本身缺少个人需求表达")
    if SUPPLY_RE.search(primary_text):
        score -= 45
        reasons.append("疑似广告/产品/供给方")

    if score >= 80:
        level = "高意向客户"
    elif score >= 55:
        level = "中意向客户"
    elif score >= 30:
        level = "低意向线索"
    elif SUPPLY_RE.search(primary_text):
        level = "广告/供给方"
    else:
        level = "噪声"
    return score, reasons, level


def make_lead_row(
    source: str,
    user: dict[str, Any],
    evidence_text: str,
    note: dict[str, Any],
    event_time: Any,
    comment_id: str = "",
) -> dict[str, Any] | None:
    score, reasons, level = score_text(evidence_text, note_text(note), source)
    account_text = f"{user.get('nickname', '')} {note.get('nickname', '')}"
    if PROVIDER_ACCOUNT_RE.search(account_text):
        score -= 60
        reasons.append("账号疑似机构/医生/科普/供给方")
        level = "广告/供给方" if score < 55 else "低意向线索"
    if level == "噪声":
        return None

    combined = f"{evidence_text} {note_text(note)}"
    tags = lead_tags(combined)
    next_action = {
        "高意向客户": "优先私信：询问症状、人群年龄、是否已有检测报告，引导填写 allergy.superelite.studio",
        "中意向客户": "可私信：围绕检测项目、费用、报告解读做轻咨询",
        "低意向线索": "先收藏观察：可用科普内容互动，不建议强销售",
        "广告/供给方": "不作为客户：仅用于竞品/内容参考",
    }.get(level, "")

    return {
        "线索等级": level,
        "意向分": score,
        "线索来源": source,
        "用户昵称": user.get("nickname", ""),
        "用户ID": user.get("user_id", ""),
        "IP属地": user.get("ip_location", "") or note.get("ip_location", ""),
        "场景标签": "；".join(tags),
        "客户痛点/证据": compact_text(evidence_text, 520),
        "命中原因": "；".join(reasons),
        "建议动作": next_action,
        "来源关键词": note.get("source_keyword", ""),
        "笔记标题": compact_text(note.get("title"), 180),
        "笔记分类": classify_note(note),
        "笔记作者": note.get("nickname", ""),
        "笔记链接": note.get("note_url", ""),
        "发生时间": ts_to_dt(event_time),
        "note_id": note.get("note_id", ""),
        "comment_id": comment_id,
        "liked_count": note.get("liked_count", ""),
        "comment_count": note.get("comment_count", ""),
    }


def build_rows() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_notes = all_jsonl("contents")
    raw_comments = all_jsonl("comments")
    notes = list({n.get("note_id"): n for n in raw_notes if n.get("note_id")}.values())
    comments = list({c.get("comment_id"): c for c in raw_comments if c.get("comment_id")}.values())
    note_by_id = {n.get("note_id"): n for n in notes}

    rows: list[dict[str, Any]] = []
    for comment in comments:
        note = note_by_id.get(comment.get("note_id"), {})
        if note.get("source_keyword") not in ALLOWED_SOURCE_KEYWORDS:
            continue
        row = make_lead_row(
            source="评论用户",
            user=comment,
            evidence_text=str(comment.get("content", "")),
            note=note,
            event_time=comment.get("create_time"),
            comment_id=str(comment.get("comment_id", "")),
        )
        if row:
            rows.append(row)

    for note in notes:
        if note.get("source_keyword") not in ALLOWED_SOURCE_KEYWORDS:
            continue
        row = make_lead_row(
            source="笔记作者",
            user=note,
            evidence_text=f"{note.get('title', '')} {note.get('desc', '')}",
            note=note,
            event_time=note.get("time"),
        )
        if row:
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        level_rank = {"高意向客户": 0, "中意向客户": 1, "低意向线索": 2, "广告/供给方": 3}
        df["_rank"] = df["线索等级"].map(level_rank).fillna(9)
        df = df.sort_values(["_rank", "意向分", "发生时间"], ascending=[True, False, False])
        df = df.drop(columns=["_rank"])

    profile_rows: list[dict[str, Any]] = []
    if not df.empty:
        grouped = df.groupby("用户ID", dropna=False)
        for user_id, group in grouped:
            group = group.sort_values("意向分", ascending=False)
            best = group.iloc[0]
            if best["线索等级"] == "广告/供给方":
                continue
            tags = sorted({tag for value in group["场景标签"] for tag in str(value).split("；") if tag})
            profile_rows.append(
                {
                    "客户等级": best["线索等级"],
                    "最高意向分": int(best["意向分"]),
                    "用户昵称": best["用户昵称"],
                    "用户ID": user_id,
                    "IP属地": best["IP属地"],
                    "客户画像": "；".join(tags),
                    "核心痛点": best["客户痛点/证据"],
                    "建议动作": best["建议动作"],
                    "触点数": int(len(group)),
                    "主要来源关键词": Counter(group["来源关键词"]).most_common(1)[0][0],
                    "最近发生时间": group["发生时间"].max(),
                    "代表笔记链接": best["笔记链接"],
                }
            )
    profiles = pd.DataFrame(profile_rows)
    if not profiles.empty:
        level_rank = {"高意向客户": 0, "中意向客户": 1, "低意向线索": 2}
        profiles["_rank"] = profiles["客户等级"].map(level_rank).fillna(9)
        profiles = profiles.sort_values(["_rank", "最高意向分", "最近发生时间"], ascending=[True, False, False])
        profiles = profiles.drop(columns=["_rank"])

    summary_rows = [
        {"指标": "原始笔记数", "数量": len(notes)},
        {"指标": "原始评论数", "数量": len(comments)},
        {"指标": "输出线索条数", "数量": len(df)},
        {"指标": "去重客户数", "数量": len(profiles)},
    ]
    if not df.empty:
        for key, count in Counter(df["线索等级"]).items():
            summary_rows.append({"指标": key, "数量": int(count)})
        for key, count in Counter(df["线索来源"]).items():
            summary_rows.append({"指标": key, "数量": int(count)})
    summary = pd.DataFrame(summary_rows)

    by_keyword: list[dict[str, Any]] = []
    if not df.empty:
        valid = df[df["线索等级"].isin(["高意向客户", "中意向客户", "低意向线索"])]
        for keyword, group in valid.groupby("来源关键词"):
            by_keyword.append(
                {
                    "来源关键词": keyword,
                    "高意向客户": int((group["线索等级"] == "高意向客户").sum()),
                    "中意向客户": int((group["线索等级"] == "中意向客户").sum()),
                    "低意向线索": int((group["线索等级"] == "低意向线索").sum()),
                    "线索合计": int(len(group)),
                    "平均意向分": round(float(group["意向分"].mean()), 1),
                }
            )
    keyword_df = pd.DataFrame(by_keyword)
    if not keyword_df.empty:
        keyword_df = keyword_df.sort_values(["高意向客户", "线索合计"], ascending=[False, False])

    return df, profiles, summary, keyword_df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    leads, profiles, summary, keyword_df = build_rows()

    leads.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUTPUT_XLSX) as writer:
        profiles.to_excel(writer, index=False, sheet_name="客户资料")
        leads.to_excel(writer, index=False, sheet_name="线索明细")
        summary.to_excel(writer, index=False, sheet_name="汇总")
        keyword_df.to_excel(writer, index=False, sheet_name="关键词效果")

    print(f"profiles={len(profiles)} leads={len(leads)}")
    print(f"csv={OUTPUT_CSV}")
    print(f"xlsx={OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
