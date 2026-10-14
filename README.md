# 光压云盘开发者 API 控制台

基于光压云盘开发者开放 API 构建的 Web 控制台，封装了文档中全部 **10 个接口**，提供可视化界面，支持点击调用所有接口，自动处理签名鉴权。

---

## 一、项目概述

### 1.1 项目背景

光压云盘为开发者提供了一套开放 API，用于实现**跨账号文件转移**——将开发者本人云盘中的文件/目录，通过接收方的 TOKEN 复制到接收方的授权目录。本项目将这些 API 封装为一个可视化的 Web 控制台，降低接入门槛。

### 1.2 核心功能

- **文件管理**：浏览云盘目录结构、查询文件/目录详情、重命名
- **预上传审核**：提交文件送审、查询审核进度、查看审核明细
- **正式上传**：发起跨账号文件转移、查询上传状态、查看成功/跳过列表

### 1.3 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python 3 + Flask | 封装 10 个 API 接口，自动签名鉴权 |
| 前端 | HTML + CSS + 原生 JavaScript | 单页应用，无需构建工具 |
| 鉴权 | MD5 + SHA512 签名 | 按光压云盘文档实现 |

### 1.4 项目结构

```
光压云盘/
├── app/                        # 应用代码
│   ├── app.py                  # Flask 后端主程序（10个接口封装 + 签名鉴权）
│   ├── requirements.txt        # Python 依赖清单
│   └── static/
│       └── index.html          # 前端单页应用
├── config/                     # 配置文件
│   ├── config.json             # 凭证配置（含 client_id / client_secret，已 gitignore）
│   └── config.example.json     # 凭证配置模板
├── deploy/                     # 部署相关
│   ├── Dockerfile              # Docker 镜像构建文件
│   └── docker-compose.yml      # Docker Compose 一键部署
├── docs/                       # 文档
│   └── 光压云盘开发者API文档.md  # 原始 API 参考文档
├── .github/
│   └── workflows/
│       └── release.yml         # GitHub Actions CI/CD 工作流
├── .dockerignore               # Docker 构建忽略规则
├── .gitignore                  # Git 忽略规则
└── README.md                   # 本说明文档
```

---

## 二、快速开始

### 2.1 环境要求

- Python 3.7+
- 依赖：`flask`、`requests`

### 2.2 安装依赖

```bash
pip install -r app/requirements.txt
```

### 2.3 配置凭证

1. 复制配置模板：

```bash
cp config/config.example.json config/config.json
```

2. 编辑 `config/config.json`，填入你的凭证：

```json
{
  "client_id": "你的_client_id",
  "client_secret": "你的_client_secret"
}
```

> 凭证获取方式：光压云盘 Web 端 → 右上角账号设置 → TOKEN管理 → 成为开发者 → 复制 client_id / client_secret
>
> 注意：开发者账号须为**会员**。
>
> **安全提示**：`config/config.json` 包含敏感凭证，已通过 `.gitignore` 排除，不会提交到 Git。

### 2.4 启动服务

```bash
cd 光压云盘
python app/app.py
```

启动成功后控制台会显示：

```
==================================================
光压云盘开发者 API 服务启动
访问地址: http://localhost:5001
==================================================
```

### 2.5 访问界面

在浏览器中打开：**http://localhost:5001**

---

## 三、Docker 部署

### 3.1 方式一：Docker Compose 一键部署（推荐）

```bash
# 1. 配置凭证
cp config/config.example.json config/config.json
# 编辑 config/config.json 填入你的 client_id 和 client_secret

# 2. 一键启动（在项目根目录执行）
docker compose -f deploy/docker-compose.yml up -d

# 3. 访问 http://localhost:5001

# 4. 查看日志
docker compose -f deploy/docker-compose.yml logs -f

# 5. 停止服务
docker compose -f deploy/docker-compose.yml down
```

### 3.2 方式二：直接运行镜像

镜像已发布到 GitHub Container Registry（GHCR）：

```bash
# 1. 配置凭证
cp config/config.example.json config/config.json
# 编辑 config/config.json 填入你的 client_id 和 client_secret

# 2. 拉取并运行
docker run -d \
  --name guangyapan-console \
  -p 5001:5001 \
  -v $(pwd)/config/config.json:/app/config.json:ro \
  ghcr.io/whboy10000/guangya_file_cross-account-transfer:latest

# 3. 访问 http://localhost:5001
```

### 3.3 方式三：本地构建镜像

```bash
# 1. 配置凭证
cp config/config.example.json config/config.json

# 2. 构建镜像
docker build -f deploy/Dockerfile -t guangyapan-console .

# 3. 运行容器
docker compose -f deploy/docker-compose.yml up -d
```

### 3.4 镜像标签说明

| 标签 | 说明 |
|------|------|
| `latest` | main 分支最新版本 |
| `vX.Y.Z` | 对应 Release 版本（如 v1.0.0） |
| `vX.Y` | 最新的小版本 |
| `main` | main 分支构建 |
| `sha-xxxxxxx` | 对应 commit 的构建 |

> **安全提示**：凭证通过 volume 挂载方式传入容器，不会打包进镜像。

---

## 四、签名鉴权说明

光压云盘所有接口均需签名鉴权，本项目已自动处理，无需手动计算。

### 3.1 请求头

每次请求须在 Header 携带以下字段：

| Header | 说明 |
|--------|------|
| `Content-Type` | `application/json` |
| `client_id` | 开发者凭证 ID |
| `nonce` | 16～32 位随机串，每个请求唯一 |
| `timestamp` | Unix 秒；与服务器时间差须 ≤ 300 秒 |
| `sign` | 签名，小写 hex |

### 3.2 签名算法

```
srcStr = "client_id=" + client_id
       + "&client_secret=" + client_secret
       + "&nonce=" + nonce
       + "&timestamp=" + timestamp

sign = hex_lower( SHA512( MD5(srcStr) ) )
```

> **注意**：先对 srcStr 做 MD5（得到 16 字节**二进制**），再对该二进制做 SHA512，最后输出小写 hex。不要对 MD5 的 hex 字符串再做 SHA512。

---

## 四、功能模块详解

### 4.1 文件管理

#### 4.1.1 获取文件列表 `get_file_list`

- **用途**：浏览开发者本人云盘目录，选取待上传的 fileId
- **接口**：`POST /userres/v1/file/get_file_list`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `parentId` | string | 否 | 父目录 ID；空字符串表示根目录 |
| `page` | uint | 否 | 页码，从 0 起 |
| `pageSize` | uint | 是 | 每页条数，≥1 |
| `dirType` | int | 否 | 目录类型：0未知/1普通/2转存/3收藏/4回收站/5直链 |
| `orderBy` | int | 是 | 排序字段：0名/1大小/2创建时间/3更新时间/4扩展名 |
| `sortType` | int | 是 | 0升序/1降序 |
| `fileTypes` | int[] | 否 | 文件类型过滤，空表示全部 |
| `resType` | int | 否 | 0不限/1文件/2目录 |
| `updated_after` | int64 | 否 | 只返回 utime ≥ 该值的项 |

**界面操作：**
- 顶部路径导航栏可点击切换目录
- 目录行点击「进入」可浏览子目录
- 点击「详情」可查看文件/目录完整信息

#### 4.1.2 获取文件详情 `get_file_detail`

- **用途**：按 fileId 查询单个文件/目录详情
- **接口**：`POST /userres/v1/file/get_file_detail`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `fileId` | string | 是 | 文件/目录 ID，长度 1～40 |

**响应包含：** 文件基本信息、目录位置、图片信息（width/height/previewUrl）、视频资源列表（分辨率/时长/码率/编码等）、大小信息（总大小/子目录数/子文件数）

#### 4.1.3 文件/文件夹重命名 `rename`

- **用途**：修改开发者本人云盘内某文件/文件夹的名称
- **接口**：`POST /userres/v1/file/rename`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `fileId` | string | 是 | 文件/目录 ID |
| `newName` | string | 是 | 新名称，长度 1～255 |

---

### 4.2 预上传审核

#### 4.2.1 预上传 `pre_upload`

- **用途**：将待上传的根文件/目录提交分享风控送审
- **接口**：`POST /developer/v1/pre_upload`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `token_id` | string | 是 | 接收方下发的 UploadToken，长度 1～20 |
| `file_ids` | string[] | 是 | 文件/目录 ID 列表，1～20 个 |

**响应：** 返回 `task_id`，用于后续状态查询和详情获取

> 提交后界面会自动将 task_id 回填到「预上传状态查询」和「预上传详情获取」的输入框。

#### 4.2.2 预上传状态查询 `pre_upload_status`

- **用途**：轮询预上传任务整体进度，直至 status=3（完成）或 4（失败）
- **接口**：`POST /developer/v1/pre_upload_status`

**状态码：**

| status | 含义 |
|--------|------|
| 0 | 未开始 |
| 1 | 提交审核中 |
| 2 | 审核中 |
| 3 | 审核完成 |
| 4 | 送审失败 |

**界面操作：**
- 「查询一次」：单次查询状态
- 「自动轮询」：每 3 秒自动查询，直到审核完成或失败（再次点击停止）

#### 4.2.3 预上传详情获取 `pre_upload_detail`

- **用途**：分页查看叶子文件审核结果（通过/拒绝/待审），用于排查 rejected/skipped
- **接口**：`POST /developer/v1/pre_upload_detail`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 预上传任务 ID |
| `filter` | string | 否 | all/passed/rejected/pending，默认 all |
| `page` | int | 否 | 从 1 开始 |
| `page_size` | int | 是 | 1～100 |

---

### 4.3 正式上传

#### 4.3.1 通过文件ID上传 `upload_by_fileid`

- **用途**：正式发起跨用户 copy，将开发者云盘中的文件写入接收方 TOKEN 目录
- **接口**：`POST /developer/v1/upload_by_fileid`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `token_id` | string | 是 | 接收方下发的 UploadToken |
| `file_ids` | string[] | 是 | 文件/目录 ID，1～20 个 |
| `duplicate_name_policy` | int | 否 | 0=自动重命名（默认），1=跳过不上传 |

**说明：**
- 无通过分享审核的文件时可能返回 **18011**
- TOKEN 首次成功使用后可能绑定当前上传方（**18002**）
- 目标侧重名自动改名，不覆盖
- 建议在 pre_upload 审核完成后 15 分钟～6 小时内调用

> 提交后界面会自动将 task_id 回填到后续查询接口的输入框。

#### 4.3.2 上传状态查询 `upload_status`

- **用途**：轮询正式上传任务，直到 success/failed
- **接口**：`POST /developer/v1/upload_status`

**状态值：**

| status | 含义 |
|--------|------|
| pending | 等待中 |
| running | 进行中 |
| success | 成功 |
| failed | 失败 |

**界面操作：**
- 「查询一次」：单次查询状态
- 「自动轮询」：每 2 秒自动查询，直到上传成功或失败（再次点击停止）

#### 4.3.3 上传跳过的文件列表 `upload_skipped_list`

- **用途**：终态后，查询上传跳过的文件列表（保留 72h）
- **接口**：`POST /developer/v1/upload_skipped_list`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 上传任务 ID |
| `reason` | string | 否 | 过滤原因（见下） |
| `cursor` | string | 否 | 翻页游标，首页不传 |
| `page_size` | int | 否 | 1～1000，默认 100 |

**跳过原因：** `audit_rejected` / `audit_expired` / `audit_pending` / `space_exhausted` / `duplicate_name` / `duplicate_dir_name` / `other`

#### 4.3.4 上传成功的文件列表 `upload_success_list`

- **用途**：终态后，查询上传成功的文件列表（保留 72h）
- **接口**：`POST /developer/v1/upload_success_list`

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 上传任务 ID |
| `cursor` | string | 否 | 翻页游标，首页不传 |
| `page_size` | int | 否 | 1～1000，默认 100 |

---

## 五、完整上传流程示例

以"将开发者云盘的某个目录转移到接收方云盘"为例：

### 步骤 1：浏览云盘，选择文件/目录

在「文件管理」标签页，通过路径导航找到要转移的文件/目录，记录其 `fileId`。

### 步骤 2：获取接收方 TOKEN_ID

接收方在光压云盘 **设置 → 账号与安全 → TOKEN管理 → 新建TOKEN**，生成 TOKEN 并授权目标目录，将 TOKEN_ID 提供给开发者。

### 步骤 3：预上传（送审）

在「预上传审核」标签页：
- 填入 `token_id`（接收方提供）
- 填入 `file_ids`（步骤1选定的文件/目录 ID，多个用逗号分隔）
- 点击「提交送审」
- 记录返回的 `task_id`

### 步骤 4：等待审核完成

点击「自动轮询」，等待状态变为「审核完成」（status=3）。

> 建议审核完成后 15 分钟～6 小时内执行步骤 5。

### 步骤 5：正式上传

在「正式上传」标签页：
- 填入 `token_id`（同步骤3）
- 填入 `file_ids`（同步骤3）
- 选择重名处理方式
- 点击「开始上传」
- 记录返回的 `task_id`

### 步骤 6：等待上传完成

点击「自动轮询」，等待状态变为「成功」（status=success）。

### 步骤 7：查看结果

上传完成后，可通过「上传跳过的文件列表」和「上传成功的文件列表」查看明细。

---

## 六、后端 API 接口清单

本项目后端封装的路由（均为 POST）：

| 后端路由 | 对应光压云盘接口 |
|----------|------------------|
| `/api/file/get_file_list` | `/userres/v1/file/get_file_list` |
| `/api/file/get_file_detail` | `/userres/v1/file/get_file_detail` |
| `/api/file/rename` | `/userres/v1/file/rename` |
| `/api/developer/pre_upload` | `/developer/v1/pre_upload` |
| `/api/developer/pre_upload_status` | `/developer/v1/pre_upload_status` |
| `/api/developer/pre_upload_detail` | `/developer/v1/pre_upload_detail` |
| `/api/developer/upload_by_fileid` | `/developer/v1/upload_by_fileid` |
| `/api/developer/upload_status` | `/developer/v1/upload_status` |
| `/api/developer/upload_skipped_list` | `/developer/v1/upload_skipped_list` |
| `/api/developer/upload_success_list` | `/developer/v1/upload_success_list` |

可直接通过 curl 测试后端接口，例如：

```bash
curl -X POST http://localhost:5001/api/file/get_file_list \
  -H "Content-Type: application/json" \
  -d '{"parentId":"","page":0,"pageSize":20,"orderBy":2,"sortType":1}'
```

---

## 七、错误码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| 18001 | UploadToken 不存在或已删除 |
| 18002 | 非绑定上传方 |
| 18003 | 上传方与接收方不能相同 |
| 18006 | 文件不属于当前上传方 |
| 18007 | 接收方空间不足 |
| 18008 | 目标目录不存在 |
| 18009 | 无权查询该上传任务 |
| 18010 | 请求过于频繁，请稍后重试 |
| 18011 | 没有可上传的分享文件 |
| 18012 | 文件数量超过限制 |
| 18013 | 服务器忙，请稍后重试 |
| 18014 | 相同文件已上传，请勿重复操作 |
| 18015 | 单次上传叶子数超过上限 |
| 18016 | 上传任务已结束，无法追加明细 |
| 18020 | 开发者凭证无效或已删除 |
| 18021 | 签名校验失败 |
| 18022 | 签名已过期 |
| 18023 | nonce 已被使用 |
| 18024 | 有效开发者凭证已达上限 |
| 18025 | 接口不在开发者白名单 |
| 18026 | 开发者已被拉黑 |

HTTP 层：鉴权失败多为 **401**，限流为 **429**，接口不支持为 **404**。

---

## 八、FileInfo 公共结构

文件列表和详情接口复用的文件信息结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `fileId` | string | 文件/目录 ID |
| `fileName` | string | 名称 |
| `fileSize` | int64 | 大小（字节）；目录可为 0 |
| `gcid` | string | 文件 gcid |
| `parentId` | string | 父目录 ID |
| `depth` | uint | 目录深度 |
| `mineType` | string | MIME 类型 |
| `fileType` | int | 0未知/1图/2视频/3音频/4文档/5压缩包/6字幕/7字体/8安装包/9种子/10代码/11其他 |
| `dirType` | int | 0未知/1普通/4回收站/5直链 |
| `resType` | int | 0未知/1文件/2目录 |
| `ext` | string | 扩展名 |
| `fullParentIds` | string | 完整父路径 ID，如 `/1/2/3` |
| `ctime` | int64 | 创建时间（Unix 秒） |
| `utime` | int64 | 更新时间（Unix 秒） |
| `thumbnail` | string | 缩略图信息 |
| `auditStatus` | int | 0未知/1审核中/2通过/3拒绝/4未知 |

---

## 九、注意事项

1. **不能上传本地文件**：这套 API 只支持跨账号转移云盘中**已有的**文件，不支持本地文件上传
2. **开发者须为会员**：申请凭证、读盘、上传前均会校验会员身份
3. **频率限制**：
   - 同一上传参数 1 分钟内不可重复提交
   - 任务未结束且 10 分钟内不能再次上传
   - pre_upload_status 轮询间隔 ≥ 3 秒
   - upload_status 轮询间隔 ≥ 1～3 秒
4. **凭证上限**：每个账号同时有效的开发者凭证上限为 2
5. **TOKEN 上限**：每个账号同时有效的 TOKEN 上限为 5
6. **时间同步**：签名 timestamp 与服务器时间差须 ≤ 300 秒
7. **数据保留**：上传成功/跳过列表保留 72 小时

---

## 十、常见问题

**Q: 签名一直失败？**
检查 client_secret 是否完整、系统时间是否同步、是否对 MD5 **二进制**再 SHA512，以及 Header 是否包含 client_id/nonce/timestamp/sign。

**Q: 为什么返回 404？**
确认请求 URL 是否和文档一致。

**Q: 同名文件/文件夹会怎样？**
上传接口参数 `duplicate_name_policy`（可选，默认 0）：0 自动追加序号（如 file(1).txt），1 跳过不重复上传。

**Q: skipped_count 为什么大于 0？**
叶子文件未通过分享审核、不可消费，或其它业务过滤会被跳过；可用预上传明细接口排查。

**Q: upload_status 返回 18009？**
确认 task_id 正确，且创建该任务时使用的 client_id 与当前查询为同一开发者账号。

**Q: 能否用 client_id 请求其他 C 端功能接口？**
不能。开发者签名仅适用于开发者相关接口。
