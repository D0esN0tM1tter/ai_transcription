from app.models.transcription_job import TranscriptionJob


class TranscriptionJobRepository:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriptionJobRepository, cls).__new__(cls)
            cls._instance.jobs = {} 
        return cls._instance

    def add_job(self, job: TranscriptionJob):
        self.jobs[job.id] = job

    def get_job(self, id: str):
        return self.jobs.get(id)
