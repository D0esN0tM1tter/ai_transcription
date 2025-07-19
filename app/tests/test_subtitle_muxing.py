from app.services.translation_service import TranslationModel
from app.models.audio import Audio
from app.services.audio_service import AudioUtils
from app.services.transcription_service import ASRMOdel
from app.models.transcription_job import TranscriptionJob
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.models.transcription import Transcription
from app.services.ffmpeg_service import FfmpegUtils
from app.services.subtitle_formatter_service import SubtitleWriter
from typing import List


def test_muxing() : 

    repo = TranscriptionJobRepository()

    job = TranscriptionJob(
        video_filename="input_video.mp4" ,

        input_language="spanish" , 
        target_languages= ["arabic" , "english" , "french"], 
        video_storage_path="app/tests/test_data/videos/news_spanish.mp4") 
    
    repo.add_job(job)
    
    # create an audio object : 
    audio = Audio(
        job_id= job.id, 
        audio_filepath="app/tests/test_data/audios/audio_5e46b96b_job_fd9f49e4.wav" , 
        language="spanish"
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

    translated_transcriptions : List[Transcription] = translator.translate_transcription_to_multiple_languages(transcription) 

     # format and save the transcriptions :
    writer = SubtitleWriter() 

    writer.batch_save(transcription_list=translated_transcriptions , 
                      output_dir="app/tests/test_data/transcriptions")
    
    ffmpeg = FfmpegUtils(transcripton_job_repo=repo)


    job : TranscriptionJob = ffmpeg.mux_subtitles(
        transcriptions_list=translated_transcriptions , 
        output_dir="app/tests/test_data/videos"
    )
    

if __name__ == "__main__" :
    test_muxing()


    