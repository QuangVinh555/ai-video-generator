import React, { useState } from 'react';
import './index.css';
import ScriptGenerator from './features/script-generator/ScriptGenerator';
import Timeline from './features/timeline/Timeline';

function App() {
  const [scriptData, setScriptData] = useState(null);
  const [scenes, setScenes] = useState([]);
  
  const handleScriptGenerated = (data) => {
    setScriptData(data);
    const initialScenes = data.scenes.map(s => ({
      ...s,
      audioUrl: null,
      isGeneratingAudio: false,
      images: [],
      selectedImage: null,
      isSearchingImages: false
    }));
    setScenes(initialScenes);
  };

  return (
    <div className="container">
      <div className="glass-card">
        <h1 className="title">✨ AI Video Creator</h1>
        
        <ScriptGenerator onScriptGenerated={handleScriptGenerated} />

        {scriptData && (
          <Timeline 
            scriptData={scriptData} 
            scenes={scenes} 
            setScenes={setScenes} 
          />
        )}
      </div>
    </div>
  );
}

export default App;
