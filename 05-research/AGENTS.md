# AGENTS.md

## 项目定位

本目录用于旅行研究资料整理。信息源需要分层使用：官方/半官方来源用于事实确认，社媒公开信息只用于趋势观察、用户关注点和选题线索。

## Skill 配置

当任务涉及社媒公开信息搜集、旅行平台内容趋势、游客关注点、避坑话题、路线讨论、预算讨论、评论线索时，优先使用 `$mediacrawler-research` skill。

Skill 路径：`/Users/town/.codex/skills/mediacrawler-research/SKILL.md`

MediaCrawler 项目路径：`/Users/town/Documents/trip/05-research/tools/MediaCrawler`

## 使用边界

- 只做小范围公开信息采集，不做大规模抓取。
- 默认先生成 dry-run 命令，再按需要执行。
- 默认单平台、少量关键词、低并发；除非明确需要，不抓评论。
- 小红书优先使用 CDP 模式复用本机 Chrome 登录态；执行前可先验证 `localhost:9222` 可连接，并用 `XiaoHongShuClient.pong()` 确认 `XHS_LOGIN_STATE_VALID=True`。
- CDP 模式仍需要人工在 Chrome 中登录、开启远程调试并确认浏览器弹窗；不要自动化登录、滑块或验证码。
- 社媒结果不能直接当事实源；价格、天气、交通、景区开放状态、门票、政策必须用官方或半官方来源交叉验证。
- API Key 读取和保密规则继承仓库根目录 `AGENTS.md`；研究文档只记录变量名，不记录真实 Key。

## 推荐输出方式

- 原始采集数据保存在 `tools/MediaCrawler/data/<platform>/<format>/`。
- 默认分析用 `jsonl`；需要重复跑关键词并去重/更新时用 `sqlite`，数据库文件为 `tools/MediaCrawler/database/sqlite_tables.db`。
- 父项目只沉淀摘要、趋势、问题清单和待核验事项。
- 需要引用本地采集结果时，记录对应 JSONL/CSV/XLSX 文件路径。

## 小红书常用命令

从 MediaCrawler 根目录执行：

```bash
rtk uv run main.py --platform xhs --lt qrcode --type search --keywords "关键词1,关键词2" --save_data_option jsonl --get_comment false --get_sub_comment false --max_comments_count_singlenotes 0 --max_concurrency_num 1
```

需要 SQLite 去重时先初始化：

```bash
rtk uv run main.py --init_db sqlite
rtk uv run main.py --platform xhs --lt qrcode --type search --keywords "关键词1,关键词2" --save_data_option sqlite --get_comment true --max_comments_count_singlenotes 20 --max_concurrency_num 1
```

## 现有工具索引

工具和 MCP 边界见 `tools-and-mcp.md`。
