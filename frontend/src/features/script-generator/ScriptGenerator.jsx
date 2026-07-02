import React, { useState } from 'react';
import { generateScriptAPI } from '../../services/api';

export default function ScriptGenerator({ onScriptGenerated }) {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerateAI = async () => {
    if (!topic) {
      alert("Vui lòng nhập chủ đề!");
      return;
    }
    setLoading(true);
    try {
      const data = await generateScriptAPI(topic);
      onScriptGenerated(data);
    } catch (err) {
      alert("Lỗi khi tạo kịch bản: " + err);
    }
    setLoading(false);
  };

  const handleGenerateMock = () => {
    const mockData = {
      title: "Hành trình khám phá Vũ trụ (Kịch bản Mẫu)",
      scenes: [
        {
          scene_number: 1,
          narration: "Vũ trụ bao la và vô tận, nơi chứa đựng vô số bí ẩn chưa được giải đáp. Hãy cùng chúng tôi bắt đầu hành trình khám phá.",
          image_keyword: "galaxy deep space stars"
        },
        {
          scene_number: 2,
          narration: "Mặt trời, nguồn sống của chúng ta, chỉ là một ngôi sao nhỏ bé trong hàng tỷ ngôi sao của dải Ngân Hà.",
          image_keyword: "glowing sun solar system"
        },
        {
          scene_number: 3,
          narration: "Và ngoài kia, liệu có sự sống nào khác đang chờ đợi chúng ta khám phá hay không?",
          image_keyword: "alien planet futuristic spaceship"
        }
      ]
    };
    onScriptGenerated(mockData);
  };

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <div className="card-header">
        <h2>📝 Khởi tạo Kịch bản</h2>
        <p className="subtitle">Nhập chủ đề để AI viết kịch bản, hoặc dùng kịch bản mẫu để test luồng Render</p>
      </div>
      
      <div className="input-group">
        <input 
          type="text" 
          className="form-input" 
          placeholder="Ví dụ: Lịch sử đế chế La Mã, Bí ẩn hố đen vũ trụ..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <div className="button-group">
          <button 
            className="btn btn-primary" 
            onClick={handleGenerateAI}
            disabled={loading}
          >
            {loading ? '⏳ Đang kết nối AI...' : '✨ Tạo bằng AI (Tốn Token)'}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={handleGenerateMock}
            disabled={loading}
          >
            🧪 Dùng kịch bản Mẫu
          </button>
        </div>
      </div>
    </div>
  );
}
