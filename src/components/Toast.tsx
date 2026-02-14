import { useEffect, useState } from "react";

type Toast = { id: string; message: string; kind: "info" | "success" | "error" };

let pushFn: ((t: Omit<Toast, "id">) => void) | null = null;

export function toast(message: string, kind: Toast["kind"] = "info") {
  pushFn?.({ message, kind });
}

export default function ToastHost() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    pushFn = (t) => {
      const id = `${Date.now()}_${Math.random()}`;
      const next: Toast = { id, ...t };
      setToasts((prev) => [...prev, next]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== id));
      }, 2600);
    };
    return () => {
      pushFn = null;
    };
  }, []);

  return (
    <div className="toastHost">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.kind}`}>
          {t.message}
        </div>
      ))}
    </div>
  );
}
