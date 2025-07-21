import logging
from fastapi import APIRouter, HTTPException , UploadFile, File , Form
from fastapi.responses import FileResponse
from app.api.schemas.job_response import JobResponse
from app.models.transcription_job import TranscriptionJob
from app.services.integration_service import IntegrationService
from typing import List
import uuid
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize router
router = APIRouter(prefix="/pipeline")

# Initialize integration service
try:

    integration_service = IntegrationService(
        db_path="app/tests/test_data/database/test_db.json",

        dirs={
            "audios_dir": "app/tests/test_data/audios",

            "processed_videos_dir": "app/tests/test_data/videos/processed",

            "srt_files_dir": "app/tests/test_data/transcriptions"
        }
    )

    logger.info("IntegrationService initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize IntegrationService: {e}")
    raise e


@router.post("/process", response_model=JobResponse)
async def process(
    video: UploadFile = File(...),
    input_language: str = Form(...),
    target_languages: List[str] = Form(...)
):
    try:
        # Save uploaded video with unique name
        video_id = uuid.uuid4().hex[:8]
        file_extension = Path(video.filename).suffix
        stored_filename = f'uploaded_video_{video_id}{file_extension}'
        stored_path = Path('app/tests/test_data/videos/uploads') / stored_filename
        stored_path.parent.mkdir(parents=True, exist_ok=True)

        with stored_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Create and process the job
        job = TranscriptionJob(
            video_storage_path=str(stored_path),
            input_language=input_language,
            target_languages=target_languages,
            processed=False
        )

        processed_job = integration_service.process(job=job)

        return JobResponse(
            job_id=processed_job.id,
            processed_video_url=processed_job.processed_video_path,
            processed=processed_job.processed , 
            target_languages=processed_job.target_languages , 
            input_language=processed_job.input_language
        )

    except Exception as e:
        logger.error(f"Error processing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/download_video/{job_id}") 
async def download_video(job_id : str) :

    job : TranscriptionJob = integration_service.transcription_job_repo.get_job(job_id) 

    if not job or not job.processed_video_path : 
        raise HTTPException(status_code=404 , detail="Processed video was not found.") 

    video_path = Path(job.processed_video_path) 

    if not video_path.exists() : 
        raise HTTPException(status_code=404 , detail="Video file was not found on the server.")
    
    return FileResponse(
        path=str(video_path) , 
        media_type="video/mkv" , 
        filename=video_path.name
    )


@router.get("download_srt_files/{job_id}") 
async def download_srt_files(job_id : str) : 
    pass