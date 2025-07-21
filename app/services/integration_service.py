from app.services.audio_service import AudioUtils 
from app.services.ffmpeg_service import FfmpegUtils
from app.services.subtitle_formatter_service import SubtitleWriter
from app.services.transcription_service import  ASRMOdel 
from app.services.translation_service import TranslationModel
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.repositories.transcription_repository import TranscriptionRepository
from app.models.transcription import Transcription 
from app.models.transcription_job import TranscriptionJob
from app.models.audio import Audio
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)



class IntegrationService : 

    def __init__(self, db_path : str , dirs : Dict[str , str]):

        # repositories :
        self.transcription_job_repo = TranscriptionJobRepository(db_path=db_path)
        self.transcription_repo = TranscriptionRepository(db_path=db_path)

        # services 
        self.ffmpeg = FfmpegUtils(transcripton_job_repo=self.transcription_job_repo)  

        self.audio_utils = AudioUtils() 

        self.asr_model = ASRMOdel() 

        self.translator = TranslationModel(
            job_repo=self.transcription_job_repo , 
            transcription_repo=self.transcription_repo
        )

        self.writer = SubtitleWriter(
            transcription_repository=self.transcription_repo
        )

        self.dirs = dirs

    

    def process(self , job : TranscriptionJob) -> TranscriptionJob: 

        # audio extraction : 
        extracted_audio : Audio = self.ffmpeg.extract_audio(
            job=job , 
            output_dir=self.dirs["audios_dir"]
        )

        # preprocessing (if needed ) 
        extracted_audio = self.audio_utils.load_resample_audio(audio=extracted_audio)

        # speech recognition : 
        transcription : Transcription = self.asr_model.transcribe(
            audio=extracted_audio , 
            translate_to_eng=False
        )

        # translation : 
        transcriptions : List[Transcription] = self.translator.translate_transcription_to_multiple_languages(transcription=transcription)

        # subtitle formatting : 
        transcriptions : List[Transcription] = self.writer.batch_save(
            transcription_list=transcriptions , 
            output_dir=self.dirs["srt_files_dir"])

        # subtitle muxing : 
        job : TranscriptionJob = self.ffmpeg.mux_subtitles(
            transcriptions_list=transcriptions , 
            output_dir=self.dirs["processed_videos_dir"]
        )

        return job


        
        

        