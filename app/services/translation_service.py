from transformers import MarianMTModel, MarianTokenizer 
from typing import Tuple
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
from typing import Dict , List
import logging
from app.repositories.transcription_job_repository import TranscriptionJobRepository
import traceback
import torch
import gc

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class TranslationModel : 

    def __init__(self , job_repo : TranscriptionJobRepository):
        try:
            if not job_repo:
                raise ValueError("TranscriptionJobRepository cannot be None")
                
            self.job_repo = job_repo
            self.models = {}
            
            logger.info("TranslationModel initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TranslationModel: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"TranslationModel initialization failed: {e}") from e

    def __Load_model(self , src_lang : str , trgt_lang : str) -> Tuple[MarianTokenizer , MarianMTModel] :  

        # Validate input parameters
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")

        try:
            # format input language : 
            src_lang = self.__language_lookup(src_lang) 
            trgt_lang = self.__language_lookup(trgt_lang)

            if not src_lang:
                raise ValueError(f"Unsupported source language: {src_lang}")
            if not trgt_lang:
                raise ValueError(f"Unsupported target language: {trgt_lang}")

            logger.info("Initializing / Looking-up translation model %s to %s" , src_lang , trgt_lang)

            pair_key = f"{src_lang}-{trgt_lang}" 

            if pair_key not in self.models : 
                try:
                    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{trgt_lang}"
                    
                    logger.info(f"Loading tokenizer for model: {model_name}")
                    tokenizer = MarianTokenizer.from_pretrained(model_name)
                    
                    logger.info(f"Loading model: {model_name}")
                    model = MarianMTModel.from_pretrained(model_name)
                    
                    self.models[pair_key] = (tokenizer , model)
                    logger.info(f"Successfully loaded model pair: {pair_key}")
                    
                except Exception as e:
                    logger.error(f"Failed to load model {model_name}: {e}")
                    # Check if it's a model availability issue
                    if "404" in str(e) or "Repository not found" in str(e):
                        raise ValueError(f"Translation model not available for language pair {src_lang}-{trgt_lang}") from e
                    elif "Out of memory" in str(e) or isinstance(e, torch.cuda.OutOfMemoryError):
                        # Try to free memory and retry
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        raise RuntimeError(f"Out of memory loading model for {src_lang}-{trgt_lang}") from e
                    else:
                        raise RuntimeError(f"Failed to load translation model for {src_lang}-{trgt_lang}: {e}") from e
            
            return self.models[pair_key]
            
        except Exception as e:
            logger.error(f"Error in __Load_model: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def translate_transcription_to_multiple_languages(self , transcription : Transcription) -> List[Transcription] : 
        
        # Validate input
        if not transcription:
            raise ValueError("Transcription cannot be None")
        if not hasattr(transcription, 'job_id') or not transcription.job_id:
            raise ValueError("Transcription must have a valid job_id")
        if not hasattr(transcription, 'input_language') or not transcription.input_language:
            raise ValueError("Transcription must have a valid input_language")
        if not hasattr(transcription, 'original_text'):
            raise ValueError("Transcription must have original_text attribute")
        if not hasattr(transcription, 'original_chunks'):
            raise ValueError("Transcription must have original_chunks attribute")
            
        logger.info("Translation to multiple languages is starting ...")
        
        try:
            # extract the parent job :
            try:
                job : TranscriptionJob = self.job_repo.get_job(transcription.job_id)
                if not job:
                    raise ValueError(f"Job with ID {transcription.job_id} not found")
            except Exception as e:
                logger.error(f"Failed to retrieve job {transcription.job_id}: {e}")
                raise RuntimeError(f"Cannot retrieve transcription job: {e}") from e

            # extract source language and target languages : 
            src_lang = transcription.input_language 
            
            if not hasattr(job, 'target_languages') or not job.target_languages:
                logger.warning(f"No target languages specified for job {transcription.job_id}")
                trgt_languages = []
            else:
                trgt_languages = job.target_languages
                if not isinstance(trgt_languages, list):
                    raise ValueError("Target languages must be a list")

            transcriptions_list : List[Transcription] = []

            # handle the original transcription first :
            try:
                transcription.translated_text = transcription.original_text
                transcription.translated_chunks = transcription.original_chunks if transcription.original_chunks else []
                transcription.target_language = transcription.input_language

                transcriptions_list.append(transcription)
                logger.info(f"Added original transcription in {src_lang}")
                
            except Exception as e:
                logger.error(f"Error setting up original transcription: {e}")
                raise RuntimeError(f"Failed to setup original transcription: {e}") from e

            # Process each target language
            for language in trgt_languages :
                try:
                    if not language or not isinstance(language, str):
                        logger.warning(f"Invalid target language: {language}, skipping")
                        continue

                    if language.lower() == src_lang.lower() :
                        logger.info(f"Skipping translation to same language: {language}")
                        continue

                    logger.info(f"Translating from {src_lang} to {language}")

                    # Validate original text before translation
                    if not transcription.original_text:
                        logger.warning(f"No original text to translate for language {language}")
                        translated_text = ""
                    else:
                        translated_text = self._translate_text(transcription.original_text, src_lang, language)

                    # Validate and translate chunks
                    if not transcription.original_chunks:
                        logger.warning(f"No original chunks to translate for language {language}")
                        translated_chunks = []
                    else:
                        translated_chunks = self._translate_chunks(transcription.original_chunks, src_lang, language)

                    translated_transcription = Transcription(
                        original_text=transcription.original_text, 
                        original_chunks=transcription.original_chunks,
                        tr_text=translated_text, 
                        tr_chunks=translated_chunks, 
                        job_id=transcription.job_id, 
                        input_language=src_lang, 
                        target_language=language, 
                        srt_filepath=transcription.srt_filepath, 
                    )

                    transcriptions_list.append(translated_transcription)
                    logger.info(f"Successfully translated to {language}")
                    
                except Exception as e:
                    logger.error(f"Failed to translate to {language}: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Continue with other languages instead of failing completely
                    continue

            logger.info(f"Translation process has finished. Generated {len(transcriptions_list)} transcriptions.")
            return transcriptions_list
            
        except Exception as e:
            logger.error(f"Error in translate_transcription_to_multiple_languages: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _translate_text(self, text : str, src_lang : str, trgt_lang : str) -> str: 
        
        # Validate inputs
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for translation: {text}")
            return ""
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")
            
        # Skip translation if text is empty or whitespace only
        if not text.strip():
            logger.warning("Empty or whitespace-only text provided for translation")
            return ""
            
        try:
            logger.info("Translating input text from %s to %s" , src_lang , trgt_lang)
            
            tokenizer, model = self.__Load_model(src_lang, trgt_lang)
            
            try:
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            except Exception as e:
                logger.error(f"Error tokenizing text: {e}")
                raise RuntimeError(f"Tokenization failed: {e}") from e
            
            try:
                with torch.no_grad():  # Save memory during inference
                    outputs = model.generate(**inputs)
            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"CUDA out of memory during translation: {e}")
                # Try to free memory
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                raise RuntimeError(f"Translation failed due to memory constraints: {e}") from e
            except Exception as e:
                logger.error(f"Error during model generation: {e}")
                raise RuntimeError(f"Translation generation failed: {e}") from e
            
            try:
                translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                return translated_text if translated_text else ""
            except Exception as e:
                logger.error(f"Error decoding translation output: {e}")
                raise RuntimeError(f"Translation decoding failed: {e}") from e
                
        except Exception as e:
            logger.error(f"Error in _translate_text: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _translate_chunks(self, chunks : List, src_lang : str, trgt_lang : str) -> List :

        # Validate inputs
        if not chunks:
            logger.warning("No chunks provided for translation")
            return []
        if not isinstance(chunks, list):
            raise ValueError("Chunks must be a list")
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")

        try:
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                try:
                    # Validate chunk structure
                    if not isinstance(chunk, dict):
                        logger.warning(f"Invalid chunk format at index {i}: {chunk}")
                        continue
                    
                    if "timestamp" not in chunk:
                        logger.warning(f"Missing timestamp in chunk at index {i}")
                        continue
                        
                    if "text" not in chunk:
                        logger.warning(f"Missing text in chunk at index {i}")
                        continue
                    
                    chunk_text = chunk["text"]
                    if not chunk_text or not isinstance(chunk_text, str):
                        logger.warning(f"Invalid text in chunk at index {i}: {chunk_text}")
                        translated_text = ""
                    else:
                        translated_text = self._translate_text(chunk_text, src_lang, trgt_lang)
                    
                    translated_chunk = {
                        "timestamp": chunk["timestamp"],
                        "text": translated_text
                    }
                    
                    translated_chunks.append(translated_chunk)
                    
                except Exception as e:
                    logger.error(f"Error translating chunk at index {i}: {e}")
                    # Continue with next chunk instead of failing completely
                    continue
            
            logger.info(f"Successfully translated {len(translated_chunks)} out of {len(chunks)} chunks")
            return translated_chunks
            
        except Exception as e:
            logger.error(f"Error in _translate_chunks: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def __language_lookup(self, language : str) -> str: 
        
        if not language or not isinstance(language, str):
            logger.warning(f"Invalid language for lookup: {language}")
            return ""
        
        try:
            lang_map = {
                "english" : "en" , 
                "french" : "fr" , 
                "arabic" : "ar" , 
                "spanish" : "es"
            }

            result = lang_map.get(language.lower(), "")
            
            if not result:
                logger.warning(f"Unsupported language: {language}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in language lookup for '{language}': {e}")
            return ""
    
    def clear_models_cache(self):
        """Clear loaded models from memory"""
        try:
            logger.info("Clearing translation models cache")
            
            for pair_key in list(self.models.keys()):
                try:
                    tokenizer, model = self.models[pair_key]
                    del tokenizer
                    del model
                    del self.models[pair_key]
                except Exception as e:
                    logger.warning(f"Error clearing model {pair_key}: {e}")
            
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            logger.info("Models cache cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing models cache: {e}")
            # Don't raise - cache clearing should be robust