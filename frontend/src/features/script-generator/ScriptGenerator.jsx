import React, { useState } from 'react';
import { generateScriptAPI } from '../../services/api';

export default function ScriptGenerator({ onScriptGenerated }) {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const data = await generateScriptAPI(topic);
      onScriptGenerated(data);
    } catch (err) {
      alert("Lỗi khi tạo kịch bản: " + err);
    }
    setLoading(false);
  };

  return (
    <div className="input-group">
      <input 
        type="text" 
        className="premium-input" 
        placeholder="Nhập chủ đề bạn muốn làm video... (vd: Sự sụp đổ của La Mã)"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />
      <button 
        className="premium-btn" 
        onClick={handleGenerate}
        disabled={loading || !topic}
      >
        {loading ? 'Đang sáng tạo...' : 'Tạo Kịch Bản'}
      </button>
      
      {loading && (
        <div className="loader">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      )}
    </div>
  );
}
