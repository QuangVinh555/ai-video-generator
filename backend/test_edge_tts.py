import asyncio
import edge_tts

async def main():
    communicate = edge_tts.Communicate("Xin chào thế giới, đây là một bài kiểm tra.", "vi-VN-HoaiMyNeural")
    async for chunk in communicate.stream():
        if chunk["type"] == "SentenceBoundary":
            print(chunk)

asyncio.run(main())
