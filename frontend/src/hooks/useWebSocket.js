import { useEffect, useRef, useState } from "react";

export default function useWebSocket(sessionId) {
  const [progress, setProgress] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    if (!sessionId) return;

    ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${sessionId}`);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setProgress((prev) => [...prev, data]);
    };

    ws.current.onerror = (err) => {
      console.log(err);
    };

    return () => ws.current?.close();
  }, [sessionId]);

  return progress;
}