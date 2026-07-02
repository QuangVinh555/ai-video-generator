import google.generativeai as genai
import json

def generate_script_service(topic: str):
    prompt = f"""
    Bạn là một chuyên gia viết kịch bản video ngắn (TikTok, YouTube Shorts) về chủ đề Lịch sử, Địa lý.
    Hãy viết một kịch bản hấp dẫn, thời lượng khoảng 45-60 giây về chủ đề: "{topic}".
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
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)
