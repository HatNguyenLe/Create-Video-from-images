import { useState } from "react";
import { generateScript } from "../api/client";

export default function ProductForm({
  productName,
  description,
  script,
  duration,
  numScenes,
  onProductName,
  onDescription,
  onScript,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await generateScript({ productName, description, duration, numScenes });
      onScript(data.script);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form">
      <label>
        Tên sản phẩm
        <input value={productName} maxLength={200} onChange={(e) => onProductName(e.target.value)} placeholder="VD: Tai nghe Bluetooth X1" />
      </label>

      <label>
        Mô tả sản phẩm
        <textarea
          rows={4}
          maxLength={3000}
          value={description}
          onChange={(e) => onDescription(e.target.value)}
          placeholder="Tính năng, ưu điểm, giá, khuyến mãi..."
        />
      </label>

      <button type="button" onClick={handleGenerate} disabled={loading || (!productName && !description)}>
        {loading ? "Đang viết kịch bản..." : "Tạo kịch bản bằng AI"}
      </button>
      {error && <p className="error">{error}</p>}

      <label>
        Kịch bản lồng tiếng (mỗi dòng một câu, tự chia đều cho các ảnh)
        <textarea
          rows={8}
          maxLength={5000}
          value={script}
          onChange={(e) => onScript(e.target.value)}
          placeholder="Để trống để hệ thống tự viết kịch bản từ mô tả"
        />
      </label>
    </div>
  );
}
