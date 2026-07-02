import requests

payload = {
    "title": "Test Video",
    "scenes": [
        {
            "audioUrl": "http://127.0.0.1:8000/assets/audio/test.mp3",
            "selectedImage": "https://picsum.photos/1080/1920",
            "narration": "Vũ trụ bao la và vô tận, nơi chứa đựng vô số bí ẩn chưa được giải đáp.",
            "image_keyword": "galaxy"
        }
    ]
}

# Create a fake audio file first
import os
os.makedirs("assets/audio", exist_ok=True)
with open("assets/audio/test.mp3", "wb") as f:
    f.write(b'fake audio content') # This will fail in moviepy but we can use a real one
