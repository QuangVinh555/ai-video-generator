import os
import time
import uuid
import requests
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def render_video_service(scenes_data: list, bgm_url: str = None):
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
    import moviepy.audio.fx.all as afx
    
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
        
        # 1. Khởi tạo đoạn Audio giọng đọc
        audio_clip = AudioFileClip(audio_path)
        
        # 2. Khởi tạo đoạn Video (Ảnh tĩnh) và cắt ghép
        image_clip = ImageClip(img_path).set_duration(audio_clip.duration)
        image_clip = image_clip.resize(height=1920)
        if image_clip.w < 1080:
            image_clip = image_clip.resize(width=1080)
        image_clip = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
        
        # 3. Gắn âm thanh giọng đọc vào ảnh
        image_clip = image_clip.set_audio(audio_clip)
        clips.append(image_clip)
        
    if not clips:
        raise Exception("Không có phân cảnh nào hợp lệ để render")
        
    # 4. Nối tất cả các phân cảnh lại thành 1 video dài
    final_video = concatenate_videoclips(clips, method="compose")
    main_audio = final_video.audio
    
    # 5. Xử lý Nhạc Nền (Background Music) NẾU CÓ
    if bgm_url:
        try:
            bgm_path = None
            if "127.0.0.1:8000/assets/" in bgm_url:
                # File đã có sẵn trong Local Server, lấy đường dẫn
                bgm_path = bgm_url.split("8000/")[-1]
            else:
                # File từ Internet, tải về
                import hashlib
                bgm_filename = hashlib.md5(bgm_url.encode()).hexdigest() + ".mp3"
                bgm_path = f"assets/audio/{bgm_filename}"
                
                if not os.path.exists(bgm_path):
                    os.makedirs(os.path.dirname(bgm_path), exist_ok=True)
                    res = requests.get(bgm_url, headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        with open(bgm_path, "wb") as f:
                            f.write(res.content)
            
            if bgm_path and os.path.exists(bgm_path):
                bgm_clip = AudioFileClip(bgm_path)
                # Lặp lại nhạc nền cho khớp với độ dài tổng của video
                bgm_clip = afx.audio_loop(bgm_clip, duration=final_video.duration)
                # Giảm âm lượng nhạc nền xuống 10%
                bgm_clip = bgm_clip.volumex(0.3)
                
                # Trộn Giọng đọc chính và Nhạc nền
                mixed_audio = CompositeAudioClip([main_audio, bgm_clip])
                final_video = final_video.set_audio(mixed_audio)
        except Exception as e:
            print("Cảnh báo: Lỗi xử lý nhạc nền:", e)
    
    # 6. Trích xuất ra file MP4
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
    
    # Dọn dẹp RAM
    final_video.close()
    for c in clips:
        c.close()
        
    return video_filename, video_path
