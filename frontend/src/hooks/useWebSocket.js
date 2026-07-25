import { useEffect, useRef, useState } from "react";

export default function useWebSocket(sessionId) {
  const [progress, setProgress] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    if (!sessionId) return;

    console.log("Opening WebSocket...");

    ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${sessionId}`);

    ws.current.onopen = () => {
      console.log("WebSocket Connected");
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Message:", data);
      setProgress((prev) => [...prev, data]);
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket Error:", err);
    };

    ws.current.onclose = (event) => {
      console.log("WebSocket Closed", event.code, event.reason);
    };

    return () => {
      console.log("Closing WebSocket");
      ws.current?.close();
    };
  }, [sessionId]);

  return progress;
}