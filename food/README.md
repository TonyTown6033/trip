# 饮食候选

本目录记录餐馆、小吃、市场和可长期解决日常吃饭的候选，用作后续人工比选和 MediaCrawler 公开口碑复核的输入。

## 用途

- 保存平台查询、地图搜索或本地推荐的结构化候选。
- 给 `$mediacrawler-research` 提供小范围关键词，避免宽泛抓取。
- 把“价格/位置候选”和“社媒口碑评价”分开，方便判断是否值得专门前往。

## 目录约定

- `food.csv`：饮食候选总表。
- `<city>/<date>-<topic>.md`：一次查询的详情、推荐排序和后续复核任务。
- `<city>/<date>-<topic>-mediacrawler-keywords.txt`：给 MediaCrawler 使用的候选关键词。

## 字段说明

饮食候选至少记录：

- `candidate_id`
- `query_date`
- `city`
- `stage`
- `source`
- `name`
- `area`
- `category`
- `estimated_price_cny`
- `must_try`
- `url`
- `research_status`
- `visit_status`
- `notes`

## 背包客约束

- 日均餐饮优先控制在 `50-60 CNY`。
- 优先本地小店、市场、米线/饵丝/盖饭等日常低价选择。
- 网红店只作为备选，除非价格、排队和路线成本都可接受。
