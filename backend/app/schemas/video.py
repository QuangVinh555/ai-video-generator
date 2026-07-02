from pydantic import BaseModel
from typing import List, Optional

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
    bgmUrl: Optional[str] = None
