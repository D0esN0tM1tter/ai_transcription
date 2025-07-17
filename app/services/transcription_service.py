import torch
import numpy as np
import gc
import librosa
import matplotlib.pyplot as plt
from typing import Dict
from app.models.transcription import Transcription
from app.services.audio_service import AudioUtils

from transformers import (

    AutoModelForSpeechSeq2Seq,

    AutoProcessor,

    AutomaticSpeechRecognitionPipeline,

    pipeline)

from typing import Optional

import logging

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class ASRMOdel : 

    def __init__(self , model_id : str = "openai/whisper-small") :

        self.model_id = model_id 
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.pipeline : Optional[AutomaticSpeechRecognitionPipeline] = None
    
    def load(self) -> AutomaticSpeechRecognitionPipeline: 
        
        try : 
            logger.info("Loading processor for model : %s" , self.model_id)
            processor = AutoProcessor.from_pretrained(self.model_id) 

            logger.info("Loading model to device : %s" , self.device)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_id , 
                torch_dtype= self.dtype ,  
                low_cpu_mem_usage = True,  
                use_safetensors = True
            ).to(self.device) 


            device_idx = 0 if self.device=="cuda" else -1 

            logger.info("Loading pipeline for model : %s" , self.model_id) 


            self.pipeline = pipeline (
                task = "automatic-speech-recognition" ,
                model=model, 
                tokenizer=processor.tokenizer, 
                feature_extractor=processor.feature_extractor, 
                device=device_idx
            )

            logger.info("ASR pipeline initilized successfully")
            return self.pipeline
        
        except Exception as e : 
            logger.error("failed to load model or pipeline : %s" , e)
            raise e

    def unload(self):  
        logger.info("Unloading ASR model and freeing memory") 

        try: 
            if self.pipeline: 
                del self.pipeline
                self.pipeline = None

            gc.collect() 

            if torch.cuda.is_available(): 

                torch.cuda.empty_cache() 

            logger.info("Resources released successfully") 

        except Exception as e: 
            logger.error("Error while unloading the model: %s", e)

    def transcribe(self , audio : AudioUtils, translate_to_eng : bool = False )-> Transcription : 

        # loading the model to the cpu first
        self.load()         

        try : 
            logger.info("transcribing audio input audio with language : %s" , audio.language)

            kwargs = {"language" : audio.language } 

            if translate_to_eng : 
                kwargs["task"] = "translate"

            transcription_content = self.pipeline(
                audio.array ,
                return_timestamps = True ,
                generate_kwargs = kwargs ) 
            
            self.unload()

            # creating an id for the transcription :
            transcription =  Transcription(
                original_text=transcription_content["text"] ,
                original_chunks=transcription_content["chunks"] , 
                input_language=audio.language, 
                job_id = audio.job_id)
            
            return transcription
        
        except Exception as e : 
            self.unload()
            logger.error("Error while transcribing the audio : %s" , e)
            raise e 
    
    def visualize_features(self , output_path ,audio : np.ndarray) :  

        if not self.pipeline : 
            raise ValueError("pipeline not initialized. call load() method") 

        processor = self.pipeline.feature_extractor
        
        array , sr = audio , 16000 

        inputs = processor(array , sr  , return_tensor = "pt")

        features = inputs.input_features[0]

        plt.figure(figsize=(12, 4))

        librosa.display.specshow(features, sr=sr, x_axis='time', y_axis='mel')

        plt.title("Log-Mel Spectrogram (Input Features)")
        plt.colorbar(format="%+2.0f dB")
        plt.tight_layout()
        plt.savefig(output_path)  
        plt.close()
