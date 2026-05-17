#!/usr/bin/env python3
"""Sync Phase 2 stage markdown/CSV candidates into research aggregate CSVs."""

from __future__ import annotations

import csv
import glob
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOTELS_PATH = ROOT / "05-research" / "flyai-candidates" / "hotels.csv"
POI_PATH = ROOT / "05-research" / "flyai-candidates" / "poi.csv"

HOTEL_FIELDS = [
    "candidate_id",
    "query_date",
    "city",
    "stage",
    "source",
    "name",
    "area",
    "check_in",
    "check_out",
    "price_cny",
    "url",
    "research_status",
    "booking_status",
    "notes",
]

POI_FIELDS = [
    "candidate_id",
    "query_date",
    "city",
    "stage",
    "source",
    "name",
    "area",
    "estimated_price_cny",
    "url",
    "research_status",
    "visit_status",
    "notes",
]

STAGE_CITY = {
    "01-kunming": "昆明",
    "02-dali": "大理",
    "03-shaxi-jianchuan": "剑川",
    "04-lijiang": "丽江",
    "05-luguhu": "泸沽湖",
    "06-shangrila-deqin": "香格里拉/德钦",
    "07-tengchong-mangshi": "腾冲/芒市",
    "08-puer-jingmai-xishuangbanna": "普洱/景迈山/西双版纳",
    "09-jianshui-yuanyang-mengzi-puzhehei": "建水/元阳/蒙自/普者黑",
    "10-kunming-return": "昆明返程",
}

STAGE_DATES = {
    "01-kunming": ("2026-05-22", "2026-05-25"),
    "02-dali": ("2026-05-25", "2026-06-03"),
    "03-shaxi-jianchuan": ("2026-06-03", "2026-06-07"),
    "04-lijiang": ("2026-06-07", "2026-06-15"),
    "05-luguhu": ("2026-06-16", "2026-06-17"),
    "06-shangrila-deqin": ("2026-06-18", "2026-06-26"),
    "07-tengchong-mangshi": ("2026-06-27", "2026-07-03"),
    "08-puer-jingmai-xishuangbanna": ("2026-07-03", "2026-07-11"),
    "09-jianshui-yuanyang-mengzi-puzhehei": ("2026-07-11", "2026-07-19"),
    "10-kunming-return": ("2026-07-18", "2026-07-20"),
}


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return [{field: row.get(field, "") for field in fields} for row in csv.DictReader(file)]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def extract_url(text: str) -> str:
    match = re.search(r"https://[^ `|]+", text)
    return match.group(0) if match else ""


def clean_notes(text: str) -> str:
    return re.sub(r"链接[：: ]*`?https://[^ `|]+`?", "", text).strip("；; ")


def collect_hotels() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path_text in sorted(glob.glob(str(ROOT / "03-stages" / "*" / "stay.md"))):
        path = Path(path_text)
        stage = path.parent.name
        check_in, check_out = STAGE_DATES.get(stage, ("待定", "待定"))
        index = 1
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| 2026-05-") or "飞猪/FlyAI" not in line:
                continue
            cells = split_markdown_row(line)
            if len(cells) < 7:
                continue
            query_date, source, name, area, price, status, notes = cells[:7]
            if not name or name == "名称":
                continue
            price_value = re.sub(r"[^0-9.]", "", price) or "待查"
            rows.append(
                {
                    "candidate_id": f"hotel-{stage}-20260515-{index:03d}",
                    "query_date": query_date,
                    "city": STAGE_CITY.get(stage, stage),
                    "stage": stage,
                    "source": source,
                    "name": name,
                    "area": area,
                    "check_in": check_in,
                    "check_out": check_out,
                    "price_cny": price_value,
                    "url": extract_url(notes),
                    "research_status": "pending",
                    "booking_status": "候选" if status == "待人工确认" else status,
                    "notes": clean_notes(notes),
                }
            )
            index += 1
    return rows


def sync_hotels() -> int:
    existing = read_csv(HOTELS_PATH, HOTEL_FIELDS)
    generated = collect_hotels()
    generated_keys = {(row["stage"], row["name"]) for row in generated}
    merged = [
        row
        for row in existing
        if (row["stage"], row["name"]) not in generated_keys
    ]
    merged.extend(generated)
    write_csv(HOTELS_PATH, HOTEL_FIELDS, merged)
    return len(merged)


def collect_pois() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path_text in sorted(glob.glob(str(ROOT / "07-attractions" / "*.csv"))):
        path = Path(path_text)
        with path.open("r", encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                rows.append(
                    {
                        "candidate_id": row.get("poi_id", ""),
                        "query_date": row.get("query_date", ""),
                        "city": row.get("city", ""),
                        "stage": row.get("stage", ""),
                        "source": row.get("source", ""),
                        "name": row.get("name", ""),
                        "area": row.get("address", ""),
                        "estimated_price_cny": row.get("estimated_ticket_cny", ""),
                        "url": "",
                        "research_status": "pending",
                        "visit_status": row.get("priority", "候选"),
                        "notes": f"{row.get('category', '')}；{row.get('notes', '')}".strip("；"),
                    }
                )
    return rows


def sync_pois() -> int:
    rows = collect_pois()
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        key = (row["stage"], row["name"], row["area"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    write_csv(POI_PATH, POI_FIELDS, deduped)
    return len(deduped)


def main() -> None:
    hotel_count = sync_hotels()
    poi_count = sync_pois()
    print(f"synced hotels: {hotel_count} rows")
    print(f"synced poi: {poi_count} rows")


if __name__ == "__main__":
    main()
