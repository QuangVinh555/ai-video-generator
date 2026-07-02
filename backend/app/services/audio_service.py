import os
import time
import uuid
import edge_tts

import json

async def generate_audio_service(text: str, voice: str):
    filename_base = f"audio_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    filename = f"{filename_base}.mp3"
    filepath = os.path.join("assets", "audio", filename)
    json_path = os.path.join("assets", "audio", f"{filename_base}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    word_boundaries = []
    
    with open(filepath, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Offset and duration in 100-nanosecond units. 1 sec = 10,000,000 units.
                start_time = chunk["offset"] / 10_000_000.0
                end_time = (chunk["offset"] + chunk["duration"]) / 10_000_000.0
                word_boundaries.append({
                    "word": chunk["text"],
                    "start": start_time,
                    "end": end_time
                })
                
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(word_boundaries, f, ensure_ascii=False, indent=2)
        
    return filename, filepath
