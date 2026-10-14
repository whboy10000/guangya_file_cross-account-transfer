<title>开发者API接入文档</title>

# **修订说明**

| 版本  | 修订日期       | 说明                |
| --- | ---------- | ----------------- |
| 1.0 | 2026.07.28 | 首版，支持TOKEN上传      |
| 1.1 | 2026.08.31 | 支持重命名，优化TOKEN上传接口 |

# 一、接入概述

## 1.1 背景与目标

本文档面向平台开发者，旨在指导开发者完成 API 接入准备、遵守频率限制，并规范开放接口的调用流程，实现安全、高效的云盘文件传输与管理。

## 1.2 角色与权限说明

本功能涉及以下两类角色，共同完成跨账号文件传输：

- **接收方**：在客户端创建 TOKEN，并授权特定云盘目录供开发者写入文件。
- **开发者**：在 Web 端获取开发者凭证，负责将自身云盘中的文件迁移至接收方的授权目录。

## 1.3 开发者能力描述

开发者在获得授权后，可通过接口实现以下操作：

- **读写本人云盘**：列出目录结构、查询文件详情（用于文件选择）、文件重命名。
- **预上传审核**：提交待传输文件进行分享风控送检，并查询审核状态与明细。
- **TOKEN上传**：基于 `token_id`与 `file_ids`发起跨账号文件转移，并轮询任务进度。

## 1.4 使用规范与合规要求

开发者在接入及调用本 API 时，须同时满足以下约束：

1. **合法合规**：严格遵守《网络安全法》《数据安全法》《个人信息保护法》及平台用户协议，不得利用接口上传、传播任何涉黄、涉政、暴恐、侵权或违反法律法规的内容。
2. **权限最小化**：仅可在接收方显式授权的目录与 TOKEN 权限范围内操作，严禁越权访问、爬取或留存非授权数据。
3. **合理调用**：遵循平台频率限制与重试策略，不得通过并发轰炸、伪造请求等方式干扰服务稳定性。
4. **责任归属**：开发者对其通过接口上传的内容及调用行为承担全部法律责任；平台有权对违规 TOKEN 进行限流、吊销及追溯处理。

## 1.5 Agent Skill

```Bash
pnpm dlx skills add guangyapan/agent-skills --skill guangyapan-token-transfer
```

# 二、接入准备

## 2.1 开发者凭证申请

### 2.1.1 限制说明

- 开发者账号须为**会员**（申请凭证、读盘、上传前均会校验）
- 每个账号同时有效的开发者凭证上限为 **2**
- 被拉黑后无法鉴权、无法新建凭证
- 同一上传参数**1分钟**内不可以重复提交，在任务尚未结束且**10分钟**内不能再次上传
- pre\_upload发起请求，建议**15分钟**以后**6小时**以内调用upload接口，pre\_upload\_status查询状态为**审核中/审核完成**都可以发起upload调用，upload会将pass的目标文件执行copy操作

### 2.1.2 申请方式

- **Web端** ：右上角账号设置->TOKEN管理->成为开发者->复制client\_id/client\_secret

![图片展示的是Web端TOKEN管理界面。界面上方显示“TOKEN管理”，右上角有“新建token”按钮。下方有两条说明，分别是TOKEN用于开发者批量管理账号或多账号数据同步；TOKEN与写入数据账号绑定，如有多个数据源需求，可生成多个TOKEN。界面右侧有一个红色框突出显示的“成为开发者”按钮，箭头指向该按钮。该图片与文档中“2.1.2申请方式”部分内容相关，直观呈现了Web端申请开发者凭证的操作入口。](https://feishu.cn/file/QzjSbVOWnoumbGxuO9McpGAbnJh)

- **PC端** ：左侧三方应用->TOKEN管理->成为开发者->复制client\_id/client\_secret

  ![图片展示了开发者API接入文档中“2.1.2申请方式”部分的Web端TOKEN管理界面。界面左侧有“应用推荐”“TOKEN管理”“三方应用”“账号设置”“帮助中心”“我的”等导航栏，其中“TOKEN管理”和“三方应用”被红色框突出显示。右侧“TOKEN管理”区域介绍TOKEN用于批量管理账号或多账号数据同步，每个TOKEN仅可绑定一个开发者账号，需对接多个数据源时需生成多个TOKEN。右上角有“+新建TOKEN”按钮，右下角有“成为开发者”按钮，也被红色框突出显示。](https://feishu.cn/file/CwJObLohiobkiBxqm3mc2bmwnyg)

## 2.2 接收方TOKEN生成

### 2.2.1 限制说明

- 每个账号，同时有效的TOKEN上限为 **5**

### 2.2.2 生成方式

- **APP端** ：设置->账号与安全->TOKEN管理->新建TOKEN->复制TOKEN
- **Web端** ：右上角账号设置->TOKEN管理->新建TOKEN->复制TOKEN
- **PC端** ：左侧三方应用->TOKEN管理->新建TOKEN->复制TOKEN

  ![这张图展示了云盘平台的TOKEN管理页面，左侧侧边栏的TOKEN管理选项被红框标注，页面右上角有同样被红框标注的“+ 新建TOKEN”按钮，用于创建TOKEN。页面中说明TOKEN的作用为方便开发者批量管理账号或多账号数据同步，且每个TOKEN仅可绑定一个开发者账号，如需对接多个数据源需分别生成多个TOKEN，页面还有跳转成为开发者的入口，对应文档中接收方TOKEN的生成相关操作场景。](https://feishu.cn/file/DwZubjNmqoIC2XxFc6DcSMdbn8d)

## 2.3 接口调用业务流程

![图片展示了接口调用业务流程。用户A（接收方）生成TOKEN，线下将TOKEN\_ID传给开发者B（上传方）。开发者B调用get\_file\_list/get\_file\_detail获取文件，再调用pre\_upload上传文件，同时传入TOKEN\_ID和file\_ID。接着调用pre\_upload\_status查询状态，最后调用upload\_by\_field或upload\_status，若通过审核，使用TOKEN\_ID将文件copy到用户A的TOKEN目录。此图直观呈现了接口调用各步骤及参数传递情况。](https://feishu.cn/file/SbjEbwkanouFpLxbyCFc3gi6nsc)

# 三、接口说明

## 3.1 签名鉴权

每次请求须在 Header 携带：

| Header     | 说明                          |
| ---------- | --------------------------- |
| client\_id | 凭证ID                        |
| nonce      | 16～32 位随机串，**每个请求唯一**       |
| timestamp  | Unix 秒；与服务器时间差须 ≤ **300** 秒 |
| sign       | 签名，小写 hex                   |

sign算法：

srcStr = "client\_id=" + client\_id

```
\+ "&client_secret=" + client_secret

\+ "&nonce=" + nonce

\+ "&timestamp=" + timestamp
```

sign = hex\_lower( SHA512( MD5(srcStr) ) )

**注意**：先对 srcStr 做 **MD5（得到 16 字节二进制）**，再对该二进制做 **SHA512**，最后输出 **小写 hex**。不要对 MD5 的 hex 字符串再做 SHA512。

## 3.2 请求响应说明

**通用请求 Header：**

| Header         | 必填 | 说明                 |
| -------------- | -- | ------------------ |
| `Content-Type` | 是  | `application/json` |
| `client_id`    | 是  | 开发者凭证 ID           |
| `nonce`        | 是  | 16～32 位随机串，请求唯一    |
| `timestamp`    | 是  | Unix 秒             |
| `sign`         | 是  | 签名                 |

**通用响应：**

| 字段     | 类型            | 说明                     |
| ------ | ------------- | ---------------------- |
| `code` | int           | `0` 成功；非 0 见附录 A       |
| `msg`  | string        | 说明文案                   |
| `data` | object / null | 业务数据；失败时可能为 `null` 或省略 |

失败响应示例：

```JSON
{
  "code": 18009,
  "msg": "无权查询该上传任务",
  "data": null
}
```

**公共结构 FileInfo（读盘列表 / 详情复用）：**

| 字段              | 类型     | 说明                                                                                                                |
| --------------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| `fileId`        | string | 文件 / 目录 ID                                                                                                        |
| `fileName`      | string | 名称                                                                                                                |
| `fileSize`      | int64  | 大小（字节）；目录可为 0                                                                                                     |
| `gcid`          | string | 文件 gcid                                                                                                           |
| `parentId`      | string | 父目录 ID                                                                                                            |
| `depth`         | uint   | 目录深度                                                                                                              |
| `mineType`      | string | MIME 类型（字段名拼写同协议）                                                                                                 |
| `fileType`      | int    | 文件类型：`0` 未知 / `1` 图 / `2` 视频 / `3` 音频 / `4` 文档 / `5` 压缩包 / `6` 字幕 / `7` 字体 / `8` 安装包 / `9` 种子 / `10` 代码 / `11` 其他 |
| `dirType`       | int    | 目录类型：`0` 未知 / `1` 普通 / `4` 回收站/ `5` 直链                                                                            |
| `resType`       | int    | `0` 未知 / `1` 文件 / `2` 目录                                                                                          |
| `ext`           | string | 扩展名                                                                                                               |
| `fullParentIds` | string | 完整父路径 ID，如 `/1/2/3`                                                                                               |
| `ctime`         | int64  | 创建时间（Unix 秒）                                                                                                      |
| `utime`         | int64  | 更新时间（Unix 秒）                                                                                                      |
| `thumbnail`     | string | 缩略图信息                                                                                                             |
| `auditStatus`   | int    | 审核状态：`0` 未知 / `1` 审核中 / `2` 通过 / `3` 拒绝 / `4` 未知                                                                  |

## 3.3 接口详情

### 3.3.1 获取文件列表

**用途：** 浏览开发者本人云盘目录，选取待上传的 \`fileId\`

**接口：** POST <https://dapi.guangyapan.com/userres/v1/file/get_file_list>

**请求参数：**

| 字段              | 类型     | 必填 | 说明                                                        |
| --------------- | ------ | -- | --------------------------------------------------------- |
| `parentId`      | string | 否  | 父目录 ID；空字符串表示根目录                                          |
| `page`          | uint   | 否  | 页码，从 0 起                                                  |
| `pageSize`      | uint   | 是  | 每页条数，≥1                                                   |
| `dirType`       | int    | 否  | 目录类型：`0` 未知 / `1` 普通 / `2` 转存 / `3` 收藏 / `4` 回收站 / `5` 直链 |
| `orderBy`       | int    | 是  | 排序字段：`0` 名 / `1` 大小 / `2` 创建时间 / `3` 更新时间 / `4` 扩展名       |
| `sortType`      | int    | 是  | `0` 升序 / `1` 降序                                           |
| `fileTypes`     | int\[] | 否  | 文件类型过滤，空表示全部                                              |
| `resType`       | int    | 否  | `0` 不限 / `1` 文件 / `2` 目录                                  |
| `updated_after` | int64  | 否  | Unix时间戳；只返回 utime >= updated\_after 的项。0 / 不传 = 全量        |

**响应参数：**

| 字段           | 类型          | 说明                       |
| ------------ | ----------- | ------------------------ |
| `code`       | int         | `0` 成功                   |
| `msg`        | string      | 说明文案                     |
| `data`       | object      | 见下表                      |
| `data.total` | uint        | 总条数                      |
| `data.list`  | FileInfo\[] | 文件 / 目录列表，元素见 `FileInfo` |

**用例：列出根目录普通文件**

```Bash
curl -sS -X POST "{DGW_HOST}/userres/v1/file/get_file_list" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "parentId": "",
    "page": 0,
    "pageSize": 20,
    "dirType": 1,
    "orderBy": 2,
    "sortType": 1,
    "fileTypes": [],
    "resType": 0,
    "updated_after": 0
  }'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 2,
    "list": [
      {
        "fileId": "fid_dir_001",
        "fileName": "素材包",
        "fileSize": 0,
        "resType": 2
      },
      {
        "fileId": "fid_file_001",
        "fileName": "demo.mp4",
        "fileSize": 10485760,
        "resType": 1,
        "ext": "mp4"
      }
    ]
  }
}
```

### 3.3.2 获取文件详情

**用途：** 按 \`fileId\` 查询单个文件 / 目录详情，确认资源后再送审或上传。

**接口：** POST <https://dapi.guangyapan.com/userres/v1/file/get_file_detail>

**请求参数：**

| 字段       | 类型     | 必填 | 说明                 |
| -------- | ------ | -- | ------------------ |
| `fileId` | string | 是  | 文件 / 目录 ID，长度 1～40 |

**响应参数：**

| 字段                                            | 类型        | 说明                                     |
| --------------------------------------------- | --------- | -------------------------------------- |
| `code`                                        | int       | `0` 成功                                 |
| `msg`                                         | string    | 说明文案                                   |
| `data`                                        | object    | 见下表                                    |
| `data.fileInfo`                               | FileInfo  | 文件信息，见 §3.0                            |
| `data.location`                               | string    | 目录位置描述                                 |
| `data.picInfo`                                | object    | 图片信息；非图片可为空                            |
| `data.picInfo.width`                          | uint      | 宽度                                     |
| `data.picInfo.height`                         | uint      | 高度                                     |
| `data.picInfo.previewUrl`                     | string    | 预览 URL                                 |
| `data.videoResource`                          | object\[] | 视频资源列表；非视频可为空                          |
| `data.videoResource[].gcid`                   | string    | 视频 gcid                                |
| `data.videoResource[].info`                   | object    | 视频信息                                   |
| `data.videoResource[].info.resolution.width`  | uint      | 宽                                      |
| `data.videoResource[].info.resolution.height` | uint      | 高                                      |
| `data.videoResource[].info.duration`          | uint      | 时长（秒）                                  |
| `data.videoResource[].info.bitRate`           | uint      | 码率                                     |
| `data.videoResource[].info.frameRate`         | uint      | 帧率                                     |
| `data.videoResource[].info.videoCodec`        | string    | 视频编码                                   |
| `data.videoResource[].info.audioCodec`        | string    | 音频编码                                   |
| `data.videoResource[].info.videoType`         | string    | 视频类型                                   |
| `data.videoResource[].info.source`            | uint      | `0` 原始 / `1` 转码 / `2` 转码 plus / `3` 无损 |
| `data.videoResource[].info.hdrType`           | uint      | `0` 无 / `1` HDR10 / `2` Dolby          |
| `data.videoResource[].info.storageType`       | uint      | 存储类型                                   |
| `data.videoResource[].info.defaultResolution` | bool      | 是否默认分辨率                                |
| `data.videoResource[].info.resolutionName`    | string    | 如 `480P`                               |
| `data.videoResource[].info.needVipType`       | int       | 所需会员类型                                 |
| `data.videoResource[].info.mimeType`          | string    | MIME                                   |
| `data.sizeInfo`                               | object    | 大小信息                                   |
| `data.sizeInfo.size`                          | uint64    | 总大小                                    |
| `data.sizeInfo.subDirCount`                   | uint      | 子文件夹数                                  |
| `data.sizeInfo.subFileCount`                  | uint      | 子文件数                                   |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/userres/v1/file/get_file_detail" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{"fileId":"fid_file_001"}'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "fileInfo": {
      "fileId": "fid_file_001",
      "fileName": "demo.mp4",
      "fileSize": 10485760,
      "resType": 1,
      "canShare": true
    },
    "location": "/素材包"
  }
}
```

### 3.3.3 文件/文件夹重命名

**用途：** 修改开发者本人云盘内某文件/文件夹的名称。

**接口：** POST <https://dapi.guangyapan.com/userres/v1/file/rename>

**请求参数：**

| 字段        | 类型     | 必填 | 说明                 |
| --------- | ------ | -- | ------------------ |
| `fileId`  | string | 是  | 文件 / 目录 ID，长度 1～40 |
| `newName` | string | 是  | 新名称，长度 1～255       |

**响应参数：**

| 字段     | 类型     | 说明     |
| ------ | ------ | ------ |
| `code` | int    | `0` 成功 |
| `msg`  | string | 说明文案   |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/userres/v1/file/rename" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -H "dt: 11" \
  -d '{
    "fileId": "fid_file_001",
    "newName": "demo-renamed.mp4"
  }'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success"
}
```

### 3.3.4 预上传

**用途：** 将待上传的根文件 / 目录提交分享风控送审。建议正式上传前先走本接口，减少 \`skipped\`。相同 token\_id + 相同文件集合在一定时间内可能复用已有任务。

**接口：** POST <https://dapi.guangyapan.com/developer/v1/pre_upload>

**请求参数：**

| 字段         | 类型        | 必填 | 说明                             |
| ---------- | --------- | -- | ------------------------------ |
| `token_id` | string    | 是  | 接收方下发的 UploadToken，长度 1～20     |
| `file_ids` | string\[] | 是  | 目录 ID 列表，**1～20** 个，须属于当前开发者云盘 |

**响应参数：**

| 字段                    | 类型     | 说明                                                  |
| --------------------- | ------ | --------------------------------------------------- |
| `code`                | int    | `0` 成功                                              |
| `msg`                 | string | 说明文案                                                |
| `data`                | object | 见下表                                                 |
| `data.task_id`        | string | 预上传任务 ID，后续 status / detail 使用                      |
| `data.status`         | int    | `0` 未开始 / `1` 提交审核中 / `2` 审核中 / `3` 审核完成 / `4` 送审失败 |
| `data.total_count`    | int    | 叶子文件总数                                              |
| `data.passed_count`   | int    | 已通过                                                 |
| `data.rejected_count` | int    | 已拒绝                                                 |
| `data.pending_count`  | int    | 审核中                                                 |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/pre_upload" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "token_id": "TOKEN20260724Abcdef1",
    "file_ids": ["fid_file_001", "fid_dir_001"]
  }'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241200001234567890123",
    "status": 2,
    "total_count": 100,
    "passed_count": 10,
    "rejected_count": 0,
    "pending_count": 90
  }
}
```

### 3.3.5 预上传状态查询

**用途：** 轮询预上传任务整体进度，直至 status=3（完成）或 4（失败），仅能查询**当前凭证对应用户**发起的任务，否则 **18009**。建议轮询间隔 ≥ 3 秒。

**接口：** POST <https://dapi.guangyapan.com/developer/v1/pre_upload_status>

**请求参数：**

| 字段        | 类型     | 必填 | 说明                    |
| --------- | ------ | -- | --------------------- |
| `task_id` | string | 是  | `pre_upload` 返回的任务 ID |

**响应参数：**

| 字段                    | 类型     | 说明                                                  |
| --------------------- | ------ | --------------------------------------------------- |
| `code`                | int    | `0` 成功；无权查询为 `18009`                                |
| `msg`                 | string | 说明文案                                                |
| `data`                | object | 见下表                                                 |
| `data.task_id`        | string | 预上传任务 ID                                            |
| `data.status`         | int    | `0` 未开始 / `1` 提交审核中 / `2` 审核中 / `3` 审核完成 / `4` 送审失败 |
| `data.total_count`    | int    | 叶子文件总数                                              |
| `data.passed_count`   | int    | 已通过                                                 |
| `data.rejected_count` | int    | 已拒绝                                                 |
| `data.pending_count`  | int    | 审核中                                                 |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/pre_upload_status" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{"task_id":"202607241200001234567890123"}'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241200001234567890123",
    "status": 3,
    "total_count": 100,
    "passed_count": 95,
    "rejected_count": 5,
    "pending_count": 0
  }
}
```

### 3.3.6 预上传详情获取

**用途：** 分页查看叶子文件审核结果（通过 / 拒绝 / 待审），用于排查 \`rejected\` / \`skipped\`。

**接口：** POST <https://dapi.guangyapan.com/developer/v1/pre_upload_detail>

**请求参数：**

| 字段          | 类型     | 必填 | 说明                                                 |
| ----------- | ------ | -- | -------------------------------------------------- |
| `task_id`   | string | 是  | 预上传任务 ID                                           |
| `filter`    | string | 否  | `all` / `passed` / `rejected` / `pending`，默认 `all` |
| `page`      | int    | 否  | 从 1 开始；≤0 按 1                                      |
| `page_size` | int    | 是  | 1～100                                              |

**响应参数：**

| 字段                         | 类型        | 说明                                |
| -------------------------- | --------- | --------------------------------- |
| `code`                     | int       | `0` 成功；过频为 `18010`                |
| `msg`                      | string    | 说明文案                              |
| `data`                     | object    | 见下表                               |
| `data.task_id`             | string    | 任务 ID                             |
| `data.status`              | int       | 同预上传：`0`～`4`                      |
| `data.total`               | int       | **当前 filter 下**总条数                |
| `data.list`                | object\[] | 当前页明细                             |
| `data.list[].file_id`      | string    | 文件 ID                             |
| `data.list[].file_name`    | string    | 文件名                               |
| `data.list[].file_size`    | int64     | 大小（字节）                            |
| `data.list[].audit_status` | string    | `pending` / `passed` / `rejected` |
| `data.list[].can_share`    | bool      | 当前是否可分享                           |
| `data.passed_count`        | int       | 通过数（任务级）                          |
| `data.rejected_count`      | int       | 拒绝数                               |
| `data.pending_count`       | int       | 待审数                               |

**用例：查看被拒文件**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/pre_upload_detail" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "task_id": "202607241200001234567890123",
    "filter": "rejected",
    "page": 1,
    "page_size": 20
  }'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241200001234567890123",
    "status": 3,
    "total": 5,
    "list": [
      {
        "file_id": "fid_leaf_009",
        "file_name": "bad.bin",
        "file_size": 1024,
        "audit_status": "rejected",
        "can_share": false
      }
    ],
    "passed_count": 95,
    "rejected_count": 5,
    "pending_count": 0
  }
}
```

### 3.3.7 通过文件ID上传

**用途：** 正式发起跨用户 copy：将开发者云盘中的文件写入接收方 TOKEN 目录。业务侧校验会员。

**接口：** POST <https://dapi.guangyapan.com/developer/v1/upload_by_fileid>

**请求参数：**

| 字段                      | 类型        | 必填 | 说明                               |
| ----------------------- | --------- | -- | -------------------------------- |
| `token_id`              | string    | 是  | <br />                           |
| `file_ids`              | string\[] | 是  | 文件 / 目录 ID，**1～20** 个；须属于当前开发者   |
| `duplicate_name_policy` | int       | 否  | 文件 / 文件夹重名处理方式：默认0，自动重命名；1，跳过不上传 |

**响应参数：**

| 字段             | 类型     | 说明                            |
| -------------- | ------ | ----------------------------- |
| `code`         | int    | `0` 成功；无可用文件等见附录 A（如 `18011`） |
| `msg`          | string | 说明文案                          |
| `data`         | object | 见下表                           |
| `data.task_id` | string | 上传任务 ID，用于 `upload_status`    |
| `data.status`  | string | 一般为 `pending`                 |

说明：

\- 无通过分享审核的文件时可能返回 **18011**

\- TOKEN 首次成功使用后可能绑定当前上传方（**18002**）

\- 目标侧重名自动改名，不覆盖

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/upload_by_fileid" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "token_id": "TOKEN20260724Abcdef1",
    "file_ids": ["fid_file_001", "fid_dir_001"]
  }'
```

成功响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241930001111222233333",
    "status": "pending"
  }
}
```

### 3.3.8 上传状态查询

**用途：** 轮询正式上传任务，直到 \`success\` / \`failed\`

**接口：** POST <https://dapi.guangyapan.com/developer/v1/upload_status>

**请求参数：**

| 字段        | 类型     | 必填 | 说明                          |
| --------- | ------ | -- | --------------------------- |
| `task_id` | string | 是  | `upload_by_fileid` 返回的任务 ID |

**响应参数：**

| 字段                   | 类型     | 说明                                           |
| -------------------- | ------ | -------------------------------------------- |
| `code`               | int    | `0` 成功；无权查询为 `18009`                         |
| `msg`                | string | 说明文案                                         |
| `data`               | object | 见下表                                          |
| `data.task_id`       | string | 任务 ID                                        |
| `data.status`        | string | `pending` / `running` / `success` / `failed` |
| `data.use_count`     | int    | `TOKEN `  **`累计`**`成功上传次数`                   |
| `data.success_count` | int    | **`本任务`**`copy 成功的叶子数`                       |
| `data.skipped_count` | int    | **`本任务`**  ` 跳过的叶子数`                         |

`task_id` 不存在或不属于当前开发者时返回 **18009**。建议轮询间隔 ≥ 1～3 秒。

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/upload_status" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{"task_id":"202607241930001111222233333"}'
```

进行中 响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241930001111222233333",
    "status": "running",
    "use_count": 0,
    "success_count": 10,
    "skipped_count": 2
  }
}
```

完成 响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "202607241930001111222233333",
    "status": "success",
    "use_count": 3,
    "success_count": 95,
    "skipped_count": 5
  }
}
```

### 3.3.9 上传跳过的文件列表

**用途：** 终态后，查询上传跳过的文件列表，保留**72h**

**接口：** POST <https://dapi.guangyapan.com/developer/v1/upload_skipped_list>

**请求参数：**

| 字段          | 类型     | 必填 | 说明                                                                                                                              |
| ----------- | ------ | -- | ------------------------------------------------------------------------------------------------------------------------------- |
| `task_id`   | string | 是  | `upload_by_fileid` 返回的任务 ID                                                                                                     |
| `reason`    | string | 否  | 过滤：`audit_rejected` / `audit_expired` / `audit_pending` / `space_exhausted` / `duplicate_name` / `duplicate_dir_name` / `other` |
| `cursor`    | string | 否  | 首页不传；翻页时将上页`next_cursor`原样填入                                                                                                    |
| `page_size` | int    | 否  | 1～1000，默认 100                                                                                                                   |

**响应参数：**

| 字段                 | 类型     | 说明                                             |
| ------------------ | ------ | ---------------------------------------------- |
| `code`             | int    | `0` 成功；无权查询为 `18009`                           |
| `msg`              | string | 说明文案                                           |
| `data`             | object | 见下表                                            |
| `data.list`        | array  | `[{ "file_id", "reason" }]`                    |
| `data.next_cursor` | string | 非空表示还有下一页：**原样**作为下次请求的 \`cursor\`；\`""\` 表示结束 |
| `data.total`       | int    | 可选，**仅首屏**（\`cursor\` 为空时）；翻页忽略                |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/upload_skipped_list" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "task_id": "202607241930001111222233333",
    "reason": "duplicate_name",
    "page_size": 100
  }'
```

响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "list": [
      { "file_id": "100001", "reason": "duplicate_name" },
      { "file_id": "100002", "reason": "duplicate_name" }
    ],
    "next_cursor": "100002",
    "total": 5
  }
}
```

### 3.3.10 上传成功的文件列表

**用途：** 终态后，查询上传成功的文件列表，保留**72h**

**接口：** POST <https://dapi.guangyapan.com/developer/v1/upload_success_list>

**请求参数：**

| 字段          | 类型     | 必填 | 说明                           |
| ----------- | ------ | -- | ---------------------------- |
| `task_id`   | string | 是  | `upload_by_fileid` 返回的任务 ID  |
| `cursor`    | string | 否  | 首页不传；翻页时将上页`next_cursor`原样填入 |
| `page_size` | int    | 否  | 1～1000，默认 100                |

**响应参数：**

| 字段                 | 类型     | 说明                                             |
| ------------------ | ------ | ---------------------------------------------- |
| `code`             | int    | `0` 成功；无权查询为 `18009`                           |
| `msg`              | string | 说明文案                                           |
| `data`             | object | 见下表                                            |
| `data.list`        | array  | `[{ "file_id"}]`                               |
| `data.next_cursor` | string | 非空表示还有下一页：**原样**作为下次请求的 \`cursor\`；\`""\` 表示结束 |
| `data.total`       | int    | 可选，**仅首屏**（\`cursor\` 为空时）；翻页忽略                |

**用例：**

```Bash
curl -sS -X POST "{DGW_HOST}/developer/v1/upload_success_list" \
  -H "Content-Type: application/json" \
  -H "client_id: ${CLIENT_ID}" \
  -H "nonce: ${NONCE}" \
  -H "timestamp: ${TS}" \
  -H "sign: ${SIGN}" \
  -d '{
    "task_id": "202607241930001111222233333",
    "page_size": 100
  }'
```

响应示例：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "list": [
      { "file_id": "200001" },
      { "file_id": "200002" }
    ],
    "next_cursor": "200002",
    "total": 95
  }
}
```

## **附录 A. 错误码**

HTTP 层：鉴权失败多为 **401**，限流为 **429**，接口不支持为 **404**。

业务 `code`（节选）：

| code  | 说明                  |
| ----- | ------------------- |
| 0     | 成功                  |
| 18001 | UploadToken 不存在或已删除 |
| 18002 | 非绑定上传方              |
| 18003 | 上传方与接收方不能相同         |
| 18006 | 文件不属于当前上传方          |
| 18007 | 接收方空间不足             |
| 18008 | 目标目录不存在             |
| 18009 | 无权查询该上传任务           |
| 18010 | 请求过于频繁，请稍后重试        |
| 18011 | 没有可上传的分享文件          |
| 18012 | 文件数量超过限制            |
| 18013 | 服务器忙，请稍后重试          |
| 18014 | 相同文件已上传，请勿重复操作      |
| 18015 | 单次上传叶子数超过上限         |
| 18016 | 上传任务已结束，无法追加明细      |
| 18020 | 开发者凭证无效或已删除         |
| 18021 | 签名校验失败              |
| 18022 | 签名已过期               |
| 18023 | nonce 已被使用          |
| 18024 | 有效开发者凭证已达上限         |
| 18025 | 接口不在开发者白名单          |
| 18026 | 开发者已被拉黑             |

## **附录 B. 常见问题**

**Q: 签名一直失败？**

检查 client\_secret是否完整、时间是否同步、是否对 MD5 **二进制**再 SHA512，以及 Header 是否包含 client\_id/nonce/timestamp/sign

**Q: 为什么返回 404？**

确认请求URL是否和文档一致

**Q: 同名文件/文件夹会怎样？**

上传接口参数duplicate\_name\_policy（可选，默认 0）：目标文件/文件夹已存在时的处理方式。0 自动追加序号（如 file(1).txt），1 跳过不重复上传

**Q: skipped\_count 为什么大于 0？**

叶子文件未通过分享审核、不可消费，或其它业务过滤会被跳过；可用预上传明细排查

**Q: upload\_status 返回 18009？**

确认 `task_id` 正确，且创建该任务时使用的 `client_id` 与当前查询为同一开发者账号

**Q: 能否用 client\_id 请求其他C端功能接口？**

不能。开发者签名仅适用于开发者相关接口。

***

