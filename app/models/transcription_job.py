import uuid
from datetime import datetime
from typing import List, Optional

class TranscriptionJob:
    def __init__(self,
                 video_storage_path: str,
                 input_language: str,
                 target_languages: List[str],
                 processed: bool = False,
                 job_id: Optional[str] = None,
                 processed_video_path: Optional[str] = "",
                 upload_date: Optional[datetime] = None):
        
        self.id = job_id or f"job_{uuid.uuid4().hex[:8]}"
        self.video_storage_path = video_storage_path
        self.processed_video_path = processed_video_path or ""
        self.input_language = input_language
        self.target_languages = target_languages
        self.upload_date: datetime = upload_date or datetime.now()
        self.processed = processed

    def _to_dict(self) -> dict:
        return {
            "job_id": self.id,
            "original_video_path": self.video_storage_path,
            "processed_video_path": self.processed_video_path,
            "input_language": self.input_language,
            "target_languages": self.target_languages,
            "upload_date": self.upload_date.isoformat(),
            "processed": self.processed
        }

    @classmethod
    def _from_dict(cls, data: dict):
        return cls(
            job_id=data["job_id"],
            video_storage_path=data["original_video_path"],
            processed_video_path=data.get("processed_video_path", ""),
            input_language=data["input_language"],
            target_languages=data["target_languages"],
            upload_date=datetime.fromisoformat(data["upload_date"]),
            processed=data["processed"]
        )

     
        



   

