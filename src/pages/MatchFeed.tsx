import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, qs } from "../api/client";
import type { PodState, RecommendationUser, RecommendationsResponse, SwipeRequest } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { useInterval } from "../hooks/useInterval";
import { toast } from "../components/Toast";

const DEMO_CANDIDATES = [
  {
    userId: "demo_u1",
    displayName: "Ava",
    roles: ["Backend"],
    skills: ["Python", "APIs", "FastAPI", "MongoDB"],
    availability: ["Mon evening", "Wed evening"],
    lastActive: "active today",
    reasons: ["You picked Frontend; they picked Backend", "Overlapping evenings"],
  },
  {
    userId: "demo_u2",
    displayName: "Noah",
    roles: ["Matching"],
    skills: ["ML", "Python", "Data"],
    availability: ["Tue evening", "Thu evening"],
    lastActive: "active 1d ago",
    reasons: ["Complements your role mix", "Strong optimization/ML"],
  },
  {
    userId: "demo_u3",
    displayName: "Mia",
    roles: ["Platform"],
    skills: ["Docker", "Git", "AWS"],
    availability: ["Fri evening", "Sat afternoon"],
    lastActive: "active 2d ago",
    reasons: ["Can deploy and keep things stable"],
  },
];


function pickTop(list?: string[], n = 3) {
  return (list || []).slice(0, n);
}

function lastActiveBadge(raw?: string) {
  if (!raw) return "unknown";
  // If backend already gives “active today” style text, pass it through.
  if (raw.includes("active") || raw.includes("ago") || raw.includes("today")) return raw;
  // Try ISO date
  const d = new Date(raw);
  if (!isNaN(d.getTime())) {
    const diffMs = Date.now() - d.getTime();
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (days <= 0) return "active today";
    if (days === 1) return "active 1d ago";
    return `active ${days}d ago`;
  }
  return raw;
}

export default function MatchFeed() {
  const nav = useNavigate();
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);

  const [candidates, setCandidates] = useState<RecommendationUser[]>([]);
  const [pod, setPod] = useState<PodState | null>(null);
  const [loading, setLoading] = useState(false);
  const [swiping, setSwiping] = useState<string | null>(null);

  const hasPod = useMemo(() => !!pod?.podId && (pod.members?.length || 0) > 0, [pod]);

  async function load() {
    if (!courseCode) return;
    setLoading(true);
   try {
  const rec = await api<RecommendationsResponse>(`/recommendations${qs({ courseCode })}`, "GET");
  const list = rec?.candidates || [];

  // If backend returns empty, fall back to demo candidates
  setCandidates(list.length ? list : DEMO_CANDIDATES);

  // Refresh pod state too
  const p = await api<PodState>(`/pod${qs({ courseCode })}`, "GET");
  setPod(p || null);

  // If pod formed, nudge user to pod page (demo flow)
  if (p?.podId && (p.members?.length || 0) > 0) {
    toast("It’s a match 💘 Pod formed!", "success");
    nav("/pod");
  }
} catch (e: any) {
  const msg = String(e?.message || "");
  const isConnRefused =
    msg.includes("Failed to fetch") ||
    msg.includes("ERR_CONNECTION_REFUSED") ||
    msg.includes("NetworkError");

  if (isConnRefused) {
    setCandidates(DEMO_CANDIDATES);
    toast("Backend offline — using demo matches.", "info");
    return;
  }

  toast(e?.message || "Failed to load matches.", "error");
} finally {
  setLoading(false);
}

  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll pod every 5s while in feed
  useInterval(async () => {
    if (!courseCode) return;
    try {
      const p = await api<PodState>(`/pod${qs({ courseCode })}`, "GET");
      setPod(p || null);
      if (p?.podId && (p.members?.length || 0) > 0) {
        toast("It’s a match 💘 Pod formed!", "success");
        nav("/pod");
      }
    } catch {
      // ignore transient polling errors
    }
  }, 5000);

  async function swipe(targetUserId: string, decision: "accept" | "pass") {
    if (!userId || !courseCode) return toast("Missing session.", "error");
    setSwiping(targetUserId);
    try {
      const payload: SwipeRequest = { courseCode, userId, targetUserId, decision };
      await api("/swipe", "POST", payload);
      // Refresh after swipe
      await load();
    } catch (e: any) {
      toast(e?.message || "Swipe failed.", "error");
    } finally {
      setSwiping(null);
    }
  }

  return (
    <div className="card">
      <h1>Match Feed</h1>
      <p className="muted">
        Accept or pass. Mutual accept triggers “It’s a match” and routes you to the Pod page.
      </p>

      {hasPod ? (
        <div className="notice">
          You already have a pod.{" "}
          <button className="link" onClick={() => nav("/pod")}>Go to Pod</button>
        </div>
      ) : null}

      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div className="muted">Course: <b>{courseCode}</b></div>
        <button className="btn" onClick={load} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {candidates.length === 0 ? (
        <div className="empty">
          <div className="emptyTitle">No matches yet</div>
          <div className="muted">Seeded demo mode should add a few profiles to recommend.</div>
        </div>
      ) : (
        <div className="grid">
          {candidates.map((u) => (
            <div key={u.userId} className="matchCard">
              <div className="matchTop">
                <div>
                  <div className="name">{u.displayName || "Anonymous"}</div>
                  <div className="muted small">
                    Roles: {pickTop(u.roles, 2).join(", ") || "n/a"}
                  </div>
                  <div className="muted small">
                    Skills: {pickTop(u.skills, 4).join(", ") || "n/a"}
                  </div>
                  <div className="muted small">
                    Availability: {pickTop(u.availability, 2).join(" • ") || "n/a"}
                  </div>
                </div>
                <span className="badge">{lastActiveBadge(u.lastActive)}</span>
              </div>

              {u.reasons?.length ? (
                <div className="why">
                  <div className="label">Why this match</div>
                  <ul>
                    {u.reasons.slice(0, 3).map((r, idx) => <li key={idx}>{r}</li>)}
                  </ul>
                </div>
              ) : null}

              <div className="actions">
                <button
                  className="btn primary"
                  onClick={() => swipe(u.userId, "accept")}
                  disabled={swiping === u.userId}
                >
                  {swiping === u.userId ? "..." : "Accept"}
                </button>
                <button
                  className="btn"
                  onClick={() => swipe(u.userId, "pass")}
                  disabled={swiping === u.userId}
                >
                  {swiping === u.userId ? "..." : "Pass"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
