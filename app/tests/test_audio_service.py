from app.services.audio_service import AudioUtils
from typing import Dict
from app.models.audio import Audio



def _print_dictionary(d : Dict) : 

    for k , v in list(d.items()) : 
        print(f"\n{k} : {v}")



def test_visuals() : 
    # create an audio object : 
    audio = Audio(
        job_id="vid_id" , 
        audio_filepath="app/tests/test_data/audios/audio_4eeb4e5d_job_62027c72.wav" , 
        language="english"
    )

    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio)

    audio_utils.visualize_waveform("app/tests/test_data/figures")
    audio_utils.visualize_mel_diagram("app/tests/test_data/figures")
    audio_utils.visualize_freq_spectrum("app/tests/test_data/figures")



def test_audio_utils() : 

    # create an audio object : 
    audio = Audio(
        job_id="vid_id" , 
        audio_filepath="app/tests/test_data/audios/audio_4eeb4e5d_job_62027c72.wav" , 
        language="english"
    )

    # encapsulate it in audio utils : 
    audio_utils = AudioUtils(audio)
    print(f"------- original audio ---------") 
    _print_dictionary(audio_utils.audio_stats())

    # resample the audio : 
    audio_utils.resample(target_sr=48000) 

    print(f"------- resampled audio ---------") 
    _print_dictionary(audio_utils.audio_stats())

    



if __name__ == "__main__" : 

    test_visuals()