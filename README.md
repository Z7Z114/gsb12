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

## 已知问题（现象，仅列出一部分）

- 上传名为 `../../evil.wav` 的文件时，文件会写到上传目录之外；
- 同一段音频处理两次会产生两条转写记录；
- 用一个会议的 `audio_file_id` 去处理另一个会议，接口照样成功；
- 给不存在的会议写田野笔记会返回 200 而不是 404；
- 时间线的 `end_time` 小于 `start_time` 也能保存；
- 真实 Whisper / pyannote / OpenAI 调用失败后，页面仍显示成功、库里存的是 mock 内容。

注意：「已知问题」只是现象清单的一部分，验收以「行为规格」为准，不要只修这里列出的现象。

## 变更说明

（由修复者填写：逐条写清每个问题的根因与修法。）
