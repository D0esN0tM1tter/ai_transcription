from transformers import MarianMTModel, MarianTokenizer 
from typing import Tuple
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
from typing import Dict , List
import logging
from app.repositories.transcription_job_repository import TranscriptionJobRepository

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class TranslationModel : 

    def __init__(self , job_repo : TranscriptionJobRepository):

        self.job_repo = job_repo
        self.models = {}

    def __Load_model(self , src_lang : str , trgt_lang : str) -> Tuple[MarianTokenizer , MarianMTModel] :  

        # format  input language : 
        src_lang = self.__language_lookup(src_lang) 
        trgt_lang = self.__language_lookup(trgt_lang)

        logger.info("Initializing / Looking-up translation model %s to %s" , src_lang , trgt_lang)

        pair_key = f"{src_lang}-{trgt_lang}" 

        if pair_key not in self.models : 

            model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{trgt_lang}" 
            tokenizer = MarianTokenizer.from_pretrained(model_name) 
            model = MarianMTModel.from_pretrained(model_name) 
            self.models[pair_key] = (tokenizer , model) 
        
        return self.models[pair_key] 
    
    def translate_transcription_to_multiple_languages(self , transcription : Transcription) -> List[Transcription] : 
        logger.info("Translation to multiple languages is starting ...")
        # extract  the parent job :
        job : TranscriptionJob = self.job_repo.get_job(transcription.job_id)

        # extract source language and target languages : 
        src_lang = transcription.input_language 
        trgt_languages = job.target_languages

        transcriptions_list : List[Transcription] = []

        # handle the original transcription first :
        transcription.translated_text = transcription.original_text
        transcription.translated_chunks = transcription.original_chunks 
        transcription.target_language = transcription.input_language

        transcriptions_list.append(transcription)


        for language in trgt_languages :

            if language.lower() == src_lang.lower() :
                continue

            translated_text = self._translate_text(transcription.original_text , src_lang , language)
            translated_chunks = self._translate_chunks(transcription.original_chunks , src_lang , language)

            translated_transcription = Transcription(

                original_text=transcription.original_text , 
                original_chunks=transcription.original_chunks ,
                tr_text = translated_text , 
                tr_chunks=translated_chunks, 
                job_id=transcription.job_id, 
                input_language=src_lang , 
                target_language=language, 
                srt_filepath=transcription.srt_filepath , 

            )

            transcriptions_list.append(translated_transcription)
        logger.info("Translation process has finished.")

        return transcriptions_list

    def _translate_text( self , text : str  , src_lang : str ,  trgt_lang) : 
        logger.info("Translating input text from %s to %s" , src_lang , trgt_lang)
        tokenizer , model = self.__Load_model(src_lang , trgt_lang) 
        inputs = tokenizer(text , return_tensors = "pt" , padding = True , truncation = True) 
        outputs = model.generate(**inputs) 
        return tokenizer.decode(outputs[0] , skip_special_tokens = True)

    def _translate_chunks(self , chunks : List , src_lang : str  , trgt_lang : str)->List :

        translated_chunks = [
            {"timestamp" : chunk["timestamp"] , 
             "text" : self._translate_text(chunk["text"] , src_lang , trgt_lang)}

             for chunk in chunks
        ]
        return translated_chunks
    
    def __language_lookup(self , language : str) : 

        lang_map = {
            "english" : "en" , 
            "french" : "fr" , 
            "arabic" : "ar" , 
        }

        return lang_map.get(language , "")
    
