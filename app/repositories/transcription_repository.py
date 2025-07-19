from app.models.transcription import Transcription
from app.repositories.base_repository import BaseRepository
from typing import List
import logging 

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class TranscriptionRepository(BaseRepository):

    _instance = None

    def __new__(cls, db_path="db.json"):
        if cls._instance is None:
            cls._instance = super(TranscriptionRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path="db.json"):
        if not hasattr(self, "_initialized"):
            super().__init__(db_path=db_path, tablename="transcriptions")
            self._initialized = True  


    def insert_transcription(self, transcription: Transcription) -> Transcription:
        self.insert(data=transcription._to_dict())
        logging.info(f"A transcription with id {transcription.id} has been inserted to the database.")
        return transcription


    def get_transcription(self, id: str) -> Transcription:
        
        data_dict =  self.get(
            key="transcription_id" , 
            value=id
        )

        if data_dict is None : 
            logger.info(f"transcription is transcription_id {id} does not exist in the database.")
            return None

        return Transcription._from_dict(data=data_dict)
    
    def update_transcription(self , id : str , new_transcription : Transcription) : 

        fields = new_transcription._to_dict()

        self.update(
            key="transcription_id" ,
            value=id , 
            fields=fields
        )

    def all_transcriptions(self) -> List[Transcription]: 
        pass
    
    def remove_transcription(self , id : str ) -> Transcription :
        pass
    

    def insert_many_transcriptions(self , transcriptions : List[Transcription]) : 

        for transcription in transcriptions : 
            self.insert_transcription(transcription)


