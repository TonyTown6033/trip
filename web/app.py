import csv
import io
import os
from pathlib import Path

import markdown
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
PROJECT = Path(__file__).parent.parent

# load .env
from dotenv import load_dotenv
load_dotenv(PROJECT / ".env")
AMAP_KEY = os.getenv("tempAMAP_MAPS_API_KEY", "")
AMAP_SECURITY = os.getenv("securityJsCode", "")

STAGES = [
    ("01-kunming", "昆明"),
    ("02-dali", "大理"),
    ("03-shaxi-jianchuan", "沙溪/剑川"),
    ("04-lijiang", "丽江"),
    ("05-luguhu", "泸沽湖"),
    ("06-shangrila-deqin", "香格里拉/德钦"),
    ("07-tengchong-mangshi", "腾冲/芒市"),
    ("08-puer-jingmai-xishuangbanna", "普洱/景迈山/西双版纳"),
    ("09-jianshui-yuanyang-mengzi-puzhehei", "建水/元阳/蒙自/普者黑"),
    ("10-kunming-return", "昆明返程"),
]

# 各站点坐标 (lng, lat) 用于高德地图
STAGE_COORDS = [
    (102.83, 25.05),   # 昆明
    (100.16, 25.69),   # 大理
    (99.92, 26.17),    # 沙溪
    (100.23, 26.87),   # 丽江
    (100.78, 27.71),   # 泸沽湖
    (99.71, 27.83),    # 香格里拉
    (98.91, 28.49),    # 德钦
    (98.49, 25.02),    # 腾冲
    (100.97, 22.79),   # 普洱/西双版纳
    (102.41, 23.37),   # 建水/元阳
    (102.83, 25.05),   # 昆明返程
]


def read_md(path: Path) -> str:
    if path.exists():
        return markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables"])
    return "<p>暂无内容</p>"


def read_csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    overview_html = read_md(PROJECT / "00-dashboard" / "overview.md")
    budget_rows = read_csv_rows(PROJECT / "00-dashboard" / "budget-tracker.csv")
    return templates.TemplateResponse(request, "index.html", {
        "overview": overview_html,
        "budget_rows": budget_rows,
        "stages": STAGES,
        "coords": STAGE_COORDS,
        "amap_key": AMAP_KEY,
        "amap_security": AMAP_SECURITY,
    })


@app.get("/route", response_class=HTMLResponse)
async def route(request: Request):
    route_html = read_md(PROJECT / "02-route" / "master-route.md")
    return templates.TemplateResponse(request, "route.html", {
        "route": route_html,
        "stages": STAGES,
        "coords": STAGE_COORDS,
        "amap_key": AMAP_KEY,
        "amap_security": AMAP_SECURITY,
    })


@app.get("/stages/{name}", response_class=HTMLResponse)
async def stage_detail(request: Request, name: str):
    stage_dir = PROJECT / "03-stages" / name
    label = dict(STAGES).get(name, name)
    tabs = {}
    for f in ["plan", "transport", "stay", "food", "backup"]:
        tabs[f] = read_md(stage_dir / f"{f}.md")
    budget_rows = read_csv_rows(stage_dir / "budget.csv")
    return templates.TemplateResponse(request, "stage.html", {
        "name": name,
        "label": label,
        "tabs": tabs,
        "budget_rows": budget_rows,
        "stages": STAGES,
    })


@app.get("/budget", response_class=HTMLResponse)
async def budget(request: Request):
    budget_rows = read_csv_rows(PROJECT / "00-dashboard" / "budget-tracker.csv")
    return templates.TemplateResponse(request, "budget.html", {
        "budget_rows": budget_rows,
    })


@app.get("/gear", response_class=HTMLResponse)
async def gear(request: Request):
    rows = read_csv_rows(PROJECT / "01-gear" / "packing-list.csv")
    return templates.TemplateResponse(request, "gear.html", {
        "rows": rows,
    })


@app.get("/food", response_class=HTMLResponse)
async def food(request: Request):
    food_dir = PROJECT / "food"
    intro_html = read_md(food_dir / "README.md")
    rows = read_csv_rows(food_dir / "food.csv")
    return templates.TemplateResponse(request, "food.html", {
        "intro": intro_html,
        "rows": rows,
    })
