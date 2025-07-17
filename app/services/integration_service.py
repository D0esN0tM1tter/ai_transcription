from app.services.audio_service import AudioUtils 
from app.services.ffmpeg_service import FfmpegUtils
from app.services.subtitle_formatter_service import SubtitleWriter
from app.services.transcription_service import  ASRMOdel 
from app.services.translation_service import TranslationModel
from typing import Dict
from app.models.transcription_job import Video
import logging

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class IntegrationService() : 

    def __init__(self ):

        logger.info("Integration service is starting ...")
        self.asr = ASRMOdel() 
        self.extractor = FfmpegUtils() 
        self.translator = TranslationModel() 
        self.writer = SubtitleWriter()
        
        

    def transcribe(
            self,
            video : Video,
            output_audio_path : str ,
            output_tr_path : str , 
            input_language : str , 
            target_language : str) -> Dict : 


        extracted_audio = self.extractor.extract_audio(
            video=video,
            output_file=output_audio_path , 
            target_language = target_language
        )

        # resample 
        audio = AudioUtils(sample=extracted_audio)
        audio.resample()

        # transcribe 
        original_transcription = self.asr.transcribe(
            audio_array=audio.array , 
            input_language=input_language
        )

        # translate :      
        if not input_language.lower() == target_language.lower() : 

            translated = [

                {"timestamp" : chunk["timestamp"] , 
                "text" : self.translator.translate(chunk["text"], input_language , target_language )}

                for chunk in original_transcription.chunks_content
            ]

            # save transcriptions as (srt , vtt , txt) format
            self.writer.save(chunks=translated , output_path=output_tr_path + f"/{target_language}")
        

        # save the original transcription as (srt , vtt , txt) format : 
        self.writer.save(chunks=transcription , output_path=output_tr_path)
        
        

        
        

        