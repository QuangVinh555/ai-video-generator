from app.celery_app import celery_app
from app.services.video_engine import render_video_service
from app.schemas.video import SceneData

@celery_app.task(bind=True, name="render_video_task")
def render_video_task(self, scenes_data_dict, bgm_url):
    """
    Background task to render video using MoviePy.
    """
    self.update_state(state='PROCESSING', meta={'progress': 10, 'message': 'Đang chuẩn bị tài nguyên...'})
    
    try:
        # Convert list of dicts back to list of SceneData Pydantic objects
        scenes_objs = [SceneData(**s) for s in scenes_data_dict]
        
        self.update_state(state='PROCESSING', meta={'progress': 30, 'message': 'Đang tạo video (hiệu ứng Ken Burns & Phụ đề)...'})
        
        # Render video
        filename, filepath = render_video_service(scenes_objs, bgm_url)
        
        self.update_state(state='PROCESSING', meta={'progress': 100, 'message': 'Hoàn tất!'})
        
        return {"status": "completed", "video_url": f"http://127.0.0.1:8000/{filepath}"}
    except Exception as e:
        # If error occurs, update state to FAILED
        # Celery natively supports FAILED state if exception is raised, 
        # but we can pass meta info if needed.
        raise Exception(f"Video Render Error: {str(e)}")
