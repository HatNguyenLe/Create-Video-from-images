import { useEffect, useState } from "react";
import { getVoices } from "../api/client";

export default function VideoSettings({ settings, onChange }) {
  const [voices, setVoices] = useState([]);
  useEffect(() => {
    getVoices().then(setVoices).catch(() => setVoices([]));
  }, []);

  const set = (key) => (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    onChange({ ...settings, [key]: key === "duration" ? Number(value) : value });
  };

  return (
    <div className="form">
      <label>
        Giọng đọc
        <select value={settings.voice} onChange={set("voice")}>
          {voices.map((v) => (
            <option key={v.id} value={v.id}>{v.label}</option>
          ))}
        </select>
      </label>

      <label>
        Tỉ lệ khung hình
        <select value={settings.aspect_ratio} onChange={set("aspect_ratio")}>
          <option value="9:16">9:16 (TikTok, Reels, Shorts)</option>
          <option value="1:1">1:1 (Feed)</option>
          <option value="16:9">16:9 (YouTube)</option>
        </select>
      </label>

      <label>
        Thời lượng: {settings.duration}s
        <input type="range" min={30} max={40} value={settings.duration} onChange={set("duration")} />
      </label>

      <label>
        Chế độ chuyển động
        <select value={settings.mode} onChange={set("mode")}>
          <option value="kenburns">Ken Burns (nhanh, chạy CPU)</option>
          <option value="ai">AI LTX-Video (cần GPU)</option>
        </select>
      </label>

      <label className="checkbox">
        <input type="checkbox" checked={settings.subtitles} onChange={set("subtitles")} />
        Hiển thị phụ đề
      </label>
    </div>
  );
}
