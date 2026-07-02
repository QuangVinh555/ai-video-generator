import os
import time
import uuid
import requests
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def render_video_service(scenes_data: list):
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    
    clips = []
    for scene in scenes_data:
        audio_path = scene.audioUrl.split("8000/")[-1]
        if not os.path.exists(audio_path):
            raise Exception(f"Không tìm thấy file audio: {audio_path}")
        
        img_ext = scene.selectedImage.split(".")[-1][:4]
        if img_ext.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
            img_ext = 'jpg'
        img_path = f"assets/images/tmp_{uuid.uuid4().hex[:6]}.{img_ext}"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        
        headers = {"User-Agent": "AIVideoGenMVP/1.0"}
        res = requests.get(scene.selectedImage, headers=headers)
        with open(img_path, "wb") as f:
            f.write(res.content)
        
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(img_path).set_duration(audio_clip.duration)
        
        image_clip = image_clip.resize(height=1920)
        if image_clip.w < 1080:
            image_clip = image_clip.resize(width=1080)
        image_clip = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
        
        image_clip = image_clip.set_audio(audio_clip)
        clips.append(image_clip)
        
    if not clips:
        raise Exception("Không có phân cảnh nào hợp lệ để render")
        
    final_video = concatenate_videoclips(clips, method="compose")
    
    os.makedirs("assets/videos", exist_ok=True)
    video_filename = f"video_{int(time.time())}.mp4"
    video_path = f"assets/videos/{video_filename}"
    
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
        
    return video_filename, video_path
