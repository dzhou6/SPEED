import { useEffect, useMemo, useState } from "react";
import { api, qs } from "../api/client";
import type { AskResponse, PodMember, PodState, SetHubRequest, TicketResponse } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { useInterval } from "../hooks/useInterval";
import { toast } from "../components/Toast";

export type CourseInfo = {
  courseCode: string;
  courseName?: string;
  syllabusText?: string;
  professor?: string;
  location?: string;
  classPolicy?: string;
  latePolicy?: string;
  officeHours?: string;
};

export type UserCoursesResponse = {
  courseCodes: string[];
  courses?: Array<{
    courseCode: string;
    courseName?: string;
  }>;
};

// JoinCourse.tsx expects res.displayName
export interface DemoAuthResponse {
  userId: string;
  courseCode: string;
  token?: string;
  displayName?: string;
}

export interface TicketResponse {
  ok: boolean;
  ticketId?: string;
  message?: string;
}

type PodMemberView = PodMember & {
  roles?: string[];
  skills?: string[];
  lastActive?: string;
  // allow older/newer contact shapes during hackathon
  contact?: PodMember["contact"] & { email?: string | null };
};

function roomSlug(raw: string) {
  return (
    raw
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "")
      .slice(0, 64) || "pod"
  );
}

async function copyLink(url: string) {
  try {
    await navigator.clipboard.writeText(url);
    toast("Copied link.", "success");
  } catch {
    // fallback if clipboard is blocked
    window.prompt("Copy this link:", url);
  }
}



function isUnlocked(meId: string, m: PodMember, unlockedIds?: string[]) {
  if (m.userId === meId) return true;
  if (m.contactUnlocked === true) return true;
  //if (m.mutualAccepted === true) return true;
  // Check if userId is in unlockedContactIds array from backend
  if (unlockedIds?.includes(m.userId)) return true;
  // Some backends might embed something else; default locked.
  return false;
}

function normalizeLinks(links?: AskResponse["links"]) {
  if (!links) return [];
  if (Array.isArray(links)) {
    return links.map((x: any) => {
      if (typeof x === "string") return { title: x, url: x };
      return { title: x.title || x.url || "link", url: x.url || x.title || "" };
    });
  }
  return [];
}

function slugifyRoom(input: string) {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
}

// Deterministic 5-letter key for PairDrop rooms
function roomKey5(input: string) {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
  }
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  let out = "";
  let x = hash;
  for (let i = 0; i < 5; i++) {
    out += letters[x % 26];
    x = Math.floor(x / 26);
  }
  return out;
}


export default function PodPage() {
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);

  const [pod, setPod] = useState<PodState | null>(null);
  const [hubDraft, setHubDraft] = useState("");
  const [loadingPod, setLoadingPod] = useState(false);

  // Help widget state
  const [question, setQuestion] = useState("");
  const [ai, setAi] = useState<AskResponse | null>(null);
  const [ticket, setTicket] = useState<TicketResponse | null>(null);
  const [asking, setAsking] = useState(false);
  const [escalating, setEscalating] = useState(false);

const leaderId = useMemo(() => {
  const p: any = pod;
  return p?.leaderId ?? p?.leaderUserId ?? p?.members?.[0]?.userId ?? null;
}, [pod]);

const meLeader = useMemo(() => {
  if (!userId) return false;
  return leaderId === userId;
}, [leaderId, userId]);

const members = useMemo<PodMemberView[]>(() => {
  const mems = (pod?.members ?? []) as PodMemberView[];

  return mems.map((m) => {
    const roles = (m as any).roles ?? (m as any).rolePrefs ?? [];
    const lastActive =
      (m as any).lastActive ??
      ((m as any).lastActiveAt ? formatLastActive((m as any).lastActiveAt) : undefined);

    return { ...m, roles, lastActive };
  });
}, [pod]);


  function formatLastActive(iso: string): string {
    try {
      const d = new Date(iso);
      const diffMs = Date.now() - d.getTime();
      const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      if (days <= 0) return "active today";
      if (days === 1) return "active 1d ago";
      return `active ${days}d ago`;
    } catch {
      return iso;
    }
  }

  async function fetchPod(showErrors = false) {
    if (!courseCode) return;
    setLoadingPod(true);
    try {
      const p = await api<PodState>(`/pod${qs({ courseCode })}`, "GET");
      setPod(p || null);
      if (p?.hubLink && !hubDraft) setHubDraft(p.hubLink);
    } catch (e: any) {
      if (showErrors) toast(e?.message || "Failed to load pod.", "error");
    } finally {
      setLoadingPod(false);
    }
  }

  async function heartbeat() {
    if (!courseCode || !userId) return;
    try {
      await api("/heartbeat", "POST", { courseCode, userId });
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    fetchPod(true);
    heartbeat();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll pod every 5 seconds (reduced frequency to avoid server spam)
  useInterval(() => {
    if (!loadingPod) { // Don't poll if already loading
      fetchPod(false);
    }
  }, 5000);

  // Heartbeat every 20 seconds
  useInterval(() => {
    heartbeat();
  }, 20000);

  async function setHub() {
    if (!courseCode || !userId) return toast("Missing session.", "error");
    if (!hubDraft.trim()) return toast("Paste a Google Doc/Sheet link.", "error");
    try {
      const payload: SetHubRequest = { courseCode, userId, hubLink: hubDraft.trim() };
      await api("/pod/hub", "POST", payload);
      toast("Pod Hub link set.", "success");
      await fetchPod(false);
    } catch (e: any) {
      toast(e?.message || "Failed to set hub link.", "error");
    }
  }

  async function askAutoRoute() {
    if (!courseCode || !userId) return toast("Missing session.", "error");
    if (!question.trim()) return toast("Type a question.", "error");
    setAsking(true);
    setTicket(null);
    setAi(null); // Clear previous answer when asking new question
    try {
      const res = await api<AskResponse>("/ask", "POST", {
        courseCode,
        question: question.trim(),
      }, userId);
      setAi(res || { layer: 1, answer: "No response." });
    } catch (e: any) {
      toast(e?.message || "Ask failed.", "error");
    } finally {
      setAsking(false);
    }
  }

  function handleQuestionChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuestion(e.target.value);
    // Clear previous answer when user starts typing a new question
    if (ai) {
      setAi(null);
    }
  }

  async function escalate() {
    if (!courseCode || !userId) return toast("Missing session.", "error");
    if (!question.trim()) return toast("Type a question.", "error");
    setEscalating(true);
    try {
      const res = await api<TicketResponse>("/tickets", "POST", {
        courseCode,
        userId,
        question: question.trim(),
      });
      setTicket(res || { message: "Ticket created." });
      toast("Ticket created. Use Pod Hub to coordinate.", "success");
      await fetchPod(false);
    } catch (e: any) {
      toast(e?.message || "Ticket failed.", "error");
    } finally {
      setEscalating(false);
    }
  }

  return (
    <div className="card">
      <h1>Pod Page</h1>
      <p className="muted">
        Contact cards unlock only after mutual accept. Pod Hub is set by leader.
      </p>

      {!hasPod ? (
        <div className="empty">
          <div className="emptyTitle">No pod yet</div>
          <div className="muted">Go to the Match Feed and Accept a few people.</div>
        </div>
      ) : (
        <>
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div className="muted">
              Pod: <b>{pod?.podId || "unknown"}</b> · Members: <b>{members.length}</b>/4
            </div>
            <button className="btn" onClick={() => fetchPod(true)} disabled={loadingPod}>
              {loadingPod ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          <div className="section">
            <div className="label">Pod members</div>
            <div className="grid">
              {members.map((m) => {
                const unlocked = userId ? isUnlocked(userId, m, pod?.unlockedContactIds) : false;
                return (
                  <div key={m.userId} className="memberCard">
                    <div className="name">{m.displayName || "Anonymous"}</div>
                    <div className="muted small">
                      {m.roles?.slice(0, 2).join(", ") || "Role n/a"} ·{" "}
                      {m.skills?.slice(0, 3).join(", ") || "Skills n/a"}
                    </div>
                    <div className={`lock ${unlocked ? "unlocked" : "locked"}`}>
                      {unlocked ? "Unlocked ✅" : "Locked 🔒"}
                    </div>

                    <div className="contact">
                      {unlocked ? (
                        <>
                          <div><b>LinkedIn:</b> {m.contact?.linkedin || "contact revealed"}</div>
                          <div><b>Discord:</b> {m.contact?.discord || "contact revealed"}</div>
                          <div><b>Email:</b> {m.contact?.email || "contact revealed"}</div>
                        </>
                      ) : (
                        <div className="muted">Mutual accept required to reveal contact.</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

             <div className="section">
  <div className="label">Pod Hub</div>

  <div className="notice">
    <div className="muted" style={{ marginBottom: 8 }}>
      Instant links (no email required). Share these with your pod:
    </div>

    <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
      <span className="badge">Video + chat</span>
      <a className="link" href={quickLinks.video} target="_blank" rel="noreferrer">open</a>
      <button className="btn" onClick={() => copyLink(quickLinks.video)}>Copy</button>
    </div>

    <div className="row" style={{ gap: 8, flexWrap: "wrap", marginTop: 8 }}>
      <span className="badge">Whiteboard</span>
      <a className="link" href={quickLinks.whiteboard} target="_blank" rel="noreferrer">open</a>
      <button className="btn" onClick={() => copyLink(quickLinks.whiteboard)}>Copy</button>
    </div>

    <div className="row" style={{ gap: 8, flexWrap: "wrap", marginTop: 8 }}>
      <span className="badge">File drop</span>
      <a className="link" href={quickLinks.files} target="_blank" rel="noreferrer">open</a>
      <button className="btn" onClick={() => copyLink(quickLinks.files)}>Copy</button>
    </div>
  </div>

  {pod?.hubLink ? (
    <div className="notice">
      Custom hub:{" "}
      <a className="link" href={pod.hubLink} target="_blank" rel="noreferrer">
        {pod.hubLink}
      </a>
    </div>
  ) : meLeader ? (
    <div className="row">
      <input
        className="input"
        value={hubDraft}
        onChange={(e) => setHubDraft(e.target.value)}
        placeholder="Optional: paste Google Doc/Sheet link"
      />
      <button className="btn primary" onClick={setHub}>
        Set custom hub link
      </button>
    </div>
  ) : (
    <div className="muted">Leader can optionally set a custom Pod Hub link.</div>
  )}
</div>



          <div className="section">
            <div className="label">Ask for Help</div>
            <div className="row">
              <input
                className="input"
                value={question}
                onChange={handleQuestionChange}
                onKeyDown={(e) => e.key === "Enter" && !asking && askAutoRoute()}
                placeholder="Ask a question about the syllabus"
              />
            </div>

            <div className="actions">
              <button className="btn primary" onClick={askAutoRoute} disabled={asking}>
                {asking ? "Asking..." : "Ask (Auto-route)"}
              </button>
              <button className="btn" onClick={escalate} disabled={escalating}>
                {escalating ? "Creating..." : "Escalate to Pod"}
              </button>
            </div>

            {ai ? (
              <div className="aiBox">
                <div className="badge">{ai.layer || "Layer ?"}</div>
                <div className="aiAnswer">{ai.answer || "No answer returned."}</div>
                {normalizeLinks(ai.links).length ? (
                  <div className="aiLinks">
                    <div className="label">Links</div>
                    <ul>
                      {normalizeLinks(ai.links).slice(0, 6).map((l, i) => (
                        <li key={i}>
                          <a className="link" href={l.url} target="_blank" rel="noreferrer">
                            {l.title || l.url}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : null}

            {ticket ? (
              <div className="notice">
                Ticket created{ticket.ticketId ? `: ${ticket.ticketId}` : ""}.{" "}
                {pod?.hubLink ? (
                  <>
                    Use Pod Hub:{" "}
                    <a className="link" href={pod.hubLink} target="_blank" rel="noreferrer">
                      open hub
                    </a>
                  </>
                ) : (
                  "Waiting on leader to set Pod Hub."
                )}
              </div>
            ) : null}
          </div>
        </>
      )}
    </div>
  );
}
