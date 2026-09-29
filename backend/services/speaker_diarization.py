from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SpeakerDiarizationService:
    ROLE_MAP = {
        "SPEAKER_00": "剪辑师",
        "SPEAKER_01": "人类学家",
        "SPEAKER_02": "导演",
        "SPEAKER_03": "学者",
    }

    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token
        self.pipeline = None
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return
        try:
            from pyannote.audio import Pipeline
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.auth_token
            )
            self._initialized = True
            logger.info("Pyannote speaker diarization pipeline initialized")
        except Exception as e:
            logger.warning(f"Could not initialize pyannote pipeline: {e}")
            self._initialized = False

    def diarize_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        self._initialize()

        if not self._initialized:
            logger.info("Using mock speaker diarization")
            return self._mock_diarize(audio_path)

        try:
            diarization = self.pipeline(audio_path)
            segments = []

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker_label": speaker,
                    "speaker_role": self.ROLE_MAP.get(speaker, "未知"),
                    "start_time": turn.start,
                    "end_time": turn.end,
                    "text": ""
                })

            logger.info(f"Generated {len(segments)} speaker segments")
            return segments

        except Exception as e:
            logger.error(f"Speaker diarization failed: {e}")
            raise RuntimeError(f"说话人识别失败: {e}") from e

    def _mock_diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        mock_segments = [
            {
                "speaker_label": "SPEAKER_00",
                "speaker_role": "剪辑师",
                "start_time": 0.0,
                "end_time": 15.5,
                "text": ""
            },
            {
                "speaker_label": "SPEAKER_01",
                "speaker_role": "人类学家",
                "start_time": 15.5,
                "end_time": 35.0,
                "text": ""
            },
            {
                "speaker_label": "SPEAKER_00",
                "speaker_role": "剪辑师",
                "start_time": 35.0,
                "end_time": 50.0,
                "text": ""
            },
            {
                "speaker_label": "SPEAKER_01",
                "speaker_role": "人类学家",
                "start_time": 50.0,
                "end_time": 72.0,
                "text": ""
            },
            {
                "speaker_label": "SPEAKER_02",
                "speaker_role": "导演",
                "start_time": 72.0,
                "end_time": 90.0,
                "text": ""
            }
        ]
        return mock_segments
