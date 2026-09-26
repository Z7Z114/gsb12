# 项目架构说明

## 数据流

```
音频文件上传
    ↓
pyannote.audio 说话人识别 (区分剪辑师/人类学家/导演)
    ↓
Whisper 音频转写 (生成带时间戳的文字记录)
    ↓
说话人 + 转写文本 合并
    ↓
OpenAI GPT 智能摘要 (生成剪辑决定清单 + 字幕说明)
    ↓
SMTP 邮件发送 (给后期团队)
```

## 后端模块说明

### 1. services/speaker_diarization.py
- 使用 pyannote/speaker-diarization-3.1 模型
- 自动识别和区分不同说话人
- 内置角色映射: SPEAKER_00=剪辑师, SPEAKER_01=人类学家, SPEAKER_02=导演

### 2. services/transcription_service.py
- 使用 OpenAI Whisper 进行语音转文字
- 支持多语言
- 输出带时间戳的分段文本

### 3. services/ai_summary_service.py
- 使用 GPT-4 生成专业的剪辑会议摘要
- 输出结构化的剪辑决定清单（优先级、类别、描述、时间线参考）
- 生成字幕说明（术语解释、文化注释、人物说明、敏感内容提示）

### 4. services/email_service.py
- SMTP 邮件服务
- 发送 HTML 格式的剪辑纪要邮件
- 支持多个收件人

## 前端模块说明

### 页面
- **MeetingList**: 会议列表，支持创建新会议
- **MeetingDetail**: 会议详情，包含所有功能模块

### 组件
- **TimelineViewer**: 可视化粗剪时间线
- **FieldNotesList**: 田野笔记展示
- **TranscriptViewer**: 带说话人识别的转写记录
- **EditDecisionsList**: 剪辑决定清单（支持优先级筛选）
- **SubtitleNotesPanel**: 字幕说明面板

## API 端点

### 会议管理
- `GET /api/v1/meetings` - 获取会议列表
- `POST /api/v1/meetings` - 创建会议
- `GET /api/v1/meetings/{id}` - 获取会议详情

### 音频处理
- `POST /api/v1/meetings/{id}/upload-audio` - 上传音频文件
- `POST /api/v1/meetings/process-audio` - 处理音频（说话人识别+转写）
- `POST /api/v1/meetings/generate-summary` - 生成AI摘要
- `POST /api/v1/meetings/full-process` - 一键完整处理流程

### 田野笔记
- `GET /api/v1/meetings/{id}/field-notes` - 获取田野笔记
- `POST /api/v1/meetings/{id}/field-notes` - 添加田野笔记

### 时间线
- `GET /api/v1/meetings/{id}/timelines` - 获取时间线
- `POST /api/v1/meetings/{id}/timelines` - 创建时间线

### 邮件
- `POST /api/v1/send-email` - 发送剪辑纪要邮件
