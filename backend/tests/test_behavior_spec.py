"""行为规格测试：逐条覆盖 README「行为规格」A-F 验收点。

这些测试在未修复的初始实现上必须失败，修复后通过。
"""
import io
import os

import pytest
from fastapi.testclient import TestClient

from main import app
from api.v1.endpoints import meeting as meeting_endpoint

UPLOAD_DIR = os.environ["UPLOAD_DIR"]


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _make_meeting(client, **overrides):
    payload = {"title": "行为规格测试会议", "description": "spec"}
    payload.update(overrides)
    resp = client.post("/api/v1/meetings", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _upload(client, meeting_id, filename="rough.wav", content=b"RIFF....WAVE"):
    resp = client.post(
        f"/api/v1/meetings/{meeting_id}/upload-audio",
        files={"file": (filename, io.BytesIO(content), "audio/wav")},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _process(client, meeting_id, audio_file_id=None):
    payload = {"meeting_id": meeting_id}
    if audio_file_id is not None:
        payload["audio_file_id"] = audio_file_id
    return client.post("/api/v1/meetings/process-audio", json=payload)


# ---------- A. 输入校验 ----------

def test_a1_meeting_title_must_be_non_empty(client):
    assert client.post("/api/v1/meetings", json={"title": ""}).status_code in (400, 422)
    assert client.post("/api/v1/meetings", json={"title": "   "}).status_code in (400, 422)
    assert client.post("/api/v1/meetings", json={}).status_code in (400, 422)


def test_a2_clip_time_validation_on_timeline_create(client):
    m = _make_meeting(client)
    base = {"meeting_id": m["id"], "title": "粗剪"}
    bad_clips = [
        {"clip_name": "负起点", "start_time": -1.0, "end_time": 10.0, "timeline_id": 0},
        {"clip_name": "倒置", "start_time": 20.0, "end_time": 10.0, "timeline_id": 0},
        {"clip_name": "等长", "start_time": 10.0, "end_time": 10.0, "timeline_id": 0},
    ]
    for clip in bad_clips:
        resp = client.post(f"/api/v1/meetings/{m['id']}/timelines",
                           json={**base, "clips": [clip]})
        assert resp.status_code in (400, 422), resp.text
    assert client.get(f"/api/v1/meetings/{m['id']}/timelines").json() == []


def test_a2_clip_time_validation_on_clip_add(client):
    m = _make_meeting(client)
    tl = client.post(f"/api/v1/meetings/{m['id']}/timelines",
                     json={"meeting_id": m["id"], "title": "粗剪", "clips": []}).json()
    resp = client.post(f"/api/v1/timelines/{tl['id']}/clips", json={
        "timeline_id": tl["id"], "clip_name": "倒置",
        "start_time": 30.0, "end_time": 5.0})
    assert resp.status_code in (400, 422)


# ---------- B. 资源存在性与归属 ----------

def test_b1_writes_to_missing_meeting_return_404(client):
    missing = 999999
    assert client.post(f"/api/v1/meetings/{missing}/field-notes", json={
        "meeting_id": missing, "content": "x"}).status_code == 404
    assert client.post(f"/api/v1/meetings/{missing}/timelines", json={
        "meeting_id": missing, "title": "t", "clips": []}).status_code == 404
    assert client.post(
        f"/api/v1/meetings/{missing}/upload-audio",
        files={"file": ("a.wav", io.BytesIO(b"RIFF"), "audio/wav")}).status_code == 404
    assert client.post("/api/v1/meetings/process-audio",
                       json={"meeting_id": missing}).status_code == 404


def test_b2_field_note_path_meeting_id_wins(client):
    a = _make_meeting(client)
    b = _make_meeting(client)
    resp = client.post(f"/api/v1/meetings/{a['id']}/field-notes", json={
        "meeting_id": b["id"], "content": "归属不一致"})
    assert 400 <= resp.status_code < 500
    assert client.get(f"/api/v1/meetings/{b['id']}/field-notes").json() == []

    ok = client.post(f"/api/v1/meetings/{a['id']}/field-notes", json={
        "meeting_id": a["id"], "content": "归属一致"})
    assert ok.status_code == 200
    assert ok.json()["meeting_id"] == a["id"]


def test_b3_clip_requires_existing_timeline_and_path_ownership(client):
    m = _make_meeting(client)
    tl = client.post(f"/api/v1/meetings/{m['id']}/timelines",
                     json={"meeting_id": m["id"], "title": "粗剪", "clips": []}).json()

    resp = client.post("/api/v1/timelines/999999/clips", json={
        "timeline_id": 999999, "clip_name": "孤儿",
        "start_time": 0.0, "end_time": 5.0})
    assert resp.status_code == 404

    other = client.post(f"/api/v1/meetings/{m['id']}/timelines",
                        json={"meeting_id": m["id"], "title": "二剪", "clips": []}).json()
    resp = client.post(f"/api/v1/timelines/{tl['id']}/clips", json={
        "timeline_id": other["id"], "clip_name": "串线",
        "start_time": 0.0, "end_time": 5.0})
    assert 400 <= resp.status_code < 500

    ok = client.post(f"/api/v1/timelines/{tl['id']}/clips", json={
        "timeline_id": tl["id"], "clip_name": "正常",
        "start_time": 0.0, "end_time": 5.0})
    assert ok.status_code == 200
    assert ok.json()["timeline_id"] == tl["id"]


# ---------- C. 音频上传 ----------

def test_c1_path_traversal_is_contained_and_filename_preserved(client):
    m = _make_meeting(client)
    resp = client.post(
        f"/api/v1/meetings/{m['id']}/upload-audio",
        files={"file": ("../../evil.wav", io.BytesIO(b"EVIL"), "audio/wav")})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    upload_root = os.path.realpath(UPLOAD_DIR)
    real_path = os.path.realpath(body["file_path"])
    assert real_path.startswith(upload_root + os.sep), "落盘路径逃逸出上传目录"
    assert os.path.isfile(real_path)


def test_c1_chinese_filename_preserved_for_display(client):
    m = _make_meeting(client)
    body = _upload(client, m["id"], filename="田野录音①.wav")
    assert body["filename"] == "田野录音①.wav"
    assert os.path.isfile(body["file_path"])


def test_c2_same_name_uploads_do_not_overwrite(client):
    m = _make_meeting(client)
    first = _upload(client, m["id"], filename="same.wav", content=b"first")
    second = _upload(client, m["id"], filename="same.wav", content=b"second")
    assert first["file_path"] != second["file_path"]
    assert os.path.isfile(first["file_path"])
    assert os.path.isfile(second["file_path"])


# ---------- D. 音频处理 ----------

def test_d1_process_audio_is_idempotent(client):
    m = _make_meeting(client)
    audio = _upload(client, m["id"])
    r1 = _process(client, m["id"], audio["id"])
    r2 = _process(client, m["id"], audio["id"])
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["data"]["transcript_id"] == r2.json()["data"]["transcript_id"]
    transcripts = client.get(f"/api/v1/meetings/{m['id']}/transcripts").json()
    assert len(transcripts) == 1


def test_d2_cross_meeting_audio_reference_rejected(client):
    a = _make_meeting(client)
    b = _make_meeting(client)
    audio = _upload(client, a["id"])
    resp = _process(client, b["id"], audio["id"])
    assert 400 <= resp.status_code < 500
    assert client.get(f"/api/v1/meetings/{b['id']}/transcripts").json() == []


def test_d3_real_transcription_failure_returns_error(client, monkeypatch):
    m = _make_meeting(client)
    audio = _upload(client, m["id"])
    svc = meeting_endpoint.processor.transcription_service
    monkeypatch.setattr(svc, "_initialized", True)

    class _BrokenModel:
        def transcribe(self, path):
            raise RuntimeError("模拟 Whisper 推理失败")

    monkeypatch.setattr(svc, "model", _BrokenModel())
    resp = _process(client, m["id"], audio["id"])
    assert resp.status_code >= 500, resp.text
    assert client.get(f"/api/v1/meetings/{m['id']}/transcripts").json() == []
    assert client.get(f"/api/v1/meetings/{m['id']}").json()["status"] == "pending"


def test_d3_real_diarization_failure_returns_error(client, monkeypatch):
    m = _make_meeting(client)
    audio = _upload(client, m["id"])
    svc = meeting_endpoint.processor.speaker_service
    monkeypatch.setattr(svc, "_initialized", True)

    class _BrokenPipeline:
        def __call__(self, path):
            raise RuntimeError("模拟 pyannote 推理失败")

    monkeypatch.setattr(svc, "pipeline", _BrokenPipeline())
    resp = _process(client, m["id"], audio["id"])
    assert resp.status_code >= 500, resp.text
    assert client.get(f"/api/v1/meetings/{m['id']}/transcripts").json() == []


# ---------- E. 外部服务失败处理 ----------

def _make_transcribed_meeting(client):
    m = _make_meeting(client)
    audio = _upload(client, m["id"])
    resp = _process(client, m["id"], audio["id"])
    assert resp.status_code == 200, resp.text
    return m


def test_e1_real_ai_summary_failure_not_saved(client, monkeypatch):
    m = _make_transcribed_meeting(client)
    ai = meeting_endpoint.processor.ai_service
    monkeypatch.setattr(ai, "_initialized", True)
    monkeypatch.setattr(ai, "api_key", "sk-test")

    class _BrokenCompletions:
        @staticmethod
        def create(**kwargs):
            raise RuntimeError("模拟 OpenAI 限流")

    class _BrokenChat:
        completions = _BrokenCompletions()

    class _BrokenClient:
        chat = _BrokenChat()

    monkeypatch.setattr(ai, "client", _BrokenClient())
    resp = client.post("/api/v1/meetings/generate-summary", json={"meeting_id": m["id"]})
    assert resp.status_code >= 500, resp.text
    assert client.get(f"/api/v1/meetings/{m['id']}/montage-notes").json() == []
    assert client.get(f"/api/v1/meetings/{m['id']}").json()["status"] == "transcribed"


def test_e2_smtp_failure_keeps_email_sent_false(client, monkeypatch):
    m = _make_transcribed_meeting(client)
    resp = client.post("/api/v1/meetings/generate-summary", json={"meeting_id": m["id"]})
    assert resp.status_code == 200, resp.text
    note_id = client.get(f"/api/v1/meetings/{m['id']}/montage-notes").json()[0]["id"]

    email_svc = meeting_endpoint.processor.email_service
    monkeypatch.setattr(email_svc, "smtp_user", "editor@example.com")
    monkeypatch.setattr(email_svc, "smtp_password", "secret")
    monkeypatch.setattr(email_svc, "smtp_host", "127.0.0.1")
    monkeypatch.setattr(email_svc, "smtp_port", 1)

    mail = client.post("/api/v1/send-email", json={
        "montage_note_id": note_id, "recipients": ["a@example.com"]})
    assert mail.json()["success"] is False
    note = client.get(f"/api/v1/montage-notes/{note_id}").json()
    assert note["email_sent"] is False


# ---------- F. 会议状态 ----------

def test_f1_full_process_failure_does_not_complete_meeting(client, monkeypatch):
    m = _make_meeting(client)
    _upload(client, m["id"])
    svc = meeting_endpoint.processor.transcription_service
    monkeypatch.setattr(svc, "_initialized", True)

    class _BrokenModel:
        def transcribe(self, path):
            raise RuntimeError("模拟模型加载后推理失败")

    monkeypatch.setattr(svc, "model", _BrokenModel())
    resp = client.post("/api/v1/meetings/full-process", json={"meeting_id": m["id"]})
    assert resp.status_code >= 500, resp.text
    assert client.get(f"/api/v1/meetings/{m['id']}").json()["status"] == "pending"


def test_f1_status_advances_monotonically_on_success(client):
    m = _make_meeting(client)
    assert m["status"] == "pending"
    audio = _upload(client, m["id"])
    _process(client, m["id"], audio["id"])
    assert client.get(f"/api/v1/meetings/{m['id']}").json()["status"] == "transcribed"
    client.post("/api/v1/meetings/generate-summary", json={"meeting_id": m["id"]})
    assert client.get(f"/api/v1/meetings/{m['id']}").json()["status"] == "summarized"
