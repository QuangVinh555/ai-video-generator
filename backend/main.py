from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import json
import time
import uuid
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import edge_tts
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Video Generator API")

# Setup CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the assets directory so frontend can access generated audio/images/videos
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

class ScriptRequest(BaseModel):
    topic: str

class AudioRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"

class SceneData(BaseModel):
    audioUrl: str
    selectedImage: str

class RenderRequest(BaseModel):
    title: str
    scenes: List[SceneData]

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Video Generator API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/generate-script")
async def generate_script(request: ScriptRequest):
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key is missing in .env")

    prompt = f"""
    Bạn là một chuyên gia viết kịch bản video ngắn (TikTok, YouTube Shorts) về chủ đề Lịch sử, Địa lý.
    Hãy viết một kịch bản hấp dẫn, thời lượng khoảng 45-60 giây về chủ đề: "{request.topic}".
    Chia kịch bản thành các phân cảnh ngắn (tối đa 5-6 cảnh).
    
    YÊU CẦU ĐỊNH DẠNG ĐẦU RA BẮT BUỘC LÀ JSON, tuân thủ chính xác cấu trúc sau:
    {{
        "title": "Tiêu đề video",
        "scenes": [
            {{
                "scene_number": 1,
                "narration": "Lời đọc tiếng Việt cho cảnh này (bắt buộc phải có, khoảng 2-3 câu ngắn gọn, kịch tính).",
                "image_keyword": "Từ khóa tìm ảnh bằng TIẾNG ANH. RẤT QUAN TRỌNG: Chỉ dùng 1-2 từ (Danh từ chung). Ví dụ: 'Vietnam', 'Mekong', 'Map', 'River', 'Agriculture'. Tuyệt đối không dùng câu dài vì hệ thống sẽ không tìm được ảnh trên Wikipedia."
            }}
        ]
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        script_data = json.loads(response.text)
        return script_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-audio")
async def generate_audio(request: AudioRequest):
    try:
        filename = f"audio_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp3"
        filepath = os.path.join("assets", "audio", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        communicate = edge_tts.Communicate(request.text, request.voice)
        await communicate.save(filepath)
        
        return {"audio_url": f"http://127.0.0.1:8000/assets/audio/{filename}", "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-images")
def search_images(query: str, limit: int = 5):
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": limit,
            "pithumbsize": 1200
        }
        headers = {"User-Agent": "AIVideoGenMVP/1.0"}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        images = []
        if "query" in data and "pages" in data["query"]:
            for page_id, page_info in data["query"]["pages"].items():
                if "thumbnail" in page_info:
                    images.append(page_info["thumbnail"]["source"])
                    
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/render-video")
def render_video(request: RenderRequest):
    try:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        import requests
        
        clips = []
        for idx, scene in enumerate(request.scenes):
            if not scene.audioUrl or not scene.selectedImage:
                continue
                
            # Xử lý đường dẫn âm thanh local
            audio_path = scene.audioUrl.split("8000/")[-1]
            if not os.path.exists(audio_path):
                raise Exception(f"Không tìm thấy file audio: {audio_path}")
            
            # Tải ảnh từ Wikipedia về máy để render
            img_ext = scene.selectedImage.split(".")[-1][:4]
            if img_ext.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
                img_ext = 'jpg'
            img_path = f"assets/images/tmp_{uuid.uuid4().hex[:6]}.{img_ext}"
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            
            headers = {"User-Agent": "AIVideoGenMVP/1.0"}
            res = requests.get(scene.selectedImage, headers=headers)
            with open(img_path, "wb") as f:
                f.write(res.content)
            
            # Tạo MoviePy Clips
            audio_clip = AudioFileClip(audio_path)
            
            # Đọc ảnh và set thời lượng bằng thời lượng âm thanh
            image_clip = ImageClip(img_path).set_duration(audio_clip.duration)
            
            # Đưa video về chuẩn Vertical (Shorts/TikTok) 1080x1920
            # Fix tỷ lệ ảnh (resize height -> 1920, crop width -> 1080) để không bị méo
            image_clip = image_clip.resize(height=1920)
            
            # Nếu ảnh bị hẹp quá 1080 thì resize width, nếu rộng thì crop
            if image_clip.w < 1080:
                image_clip = image_clip.resize(width=1080)
            
            image_clip = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
            
            # Gắn audio vào ảnh
            image_clip = image_clip.set_audio(audio_clip)
            clips.append(image_clip)
            
        if not clips:
            raise Exception("Không có phân cảnh nào hợp lệ để render")
            
        final_video = concatenate_videoclips(clips, method="compose")
        
        os.makedirs("assets/videos", exist_ok=True)
        video_filename = f"video_{int(time.time())}.mp4"
        video_path = f"assets/videos/{video_filename}"
        
        # Render xuất video mp4 (ẩn log để tránh rác terminal)
        final_video.write_videofile(
            video_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger=None
        )
        
        final_video.close()
        for c in clips:
            c.close()
            
        return {"video_url": f"http://127.0.0.1:8000/{video_path}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
