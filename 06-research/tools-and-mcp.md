# Tools And MCP

## Agent 可用优先级

| 用途 | 工具 | 边界 |
|---|---|---|
| 地图/POI/路线 | 高德地图 MCP / 百度地图 MCP | 查询和比选，不替代现场判断 |
| 火车票 | `12306 MCP` | 只查车次和余票，购票人工完成 |
| 天气 | 和风天气 / 彩云天气 | 出发前和途中滚动查询 |
| 社媒公开信息搜集 | `MediaCrawler` + `$mediacrawler-research` skill | 小范围、人工登录确认、只做研究素材采集 |
| 预算记录 | 飞书多维表格 / Notion / 本地 CSV | 本项目默认本地 CSV |

## 当前 Codex MCP 配置状态

已写入 `/Users/town/.codex/config.toml`：

| MCP | 配置名 | 命令 | 状态 |
|---|---|---|---|
| 12306 | `train_12306` | `uvx mcp-server-12306` | 已配置，独立启动测试通过 |
| 高德地图 | `amap` | `npx -y @amap/amap-maps-mcp-server` | 已配置，Web Service Key REST 校验通过，独立启动测试通过 |
| Weather | `weather` | `npx -y @dangahagan/weather-mcp` | 已配置，独立启动无报错但需重启 Codex 后用工具验证 |
| Filesystem | `filesystem` | `npx -y @modelcontextprotocol/server-filesystem /Users/town` | 已可用 |
| Memory | `memory` | `npx -y @modelcontextprotocol/server-memory` | 已可用但偏慢 |
| Fetch | `fetch` | `uvx mcp-server-fetch` | 当前会话测试为 `Transport closed` |
| Git | `git` | `uvx mcp-server-git==2026.1.14 --repository /Users/town/Projects/apidocs` | 可用但指向非本项目 |

当前未启用：

| MCP | 原因 |
|---|---|
| 彩云天气 MCP | 本机没有 `CAIYUN_WEATHER_API_TOKEN` |
| 飞书/Notion MCP | 未提供对应账号/API 配置 |

新增 MCP 通常需要重启 Codex 会话后才会暴露为工具。

申请步骤见：`api-key-application-guide.md`

## 人工确认入口

- 铁路：`12306`
- 机票/航班：航旅纵横、携程、飞猪、同程
- 住宿：携程、飞猪、美团、Booking
- 景区：游云南、景区官方公众号/小程序
- 地图：高德地图、百度地图
- 天气：和风天气、彩云天气、中国天气、云南气象

## FlyAI -> MediaCrawler 复核流

- FlyAI 查询结果统一记录到 `flyai-candidates/`。
- 候选住宿总表：`flyai-candidates/hotels.csv`。
- 候选景点/体验总表：`flyai-candidates/poi.csv`。
- 每次候选详情页附带 MediaCrawler 关键词文件，用于后续小范围公开口碑检索。
- MediaCrawler 复核后更新候选表的 `research_status`，再同步到对应阶段的 `stay.md`、`plan.md` 或 `backup.md`。

## 禁止自动化

- 自动登录
- 自动抢票
- 绕验证码
- 实名购票
- 支付
- 退改签
