import uuid
from datetime import datetime
from typing import Dict, Optional

class Transcription:

    def __init__(self,
                 original_text: str,
                 job_id : str,
                 original_chunks: Dict,
                 input_language : str,
                 tr_text: Optional[str] = None,
                 tr_chunks: Optional[Dict]= None,
                 target_language: Optional[str] = None,
                 srt_filepath: Optional[str] = None,
                 ):
        
        self.id = f"transcription_{uuid.uuid4().hex[:8]}_{job_id}"
        self.job_id = job_id
        self.original_text = original_text
        self.original_chunks = original_chunks
        self.translated_text = tr_text
        self.translated_chunks = tr_chunks
        self.input_language = input_language
        self.target_language = target_language
        self.srt_filepath = srt_filepath
        self.creation_datetime = datetime.now()



    def __repr__(self):
        return (f"Transcription(id='{self.id}', jonb_id='{self.job_id}', "
                f"original_language='{self.input_language}', target_language='{self.target_language}', "
                f"original_filepath='{self.srt_filepath}"
                f"created_at='{self.creation_datetime}')")
