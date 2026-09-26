from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import json

from database.database import get_db
from database import models
from models.schemas import (
    MeetingCreate, MeetingResponse,
    FieldNoteCreate, FieldNoteResponse,
    TimelineCreate, TimelineResponse, TimelineClipCreate, TimelineClipResponse,
    TranscriptResponse,
    MontageNoteCreate, MontageNoteResponse,
    AudioFileCreate, AudioFileResponse,
    ProcessAudioRequest, ProcessMeetingRequest, SendEmailRequest,
    ProcessResult
)
from services.meeting_processor import MeetingProcessor
from core.config import settings

router = APIRouter()

# 可测性改造：上传目录可配置，默认行为不变（仍为 uploads）
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

processor = MeetingProcessor()


@router.get("/meetings", response_model=List[MeetingResponse])
def get_meetings(db: Session = Depends(get_db)):
    meetings = db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).all()
    return meetings


@router.post("/meetings", response_model=MeetingResponse)
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    db_meeting = models.Meeting(**meeting.model_dump())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("/meetings/{meeting_id}/upload-audio", response_model=AudioFileResponse)
async def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    duration: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    file_location = os.path.join(UPLOAD_DIR, f"meeting_{meeting_id}_{file.filename}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_file = models.AudioFile(
        meeting_id=meeting_id,
        filename=file.filename,
        file_path=file_location,
        duration=duration
    )
    db.add(audio_file)
    db.commit()
    db.refresh(audio_file)

    return audio_file


@router.get("/meetings/{meeting_id}/audio", response_model=List[AudioFileResponse])
def get_meeting_audio(meeting_id: int, db: Session = Depends(get_db)):
    audio_files = db.query(models.AudioFile).filter(
        models.AudioFile.meeting_id == meeting_id
    ).all()
    return audio_files


@router.post("/meetings/process-audio", response_model=ProcessResult)
def process_audio(request: ProcessAudioRequest, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    audio_file = None
    if request.audio_file_id:
        audio_file = db.query(models.AudioFile).filter(
            models.AudioFile.id == request.audio_file_id
        ).first()
    else:
        audio_file = db.query(models.AudioFile).filter(
            models.AudioFile.meeting_id == request.meeting_id
        ).first()

    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")

    result = processor.process_audio_file(audio_file.file_path)

    transcript = models.Transcript(
        meeting_id=request.meeting_id,
        audio_file_id=audio_file.id,
        full_text=result["full_text"]
    )
    db.add(transcript)
    db.flush()

    for seg in result["segments"]:
        segment = models.SpeakerSegment(
            transcript_id=transcript.id,
            speaker_label=seg["speaker_label"],
            speaker_role=seg["speaker_role"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
            text=seg["text"]
        )
        db.add(segment)

    meeting.status = "transcribed"
    db.commit()
    db.refresh(transcript)

    return ProcessResult(
        success=True,
        message="音频处理完成，已生成带说话人识别的转写文本",
        data={"transcript_id": transcript.id}
    )


@router.get("/meetings/{meeting_id}/transcripts", response_model=List[TranscriptResponse])
def get_meeting_transcripts(meeting_id: int, db: Session = Depends(get_db)):
    transcripts = db.query(models.Transcript).filter(
        models.Transcript.meeting_id == meeting_id
    ).all()
    return transcripts


@router.get("/transcripts/{transcript_id}", response_model=TranscriptResponse)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript


@router.post("/meetings/{meeting_id}/field-notes", response_model=FieldNoteResponse)
def create_field_note(note: FieldNoteCreate, db: Session = Depends(get_db)):
    db_note = models.FieldNote(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/meetings/{meeting_id}/field-notes", response_model=List[FieldNoteResponse])
def get_field_notes(meeting_id: int, db: Session = Depends(get_db)):
    notes = db.query(models.FieldNote).filter(
        models.FieldNote.meeting_id == meeting_id
    ).order_by(models.FieldNote.timestamp).all()
    return notes


@router.post("/meetings/{meeting_id}/timelines", response_model=TimelineResponse)
def create_timeline(timeline: TimelineCreate, db: Session = Depends(get_db)):
    db_timeline = models.Timeline(
        meeting_id=timeline.meeting_id,
        title=timeline.title
    )
    db.add(db_timeline)
    db.flush()

    for clip in timeline.clips:
        db_clip = models.TimelineClip(
            timeline_id=db_timeline.id,
            clip_name=clip.clip_name,
            start_time=clip.start_time,
            end_time=clip.end_time,
            source_file=clip.source_file,
            notes=clip.notes
        )
        db.add(db_clip)

    db.commit()
    db.refresh(db_timeline)
    return db_timeline


@router.get("/meetings/{meeting_id}/timelines", response_model=List[TimelineResponse])
def get_timelines(meeting_id: int, db: Session = Depends(get_db)):
    timelines = db.query(models.Timeline).filter(
        models.Timeline.meeting_id == meeting_id
    ).all()
    return timelines


@router.post("/timelines/{timeline_id}/clips", response_model=TimelineClipResponse)
def add_timeline_clip(clip: TimelineClipCreate, db: Session = Depends(get_db)):
    db_clip = models.TimelineClip(**clip.model_dump())
    db.add(db_clip)
    db.commit()
    db.refresh(db_clip)
    return db_clip


@router.post("/meetings/generate-summary", response_model=ProcessResult)
def generate_summary(request: ProcessMeetingRequest, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    transcripts = db.query(models.Transcript).filter(
        models.Transcript.meeting_id == request.meeting_id
    ).all()

    if not transcripts:
        raise HTTPException(status_code=400, detail="No transcripts found for this meeting")

    all_segments = []
    for transcript in transcripts:
        segments = db.query(models.SpeakerSegment).filter(
            models.SpeakerSegment.transcript_id == transcript.id
        ).order_by(models.SpeakerSegment.start_time).all()
        for seg in segments:
            all_segments.append({
                "speaker_label": seg.speaker_label,
                "speaker_role": seg.speaker_role,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "text": seg.text
            })

    field_notes = db.query(models.FieldNote).filter(
        models.FieldNote.meeting_id == request.meeting_id
    ).all()
    field_note_contents = [note.content for note in field_notes]

    summary = processor.generate_montage_summary(all_segments, field_note_contents)

    edit_decisions_json = json.dumps(summary.get("edit_decisions", []), ensure_ascii=False)
    subtitle_notes_json = json.dumps(summary.get("subtitle_notes", {}), ensure_ascii=False)

    montage_note = models.MontageNote(
        meeting_id=request.meeting_id,
        content=summary.get("content", ""),
        edit_decisions=edit_decisions_json,
        subtitle_notes=subtitle_notes_json
    )
    db.add(montage_note)

    meeting.status = "summarized"
    db.commit()
    db.refresh(montage_note)

    return ProcessResult(
        success=True,
        message="蒙太奇纪要生成完成",
        data={"montage_note_id": montage_note.id}
    )


@router.get("/meetings/{meeting_id}/montage-notes", response_model=List[MontageNoteResponse])
def get_montage_notes(meeting_id: int, db: Session = Depends(get_db)):
    notes = db.query(models.MontageNote).filter(
        models.MontageNote.meeting_id == meeting_id
    ).all()

    result = []
    for note in notes:
        note_dict = {
            "id": note.id,
            "meeting_id": note.meeting_id,
            "content": note.content,
            "edit_decisions": note.edit_decisions,
            "subtitle_notes": note.subtitle_notes,
            "created_at": note.created_at,
            "email_sent": note.email_sent,
            "email_recipients": note.email_recipients
        }
        result.append(note_dict)

    return result


@router.get("/montage-notes/{note_id}")
def get_montage_note_detail(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.MontageNote).filter(models.MontageNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Montage note not found")

    return {
        "id": note.id,
        "meeting_id": note.meeting_id,
        "content": note.content,
        "edit_decisions": json.loads(note.edit_decisions) if note.edit_decisions else [],
        "subtitle_notes": json.loads(note.subtitle_notes) if note.subtitle_notes else {},
        "created_at": note.created_at,
        "email_sent": note.email_sent,
        "email_recipients": note.email_recipients
    }


@router.post("/send-email", response_model=ProcessResult)
def send_summary_email(request: SendEmailRequest, db: Session = Depends(get_db)):
    montage_note = db.query(models.MontageNote).filter(
        models.MontageNote.id == request.montage_note_id
    ).first()
    if not montage_note:
        raise HTTPException(status_code=404, detail="Montage note not found")

    meeting = db.query(models.Meeting).filter(
        models.Meeting.id == montage_note.meeting_id
    ).first()

    edit_decisions = json.loads(montage_note.edit_decisions) if montage_note.edit_decisions else []
    subtitle_notes = json.loads(montage_note.subtitle_notes) if montage_note.subtitle_notes else {}

    success = processor.send_summary_email(
        recipients=request.recipients,
        meeting_title=meeting.title if meeting else "剪辑会议",
        montage_note={"content": montage_note.content},
        edit_decisions=edit_decisions,
        subtitle_notes=subtitle_notes
    )

    if success:
        montage_note.email_sent = True
        montage_note.email_recipients = ", ".join(request.recipients)
        db.commit()

    return ProcessResult(
        success=success,
        message="邮件已发送" if success else "邮件发送失败",
        data={"recipients": request.recipients}
    )


@router.post("/meetings/full-process", response_model=ProcessResult)
def full_process_meeting(request: ProcessMeetingRequest, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    audio_file = db.query(models.AudioFile).filter(
        models.AudioFile.meeting_id == request.meeting_id
    ).first()

    if audio_file:
        result = processor.process_audio_file(audio_file.file_path)

        transcript = models.Transcript(
            meeting_id=request.meeting_id,
            audio_file_id=audio_file.id,
            full_text=result["full_text"]
        )
        db.add(transcript)
        db.flush()

        for seg in result["segments"]:
            segment = models.SpeakerSegment(
                transcript_id=transcript.id,
                speaker_label=seg["speaker_label"],
                speaker_role=seg["speaker_role"],
                start_time=seg["start_time"],
                end_time=seg["end_time"],
                text=seg["text"]
            )
            db.add(segment)

    all_segments = []
    transcripts = db.query(models.Transcript).filter(
        models.Transcript.meeting_id == request.meeting_id
    ).all()

    for transcript in transcripts:
        segments = db.query(models.SpeakerSegment).filter(
            models.SpeakerSegment.transcript_id == transcript.id
        ).order_by(models.SpeakerSegment.start_time).all()
        for seg in segments:
            all_segments.append({
                "speaker_label": seg.speaker_label,
                "speaker_role": seg.speaker_role,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "text": seg.text
            })

    field_notes = db.query(models.FieldNote).filter(
        models.FieldNote.meeting_id == request.meeting_id
    ).all()
    field_note_contents = [note.content for note in field_notes]

    summary = processor.generate_montage_summary(all_segments, field_note_contents)

    edit_decisions_json = json.dumps(summary.get("edit_decisions", []), ensure_ascii=False)
    subtitle_notes_json = json.dumps(summary.get("subtitle_notes", {}), ensure_ascii=False)

    montage_note = models.MontageNote(
        meeting_id=request.meeting_id,
        content=summary.get("content", ""),
        edit_decisions=edit_decisions_json,
        subtitle_notes=subtitle_notes_json
    )
    db.add(montage_note)

    meeting.status = "completed"
    db.commit()
    db.refresh(montage_note)

    return ProcessResult(
        success=True,
        message="完整处理流程完成：音频转写 → 说话人识别 → AI摘要 → 蒙太奇纪要生成",
        data={"montage_note_id": montage_note.id}
    )
