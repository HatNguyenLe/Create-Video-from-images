import { useEffect, useState } from "react";
import ImageUploader from "./components/ImageUploader.jsx";
import ProductForm from "./components/ProductForm.jsx";
import VideoSettings from "./components/VideoSettings.jsx";
import JobProgress from "./components/JobProgress.jsx";
import VideoPreview from "./components/VideoPreview.jsx";
import TrainingManager from "./components/TrainingManager.jsx";
import { useVideoJob } from "./hooks/useVideoJob";

const DEFAULT_SETTINGS = {
  voice: "vi-VN-HoaiMyNeural",
  aspect_ratio: "9:16",
  duration: 35,
  mode: "kenburns",
  subtitles: true,
};

export default function App() {
  const [images, setImages] = useState([]);
  const [productName, setProductName] = useState("");
  const [description, setDescription] = useState("");
  const [script, setScript] = useState("");
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [view, setView] = useState("create");
  const { job, error, busy, start } = useVideoJob();

  useEffect(() => () => images.forEach((img) => URL.revokeObjectURL(img.preview)), []); // eslint-disable-line

  const canSubmit = images.length > 0 && (script.trim() || description.trim() || productName.trim()) && !busy;

  const handleSubmit = (e) => {
    e.preventDefault();
    start({ images, productName, description, script, settings });
  };

  return (
    <div className="container">
      <header>
        <div className="topbar"><div><h1>Affiliate Video Generator</h1><p>Tạo video 30–40 giây giới thiệu sản phẩm từ hình ảnh và kịch bản</p></div><nav><button type="button" className={view === "create" ? "nav-active" : ""} onClick={() => setView("create")}>Tạo video</button><button type="button" className={view === "training" ? "nav-active" : ""} onClick={() => setView("training")}>Quản lý & Fine-tuning</button></nav></div>
      </header>

      {view === "training" ? <TrainingManager /> : <form className="layout" onSubmit={handleSubmit}>
        <section className="card">
          <h2>1. Hình ảnh sản phẩm</h2>
          <ImageUploader images={images} onChange={setImages} />
        </section>

        <section className="card">
          <h2>2. Nội dung</h2>
          <ProductForm
            productName={productName}
            description={description}
            script={script}
            duration={settings.duration}
            numScenes={images.length}
            onProductName={setProductName}
            onDescription={setDescription}
            onScript={setScript}
          />
        </section>

        <section className="card">
          <h2>3. Cài đặt video</h2>
          <VideoSettings settings={settings} onChange={setSettings} />
          <button type="submit" className="primary" disabled={!canSubmit}>
            {busy ? "Đang tạo video..." : "Tạo video"}
          </button>
          {error && <p className="error">{error}</p>}
          <JobProgress job={job} />
        </section>

        <section className="card">
          <h2>4. Kết quả</h2>
          <VideoPreview job={job} />
        </section>
      </form>}
    </div>
  );
}
