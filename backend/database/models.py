from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending")

    audio_files = relationship("AudioFile", back_populates="meeting")
    field_notes = relationship("FieldNote", back_populates="meeting")
    timelines = relationship("Timeline", back_populates="meeting")
    transcripts = relationship("Transcript", back_populates="meeting")
    montage_notes = relationship("MontageNote", back_populates="meeting")


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    filename = Column(String(255))
    file_path = Column(String(500))
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="audio_files")
    transcripts = relationship("Transcript", back_populates="audio_file")


class SpeakerSegment(Base):
    __tablename__ = "speaker_segments"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"))
    speaker_label = Column(String(100))
    speaker_role = Column(String(50))
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(Text)

    transcript = relationship("Transcript", back_populates="segments")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"))
    full_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="transcripts")
    audio_file = relationship("AudioFile", back_populates="transcripts")
    segments = relationship("SpeakerSegment", back_populates="transcript")


class FieldNote(Base):
    __tablename__ = "field_notes"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    timestamp = Column(Float, nullable=True)
    content = Column(Text)
    author = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="field_notes")


class TimelineClip(Base):
    __tablename__ = "timeline_clips"

    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timelines.id"))
    clip_name = Column(String(255))
    start_time = Column(Float)
    end_time = Column(Float)
    source_file = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    timeline = relationship("Timeline", back_populates="clips")


class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="timelines")
    clips = relationship("TimelineClip", back_populates="timeline")


class MontageNote(Base):
    __tablename__ = "montage_notes"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    content = Column(Text)
    edit_decisions = Column(Text)
    subtitle_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email_sent = Column(Boolean, default=False)
    email_recipients = Column(String(1000), nullable=True)

    meeting = relationship("Meeting", back_populates="montage_notes")
