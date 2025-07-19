from app.models.transcription_job import TranscriptionJob
from app.repositories.base_repository import BaseRepository 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptionJobRepository(BaseRepository):

    _instance = None

    def __new__(cls, db_path="db.json"):
        if cls._instance is None:
            cls._instance = super(TranscriptionJobRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path="db.json"):
        if not hasattr(self, "_initialized"):
            super().__init__(db_path=db_path, tablename="transcription_jobs")
            self.jobs = {}
            self._initialized = True  

    def insert_job(self, job: TranscriptionJob) -> TranscriptionJob:
        self.insert(data=job._to_dict())
        logging.info(f"A transcription job with id {job.id} has been inserted to the database.")
        return job


    def get_job(self, id: str) -> TranscriptionJob :
        data_dict =  self.get(key="job_id" , value=id)

        if data_dict is None : 
            return None
        
        return TranscriptionJob._from_dict(data_dict) 

    def update_job(self , id , new_job : TranscriptionJob) : 

        fields = new_job._to_dict() 

        self.update(
            key="job_id" , 
            value=id, 
            fields= fields
        )

        return new_job
    
    def all_jobs(self) : 
        pass

    def remove_job(self , id : str) : 
       pass

