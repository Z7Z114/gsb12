# 民族志纪录片剪辑会议蒙太奇纪要系统

一个全栈应用，用于处理民族志纪录片剪辑会议的自动化纪要生成。前端 React + TypeScript 展示粗剪
时间线与田野笔记；后端 FastAPI 负责说话人识别、音频转写、AI 摘要与邮件通知。

## 项目结构

```
backend/     # FastAPI 后端
  main.py
  api/v1/endpoints/meeting.py
  services/  # 说话人识别 / 转写 / AI 摘要 / 邮件
  database/  # SQLAlchemy 模型
  models/    # Pydantic schema
frontend/    # React 前端
```

## 快速开始

```bash
cd backend
pip install -r requirements.txt
python -m pytest
uvicorn main:app --reload
```

```bash
cd frontend
npm install
npm start
```

`requirements.txt` 只包含轻量依赖；pyannote / Whisper / torch 等重型依赖是**可选**的。
未安装重型依赖、或未配置 OPENAI_API_KEY / PYANNOTE_AUTH_TOKEN / SMTP 时，后端确定性走 mock
离线分支，整个流程仍可用，便于本地开发和离线测试。

## 行为规格（验收标准）

以下条款是唯一验收标准。每条都必须满足，且不得为了通过测试而放宽断言或删除用例。
所有接口前缀为 `/api/v1`（例如 `POST /api/v1/meetings`）。

### A. 输入校验

A1. `POST /api/v1/meetings` 的 `title` 必须是非空字符串；缺失或空白要返回 4xx。

A2. 创建时间线片段时，`start_time`、`end_time` 必须是数值且 `start_time >= 0`、`end_time > start_time`；
不满足要返回 4xx，不得落库。

### B. 资源存在性与归属

B1. 针对不存在会议的写操作（田野笔记、时间线、音频上传、音频处理）必须返回 404，
不得凭空创建孤儿记录。

B2. `POST /api/v1/meetings/<meeting_id>/field-notes` 必须以**路径里的 meeting_id 为准**：
请求体中的 `meeting_id` 与路径不一致时要返回 4xx（或忽略请求体并强制使用路径值），
最终落库的 `meeting_id` 必须等于路径值。

B3. 时间线片段必须绑定到已存在的时间线；`POST /api/v1/timelines/<timeline_id>/clips`
在时间线不存在时返回 404，并且落库的 `timeline_id` 必须等于路径值。

### C. 音频上传

C1. 上传文件的**展示用 `filename` 保留原始文件名（含中文）**，但落盘路径必须安全化：
去掉路径成分、防止 `../` 逃逸；最终写入的路径必须始终位于上传目录内
（用 `file_path` 解析后的真实路径校验，不得写到上传目录之外）。

C2. 同一会议重复上传同名文件不得互相覆盖：落盘文件名要能区分（例如加唯一前缀），
两次上传返回的 `file_path` 必须不同，且两个文件都真实存在。

### D. 音频处理

D1. `POST /api/v1/meetings/process-audio` 必须幂等：对**同一个 `audio_file_id`** 重复调用，
不得重复插入转写记录（第二次应复用既有结果或返回既有 transcript_id），转写条数不随调用次数增长。

D2. `audio_file_id` 必须属于请求里的 `meeting_id`；跨会议引用别人的音频文件要返回 4xx，
不得把转写挂到错误的会议下。

D3. 未安装重型依赖时允许走 mock 离线分支；但一旦真实模型/服务已加载、真实调用失败
（模型加载异常、推理异常、网络错误、限流等），不得用 mock 文本冒充成功结果，
必须如实返回错误响应。

### E. 外部服务失败处理

E1. AI 摘要：未配置 OPENAI_API_KEY 时允许走 mock 并落库；已配置但真实调用失败时必须返回错误，
不得把 mock 摘要落库。

E2. 邮件：未配置 SMTP 时允许 mock 并标记已发送；SMTP 已配置但发送失败时必须如实返回失败，
`email_sent` 保持 false。

### F. 会议状态

F1. 会议状态只能按 `pending -> transcribed -> summarized/completed` 单调推进；
处理失败时不得把状态更新为已完成。

## 变更说明

以下按「行为规格」逐条说明根因与修法，对应测试见 `backend/tests/test_behavior_spec.py`。

### A. 输入校验

- **A1 会议标题**：`MeetingCreate.title` 原无任何校验，空串/纯空白也能落库。
  修法：在 `models/schemas.py` 的 `MeetingBase` 上加 `field_validator`，
  空白标题抛 `ValueError`，FastAPI 自动返回 422。
- **A2 片段时间**：`TimelineClipBase` 原未校验 `start_time`/`end_time`，
  负数起点、`end_time <= start_time` 都能保存。修法：在 `TimelineClipBase` 上加
  `start_time >= 0` 的字段校验和 `end_time > start_time` 的 `model_validator`，
  建时间线与追加片段两个入口同时生效，非法输入返回 422 且不落库。

### B. 资源存在性与归属

- **B1 孤儿记录**：`POST /meetings/{id}/field-notes`、`POST /meetings/{id}/timelines`
  的函数签名根本没接收路径里的 `meeting_id`，直接按请求体落库，会议不存在也返回 200。
  修法：两个端点补上路径参数，先查会议、不存在返回 404。
- **B2 归属不一致**：田野笔记/时间线/片段的请求体 id 与路径 id 不一致时会被静默采信。
  修法：三个端点一律以路径 id 为准，请求体 id 与路径不一致返回 400，
  落库记录强制使用路径值。
- **B3 片段挂到不存在的时间线**：`POST /timelines/{timeline_id}/clips` 同样丢弃了
  路径参数，可往任意 `timeline_id` 写孤儿片段。修法：先校验时间线存在（否则 404），
  请求体 `timeline_id` 与路径不一致返回 400。

### C. 音频上传

- **C1 路径逃逸**：原实现把 `file.filename` 直接拼进落盘路径，`../../evil.wav`
  会写到上传目录之外。修法：新增 `_safe_upload_path()`——先做 `\`→`/` 归一化再取
  `basename` 去掉路径成分、折叠 `..`，加 UUID 前缀后用 `realpath` 校验最终路径
  必须位于上传目录内；数据库 `filename` 字段仍保留原始文件名（含中文）用于展示。
- **C2 同名覆盖**：原落盘名是固定的 `meeting_{id}_{filename}`，同名重复上传互相覆盖。
  修法：落盘文件名加 UUID 唯一前缀，两次上传 `file_path` 不同且文件都真实存在。

### D. 音频处理

- **D1 重复转写**：`process-audio` 每次都新建 `Transcript`。修法：处理前按
  `audio_file_id` 查既有转写，存在则直接返回既有 `transcript_id`，不重复插入。
- **D2 跨会议引用**：原实现只按 `audio_file_id` 查文件、不校验归属，能把 A 会议的
  音频转写挂到 B 会议。修法：显式校验 `audio_file.meeting_id == request.meeting_id`，
  不一致返回 400。
- **D3 失败伪装成功**：`speaker_diarization` / `transcription` 在真实模型已加载、
  推理失败时 `except` 里回落 `_mock_*`，把 mock 文本当真实结果落库。修法：真实调用
  失败改为抛 `RuntimeError`；端点捕获后回滚事务并返回 502，不落库、不推进状态。
  mock 分支只保留给「依赖未安装/未配置」的离线场景。

### E. 外部服务失败处理

- **E1 AI 摘要**：`ai_summary_service` 在 OpenAI 调用失败、或返回内容不是合法 JSON 时
  回落 `_mock_summary` 并落库。修法：两种情况都改为抛错，`generate-summary` 与
  `full-process` 捕获后回滚并返回 502，不写蒙太奇纪要、不推进状态；
  仅未配置 `OPENAI_API_KEY` 时走 mock。
- **E2 邮件**：原实现已区分「未配置 SMTP 走 mock」与「发送失败返回 False」，
  保持该行为；补充测试确认 SMTP 已配置但发送失败时响应 `success=false`
  且 `email_sent` 保持 false。

### F. 会议状态

- **F1 状态机**：原实现在各处直接赋值 `meeting.status`，处理失败也会把会议推进为
  `transcribed`/`summarized`/`completed`。修法：新增 `_advance_meeting_status()`，
  只允许 `pending -> transcribed -> summarized/completed` 单调推进；
  所有处理路径先做事务回滚再返回错误，失败时状态原地不动。
