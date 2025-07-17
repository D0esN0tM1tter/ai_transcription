import uuid
from datetime import datetime
from typing import List

class TranscriptionJob:

    def __init__(self,
                 video_filename: str,
                 video_storage_path  : str,
                 input_language: str, 
                 target_languages : List[str] , 
                 processed: bool = False):
        
        self.id = f"job_{uuid.uuid4().hex[:8]}"
        self.video_filename = video_filename
        self.video_storage_path = video_storage_path
        self.input_language = input_language
        self.target_languages = target_languages
        self.upload_date = datetime.now()
        self.processed = processed
    

    def __repr__(self):
        return (f"Video(id={self.id}, original_filename={self.video_filename}, "
                f"stored_path={self.video_storage_path}, input_language={self.input_language}, target_language={self.target_languages} "
                f"upload_date={self.upload_date}, processed={self.processed})")


