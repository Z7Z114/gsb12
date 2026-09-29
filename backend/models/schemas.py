from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title 必须是非空字符串")
        return v


class MeetingCreate(MeetingBase):
    pass


class MeetingResponse(MeetingBase):
    id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class FieldNoteBase(BaseModel):
    content: str
    timestamp: Optional[float] = None
    author: Optional[str] = None


class FieldNoteCreate(FieldNoteBase):
    meeting_id: int


class FieldNoteResponse(FieldNoteBase):
    id: int
    meeting_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TimelineClipBase(BaseModel):
    clip_name: str
    start_time: float
    end_time: float
    source_file: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("start_time")
    @classmethod
    def start_time_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("start_time 必须 >= 0")
        return v

    @model_validator(mode="after")
    def end_time_must_be_after_start_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time 必须大于 start_time")
        return self


class TimelineClipCreate(TimelineClipBase):
    timeline_id: int


class TimelineClipResponse(TimelineClipBase):
    id: int
    timeline_id: int

    class Config:
        from_attributes = True


class TimelineBase(BaseModel):
    title: str


class TimelineCreate(TimelineBase):
    meeting_id: int
    clips: Optional[List[TimelineClipCreate]] = []


class TimelineResponse(TimelineBase):
    id: int
    meeting_id: int
    created_at: datetime
    clips: List[TimelineClipResponse] = []

    class Config:
        from_attributes = True


class SpeakerSegmentBase(BaseModel):
    speaker_label: str
    speaker_role: Optional[str] = None
    start_time: float
    end_time: float
    text: str


class SpeakerSegmentResponse(SpeakerSegmentBase):
    id: int
    transcript_id: int

    class Config:
        from_attributes = True


class TranscriptBase(BaseModel):
    full_text: str


class TranscriptCreate(TranscriptBase):
    meeting_id: int
    audio_file_id: Optional[int] = None
    segments: List[SpeakerSegmentBase] = []


class TranscriptResponse(TranscriptBase):
    id: int
    meeting_id: int
    audio_file_id: Optional[int] = None
    created_at: datetime
    segments: List[SpeakerSegmentResponse] = []

    class Config:
        from_attributes = True


class MontageNoteBase(BaseModel):
    content: str
    edit_decisions: str
    subtitle_notes: str


class MontageNoteCreate(MontageNoteBase):
    meeting_id: int


class MontageNoteResponse(MontageNoteBase):
    id: int
    meeting_id: int
    created_at: datetime
    email_sent: bool
    email_recipients: Optional[str] = None

    class Config:
        from_attributes = True


class AudioFileBase(BaseModel):
    filename: str
    file_path: str
    duration: Optional[float] = None


class AudioFileCreate(AudioFileBase):
    meeting_id: int


class AudioFileResponse(AudioFileBase):
    id: int
    meeting_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessAudioRequest(BaseModel):
    meeting_id: int
    audio_file_id: Optional[int] = None


class ProcessMeetingRequest(BaseModel):
    meeting_id: int


class SendEmailRequest(BaseModel):
    montage_note_id: int
    recipients: List[str]


class ProcessResult(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
