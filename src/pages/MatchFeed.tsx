import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, qs } from "../api/client";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { useToast } from "../components/Toast";
import type {
  AskResponse,
  CourseInfo,
  PodState,
  RecommendationUser,
  RecommendationsResponse,
  SwipeRequest,
} from "../api/types";

const DEMO_CANDIDATES: RecommendationUser[] = [
  {
    userId: "demo-1",
    displayName: "Avery",
    rolePrefs: ["Frontend"],
    skills: ["React", "UI polish", "Docs"],
    availability: ["Mon 2–4", "Wed 6–8"],
    lastActiveAt: new Date().toISOString(),
    score: 0.78,
    reasons: ["Similar availability", "Complementary role"],
  },
  {
    userId: "demo-2",
    displayName: "Jordan",
    rolePrefs: ["Backend"],
    skills: ["API design", "MongoDB", "FastAPI"],
    availability: ["Tue 1–3", "Thu 5–7"],
    lastActiveAt: new Date(Date.now() - 86400000).toISOString(),
    score: 0.74,
    reasons: ["Strong backend fit", "Overlapping times"],
  },
];

function fmtActive(iso?: string | null) {
  if (!iso) return "unknown";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "unknown";
  const days = Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24));
  if (days <= 0) return "active today";
  if (days === 1) return "active 1d ago";
  return `active ${days}d ago`;
}

export default function MatchFeed() {
  const nav = useNavigate();
  const toast = useToast();

  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);

  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null);
  const [candidates, setCandidates] = useState<RecommendationUser[]>([]);
  const [pod, setPod] = useState<PodState | null>(null);

  const [loading, setLoading] = useState(false);
  const [swiping, setSwiping] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [ai, setAi] = useState<AskResponse | null>(null);
  const [asking, setAsking] = useState(false);

  const [matchMode, setMatchMode] = useLocalStorage<"quickmatch" | "skillmatch">(
    "cc_matchMode",
    "skillmatch"
  );

  const hasPod = useMemo(() => {
    if (pod?.hasPod === false) return false;
    return !!pod?.podId && (pod as any)?.members?.length > 0;
  }, [pod]);

  async function loadAll() {
    if (!courseCode) return;
    setLoading(true);
    try {
      const rec = await api<RecommendationsResponse>(
        `/recommendations${qs({ courseCode, mode: matchMode })}`,
        "GET"
      );
      const list = rec?.candidates || [];
      setCandidates(list.length ? list : []);

      const p = await api<PodState>(`/pod${qs({ courseCode })}`, "GET");
      setPod(p || null);

      if (p?.podId && ((p as any)?.members?.length || 0) > 0) {
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
      } else {
        toast(e?.message || "Failed to load matches.", "error");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseCode, matchMode]);

  useEffect(() => {
    async function loadCourse() {
      if (!courseCode) return;
      try {
        const c = await api<CourseInfo>(`/course${qs({ courseCode })}`, "GET");
        setCourseInfo(c || null);
      } catch {
        // ignore: course info is optional for feed
      }
    }
    loadCourse();
  }, [courseCode]);

  async function swipe(targetUserId: string, decision: "accept" | "pass") {
    if (!userId || !courseCode) return toast("Missing session.", "error");
    setSwiping(targetUserId);
    try {
      const payload: SwipeRequest = { courseCode, targetUserId, decision };
      await api("/swipe", "POST", payload, userId);
      await loadAll();
    } catch (e: any) {
      toast(e?.message || "Swipe failed.", "error");
    } finally {
      setSwiping(null);
    }
  }

  async function askQuestion() {
    if (!userId || !courseCode) return toast("Missing session.", "error");
    if (!question.trim()) return toast("Type a question.", "error");
    setAsking(true);
    setAi(null);
    try {
      const res = await api<AskResponse>(
        "/ask",
        "POST",
        { courseCode, question: question.trim() },
        userId
      );
      setAi(res || { layer: 1, answer: "No response." });
    } catch (e: any) {
      toast(e?.message || "Ask failed.", "error");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Match Feed</h1>
          <div className="muted">
            {courseInfo?.courseName ? (
              <>
                <b>{courseCode}</b> · {courseInfo.courseName}
              </>
            ) : (
              <>{courseCode}</>
            )}
          </div>
        </div>

        <div className="row" style={{ gap: 8 }}>
          <button
            className={matchMode === "quickmatch" ? "btn" : "btn ghost"}
            onClick={() => setMatchMode("quickmatch")}
            disabled={loading}
            title="Faster matching: availability + overlap"
          >
            Quick
          </button>
          <button
            className={matchMode === "skillmatch" ? "btn" : "btn ghost"}
            onClick={() => setMatchMode("skillmatch")}
            disabled={loading}
            title="Stronger matching: roles + skills"
          >
            Skill
          </button>
        </div>
      </div>

      {hasPod ? (
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
          <div className="muted">You’re in a pod.</div>
          <button className="btn" onClick={() => nav("/pod")}>
            Go to Pod
          </button>
        </div>
      ) : null}

      <div style={{ marginTop: 16 }}>
        <h2>People</h2>
        {loading ? <div className="muted">Loading…</div> : null}

        {!loading && candidates.length === 0 ? (
          <div className="empty">
            <div className="emptyTitle">No matches yet</div>
            <div className="muted">Try switching mode, or come back later.</div>
          </div>
        ) : null}

        <div className="grid" style={{ marginTop: 12 }}>
          {candidates.map((c) => (
            <div key={c.userId} className="card" style={{ padding: 14 }}>
              <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{c.displayName}</div>
                  <div className="muted">
                    {c.rolePrefs?.slice(0, 2).join(", ") || "Role n/a"} · {fmtActive(c.lastActiveAt)}
                  </div>
                </div>
                <div className="muted">score {Math.round((c.score || 0) * 100)}%</div>
              </div>

              <div style={{ marginTop: 10 }}>
                <div className="muted">Skills</div>
                <div>{(c.skills || []).slice(0, 6).join(" · ") || "—"}</div>
              </div>

              <div style={{ marginTop: 10 }}>
                <div className="muted">Why</div>
                <ul style={{ margin: "6px 0 0 16px" }}>
                  {(c.reasons || []).slice(0, 3).map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>

              <div className="row" style={{ gap: 8, marginTop: 12 }}>
                <button
                  className="btn ghost"
                  onClick={() => swipe(c.userId, "pass")}
                  disabled={swiping === c.userId}
                >
                  Pass
                </button>
                <button
                  className="btn"
                  onClick={() => swipe(c.userId, "accept")}
                  disabled={swiping === c.userId}
                >
                  Accept
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 18 }}>
        <h2>Ask the Syllabus Assistant</h2>
        <div className="row" style={{ gap: 8, marginTop: 8 }}>
          <input
            style={{ flex: 1 }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something about the course…"
          />
          <button className="btn" onClick={askQuestion} disabled={asking}>
            {asking ? "Asking…" : "Ask"}
          </button>
        </div>

        {ai ? (
          <div style={{ marginTop: 10 }}>
            <div className="muted">Layer {ai.layer}</div>
            <pre style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>{ai.answer}</pre>
          </div>
        ) : null}
      </div>
    </div>
  );
}
