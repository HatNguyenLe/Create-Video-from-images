export default function VideoPreview({ job }) {
  if (job?.status !== "completed") {
    return <p className="muted">Video sẽ hiển thị ở đây sau khi tạo xong.</p>;
  }
  return (
    <div className="preview">
      <video src={job.video_url} controls />
      <a className="primary" href={job.video_url} download>
        Tải video
      </a>
      {job.script && (
        <details>
          <summary>Kịch bản đã dùng</summary>
          <pre>{job.script}</pre>
        </details>
      )}
    </div>
  );
}
