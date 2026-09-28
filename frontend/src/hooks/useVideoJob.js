import { useEffect, useRef, useState } from "react";
import { createVideo, getJob } from "../api/client";

const POLL_MS = 2000;

export function useVideoJob() {
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const timer = useRef(null);

  const stop = () => clearInterval(timer.current);
  useEffect(() => stop, []);

  const start = async (payload) => {
    stop();
    setError("");
    setJob({ status: "queued", progress: 0, message: "Đang gửi yêu cầu" });
    try {
      const { job_id } = await createVideo(payload);
      timer.current = setInterval(async () => {
        try {
          const data = await getJob(job_id);
          setJob(data);
          if (data.status === "completed" || data.status === "failed") stop();
        } catch (e) {
          stop();
          setError(e.message);
        }
      }, POLL_MS);
    } catch (e) {
      setJob(null);
      setError(e.message);
    }
  };

  const busy = job && (job.status === "queued" || job.status === "running");
  return { job, error, busy, start };
}
