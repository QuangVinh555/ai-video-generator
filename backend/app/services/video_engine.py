import os
import time
import uuid
import requests
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def generate_subtitle_clips(audio_path, duration, text=""):
    from moviepy.editor import ImageClip
    json_path = audio_path.replace(".mp3", ".json")
    word_boundaries = []
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            word_boundaries = json.load(f)
            
    if not word_boundaries and text:
        words = text.split()
        if not words:
            return []
        
        total_chars = sum(len(w) for w in words)
        current_time = 0.0
        for w in words:
            w_duration = (len(w) / total_chars) * duration
            word_boundaries.append({
                "word": w,
                "start": current_time,
                "end": current_time + w_duration
            })
            current_time += w_duration
            
    if not word_boundaries:
        print("DEBUG: word_boundaries is STILL empty after fallback!")
        return []

    print(f"DEBUG: Generating subtitles for {len(word_boundaries)} words.")
    font_path = "assets/fonts/Montserrat-Black.ttf"
    try:
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()
        
    chunk_size = 5
    sub_clips = []
    
    for i in range(0, len(word_boundaries), chunk_size):
        chunk = word_boundaries[i:i+chunk_size]
        if i + chunk_size < len(word_boundaries):
            chunk_display_end = word_boundaries[i+chunk_size]['start']
        else:
            chunk_display_end = duration
            
        for j, word in enumerate(chunk):
            highlight_start = word['start']
            if j < len(chunk) - 1:
                highlight_end = chunk[j+1]['start']
            else:
                highlight_end = chunk_display_end
                
            if highlight_end > duration:
                highlight_end = duration
            if highlight_start >= duration:
                continue
                
            img = Image.new('RGBA', (1080, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            texts = [w['word'] for w in chunk]
            total_text = " ".join(texts)
            
            try:
                bbox = draw.textbbox((0, 0), total_text, font=font)
                total_width = bbox[2] - bbox[0]
            except AttributeError:
                total_width, _ = draw.textsize(total_text, font=font)
                
            start_x = (1080 - total_width) / 2
            y = 50
            
            current_x = start_x
            for k, w in enumerate(chunk):
                text = w['word']
                fill_color = (252, 211, 77, 255) if k == j else (255, 255, 255, 255)
                stroke_color = (0, 0, 0, 255)
                
                try:
                    draw.text((current_x, y), text, font=font, fill=fill_color, stroke_width=6, stroke_fill=stroke_color)
                except TypeError:
                    draw.text((current_x+4, y+4), text, font=font, fill=stroke_color)
                    draw.text((current_x, y), text, font=font, fill=fill_color)
                
                try:
                    w_bbox = draw.textbbox((0, 0), text + " ", font=font)
                    w_width = w_bbox[2] - w_bbox[0]
                except AttributeError:
                    w_width, _ = draw.textsize(text + " ", font=font)
                
                current_x += w_width
                
            img_array = np.array(img)
            color = img_array[:, :, :3]
            mask = img_array[:, :, 3] / 255.0
            
            txt_clip = ImageClip(color).set_mask(ImageClip(mask, ismask=True))
            txt_clip = txt_clip.set_start(highlight_start).set_end(highlight_end)
            txt_clip = txt_clip.set_position(('center', 1350))
            
            sub_clips.append(txt_clip)
            
    return sub_clips

def render_video_service(scenes_data: list, bgm_url: str = None):
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip
    import moviepy.audio.fx.all as afx
    
    clips = []
    for idx, scene in enumerate(scenes_data):
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
        duration = audio_clip.duration
        
        # 2. Khởi tạo đoạn Video (Ảnh tĩnh) và cắt ghép cơ bản
        base_img = ImageClip(img_path).set_duration(duration)
        base_img = base_img.resize(height=1920)
        if base_img.w < 1080:
            base_img = base_img.resize(width=1080)
        base_img = base_img.crop(x_center=base_img.w/2, y_center=base_img.h/2, width=1080, height=1920)
        
        # 3. Áp dụng hiệu ứng Ken Burns động
        zoom_speed = 0.03
        if idx % 2 == 0:
            zoomed_img = base_img.resize(lambda t: 1 + zoom_speed * t)
        else:
            start_scale = 1 + zoom_speed * duration
            zoomed_img = base_img.resize(lambda t: start_scale - zoom_speed * t)
        
        # Khởi tạo danh sách các layer (lớp) cho phân cảnh này
        layer_clips = [zoomed_img.set_position('center')]
        
        # 3.5 Khởi tạo Subtitle Clip (Phụ đề Karaoke)
        sub_clips = generate_subtitle_clips(audio_path, duration, scene.narration)
        layer_clips.extend(sub_clips)
        
        # Trộn tất cả vào 1 khung 1080x1920
        scene_clip = CompositeVideoClip(layer_clips, size=(1080, 1920))
        scene_clip = scene_clip.set_duration(duration)
        
        # 4. Gắn âm thanh giọng đọc vào phân cảnh
        scene_clip = scene_clip.set_audio(audio_clip)
        clips.append(scene_clip)
        
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
                # Giảm âm lượng nhạc nền xuống 20%
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
