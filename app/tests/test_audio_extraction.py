from app.services.ffmpeg_service import FfmpegUtils 
from typing import Dict
from app.models.transcription_job import TranscriptionJob
from app.repositories.transcription_job_repository import TranscriptionJobRepository
import logging 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)


def test_audio_extraction() -> Dict : 

    logging.info("audio extraction test is starting ...")

    job_repo = TranscriptionJobRepository(
        db_path="app/tests/test_db.json" , 
    )

    # create a transcription Job : 
    job = TranscriptionJob(
        input_language="french" , 
        target_languages= ["arabic" , "french" , "spanish"], 
        video_storage_path="app/tests/test_data/videos/news_french.mp4")  
    
    logger.info(f"A Job object has been created : {job}")



    # Audio extraction with ffmpeg service : 
    extractor = FfmpegUtils(transcripton_job_repo=job_repo) 
    
    extracted_audio = extractor.extract_audio(
        job=job , 
        output_dir="app/tests/test_data/audios" , 
    )

    print(f'extracted audio : {extracted_audio}')

 
if __name__ == "__main__" : 
    test_audio_extraction()
