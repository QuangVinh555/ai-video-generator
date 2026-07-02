import React, { useState } from 'react';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000/api';

function App() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [scriptData, setScriptData] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [renderLoading, setRenderLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  
  const handleGenerateScript = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/generate-script`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      setScriptData(data);
      
      // Khởi tạo state cho các phân cảnh (scenes)
      const initialScenes = data.scenes.map(s => ({
        ...s,
        audioUrl: null,
        isGeneratingAudio: false,
        images: [],
        selectedImage: null,
        isSearchingImages: false
      }));
      setScenes(initialScenes);
      
    } catch (err) {
      alert("Lỗi khi tạo kịch bản: " + err);
    }
    setLoading(false);
  };

  const generateAudio = async (index, text) => {
    const newScenes = [...scenes];
    newScenes[index].isGeneratingAudio = true;
    setScenes([...newScenes]);
    
    try {
      const res = await fetch(`${API_BASE}/generate-audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'vi-VN-HoaiMyNeural' })
      });
      const data = await res.json();
      newScenes[index].audioUrl = data.audio_url; 
    } catch (err) {
      alert("Lỗi khi tạo giọng đọc: " + err);
    }
    newScenes[index].isGeneratingAudio = false;
    setScenes([...newScenes]);
  };

  const searchImages = async (index, keyword) => {
    const newScenes = [...scenes];
    newScenes[index].isSearchingImages = true;
    setScenes([...newScenes]);
    
    try {
      const res = await fetch(`${API_BASE}/search-images?query=${encodeURIComponent(keyword)}&limit=5`);
      const data = await res.json();
      newScenes[index].images = data.images || [];
      if(data.images && data.images.length > 0) {
        newScenes[index].selectedImage = data.images[0];
      }
    } catch (err) {
      alert("Lỗi khi tìm ảnh: " + err);
    }
    newScenes[index].isSearchingImages = false;
    setScenes([...newScenes]);
  };

  const updateNarration = (index, newText) => {
    const newScenes = [...scenes];
    newScenes[index].narration = newText;
    setScenes(newScenes);
  };

  const updateKeyword = (index, newText) => {
    const newScenes = [...scenes];
    newScenes[index].image_keyword = newText;
    setScenes(newScenes);
  };

  const selectImage = (sceneIndex, imgUrl) => {
    const newScenes = [...scenes];
    newScenes[sceneIndex].selectedImage = imgUrl;
    setScenes(newScenes);
  };

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
      const res = await fetch(`${API_BASE}/render-video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: scriptData.title,
          scenes: scenes.map(s => ({
            audioUrl: s.audioUrl,
            selectedImage: s.selectedImage
          }))
        })
      });
      const data = await res.json();
      if (res.ok) {
        setVideoUrl(data.video_url);
      } else {
        alert("Lỗi Render: " + data.detail);
      }
    } catch (err) {
      alert("Lỗi Render: " + err);
    }
    setRenderLoading(false);
  };

  return (
    <div className="container">
      <div className="glass-card">
        <h1 className="title">✨ AI Video Creator</h1>
        
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
            onClick={handleGenerateScript}
            disabled={loading || !topic}
          >
            {loading ? 'Đang sáng tạo...' : 'Tạo Kịch Bản'}
          </button>
        </div>

        {loading && (
          <div className="loader">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}

        {scriptData && !loading && (
          <div className="timeline">
            <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '1rem', fontWeight: 600 }}>
              🎬 {scriptData.title}
            </h2>
            
            {scenes.map((scene, idx) => (
              <div key={idx} className="scene-card">
                <div className="scene-header">
                  <span className="scene-number">Phân cảnh {scene.scene_number}</span>
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                    <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>Từ khóa:</span>
                    <input 
                      type="text" 
                      value={scene.image_keyword || ""} 
                      onChange={(e) => updateKeyword(idx, e.target.value)}
                      style={{background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '4px 12px', borderRadius: '20px', outline: 'none', fontSize: '0.9rem', width: '150px'}}
                    />
                  </div>
                </div>
                
                <div className="scene-content">
                  <div className="scene-text-section">
                    <textarea 
                      className="narration-box"
                      value={scene.narration}
                      onChange={(e) => updateNarration(idx, e.target.value)}
                      title="Bạn có thể sửa lời đọc tại đây"
                    />
                    
                    <div className="scene-actions">
                      <button 
                        className="action-btn"
                        onClick={() => generateAudio(idx, scene.narration)}
                        disabled={scene.isGeneratingAudio}
                      >
                        {scene.isGeneratingAudio ? '⏳ Đang tạo...' : '🎙️ Tạo Giọng Đọc'}
                      </button>
                      
                      {scene.audioUrl && (
                        <audio controls src={scene.audioUrl} />
                      )}
                    </div>
                  </div>
                  
                  <div className="visual-section">
                    <div className="image-preview">
                      {scene.selectedImage ? (
                        <img src={scene.selectedImage} alt="preview" />
                      ) : (
                        <span style={{color: '#64748b'}}>Chưa có hình ảnh</span>
                      )}
                    </div>
                    
                    <div className="scene-actions" style={{justifyContent: 'center'}}>
                      <button 
                        className="action-btn primary"
                        onClick={() => searchImages(idx, scene.image_keyword)}
                        disabled={scene.isSearchingImages}
                      >
                        {scene.isSearchingImages ? '⏳ Đang tìm...' : '🔍 Tìm Ảnh (Wikipedia)'}
                      </button>
                    </div>

                    {scene.images.length > 0 && (
                      <div className="image-gallery">
                        {scene.images.map((img, imgIdx) => (
                          <img 
                            key={imgIdx} 
                            src={img} 
                            className={`gallery-img ${scene.selectedImage === img ? 'selected' : ''}`}
                            onClick={() => selectImage(idx, img)}
                            alt="gallery thumbnail"
                            title="Bấm để chọn ảnh này"
                          />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
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
        )}
      </div>
    </div>
  );
}

export default App;
