from app.models.transcription import Transcription


class TranscriptionRepository:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriptionRepository, cls).__new__(cls)
            cls._instance.transcriptions = {} 
        return cls._instance

    def add_job(self, transcription: Transcription):
        self.transcriptions[transcription.id] = transcription

    def get_job(self, id: str):
        return self.transcriptions.get(id)
