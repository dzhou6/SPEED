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
      // Works whether backend expects {courseCode} or ignores it.
      const res = await api<DemoAuthResponse>("/auth/demo", "POST", { courseCode: normalized });
      if (!res?.userId) throw new Error("Backend did not return userId.");
      setStoredCourse(normalized);
      setUserId(res.userId);
      if (res.displayName) setDisplayName(res.displayName);
      toast("Joined! Build your profile.", "success");
      nav("/profile");
    } catch (e: any) {
    // OFFLINE DEMO FALLBACK: if backend isn't running, still proceed for demo
    const msg = String(e?.message || "");
    const isConnRefused =
      msg.includes("Failed to fetch") ||
      msg.includes("ERR_CONNECTION_REFUSED") ||
      msg.includes("NetworkError");

    if (isConnRefused) {
      const demoUserId = `demo_${Math.random().toString(16).slice(2)}`;
      setStoredCourse(normalized);
      setUserId(demoUserId);
      setDisplayName("Demo User");
      toast("Backend offline — continuing in demo mode.", "info");
      nav("/profile");
      return;
    }

    toast(e?.message || "Join failed.", "error");
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
