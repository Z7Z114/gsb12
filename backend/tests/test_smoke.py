"""冒烟测试：只覆盖顺利路径，在未修复的初始快照上必须全绿。"""
import io

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _make_meeting(client, **overrides):
    payload = {"title": "第3批民族志纪录片粗剪会议", "description": "机位与伦理讨论"}
    payload.update(overrides)
    resp = client.post("/api/v1/meetings", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_create_and_get_meeting(client):
    m = _make_meeting(client)
    assert m["title"] == "第3批民族志纪录片粗剪会议"
    detail = client.get(f"/api/v1/meetings/{m['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == m["id"]


def test_list_meetings(client):
    _make_meeting(client)
    resp = client.get("/api/v1/meetings")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list) and len(resp.json()) >= 1


def test_upload_audio(client):
    m = _make_meeting(client)
    resp = client.post(
        f"/api/v1/meetings/{m['id']}/upload-audio",
        files={"file": ("rough_cut.wav", io.BytesIO(b"RIFF....WAVE"), "audio/wav")},
        data={"duration": "12.5"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["filename"] == "rough_cut.wav"
    assert body["meeting_id"] == m["id"]


def test_process_audio_mock(client):
    m = _make_meeting(client)
    up = client.post(
        f"/api/v1/meetings/{m['id']}/upload-audio",
        files={"file": ("rough_cut.wav", io.BytesIO(b"RIFF....WAVE"), "audio/wav")},
    )
    assert up.status_code == 200
    resp = client.post("/api/v1/meetings/process-audio", json={"meeting_id": m["id"]})
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is True

    transcripts = client.get(f"/api/v1/meetings/{m['id']}/transcripts").json()
    assert len(transcripts) == 1
    assert transcripts[0]["segments"], "转写应带说话人分段"


def test_field_note(client):
    m = _make_meeting(client)
    resp = client.post(
        f"/api/v1/meetings/{m['id']}/field-notes",
        json={"meeting_id": m["id"], "content": "现场观察记录", "timestamp": 3.5},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["meeting_id"] == m["id"]

    notes = client.get(f"/api/v1/meetings/{m['id']}/field-notes").json()
    assert len(notes) == 1


def test_timeline_and_clips(client):
    m = _make_meeting(client)
    resp = client.post(f"/api/v1/meetings/{m['id']}/timelines", json={
        "meeting_id": m["id"], "title": "第一版粗剪",
        "clips": [{"clip_name": "开场长镜头", "start_time": 0.0, "end_time": 270.0,
                   "timeline_id": 0}],
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "第一版粗剪"
    assert len(body["clips"]) == 1

    timelines = client.get(f"/api/v1/meetings/{m['id']}/timelines").json()
    assert len(timelines) == 1


def test_summary_and_email_mock(client):
    m = _make_meeting(client)
    client.post(
        f"/api/v1/meetings/{m['id']}/upload-audio",
        files={"file": ("a.wav", io.BytesIO(b"RIFF"), "audio/wav")},
    )
    client.post("/api/v1/meetings/process-audio", json={"meeting_id": m["id"]})

    resp = client.post("/api/v1/meetings/generate-summary", json={"meeting_id": m["id"]})
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is True

    notes = client.get(f"/api/v1/meetings/{m['id']}/montage-notes").json()
    assert notes, "摘要应生成蒙太奇纪要"
    note_id = notes[0]["id"]

    mail = client.post("/api/v1/send-email", json={
        "montage_note_id": note_id, "recipients": ["editor@example.com"]})
    assert mail.status_code == 200, mail.text
    assert mail.json()["success"] is True
