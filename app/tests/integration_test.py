from app.services.audio_service import AudioUtils 
from app.services.ffmpeg_service import FfmpegUtils
from app.services.subtitle_formatter_service import SubtitleWriter
from app.services.transcription_service import  ASRMOdel 
from app.services.translation_service import TranslationModel
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.models.transcription_job import TranscriptionJob
from app.models.transcription import Transcription
from typing import List

def integration_test_separate() : 

    # video data : 
    video_data = {
        "input_filepath" : "app/tests/test_data/huberman.mp4" , 
        "output_filepath" : "app/tests/test_data/huberman.wav" , 
        "input_language"  : "english" ,
        "srt_filepath" :  "app/tests/test_data/huberman.srt"

    }

    # audio extraction : 
    ffmpeg_utils =  FfmpegUtils()
    
    audio_data = ffmpeg_utils.extract_audio(
        duration="00:00:10" , 
        input_file=video_data["input_filepath"] , 
        output_file=video_data["output_filepath"] , 
        input_language=video_data["input_language"]
    )
    
    # resampling : 
    audio_utils = AudioUtils(audio_data)
    audio_utils.resample()

    # tramscription : 
    asr = ASRMOdel() 
    transcription = asr.transcribe(audio_utils.array
                                   ,audio_utils.language,
                                    translate_to_eng=False) 
    

    # translation : 
    translator =  TranslationModel()
    
    translated_chunks  = [

        {"timestamp" : chunk["timestamp"] , 
         "text" : translator.translate(chunk["text"] , src_lang=audio_utils.language , trgt_lang="arabic")} 
         for chunk in transcription
    ]

    # formatting :
    writer = SubtitleWriter(translated_chunks) 
    writer.save(path = video_data["srt_filepath"])


def integration_test() :
    
    repo = TranscriptionJobRepository()

    job = TranscriptionJob(
        video_filename="input_video.mp4" , 
        input_language="french" , 
        target_languages= ["arabic" , "english"], 
        video_storage_path="app/tests/test_data/videos/news_french.mp4") 
    
    repo.add_job(job)

     # Audio extraction with ffmpeg service : 
    ffmpeg = FfmpegUtils(repo) 
    
    extracted_audio = ffmpeg.extract_audio(
        job=job , 
        output_dir="app/tests/test_data/audios" , 
    )
    
    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio=extracted_audio)

    # create the model object and run inference : 
    asr = ASRMOdel(model_id="openai/whisper-tiny") 

    transcription = asr.transcribe(
        audio=audio_utils
    )

    # translate the the transcription : 
    translator = TranslationModel(repo) 

    translated_transcriptions = translator.translate_transcription_to_multiple_languages(transcription) 


    # format and save the transcriptions :
    writer = SubtitleWriter() 

    transcriptions : List[Transcription] = writer.batch_save(transcriptions_list=translated_transcriptions , 
                      output_dir="app/tests/test_data/transcriptions") 
    

    ffmpeg.mux_subtitles(
        transcriptions_list=transcriptions , 
        output_dir="app/tests/transcriptions"
    )

if __name__ == "__main__" : 
    integration_test()

