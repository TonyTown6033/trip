# FlyAI Candidates

本目录记录 FlyAI/飞猪查到的候选住宿、景点、交通或本地体验，用作后续人工比选和 MediaCrawler 公开口碑复核的输入。

## 用途

- 保存 FlyAI 查询结果的结构化快照。
- 给 `$mediacrawler-research` 提供小范围关键词，避免宽泛抓取。
- 把“价格/位置候选”和“社媒口碑评价”分开，方便判断是否值得入住或游玩。

## 目录约定

- `hotels.csv`：住宿候选总表。
- `poi.csv`：景点/体验候选总表。
- `<city>/<date>-<topic>.md`：一次查询的详情、推荐排序和后续复核任务。
- `<city>/<date>-<topic>-mediacrawler-keywords.txt`：给 MediaCrawler 使用的候选关键词。

## 字段说明

住宿候选至少记录：

- `candidate_id`
- `query_date`
- `city`
- `stage`
- `source`
- `name`
- `area`
- `check_in`
- `check_out`
- `price_cny`
- `url`
- `research_status`
- `booking_status`
- `notes`

景点/体验候选至少记录：

- `candidate_id`
- `query_date`
- `city`
- `stage`
- `source`
- `name`
- `area`
- `estimated_price_cny`
- `url`
- `research_status`
- `visit_status`
- `notes`

## MediaCrawler 复核边界

- 只用候选名称、城市、区域组成小关键词集。
- 优先小红书/微博/贴吧等公开内容，低并发、少量评论。
- 不自动登录、不绕验证码、不抓私密内容、不做大规模采集。
- 输出只做参考，不替代现场安全判断和平台下单页确认。
