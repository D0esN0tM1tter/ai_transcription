from app.services.ffmpeg_service import FfmpegUtils 
from typing import Dict
from app.models.transcription_job import TranscriptionJob
import logging 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)


def test_audio_extraction() -> Dict : 

    logging.info("audio extraction test is starting ...")

    # create a transcription Job : 
    job = TranscriptionJob(
        video_filename="input_video.mp4" , 
        input_language="spanish" , 
        target_languages= ["arabic" , "french" , "spanish"], 
        video_storage_path="app/tests/test_data/videos/news_spanish.mp4")  
    
    logger.info(f"A Job object has been created : {job}")

    # Audio extraction with ffmpeg service : 
    extractor = FfmpegUtils(transcripton_job_repo=None) 
    
    extracted_audio = extractor.extract_audio(
        job=job , 
        output_dir="app/tests/test_data/audios" , 
    )

    print(f'extracted audio : {extracted_audio}')

 
if __name__ == "__main__" : 
    test_audio_extraction()
