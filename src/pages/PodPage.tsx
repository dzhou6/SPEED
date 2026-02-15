import { useEffect, useMemo, useState } from "react";
import { api, qs } from "../api/client";
import type { AskResponse, PodMember, PodState, SetHubRequest, TicketResponse } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { useInterval } from "../hooks/useInterval";
import { toast } from "../components/Toast";

function isUnlocked(meId: string, m: PodMember, unlockedIds?: string[]) {
  if (m.userId === meId) return true;
  if (m.contactUnlocked === true) return true;
  if (m.mutualAccepted === true) return true;
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

  const meLeader = useMemo(() => {
    if (!userId) return false;
    return pod?.leaderId === userId || pod?.leaderUserId === userId;
  }, [pod?.leaderId, pod?.leaderUserId, userId]);

  const members = useMemo(() => {
    const mems = pod?.members || [];
    // Map rolePrefs to roles for compatibility
    return mems.map(m => ({
      ...m,
      roles: m.roles || m.rolePrefs,
      lastActive: m.lastActive || (m.lastActiveAt ? formatLastActive(m.lastActiveAt) : undefined)
    }));
  }, [pod?.members]);
  const hasPod = useMemo(() => {
    if (pod?.hasPod === false) return false;
    return !!pod?.podId && members.length > 0;
  }, [pod?.hasPod, pod?.podId, members.length]);
  
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
      const payload: SetHubRequest = { courseCode, hubLink: hubDraft.trim() };
      await api("/pod/hub", "POST", payload, userId);
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
        question: question.trim(),
      }, userId);
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
            {pod?.hubLink ? (
              <div className="notice">
                Hub link:{" "}
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
                  placeholder="Paste Google Doc/Sheet link"
                />
                <button className="btn primary" onClick={setHub}>
                  Set Pod Hub link
                </button>
              </div>
            ) : (
              <div className="muted">Waiting for leader to set Pod Hub.</div>
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
