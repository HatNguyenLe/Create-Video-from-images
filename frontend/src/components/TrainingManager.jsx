import { useEffect, useState } from "react";

const emptyForm = { name: "", videos: [], captions: [], epochs: 10, rank: 16 };

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Lỗi ${response.status}`);
  return data;
}

export default function TrainingManager() {
  const [datasets, setDatasets] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [training, setTraining] = useState(null);

  const load = () => api("/api/training/datasets").then(setDatasets).catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  const chooseVideos = (event) => {
    const videos = Array.from(event.target.files).slice(0, 20);
    setForm({ ...form, videos, captions: videos.map(() => "") });
    setError("");
  };

  const importVideos = async (event) => {
    event.preventDefault();
    if (!form.videos.length) return setError("Cần chọn ít nhất một video.");
    setBusy(true); setError(""); setMessage("");
    const body = new FormData();
    body.append("name", form.name);
    form.videos.forEach((video) => body.append("videos", video));
    body.append("captions", JSON.stringify(form.captions));
    try {
      await api("/api/training/datasets", { method: "POST", body });
      setForm(emptyForm);
      setMessage("Dataset đã được import và chuẩn bị metadata.");
      await load();
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  };

  const remove = async (id) => {
    if (!window.confirm("Xóa dataset này?")) return;
    try { await api(`/api/training/datasets/${id}`, { method: "DELETE" }); await load(); }
    catch (e) { setError(e.message); }
  };

  const train = async (datasetId) => {
    setBusy(true); setError(""); setMessage("");
    const body = new FormData();
    body.append("dataset_id", datasetId); body.append("epochs", form.epochs); body.append("rank", form.rank);
    try {
      const job = await api("/api/training/jobs", { method: "POST", body });
      setTraining(job);
      setMessage(job.status === "failed" ? "Fine-tuning chưa được thực hiện." : "Fine-tuning đang chạy.");
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  };

  return <div className="training-page">
    <div className="training-intro">
      <div><p className="eyebrow">MODEL LAB</p><h2>Quản lý dataset & fine-tuning</h2><p className="muted">Import video mẫu có phong cách bạn muốn học. Hệ thống tạo metadata.jsonl để dùng cho trainer video.</p></div>
      <span className="hardware-note">GPU hiện tại: MX130 / 2GB<br /><b>Chỉ đủ chuẩn bị dataset</b></span>
    </div>

    <section className="training-grid">
      <form className="card form" onSubmit={importVideos}>
        <h3>Import video huấn luyện</h3>
        <label>Tên dataset<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Ví dụ: mỹ phẩm studio" /></label>
        <label>Video mẫu (MP4, MOV, WEBM; tối đa 20 video)<input type="file" accept="video/mp4,video/quicktime,video/webm" multiple onChange={chooseVideos} /></label>
        {form.videos.length > 0 && <div className="caption-list">{form.videos.map((video, index) => <label key={video.name + index}>{video.name}<textarea rows="2" placeholder="Caption/prompt mô tả cảnh (không bắt buộc)" value={form.captions[index]} onChange={(e) => { const captions = [...form.captions]; captions[index] = e.target.value; setForm({ ...form, captions }); }} /></label>)}</div>}
        <button className="primary" disabled={busy || !form.videos.length}>{busy ? "Đang xử lý..." : "Import & chuẩn bị dataset"}</button>
      </form>

      <section className="card form"><h3>Cấu hình fine-tuning</h3><label>Epochs<input type="number" min="1" max="100" value={form.epochs} onChange={(e) => setForm({ ...form, epochs: Number(e.target.value) })} /></label><label>LoRA rank<input type="number" min="4" max="64" step="4" value={form.rank} onChange={(e) => setForm({ ...form, rank: Number(e.target.value) })} /></label><p className="muted">Fine-tuning video cần GPU CUDA mạnh. Trên MX130, nút chạy sẽ kiểm tra và dừng an toàn thay vì làm treo máy.</p>{training && <div className="progress"><p>{training.message}</p>{training.error && <p className="error">{training.error}</p>}</div>}</section>
    </section>

    {message && <p className="success">{message}</p>}{error && <p className="error">{error}</p>}
    <section className="card"><h3>Dataset đã import ({datasets.length})</h3>{datasets.length === 0 ? <p className="muted">Chưa có dataset.</p> : <div className="dataset-list">{datasets.map((dataset) => <div className="dataset-row" key={dataset.id}><div><b>{dataset.name}</b><span>{dataset.video_count} video · {Math.round(dataset.total_bytes / 1024 / 1024)} MB · {dataset.status}</span></div><div className="row-actions"><button type="button" disabled={busy} onClick={() => train(dataset.id)}>Fine-tune</button><button type="button" onClick={() => remove(dataset.id)}>Xóa</button></div></div>)}</div>}</section>
  </div>;
}
