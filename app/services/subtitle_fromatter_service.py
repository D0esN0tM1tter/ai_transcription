from typing import List, Dict

class SubtitleWriter:
    def __init__(self):
        return


    @staticmethod
    def _format_timestamp(seconds: float) -> str:

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def save_as_srt(self, chunks: List[Dict]):
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks, start=1):
                start_ts = self._format_timestamp(chunk['start'])
                end_ts = self._format_timestamp(chunk['end'])
                f.write(f"{i}\n")
                f.write(f"{start_ts} --> {end_ts}\n")
                f.write(f"{chunk['text'].strip()}\n\n")
