export const API_BASE = 'http://127.0.0.1:8000/api';

export const generateScriptAPI = async (topic) => {
  const res = await fetch(`${API_BASE}/generate-script`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const generateAudioAPI = async (text) => {
  const res = await fetch(`${API_BASE}/generate-audio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice: 'vi-VN-HoaiMyNeural' })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const searchImagesAPI = async (keyword) => {
  const res = await fetch(`${API_BASE}/search-images?query=${encodeURIComponent(keyword)}&limit=5`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const renderVideoAPI = async (title, scenes) => {
  const res = await fetch(`${API_BASE}/render-video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, scenes })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Lỗi render");
  return data;
};
