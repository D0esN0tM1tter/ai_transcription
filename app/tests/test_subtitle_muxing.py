from app.services.ffmpeg_service import FfmpegUtils



def test_subtitles_muxing() :

    video_path = "app/tests/test_data/videos/huberman.mp4" 

    srt_paths = {

        "en" : "app/tests/test_data/transcriptions/transcription_da1520d1_job_5cf14bcd_english.srt" , 
        "ar" : "app/tests/test_data/transcriptions/transcription_6fa5931f_job_5cf14bcd_arabic.srt" , 
        "fr" : "app/tests/test_data/transcriptions/transcription_280dde29_job_5cf14bcd_french.srt"

    }

    utils = FfmpegUtils() 

    utils.mux_subtitles(
        video_path=video_path , 
        srt_paths=srt_paths , 
        output_path="app/tests/test_data/videos/huberman_subs.mkv"
    )



if __name__ == "__main__" : 
    test_subtitles_muxing()