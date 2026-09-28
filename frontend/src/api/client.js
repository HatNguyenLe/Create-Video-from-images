async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg || d).join(", ") : data.detail;
    throw new Error(detail || `Lỗi ${res.status}`);
  }
  return data;
}

export const getVoices = () => fetch("/api/voices").then(handle);

export function generateScript({ productName, description, duration, numScenes }) {
  const form = new FormData();
  form.append("product_name", productName);
  form.append("description", description);
  form.append("duration", duration);
  form.append("num_scenes", Math.max(numScenes, 1));
  return fetch("/api/scripts/generate", { method: "POST", body: form }).then(handle);
}

export function createVideo({ images, productName, description, script, settings }) {
  const form = new FormData();
  images.forEach((img) => form.append("images", img.file));
  form.append("product_name", productName);
  form.append("description", description);
  form.append("script", script);
  Object.entries(settings).forEach(([key, value]) => form.append(key, value));
  return fetch("/api/videos", { method: "POST", body: form }).then(handle);
}

export const getJob = (jobId) => fetch(`/api/videos/${jobId}`).then(handle);
