from app.services.transcription_service import ASRMOdel
from app.services.audio_service import AudioUtils
from app.models.audio import Audio


def test_asr_model() : 

     # create an audio object : 
    audio = Audio(
        job_id="vid_id" , 
        audio_filepath="app/tests/test_data/audios/audio_4eeb4e5d_job_62027c72.wav" , 
        language="french"
    )

    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio=audio)

    # create the model object and run inference : 
    asr = ASRMOdel(model_id="openai/whisper-small") 
    trannscription = asr.transcribe(
    )

    
    print("\n ------------ Transcription -------------\n") 
    print(trannscription.__repr__())
    print(trannscription.original_text) 
    print(trannscription.original_chunks)



if __name__ == "__main__" : 
    test_asr_model()

   


