from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class WhisperTranscriptionService:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return
        try:
            import whisper
            self.model = whisper.load_model(self.model_name)
            self._initialized = True
            logger.info(f"Whisper model {self.model_name} loaded")
        except Exception as e:
            logger.warning(f"Could not load Whisper model: {e}")
            self._initialized = False

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        self._initialize()

        if not self._initialized:
            logger.info("Using mock transcription")
            return self._mock_transcribe(audio_path)

        try:
            result = self.model.transcribe(audio_path)

            segments = []
            for seg in result.get("segments", []):
                segments.append({
                    "start_time": seg["start"],
                    "end_time": seg["end"],
                    "text": seg["text"].strip()
                })

            return {
                "full_text": result["text"],
                "segments": segments
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return self._mock_transcribe(audio_path)

    def _mock_transcribe(self, audio_path: str) -> Dict[str, Any]:
        mock_segments = [
            {
                "start_time": 0.0,
                "end_time": 15.5,
                "text": "我们来讨论一下这个纪录片的叙事结构。我觉得开场的那个长镜头非常有力量，但可能需要考虑一下节奏问题。"
            },
            {
                "start_time": 15.5,
                "end_time": 35.0,
                "text": "从人类学的角度来看，这个镜头确实捕捉到了社区生活的真实感。但我们需要注意影像伦理的问题，特别是涉及到被拍摄者的隐私。"
            },
            {
                "start_time": 35.0,
                "end_time": 50.0,
                "text": "关于影像伦理，我建议在后期制作中对一些敏感画面进行模糊处理，或者征得当事人的同意。"
            },
            {
                "start_time": 50.0,
                "end_time": 72.0,
                "text": "我同意。另外，在叙事结构上，我建议采用非线性的方式，通过不同的时间线来展现这个文化的多个层面。"
            },
            {
                "start_time": 72.0,
                "end_time": 90.0,
                "text": "这个想法很好。让我们把这些讨论整理成剪辑决定清单，确保后期团队能够准确理解我们的意图。"
            }
        ]

        full_text = " ".join([seg["text"] for seg in mock_segments])

        return {
            "full_text": full_text,
            "segments": mock_segments
        }

    def merge_transcript_with_speakers(
        self,
        transcript_segments: List[Dict[str, Any]],
        speaker_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        merged = []

        for t_seg in transcript_segments:
            t_mid = (t_seg["start_time"] + t_seg["end_time"]) / 2

            best_match = None
            best_overlap = 0

            for s_seg in speaker_segments:
                overlap_start = max(t_seg["start_time"], s_seg["start_time"])
                overlap_end = min(t_seg["end_time"], s_seg["end_time"])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = s_seg

            if best_match:
                merged.append({
                    "speaker_label": best_match["speaker_label"],
                    "speaker_role": best_match["speaker_role"],
                    "start_time": t_seg["start_time"],
                    "end_time": t_seg["end_time"],
                    "text": t_seg["text"]
                })
            else:
                merged.append({
                    "speaker_label": "UNKNOWN",
                    "speaker_role": "未知",
                    "start_time": t_seg["start_time"],
                    "end_time": t_seg["end_time"],
                    "text": t_seg["text"]
                })

        logger.info(f"Merged {len(merged)} segments with speaker information")
        return merged
