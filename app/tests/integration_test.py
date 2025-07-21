from app.services.audio_service import AudioUtils 
from app.services.ffmpeg_service import FfmpegUtils
from app.services.subtitle_formatter_service import SubtitleWriter
from app.services.transcription_service import  ASRMOdel 
from app.services.translation_service import TranslationModel
from app.services.integration_service import IntegrationService
from app.repositories.transcription_job_repository import TranscriptionJobRepository 
from app.repositories.transcription_repository import TranscriptionRepository
from app.models.transcription import Transcription 
from app.models.transcription_job import TranscriptionJob
from app.models.audio import Audio


def integration_test() : 

    job_repo = TranscriptionJobRepository(
        db_path="app/tests/test_data/database/test_db.json" , 
    )

    transcription_repo = TranscriptionRepository(
        db_path="app/tests/test_data/database/test_db.json"
    )

    # create a transcription Job : 
    job = TranscriptionJob(
        input_language="french" , 
        target_languages= ["arabic" , "french" , "english"], 
        video_storage_path="app/tests/test_data/videos/news_french.mp4") 
    
    ffmpeg = FfmpegUtils(transcripton_job_repo= job_repo) 
    audio_utils = AudioUtils() 
    asr_model = ASRMOdel()
    translator = TranslationModel(job_repo=job_repo , transcription_repo=transcription_repo)
    writer =  SubtitleWriter(transcription_repository=transcription_repo)  


    
    integration : IntegrationService = IntegrationService(
        ffmpeg=ffmpeg, 
        audio_utils=audio_utils , 
        asr_model=asr_model, 
        translator=translator , 
        writer = writer , 
        audios_dir="app/tests/test_data/audios" , 
        srt_dir="app/tests/test_data/transcriptions" , 
        processed_videos_dir="app/tests/test_data/videos/processed"

    )

    integration.process(job)


if __name__ == "__main__" : 
    integration_test()