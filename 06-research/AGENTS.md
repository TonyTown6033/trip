# AGENTS.md

## 项目定位

本目录用于旅行研究资料整理。信息源需要分层使用：官方/半官方来源用于事实确认，社媒公开信息只用于趋势观察、用户关注点和选题线索。

## Skill 配置

当任务涉及社媒公开信息搜集、旅行平台内容趋势、游客关注点、避坑话题、路线讨论、预算讨论、评论线索时，优先使用 `$mediacrawler-research` skill。

Skill 路径：`/Users/town/.codex/skills/mediacrawler-research/SKILL.md`

MediaCrawler 项目路径：`/Users/town/Documents/trip/06-research/tools/MediaCrawler`

## 使用边界

- 只做小范围公开信息采集，不做大规模抓取。
- 不自动登录、不绕验证码、不替代人工确认。
- 默认先生成 dry-run 命令，再按需要执行。
- 默认单平台、少量关键词、低并发；除非明确需要，不抓评论。
- 社媒结果不能直接当事实源；价格、天气、交通、景区开放状态、门票、政策必须用官方或半官方来源交叉验证。

## 推荐输出方式

- 原始采集数据保存在 `tools/MediaCrawler/data/<platform>/<format>/`。
- 父项目只沉淀摘要、趋势、问题清单和待核验事项。
- 需要引用本地采集结果时，记录对应 JSONL/CSV/XLSX 文件路径。

## 现有工具索引

工具和 MCP 边界见 `tools-and-mcp.md`。
