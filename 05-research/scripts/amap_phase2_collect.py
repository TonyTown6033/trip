#!/usr/bin/env python3
"""Collect Phase 2 AMap POI candidates via REST Web Service."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
ATTRACTIONS_DIR = ROOT / "07-attractions"
FOOD_PATH = ROOT / "food" / "food.csv"
SOURCE = "高德地图 REST place/text"
QUERY_DATE = date.today().isoformat()

ATTRACTION_FIELDS = [
    "poi_id",
    "query_date",
    "city",
    "stage",
    "source",
    "name",
    "category",
    "type",
    "address",
    "location",
    "estimated_ticket_cny",
    "opening_hours",
    "reservation",
    "priority",
    "notes",
]

FOOD_FIELDS = [
    "candidate_id",
    "query_date",
    "city",
    "stage",
    "source",
    "name",
    "area",
    "category",
    "estimated_price_cny",
    "must_try",
    "url",
    "research_status",
    "visit_status",
    "notes",
]

ATTRACTION_EXCLUDED_TYPE_PREFIXES = (
    "住宿服务;",
    "生活服务;",
    "购物服务;",
    "餐饮服务;",
    "交通设施服务;",
    "医疗保健服务;",
    "公司企业;",
    "政府机构及社会团体;",
    "商务住宅;",
)

ATTRACTION_ALLOWED_TYPE_PREFIXES = (
    "风景名胜;",
    "科教文化服务;",
    "地名地址信息;自然地名;",
    "交通设施服务;火车站;",
    "交通设施服务;长途汽车站;",
)

ATTRACTION_ALLOWED_NAMES = ("古城", "古镇", "老街", "夜市", "市场", "集市", "步行街")
ATTRACTION_EXCLUDED_NAME_TOKENS = (
    "停车场",
    "停车点",
    "等候厅",
    "休息厅",
    "贵宾室",
    "售票处",
    "文物管理所",
    "游客集散中心",
    "游乐场",
)


@dataclass(frozen=True)
class Stage:
    stage: str
    city: str
    filename: str
    search_city: str
    attraction_queries: tuple[tuple[str, str, str], ...]
    food_queries: tuple[tuple[str, str, str, str, str], ...]


STAGES = [
    Stage(
        stage="01-kunming",
        city="昆明",
        filename="kunming.csv",
        search_city="昆明",
        attraction_queries=(
            ("翠湖 公园", "湖边/公园", "免费慢逛，适合到达后低强度"),
            ("云南大学", "校园/街区", "免费慢逛，注意校区开放规则"),
            ("昆明老街", "古城/街区", "免费慢逛，注意游客价"),
            ("云南省博物馆", "博物馆/室内", "雨天备选，预约待查"),
            ("官渡古镇", "古镇/村落", "免费慢逛，适合预算日"),
        ),
        food_queries=(
            ("米线", "米线/简餐", "10-30", "米线/饵丝", "低价正餐候选"),
            ("小吃", "小吃", "10-30", "小吃/早点", "低价补充"),
            ("农贸市场", "市场", "5-30", "水果/早点/简餐", "长期补给候选"),
        ),
    ),
    Stage(
        stage="05-luguhu",
        city="泸沽湖",
        filename="luguhu.csv",
        search_city="丽江",
        attraction_queries=(
            ("泸沽湖", "湖边/公园", "天气和道路允许时保留"),
            ("大落水村", "村落/住宿区", "优先住宿和低强度湖边活动"),
            ("里格半岛", "湖边/观景", "天气好再去，不硬排"),
            ("草海 走婚桥", "湖边/湿地", "雨天和道路差时跳过"),
            ("女神湾", "湖边/观景", "路程较绕，拼车时再考虑"),
        ),
        food_queries=(
            ("泸沽湖 米线", "米线/简餐", "15-35", "米线/简餐", "低价正餐候选"),
            ("大落水 餐馆", "湖边餐馆", "20-50", "家常菜/简餐", "住宿附近吃饭候选"),
            ("泸沽湖 超市", "补给", "5-30", "饮水/水果/零食", "湖区补给候选"),
        ),
    ),
    Stage(
        stage="06-shangrila-deqin",
        city="香格里拉/德钦",
        filename="shangrila-deqin.csv",
        search_city="迪庆",
        attraction_queries=(
            ("独克宗古城", "古城/街区", "高海拔适应日低强度慢走"),
            ("松赞林寺", "人文景区", "门票待查，身体状态允许再去"),
            ("纳帕海", "草原/湿地", "天气好再去，默认不硬排"),
            ("普达措国家公园", "自然景区", "门票和交通待查，预算紧张时跳过"),
            ("飞来寺 梅里雪山", "雪山/观景", "德钦天气窗口允许时保留"),
            ("雾浓顶", "雪山/观景", "德钦可选观景点"),
        ),
        food_queries=(
            ("香格里拉 米线", "米线/简餐", "15-35", "米线/简餐", "低价正餐候选"),
            ("独克宗 餐馆", "古城餐馆", "20-55", "牦牛肉/藏餐/简餐", "古城附近吃饭候选"),
            ("德钦 餐馆", "县城餐馆", "20-55", "简餐/藏餐", "德钦过渡餐食候选"),
            ("香格里拉 农贸市场", "市场", "5-30", "水果/早点/补给", "高海拔补给候选"),
        ),
    ),
    Stage(
        stage="07-tengchong-mangshi",
        city="腾冲/芒市",
        filename="tengchong-mangshi.csv",
        search_city="保山",
        attraction_queries=(
            ("和顺古镇", "古镇/村落", "慢逛核心，可按天气调整"),
            ("腾冲热海", "温泉/地热", "门票待查，预算紧张时跳过"),
            ("叠水河瀑布", "自然景区", "市区低强度备选"),
            ("北海湿地", "湿地/自然", "雨季看天气和交通"),
            ("勐焕大金塔", "人文景区", "芒市可选，注意门票"),
            ("树包塔", "人文景区", "芒市低强度备选"),
        ),
        food_queries=(
            ("腾冲 饵丝", "饵丝/小吃", "10-30", "饵丝/稀豆粉", "低价正餐候选"),
            ("腾冲 农贸市场", "市场", "5-30", "水果/早点/简餐", "补给候选"),
            ("芒市 小吃", "小吃", "10-35", "撒撇/泡鲁达/简餐", "芒市低价小吃候选"),
            ("芒市 农贸市场", "市场", "5-30", "水果/早点/补给", "补给候选"),
        ),
    ),
    Stage(
        stage="08-puer-jingmai-xishuangbanna",
        city="普洱/景迈山/西双版纳",
        filename="puer-jingmai-xishuangbanna.csv",
        search_city="普洱",
        attraction_queries=(
            ("普洱茶马古道旅游景区", "人文景区", "门票待查，雨天降低优先级"),
            ("梅子湖公园", "湖边/公园", "低强度市区备选"),
            ("景迈山", "茶山/村寨", "只在天气和道路确认后保留"),
            ("翁基古寨", "茶山/村寨", "景迈山内可选"),
            ("曼听公园", "公园/人文", "景洪低强度备选"),
            ("告庄西双景", "街区/夜市", "控制消费，避开高价店"),
            ("中科院西双版纳热带植物园", "自然景区", "门票和往返时间待查"),
        ),
        food_queries=(
            ("普洱 米干", "米干/简餐", "10-30", "米干/米线", "低价正餐候选"),
            ("普洱 农贸市场", "市场", "5-30", "水果/早点/补给", "补给候选"),
            ("景洪 傣味", "傣味/简餐", "20-50", "傣味/简餐", "景洪吃饭候选"),
            ("景洪 农贸市场", "市场", "5-30", "水果/早点/补给", "热带水果和补给候选"),
        ),
    ),
    Stage(
        stage="09-jianshui-yuanyang-mengzi-puzhehei",
        city="建水/元阳/蒙自/普者黑",
        filename="jianshui-yuanyang-mengzi-puzhehei.csv",
        search_city="红河",
        attraction_queries=(
            ("建水古城", "古城/街区", "低强度主线"),
            ("朱家花园", "人文景区", "门票待查，预算允许再进"),
            ("团山民居", "古村/人文", "交通顺路时考虑"),
            ("元阳哈尼梯田", "梯田/自然", "能见度和道路正常才保留"),
            ("蒙自南湖公园", "湖边/公园", "恢复体力和低预算日"),
            ("碧色寨", "人文景区", "蒙自可选，注意交通"),
            ("普者黑景区", "湖区/自然", "天气和住宿价格允许时保留"),
        ),
        food_queries=(
            ("建水 烧豆腐", "小吃", "10-30", "烧豆腐/米线", "低价正餐候选"),
            ("建水 农贸市场", "市场", "5-30", "水果/早点/补给", "补给候选"),
            ("蒙自 过桥米线", "米线/简餐", "10-35", "过桥米线", "蒙自主食候选"),
            ("蒙自 农贸市场", "市场", "5-30", "水果/早点/补给", "补给候选"),
            ("普者黑 餐馆", "景区餐馆", "20-50", "简餐/家常菜", "景区吃饭候选"),
        ),
    ),
    Stage(
        stage="10-kunming-return",
        city="昆明返程",
        filename="kunming-return.csv",
        search_city="昆明",
        attraction_queries=(
            ("昆明站", "交通枢纽", "返程交通和住宿定位"),
            ("昆明老街", "古城/街区", "返程缓冲慢逛"),
            ("翠湖 公园", "湖边/公园", "低强度返程缓冲"),
            ("南屏步行街", "街区/补给", "返程补给和简餐"),
        ),
        food_queries=(),
    ),
]


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def amap_get(path: str, params: dict[str, str], sleep_seconds: float) -> dict:
    key = os.environ["AMAP_MAPS_API_KEY"]
    query = urllib.parse.urlencode({**params, "key": key})
    url = f"https://restapi.amap.com/v3/{path}?{query}"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    time.sleep(sleep_seconds)
    if data.get("status") != "1":
        raise RuntimeError(f"AMap API error: {data.get('info')} ({data.get('infocode')})")
    return data


def search_pois(
    keywords: str,
    city: str,
    *,
    offset: int,
    sleep_seconds: float,
    types: str = "",
) -> list[dict]:
    data = amap_get(
        "place/text",
        {
            "keywords": keywords,
            "city": city,
            "citylimit": "false",
            "children": "0",
            "offset": str(offset),
            "page": "1",
            "extensions": "base",
            **({"types": types} if types else {}),
        },
        sleep_seconds,
    )
    return [poi for poi in data.get("pois", []) if isinstance(poi, dict)]


def scalar(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "|".join(scalar(item) for item in value if scalar(item))
    return str(value)


def dedupe_pois(rows: Iterable[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for row in rows:
        key = scalar(row.get("id")) or f"{scalar(row.get('name'))}|{scalar(row.get('location'))}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def is_attraction_poi(poi: dict) -> bool:
    poi_type = scalar(poi.get("type"))
    name = scalar(poi.get("name"))
    if any(token in name for token in ATTRACTION_EXCLUDED_NAME_TOKENS):
        return False
    if not poi_type:
        return True
    if poi_type.startswith(ATTRACTION_ALLOWED_TYPE_PREFIXES):
        return True
    return any(token in name for token in ATTRACTION_ALLOWED_NAMES) and not poi_type.startswith(
        ATTRACTION_EXCLUDED_TYPE_PREFIXES
    )


def collect_attractions(stage: Stage, sleep_seconds: float, limit_per_query: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pois_with_meta: list[tuple[dict, str, str]] = []
    for keywords, category, notes in stage.attraction_queries:
        for poi in search_pois(keywords, stage.search_city, offset=limit_per_query, sleep_seconds=sleep_seconds):
            pois_with_meta.append((poi, category, notes))

    seen: set[str] = set()
    counter = 1
    for poi, category, notes in pois_with_meta:
        key = scalar(poi.get("id")) or f"{scalar(poi.get('name'))}|{scalar(poi.get('location'))}"
        if key in seen:
            continue
        if not is_attraction_poi(poi):
            continue
        seen.add(key)
        rows.append(
            {
                "poi_id": f"poi-{stage.stage}-{QUERY_DATE.replace('-', '')}-{counter:03d}",
                "query_date": QUERY_DATE,
                "city": stage.city,
                "stage": stage.stage,
                "source": SOURCE,
                "name": scalar(poi.get("name")),
                "category": category,
                "type": scalar(poi.get("type")),
                "address": scalar(poi.get("address")),
                "location": scalar(poi.get("location")),
                "estimated_ticket_cny": "待查",
                "opening_hours": "待查",
                "reservation": "待查",
                "priority": "候选",
                "notes": notes,
            }
        )
        counter += 1
    return rows


def collect_food(stage: Stage, sleep_seconds: float, limit_per_query: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    counter = 1
    seen: set[str] = set()
    for keywords, category, price, must_try, notes in stage.food_queries:
        pois = search_pois(
            keywords,
            stage.search_city,
            offset=limit_per_query,
            sleep_seconds=sleep_seconds,
            types="050000|060000",
        )
        for poi in pois:
            key = scalar(poi.get("id")) or f"{scalar(poi.get('name'))}|{scalar(poi.get('location'))}"
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "candidate_id": f"food-{stage.stage}-{QUERY_DATE.replace('-', '')}-{counter:03d}",
                    "query_date": QUERY_DATE,
                    "city": stage.city,
                    "stage": stage.stage,
                    "source": SOURCE,
                    "name": scalar(poi.get("name")),
                    "area": scalar(poi.get("address")),
                    "category": category,
                    "estimated_price_cny": price,
                    "must_try": must_try,
                    "url": "",
                    "research_status": "pending",
                    "visit_status": "候选",
                    "notes": f"{notes}；POI类型：{scalar(poi.get('type'))}",
                }
            )
            counter += 1
    return rows


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [{field: row.get(field, "") for field in fields} for row in reader]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_food(rows: list[dict[str, str]], force_stages: set[str]) -> int:
    existing = read_csv(FOOD_PATH, FOOD_FIELDS)
    if force_stages:
        existing = [row for row in existing if row["stage"] not in force_stages]
    existing_keys = {(row["stage"], row["name"], row["area"]) for row in existing}
    additions = [row for row in rows if (row["stage"], row["name"], row["area"]) not in existing_keys]
    if additions:
        write_csv(FOOD_PATH, FOOD_FIELDS, existing + additions)
    return len(additions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing attraction CSVs and replace food rows for selected stages")
    parser.add_argument("--force-attractions", action="store_true", help="overwrite existing attraction CSVs")
    parser.add_argument("--force-food", action="store_true", help="replace food rows for selected stages")
    parser.add_argument("--stage", action="append", default=[], help="stage id to collect; may be passed multiple times")
    parser.add_argument("--sleep", type=float, default=0.2, help="seconds between AMap REST calls")
    parser.add_argument("--limit-per-query", type=int, default=8)
    args = parser.parse_args()

    load_env(ENV_PATH)
    if not os.environ.get("AMAP_MAPS_API_KEY"):
        raise SystemExit("missing AMAP_MAPS_API_KEY")

    selected = set(args.stage)
    stages = [stage for stage in STAGES if not selected or stage.stage in selected]

    generated_food: list[dict[str, str]] = []
    force_food_stages: set[str] = set()
    for stage in stages:
        attraction_path = ATTRACTIONS_DIR / stage.filename
        force_attractions = args.force or args.force_attractions
        force_food = args.force or args.force_food
        if attraction_path.exists() and not force_attractions:
            print(f"skip attractions: {stage.stage} -> {attraction_path.relative_to(ROOT)} exists")
        else:
            attraction_rows = collect_attractions(stage, args.sleep, args.limit_per_query)
            write_csv(attraction_path, ATTRACTION_FIELDS, attraction_rows)
            print(f"wrote attractions: {stage.stage} -> {attraction_path.relative_to(ROOT)} ({len(attraction_rows)} rows)")

        if stage.food_queries:
            existing_food = read_csv(FOOD_PATH, FOOD_FIELDS)
            has_food = any(row["stage"] == stage.stage for row in existing_food)
            if has_food and not force_food:
                print(f"skip food: {stage.stage} already has rows")
            else:
                generated_food.extend(collect_food(stage, args.sleep, args.limit_per_query))
                if force_food:
                    force_food_stages.add(stage.stage)

    added_food = append_food(generated_food, force_food_stages)
    if generated_food:
        print(f"wrote food additions: {added_food} rows -> {FOOD_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
