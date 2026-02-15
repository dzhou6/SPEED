import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { DemoAuthResponse } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { toast } from "../components/Toast";

export default function JoinCourse() {
  const nav = useNavigate();
  const [courseCode, setCourseCode] = useState("CS471");
  const [, setStoredCourse] = useLocalStorage<string | null>("cc_courseCode", null);
  const [, setUserId] = useLocalStorage<string | null>("cc_userId", null);
  const [, setDisplayName] = useLocalStorage<string | null>("cc_displayName", null);
  const [loading, setLoading] = useState(false);

  const normalized = useMemo(() => courseCode.trim().toUpperCase(), [courseCode]);

  async function join() {
    if (!normalized) return toast("Enter a course code.", "error");
    setLoading(true);
    try {
      // Clear any old invalid userIds first
      const oldUserId = localStorage.getItem("cc_userId");
      if (oldUserId && !/^[0-9a-fA-F]{24}$/.test(oldUserId)) {
        localStorage.removeItem("cc_userId");
        localStorage.removeItem("cc_courseCode");
        localStorage.removeItem("cc_displayName");
      }
      
      // Call backend to create/get user
      const res = await api<DemoAuthResponse>("/auth/demo", "POST", { courseCode: normalized });
      if (!res?.userId) throw new Error("Backend did not return userId.");
      
      // Validate the userId is a valid ObjectId
      if (!/^[0-9a-fA-F]{24}$/.test(res.userId)) {
        throw new Error("Backend returned invalid userId format. Please try again.");
      }
      
      setStoredCourse(normalized);
      setUserId(res.userId);
      if (res.displayName) setDisplayName(res.displayName);
      toast("Joined! Build your profile.", "success");
      nav("/profile");
    } catch (e: any) {
    const msg = String(e?.message || "");
    const isConnRefused =
      msg.includes("Failed to fetch") ||
      msg.includes("ERR_CONNECTION_REFUSED") ||
      msg.includes("NetworkError");

    // Only use offline fallback if backend is truly unreachable
    // But note: this creates invalid userIds that won't work with real backend
    if (isConnRefused) {
      toast("Backend is offline. Please start the backend server first.", "error");
      // Don't create demo userId - it won't work with backend
      // User needs to start backend and try again
      return;
    }

    // For other errors (like 400, 500, etc), show the error
    toast(e?.message || "Join failed. Make sure backend is running.", "error");
  } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h1>Landing / Join Course</h1>
      <p className="muted">
        Demo login only. No real auth. This is built for a clean 2-minute judge flow.
      </p>

      <div className="row">
        <label className="label">Course code</label>
        <input
          className="input"
          value={courseCode}
          onChange={(e) => setCourseCode(e.target.value)}
          placeholder="CS471"
        />
      </div>

      <button className="btn primary" onClick={join} disabled={loading}>
        {loading ? "Joining..." : "Join"}
      </button>

      <div className="hr" />

      <button
        className="btn"
        onClick={() => {
          localStorage.removeItem("cc_userId");
          localStorage.removeItem("cc_courseCode");
          localStorage.removeItem("cc_displayName");
          toast("Local demo session cleared.", "info");
        }}
      >
        Reset demo session
      </button>
    </div>
  );
}
