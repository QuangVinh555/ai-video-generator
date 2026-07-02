import React, { useState } from 'react';
import SceneCard from './SceneCard';
import { renderVideoAPI } from '../../services/api';

export default function Timeline({ scriptData, scenes, setScenes }) {
  const [renderLoading, setRenderLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);

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
      const data = await renderVideoAPI(scriptData.title, formattedScenes);
      setVideoUrl(data.video_url);
    } catch (err) {
      alert("Lỗi Render: " + err);
    }
    setRenderLoading(false);
  };

  return (
    <div className="timeline">
      <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '1rem', fontWeight: 600 }}>
        🎬 {scriptData.title}
      </h2>
      
      {scenes.map((scene, idx) => (
        <SceneCard 
          key={idx} 
          scene={scene} 
          index={idx} 
          scenes={scenes} 
          setScenes={setScenes} 
        />
      ))}
      
      {scenes.length > 0 && (
        <div style={{ textAlign: 'center', marginTop: '3rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <button 
            className="premium-btn" 
            style={{ padding: '1.2rem 4rem', fontSize: '1.3rem', borderRadius: '50px', background: 'linear-gradient(135deg, #10b981, #059669)' }}
            onClick={handleRenderVideo}
            disabled={renderLoading}
          >
            {renderLoading ? '⏳ Đang Render Video (Chờ 1-2 phút)...' : '🎞️ Render Video (Hoàn thiện)'}
          </button>
          
          {videoUrl && (
            <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.5)', borderRadius: '16px' }}>
              <h3 style={{ color: '#10b981', marginBottom: '1rem' }}>🎉 Video của bạn đã sẵn sàng!</h3>
              <video controls src={videoUrl} style={{ height: '500px', borderRadius: '12px' }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
