import React from 'react';
import { generateAudioAPI, searchImagesAPI } from '../../services/api';

export default function SceneCard({ scene, index, scenes, setScenes }) {
  
  const updateNarration = (newText) => {
    const newScenes = [...scenes];
    newScenes[index].narration = newText;
    setScenes(newScenes);
  };

  const updateKeyword = (newText) => {
    const newScenes = [...scenes];
    newScenes[index].image_keyword = newText;
    setScenes(newScenes);
  };

  const selectImage = (imgUrl) => {
    const newScenes = [...scenes];
    newScenes[index].selectedImage = imgUrl;
    setScenes(newScenes);
  };

  const generateAudio = async () => {
    const newScenes = [...scenes];
    newScenes[index].isGeneratingAudio = true;
    setScenes([...newScenes]);
    try {
      const data = await generateAudioAPI(scene.narration);
      newScenes[index].audioUrl = data.audio_url; 
    } catch (err) {
      alert("Lỗi khi tạo giọng đọc: " + err);
    }
    newScenes[index].isGeneratingAudio = false;
    setScenes([...newScenes]);
  };

  const searchImages = async () => {
    const newScenes = [...scenes];
    newScenes[index].isSearchingImages = true;
    setScenes([...newScenes]);
    try {
      const data = await searchImagesAPI(scene.image_keyword);
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

  return (
    <div className="scene-card">
      <div className="scene-header">
        <span className="scene-number">Phân cảnh {scene.scene_number}</span>
        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <span style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>Từ khóa:</span>
          <input 
            type="text" 
            className="form-input"
            value={scene.image_keyword || ""} 
            onChange={(e) => updateKeyword(e.target.value)}
            style={{ padding: '4px 12px', fontSize: '0.9rem', width: '200px' }}
          />
        </div>
      </div>
      
      <div className="scene-content">
        <div className="scene-text-section">
          <textarea 
            className="narration-box"
            value={scene.narration}
            onChange={(e) => updateNarration(e.target.value)}
            title="Bạn có thể sửa lời đọc tại đây"
          />
          
          <div className="scene-actions">
            <button 
              className="btn btn-primary"
              onClick={generateAudio}
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
              <span style={{color: 'var(--text-muted)'}}>Chưa có hình ảnh</span>
            )}
          </div>
          
          <div className="scene-actions" style={{justifyContent: 'center'}}>
            <button 
              className="btn btn-secondary"
              onClick={searchImages}
              disabled={scene.isSearchingImages}
            >
              {scene.isSearchingImages ? '⏳ Đang tìm...' : '🔍 Tìm Ảnh'}
            </button>
          </div>

          {scene.images && scene.images.length > 0 && (
            <div className="image-gallery">
              {scene.images.map((img, imgIdx) => (
                <img 
                  key={imgIdx} 
                  src={img} 
                  className={`gallery-img ${scene.selectedImage === img ? 'selected' : ''}`}
                  onClick={() => selectImage(img)}
                  alt="gallery thumbnail"
                  title="Bấm để chọn ảnh này"
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
