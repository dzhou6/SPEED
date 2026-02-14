import { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { RolePref } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { toast } from "../components/Toast";

// Check if string is a valid MongoDB ObjectId format (24 hex characters)
function isValidObjectId(id: string | null): boolean {
  if (!id) return false;
  return /^[0-9a-fA-F]{24}$/.test(id);
}

const ROLE_OPTIONS: RolePref[] = ["Frontend", "Backend", "Matching", "Platform"];

const SKILL_OPTIONS = [
  "Python", "JavaScript", "React", "APIs", "FastAPI", "MongoDB", "ML", "Writing",
  "Docker", "Git", "AWS", "Azure", "UI/UX", "Testing", "Data", "Security"
];

const AVAIL_BLOCKS = [
  "Mon evening", "Tue evening", "Wed evening", "Thu evening", "Fri evening",
  "Sat morning", "Sat afternoon", "Sun afternoon"
];

export default function ProfileBuilder() {
  const nav = useNavigate();
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);
  const [storedName, setStoredName] = useLocalStorage<string | null>("cc_displayName", null);

  const [displayName, setDisplayName] = useState(storedName || "");
  const [roles, setRoles] = useState<RolePref[]>(["Frontend"]);
  const [skills, setSkills] = useState<string[]>(["JavaScript", "React"]);
  const [availability, setAvailability] = useState<string[]>(["Mon evening", "Wed evening"]);
  const [goals, setGoals] = useState<string>("exam prep");
  const [loading, setLoading] = useState(false);

  const canSave = useMemo(() => roles.length >= 1 && roles.length <= 2, [roles]);

  function toggleRole(r: RolePref) {
    setRoles((prev) => {
      const exists = prev.includes(r);
      if (exists) return prev.filter((x) => x !== r);
      if (prev.length >= 2) {
        toast("Pick up to 2 roles.", "info");
        return prev;
      }
      return [...prev, r];
    });
  }

  function toggle(list: string[], item: string, set: (v: string[]) => void) {
    set(list.includes(item) ? list.filter((x) => x !== item) : [...list, item]);
  }

  // Redirect if userId is invalid - check immediately on mount
  useEffect(() => {
    if (userId && !isValidObjectId(userId)) {
      console.log("Invalid userId detected, redirecting to join page");
      localStorage.removeItem("cc_userId");
      localStorage.removeItem("cc_courseCode");
      localStorage.removeItem("cc_displayName");
      toast("Invalid session. Please join the course again.", "error");
      nav("/", { replace: true });
    }
  }, [userId, nav]);

  async function save() {
    if (!userId || !courseCode) {
      toast("Missing session. Go back to Join.", "error");
      nav("/");
      return;
    }
    
    // Validate userId format before making API call
    if (!isValidObjectId(userId)) {
      toast("Invalid session. Please join the course again.", "error");
      localStorage.removeItem("cc_userId");
      localStorage.removeItem("cc_courseCode");
      localStorage.removeItem("cc_displayName");
      nav("/");
      return;
    }
    
    if (!canSave) return toast("Choose 1–2 roles.", "error");

    setLoading(true);
    try {
      // Backend expects rolePrefs (not roles) and doesn't need userId in body (uses header)
      const payload = {
        courseCode,
        displayName: displayName.trim() || undefined,
        rolePrefs: roles,  // Backend expects rolePrefs
        skills,
        availability,
        goals: goals.trim() || undefined,
      };
      console.log("Saving profile with userId:", userId, "courseCode:", courseCode, "userId length:", userId?.length);
      // Pass userId explicitly to ensure we use the component's state value
      await api("/profile", "POST", payload, userId);
      if (displayName.trim()) setStoredName(displayName.trim());
      toast("Profile saved. Swipe matches.", "success");
      nav("/feed");
      } catch (e: any) {
    const msg = String(e?.message || "");
    console.error("Profile save error:", msg, e);
    
    // Handle invalid session error - redirect to join
    if (msg.includes("Invalid session") || msg.includes("No session found")) {
      // Clear localStorage only on session errors
      localStorage.removeItem("cc_userId");
      localStorage.removeItem("cc_courseCode");
      localStorage.removeItem("cc_displayName");
      toast(msg, "error");
      nav("/");
      return;
    }
    
    const isConnRefused =
      msg.includes("Failed to fetch") ||
      msg.includes("ERR_CONNECTION_REFUSED") ||
      msg.includes("NetworkError");

    if (isConnRefused) {
      const localProfile = {
        userId,
        courseCode,
        displayName,
        roles,
        skills,
        availability,
        goals,
      };
      localStorage.setItem("cc_profile", JSON.stringify(localProfile));
      toast("Backend offline — saved locally. Continuing demo.", "info");
      nav("/feed");
      return;
    }

    toast(e?.message || "Save failed.", "error");
  }



      setLoading(false);
    }
  

  return (
    <div className="card">
      <h1>Profile Builder</h1>
      <p className="muted">Keep it simple. This is the judge-friendly demo path.</p>

      <div className="row">
        <label className="label">Display name (optional)</label>
        <input className="input" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="David" />
      </div>

      <div className="section">
        <div className="label">Role preferences (choose 1–2)</div>
        <div className="chips">
          {ROLE_OPTIONS.map((r) => (
            <button
              key={r}
              className={`chip ${roles.includes(r) ? "on" : ""}`}
              onClick={() => toggleRole(r)}
              type="button"
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <div className="label">Skills tags</div>
        <div className="chips">
          {SKILL_OPTIONS.map((s) => (
            <button
              key={s}
              className={`chip ${skills.includes(s) ? "on" : ""}`}
              onClick={() => toggle(skills, s, setSkills)}
              type="button"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <div className="label">Availability</div>
        <div className="chips">
          {AVAIL_BLOCKS.map((b) => (
            <button
              key={b}
              className={`chip ${availability.includes(b) ? "on" : ""}`}
              onClick={() => toggle(availability, b, setAvailability)}
              type="button"
            >
              {b}
            </button>
          ))}
        </div>
      </div>

      <div className="row">
        <label className="label">Goals (optional)</label>
        <input className="input" value={goals} onChange={(e) => setGoals(e.target.value)} placeholder="exam prep, homework help..." />
      </div>

      <button className="btn primary" onClick={save} disabled={loading}>
        {loading ? "Saving..." : "Save profile"}
      </button>
    </div>
  );

}