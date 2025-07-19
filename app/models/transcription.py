import uuid
from datetime import datetime
from typing import Dict, Optional


class Transcription:
    def __init__(self,
                 original_text: str,
                 job_id: str,
                 original_chunks: Dict,
                 input_language: str,
                 tr_text: Optional[str] = None,
                 tr_chunks: Optional[Dict] = None,
                 target_language: Optional[str] = None,
                 srt_filepath: Optional[str] = None,
                 creation_datetime: Optional[datetime] = None,
                 transcription_id: Optional[str] = None):
        
        self.id = transcription_id or f"transcription_{uuid.uuid4().hex[:8]}_{job_id}"
        self.job_id = job_id
        self.original_text = original_text
        self.original_chunks = original_chunks
        self.translated_text = tr_text
        self.translated_chunks = tr_chunks
        self.input_language = input_language
        self.target_language = target_language
        self.srt_filepath = srt_filepath
        self.creation_datetime: datetime = creation_datetime or datetime.now()

    def _to_dict(self) -> dict:
        return {
            "transcription_id": self.id,
            "job_id": self.job_id,
            "original_text": self.original_text,
            "original_chunks": self.original_chunks,
            "translated_text": self.translated_text,
            "translated_chunks": self.translated_chunks,
            "input_language": self.input_language,
            "current_language": self.target_language,
            "srt_filepath": self.srt_filepath,
            "creation_datetime": self.creation_datetime.isoformat()
        }

    @classmethod
    def _from_dict(cls, data: dict):
        return cls(
            transcription_id=data["transcription_id"],
            job_id=data["job_id"],
            original_text=data["original_text"],
            original_chunks=data["original_chunks"],
            tr_text=data.get("translated_text"),
            tr_chunks=data.get("translated_chunks"),
            input_language=data["input_language"],
            target_language=data.get("current_language"),
            srt_filepath=data.get("srt_filepath"),
            creation_datetime=datetime.fromisoformat(data["creation_datetime"])
        )
