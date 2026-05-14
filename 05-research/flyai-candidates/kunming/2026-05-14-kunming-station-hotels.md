# 昆明站住宿候选

## 查询条件

- 查询日期：2026-05-14
- 来源：飞猪/FlyAI
- 城市：昆明
- POI：昆明站
- 入住：2026-05-22
- 离店：2026-05-25
- 偏好：青旅、低价、近昆明站、多人间/床位优先
- 预算上限：单晚 `100 CNY`

## 行程背景

- 2026-05-20 17:45：K739 杭州南 -> 昆明。
- 2026-05-22 05:31：抵达昆明站。
- 到达日需要优先确认 `24h 前台`、`早到寄存行李`、`储物柜`、`取消政策`。

## 候选

| ID | 名称 | 区域 | 价格 | 链接 | 复核状态 | 备注 |
|---|---|---|---:|---|---|---|
| hotel-kunming-20260522-001 | 阡陌之旅青年旅社 | 近昆明站；春城时代广场上海沙龙 B 座 | ¥21 | https://a.feizhu.com/0OXbXF | pending | 2023 装修；低价优先 |
| hotel-kunming-20260522-002 | 澜舍女生精品青旅（昆明火车站店） | 近昆明站；鑫都韵城 7 栋 | ¥25 | https://a.feizhu.com/14iDSz | pending | 女生青旅；若适用再考虑 |
| hotel-kunming-20260522-003 | 昆明拾光里青年旅社 | 近昆明站；鑫都韵城 9 栋 | ¥26 | https://a.feizhu.com/065kWQ | pending | 低价优先；重点复核 |
| hotel-kunming-20260522-004 | 昆明小鹿不在家青年旅社 | 近昆明站；鑫都韵城 10 栋 | ¥30 | https://a.feizhu.com/06poNK | pending | 低价备选；重点复核 |
| hotel-kunming-20260522-005 | 云同青旅民宿(昆明火车站店) | 近昆明站；鑫都韵城 17 栋 | ¥42 | https://a.feizhu.com/1Z50zA | pending | 2024 装修；重点复核 |
| hotel-kunming-20260522-006 | 昆明流年时光青年旅社 | 近昆明站；鑫都韵城 10 栋 | ¥45 | https://a.feizhu.com/002ICI | pending | 价格中档 |
| hotel-kunming-20260522-007 | 翠花青旅民宿(环城南路地铁口店) | 近昆明站/环城南路地铁口 | ¥66 | https://a.feizhu.com/4QQJJz | pending | 前台地址与住宿地址可能不同 |

## 当前推荐

1. `昆明拾光里青年旅社`：价格低，位置适合清晨到站，优先复核卫生、噪音、寄存。
2. `昆明小鹿不在家青年旅社`：同片区低价备选，优先复核真实评价。
3. `云同青旅民宿(昆明火车站店)`：装修较新，若口碑明显更稳可接受更高价格。
4. `翠花青旅民宿(环城南路地铁口店)`：地铁便利，但需特别核验前台/住宿地址。

## MediaCrawler 复核任务

目标：判断候选是否值得入住，重点看安全、卫生、噪音、床位体验、寄存行李、实际位置。

建议平台：

- `xhs`：优先，关键词少量搜索，适合住宿体验帖。
- `wb` 或 `tieba`：补充负面口碑和避雷信息。

建议关键词见：

- `2026-05-14-kunming-station-hotels-mediacrawler-keywords.txt`

建议参数：

- `--platform xhs`
- `--type search`
- `--get-comment true`
- `--get-sub-comment false`
- `--max-comments 10`
- `--max_concurrency_num 1`
- `--save_data_option jsonl`

复核后更新：

- `hotels.csv` 的 `research_status`
- 本文件候选表的 `复核状态`
- `03-stages/01-kunming/stay.md` 的最终推荐
