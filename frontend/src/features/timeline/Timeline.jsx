import React, { useState } from 'react';
import SceneCard from './SceneCard';
import { renderVideoAPI } from '../../services/api';

export default function Timeline({ scriptData, scenes, setScenes }) {
  const [renderLoading, setRenderLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [bgmUrl, setBgmUrl] = useState("");

  const handleRenderVideo = async () => {
    for (let i = 0; i < scenes.length; i++) {
      if (!scenes[i].audioUrl || !scenes[i].selectedImage) {
        alert(`Phân cảnh ${i + 1} chưa tạo đủ âm thanh hoặc hình ảnh!`);
        return;
      }
    }
    
    setRenderLoading(true);
    setVideoUrl(null);
    try {
      const formattedScenes = scenes.map(s => ({
        audioUrl: s.audioUrl,
        selectedImage: s.selectedImage
      }));
      const data = await renderVideoAPI(scriptData.title, formattedScenes, bgmUrl || null);
      setVideoUrl(data.video_url);
    } catch (err) {
      alert("Lỗi Render: " + err);
    }
    setRenderLoading(false);
  };

  return (
    <div className="card">
      <div className="card-header" style={{ textAlign: 'center' }}>
        <h2>🎬 {scriptData.title}</h2>
        <p className="subtitle">Kiểm tra âm thanh, hình ảnh và nhạc nền trước khi xuất file</p>
      </div>
      
      <div className="scene-list">
        {scenes.map((scene, idx) => (
          <SceneCard 
            key={idx} 
            scene={scene} 
            index={idx} 
            scenes={scenes} 
            setScenes={setScenes} 
          />
        ))}
      </div>
      
      {scenes.length > 0 && (
        <div style={{ marginTop: '3rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(15, 23, 42, 0.5)', padding: '1rem 2rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <span style={{ color: 'white', fontWeight: 600 }}>🎵 Chọn Nhạc Nền:</span>
              <select 
                className="form-input"
                style={{ width: 'auto', padding: '0.6rem 1rem' }}
                value={bgmUrl} 
                onChange={(e) => setBgmUrl(e.target.value)}
              >
                <option value="">🚫 Không dùng nhạc</option>
                <option value="http://127.0.0.1:8000/assets/audio/bgm/epic.mp3">⚔️ Hào hùng (Epic Battle)</option>
                <option value="http://127.0.0.1:8000/assets/audio/bgm/enigma.mp3">🕵️ Bí ẩn (Enigma)</option>
                <option value="http://127.0.0.1:8000/assets/audio/bgm/sunshine.mp3">🌅 Nhẹ nhàng (City Sunshine)</option>
              </select>
              
              {bgmUrl && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '1rem' }}>
                  <audio controls src={bgmUrl} />
                </div>
              )}
            </div>

            <button 
              className="btn btn-success" 
              style={{ padding: '1.2rem 4rem', fontSize: '1.2rem', width: '100%', maxWidth: '400px' }}
              onClick={handleRenderVideo}
              disabled={renderLoading}
            >
              {renderLoading ? '⏳ Đang Render (Chờ 1-2 phút)...' : '🎞️ XUẤT VIDEO'}
            </button>
          </div>
          
          {videoUrl && (
            <div style={{ marginTop: '2rem', textAlign: 'center', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '2rem', borderRadius: '16px' }}>
              <h3 style={{ color: 'var(--accent)', marginBottom: '1.5rem' }}>🎉 Hoàn tất! Video của bạn đã sẵn sàng</h3>
              <video controls src={videoUrl} style={{ width: '100%', maxWidth: '600px', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
