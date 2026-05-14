# API Key Application Guide

当前日期：`2026-05-13`

本文记录旅行规划相关 MCP/API 的申请入口、需要的账号、权限和配置字段。不要把真实 Key、Token、Secret 写入本项目文件。

## 优先级

| 优先级 | 服务 | 是否必须 | 说明 |
|---|---|---|---|
| P0 | 高德地图 | 建议申请 | POI、路线、距离、周边搜索最实用 |
| P0 | 12306 MCP | 不需要 Key | 已配置 `uvx mcp-server-12306` |
| P1 | 彩云天气 | 可选 | 分钟级降水和天气，官方 MCP 使用 Token |
| P1 | 和风天气 | 可选 | 天气 API 成熟，推荐 JWT，但 MCP 需看具体实现 |
| P2 | 飞书多维表格 | 可选 | 适合把预算和行程同步到表格 |
| P2 | Notion | 可选 | 适合知识库和行程笔记 |
| P2 | Airtable | 可选 | 适合结构化表格，但国内使用不一定最顺手 |

## 高德地图

申请的是高德开放平台 `Web 服务` Key。

### 入口

- 高德 MCP 创建 Key：https://lbs.amap.com/api/mcp-server/create-project-and-key
- Web 服务 API 创建 Key：https://lbs.amap.com/api/webservice/create-project-and-key
- 控制台：https://console.amap.com/

### 步骤

1. 登录高德开放平台控制台。
2. 进入 `应用管理`。
3. 创建新应用，建议应用名：`mcp-amap-travel-assistant`。
4. 在应用下点击 `添加 Key`。
5. `服务平台` 选择 `Web 服务`。
6. 保存后复制 `Key`。

### 配置字段

Node.js MCP 常用：

```toml
[mcp_servers.amap]
type = "stdio"
command = "npx"
args = ["-y", "@amap/amap-maps-mcp-server"]
env = { AMAP_MAPS_API_KEY = "不要把真实Key写进文档" }
```

官方 Streamable HTTP 方式：

```toml
[mcp_servers.amap_http]
url = "https://mcp.amap.com/mcp?key=你的Key"
```

推荐本机环境变量名：`AMAP_MAPS_API_KEY`

### 注意

- 个人认证开发者通常有月免费配额。
- 配额、QPS、计费以高德控制台为准。
- 地图、搜索、天气等服务可能分别计入不同配额。

## 12306

### 结论

不需要 API Key，不需要 12306 登录。

当前已配置：

```toml
[mcp_servers.train_12306]
type = "stdio"
command = "uvx"
args = ["mcp-server-12306"]
startup_timeout_sec = 60
```

### 能做

- 查余票
- 查车次
- 查票价
- 查经停站
- 查中转
- 查车站

### 不能做

- 不能登录
- 不能购票
- 不能候补
- 不能支付
- 不能改签/退票

真实购票仍然使用 `12306` 官网/App。

## 彩云天气

### 入口

- API 文档：https://docs.caiyunapp.com/weather-api/
- 开放平台：https://platform.caiyunapp.com
- 官方 MCP：https://github.com/caiyunapp/mcp-caiyun-weather

### 步骤

1. 注册并登录彩云开放平台。
2. 进入访问控制。
3. 新系统优先使用 `API 凭证管理` 创建 `App Key & App Secret`。
4. 如果使用官方 MCP，则进入 `Token 管理` 获取 Token。
5. 保存 Token 到本机环境变量。

### 配置字段

官方 MCP 常见环境变量：

```text
CAIYUN_WEATHER_API_TOKEN
```

Token 认证也可通过：

- query：`token`
- header：`Authorization: Bearer {token}`

### 注意

- 官方文档建议新系统使用 `App Key & App Secret`，但官方 MCP 当前使用 `CAIYUN_WEATHER_API_TOKEN`。
- 免费额度和计费以彩云 API 管理平台为准。

## 和风天气 QWeather

### 入口

- 开发者网站：https://dev.qweather.com/
- 控制台：https://console.qweather.com/project
- 项目和凭据：https://dev.qweather.com/docs/configuration/project-and-key/
- 身份认证：https://dev.qweather.com/docs/configuration/authentication/

### 步骤

1. 注册并登录和风天气开发者账号。
2. 进入控制台 `项目管理`。
3. 创建项目。
4. 进入项目后添加凭据。
5. 推荐创建 `JSON Web Token` 凭据：
   - 本地生成 Ed25519 公私钥。
   - 上传公钥到控制台。
   - 记录 `kid` 和项目 ID。
6. 也可以创建 `API KEY`，但官方提示安全性较弱，且未来会逐步限制。

### 配置字段

官方 API 字段：

- API Key header：`X-QW-Api-Key`
- API Key query：`key`
- JWT header：`Authorization: Bearer {JWT}`

常见环境变量名，具体以 MCP README 为准：

```text
QWEATHER_API_KEY
QWEATHER_API_HOST
QWEATHER_KEY_ID
QWEATHER_PROJECT_ID
QWEATHER_PRIVATE_KEY
```

### 注意

- 和风天气未确认有统一官方 MCP Server。
- 如果只是旅行途中查天气，彩云 MCP 或高德天气可能更省事。

## 飞书多维表格

### 入口

- 飞书开放平台：https://open.feishu.cn/
- 官方 MCP：https://github.com/larksuite/lark-openapi-mcp

### 步骤

1. 登录飞书开放平台。
2. 创建企业自建应用。
3. 获取 `App ID` 和 `App Secret`。
4. 申请多维表格权限，例如：
   - `bitable:app:readonly`
   - `bitable:app`
5. 如果用用户身份调用，配置 OAuth redirect：
   - `http://localhost:3000/callback`
6. 把应用添加到对应多维表格或文档协作者。

### 配置字段

官方 MCP 常见环境变量：

```text
APP_ID
APP_SECRET
USER_ACCESS_TOKEN
LARK_TOOLS
LARK_DOMAIN
LARK_TOKEN_MODE
```

### 注意

- 飞书不是简单 API Key，而是应用凭证 + token。
- 企业自建应用权限变更可能需要管理员审核。

## Notion

### 入口

- Developer portal：https://developers.notion.com/
- Integrations：https://www.notion.so/profile/integrations
- Notion MCP：https://developers.notion.com/guides/mcp/get-started-with-mcp

### 推荐方式

优先使用官方远程 MCP：

```toml
[mcp_servers.notion]
url = "https://mcp.notion.com/mcp"
```

这种方式走 OAuth，不需要手动保存 Token。

### Token 方式

如果使用本地旧 MCP：

- Internal connection：workspace owner 创建，复制 installation access token。
- PAT：Personal access tokens 创建后复制 token。
- Page/database 需要显式授权给 connection。

常见环境变量：

```text
NOTION_TOKEN
OPENAPI_MCP_HEADERS
```

## Airtable

### 入口

- Developer Hub：https://airtable.com/developers
- PAT 文档：https://support.airtable.com/docs/creating-personal-access-tokens
- Airtable MCP：https://support.airtable.com/docs/using-the-airtable-mcp-server

### 步骤

1. 登录 Airtable。
2. 进入 Developer Hub。
3. 创建 Personal Access Token。
4. 选择 scopes。
5. 选择允许访问的 base/workspace。
6. 复制 PAT。

### MCP 推荐 scopes

- `data.records:read`
- `data.records:write`
- `schema.bases:read`
- `schema.bases:write`
- `data.recordComments:read`
- `data.recordComments:write`
- `workspacesAndBases:read`
- `webhook:manage`

### 配置

官方远程 MCP：

```toml
[mcp_servers.airtable]
url = "https://mcp.airtable.com/mcp"
```

PAT 方式需要 MCP 客户端支持自定义 header：

```text
Authorization: Bearer your_personal_access_token
```

### 注意

- Airtable 旧 API Key 已废弃。
- 实际权限同时受 PAT scope 和用户在 base/workspace 中的权限限制。

## 推荐执行顺序

1. 先申请高德 `Web 服务` Key，接 `AMAP_MAPS_API_KEY`。
2. 如果需要更细的降雨预报，再申请彩云 `CAIYUN_WEATHER_API_TOKEN`。
3. 如果要云端同步预算，优先选飞书多维表格；如果只本地使用，继续用 CSV。
4. `12306 MCP` 不用申请，重启 Codex 后直接验证工具是否暴露。

