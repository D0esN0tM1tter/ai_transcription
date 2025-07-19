from app.services.subtitle_formatter_service import SubtitleWriter
from app.models.audio import Audio
from app.services.transcription_service import ASRMOdel
from app.services.audio_service import AudioUtils
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.models.transcription_job import TranscriptionJob
from app.services.translation_service import TranslationModel



def test_subtitle_formatting() : 

    repo = TranscriptionJobRepository()

    job = TranscriptionJob(
        video_filename="input_video.mp4" , 
        input_language="french" , 
        target_languages= ["arabic" , "english"], 
        video_storage_path="app/tests/test_data/videos/news_french.mp4") 
    
    repo.add_job(job)
    

    # create an audio object : 
    audio = Audio(
        job_id= job.id, 
        audio_filepath="app/tests/test_data/audios/audio_9dca7ccc_job_f6c1f86c.wav" , 
        language="french"
    )

    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio=audio)

    # create the model object and run inference : 
    asr = ASRMOdel(model_id="openai/whisper-small") 

    transcription = asr.transcribe(
        audio=audio_utils
    )

    # translate the the transcription : 
    translator = TranslationModel(repo) 

    transcriptions_list = translator.translate_transcription_to_multiple_languages(transcription) 


    # format and save the transcriptions :
    writer = SubtitleWriter() 

    writer.batch_save(transcription_list=transcriptions_list , 
                      output_dir="app/tests/test_data/transcriptions")


if __name__ == "__main__" : 
    test_subtitle_formatting()