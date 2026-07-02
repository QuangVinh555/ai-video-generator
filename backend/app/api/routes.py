from fastapi import APIRouter, HTTPException
from app.schemas.video import ScriptRequest, AudioRequest, RenderRequest
from app.services.llm_service import generate_script_service
from app.services.audio_service import generate_audio_service
from app.services.image_service import search_images_service
from app.services.video_engine import render_video_service
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/api/generate-script")
async def generate_script(request: ScriptRequest):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="Gemini API Key is missing")
    try:
        return generate_script_service(request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate-audio")
async def generate_audio(request: AudioRequest):
    try:
        filename, filepath = await generate_audio_service(request.text, request.voice)
        return {"audio_url": f"http://127.0.0.1:8000/{filepath}", "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/search-images")
def search_images(query: str, limit: int = 5):
    try:
        images = search_images_service(query, limit)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.tasks import render_video_task
from app.celery_app import celery_app
from celery.result import AsyncResult

@router.post("/api/render-video")
def render_video(request: RenderRequest):
    try:
        # Pydantic objects convert to dicts for Celery serialization
        scenes_dict = [scene.dict() for scene in request.scenes]
        # Gọi Celery chạy ngầm
        task = render_video_task.delay(scenes_dict, request.bgmUrl)
        return {"task_id": task.id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "task_status": task_result.status,
    }
    
    if task_result.status == 'PROCESSING':
        # Get progress from meta if exists
        response["meta"] = task_result.info if task_result.info else {}
    elif task_result.status == 'SUCCESS':
        response["task_result"] = task_result.result
    elif task_result.status == 'FAILURE':
        response["task_result"] = str(task_result.info)
        
    return response
