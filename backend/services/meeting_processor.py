from typing import List, Dict, Any, Optional
import logging
import os

from core.config import settings
from services.speaker_diarization import SpeakerDiarizationService
from services.transcription_service import WhisperTranscriptionService
from services.ai_summary_service import AISummaryService
from services.email_service import EmailService

logger = logging.getLogger(__name__)


class MeetingProcessor:
    def __init__(self):
        self.speaker_service = SpeakerDiarizationService(settings.PYANNOTE_AUTH_TOKEN)
        self.transcription_service = WhisperTranscriptionService(settings.WHISPER_MODEL)
        self.ai_service = AISummaryService(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
        self.email_service = EmailService(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.SMTP_FROM_EMAIL
        )

    def process_audio_file(self, audio_path: str) -> Dict[str, Any]:
        logger.info(f"Processing audio file: {audio_path}")

        speaker_segments = self.speaker_service.diarize_audio(audio_path)
        logger.info(f"Speaker diarization complete: {len(speaker_segments)} segments")

        transcription = self.transcription_service.transcribe_audio(audio_path)
        logger.info(f"Transcription complete: {len(transcription['segments'])} segments")

        merged_segments = self.transcription_service.merge_transcript_with_speakers(
            transcription["segments"],
            speaker_segments
        )

        result = {
            "full_text": transcription["full_text"],
            "segments": merged_segments
        }

        return result

    def generate_montage_summary(
        self,
        segments: List[Dict[str, Any]],
        field_notes: List[str] = None
    ) -> Dict[str, Any]:
        logger.info("Generating montage summary...")
        summary = self.ai_service.generate_montage_summary(segments, field_notes)
        logger.info("Montage summary generated successfully")
        return summary

    def send_summary_email(
        self,
        recipients: List[str],
        meeting_title: str,
        montage_note: Dict[str, Any],
        edit_decisions: List[Dict[str, Any]],
        subtitle_notes: Dict[str, Any]
    ) -> bool:
        logger.info(f"Sending summary email to {len(recipients)} recipients...")
        success = self.email_service.send_montage_summary(
            recipients, meeting_title, montage_note, edit_decisions, subtitle_notes
        )
        if success:
            logger.info("Email sent successfully")
        else:
            logger.warning("Email sending failed or mocked")
        return success
