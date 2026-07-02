import os
import time
import uuid
import edge_tts

async def generate_audio_service(text: str, voice: str):
    filename = f"audio_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp3"
    filepath = os.path.join("assets", "audio", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)
    return filename, filepath
