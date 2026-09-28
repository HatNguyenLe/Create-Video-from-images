const MAX_IMAGES = 10;
const ACCEPT = ["image/jpeg", "image/png", "image/webp"];

export default function ImageUploader({ images, onChange }) {
  const addFiles = (fileList) => {
    const files = Array.from(fileList).filter((f) => ACCEPT.includes(f.type));
    const next = files
      .slice(0, MAX_IMAGES - images.length)
      .map((file) => ({ id: crypto.randomUUID(), file, preview: URL.createObjectURL(file) }));
    onChange([...images, ...next]);
  };

  const remove = (id) => {
    const img = images.find((i) => i.id === id);
    if (img) URL.revokeObjectURL(img.preview);
    onChange(images.filter((i) => i.id !== id));
  };

  const move = (index, delta) => {
    const target = index + delta;
    if (target < 0 || target >= images.length) return;
    const next = [...images];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };

  return (
    <div>
      <label
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          addFiles(e.dataTransfer.files);
        }}
      >
        <input type="file" accept={ACCEPT.join(",")} multiple hidden onChange={(e) => addFiles(e.target.files)} />
        Kéo thả hoặc bấm để chọn ảnh (tối đa {MAX_IMAGES}, mỗi ảnh là một cảnh)
      </label>

      <div className="thumbs">
        {images.map((img, i) => (
          <div key={img.id} className="thumb">
            <img src={img.preview} alt={`Ảnh ${i + 1}`} />
            <span className="badge">{i + 1}</span>
            <div className="thumb-actions">
              <button type="button" onClick={() => move(i, -1)}>◀</button>
              <button type="button" onClick={() => remove(img.id)}>✕</button>
              <button type="button" onClick={() => move(i, 1)}>▶</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
