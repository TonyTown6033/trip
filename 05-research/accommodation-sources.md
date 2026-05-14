# Accommodation Sources

记录住宿平台、区域和价格查询规则。

## 优先平台

- 携程
- 飞猪
- 美团
- Booking

## 每条记录至少包含

- 查询时间
- 平台
- 城市/区域
- 入住和离店日期
- 价格
- 取消政策
- 评分和位置备注

## FlyAI 候选库

- 目录：`flyai-candidates/`
- 住宿总表：`flyai-candidates/hotels.csv`
- 景点/体验总表：`flyai-candidates/poi.csv`
- 用途：记录 FlyAI 查到的候选，再交给 `$mediacrawler-research` 做公开口碑复核。
- 当前昆明住宿候选：`flyai-candidates/kunming/2026-05-14-kunming-station-hotels.md`

## 背包客约束

- 单晚住宿优先控制在 `35-80 CNY`。
- 优先青旅床位、低价客栈、连住优惠、可做饭住宿。
