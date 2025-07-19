from app.services.translation_service import TranslationModel
from app.models.audio import Audio
from app.services.audio_service import AudioUtils
from app.services.transcription_service import ASRMOdel
from app.models.transcription_job import TranscriptionJob
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.repositories.transcription_repository import TranscriptionRepository
from app.services.ffmpeg_service import FfmpegUtils

from app.models.transcription import Transcription
from typing import List


def test_translation_model() : 

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
    
    # Audio extraction with ffmpeg service : 
    extractor = FfmpegUtils(transcripton_job_repo=job_repo) 
    
    extracted_audio = extractor.extract_audio(
        job=job , 
        output_dir="app/tests/test_data/audios" , 
    )

    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio=extracted_audio)

    # create the model object and run inference : 
    asr = ASRMOdel(model_id="openai/whisper-small" , transcription_repo=transcription_repo) 

    transcription = asr.transcribe(
        audio=audio_utils

    )

    # translate the the transcription : 
    translator = TranslationModel(job_repo=job_repo , transcription_repo=transcription_repo) 

    translated_transcriptions : List[Transcription] = translator.translate_transcription_to_multiple_languages(transcription) 



if __name__ == "__main__" :
    test_translation_model()


    