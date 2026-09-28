export default function JobProgress({ job }) {
  if (!job) return null;
  return (
    <div className="progress">
      <div className="progress-bar">
        <div className={`progress-fill ${job.status}`} style={{ width: `${job.progress}%` }} />
      </div>
      <p>
        {job.message} ({job.progress}%)
      </p>
      {job.error && <p className="error">{job.error}</p>}
    </div>
  );
}
