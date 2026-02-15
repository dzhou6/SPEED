import { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, qs } from "../api/client";
import type { DemoAuthResponse, CourseInfo } from "../api/types";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { toast } from "../components/Toast";

export default function JoinCourse() {
  const nav = useNavigate();
  const [courseCode, setCourseCode] = useState("CS471");
  const [, setStoredCourse] = useLocalStorage<string | null>("cc_courseCode", null);
  const [, setUserId] = useLocalStorage<string | null>("cc_userId", null);
  const [, setDisplayName] = useLocalStorage<string | null>("cc_displayName", null);
  const [loading, setLoading] = useState(false);
  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null);
  const [loadingCourseInfo, setLoadingCourseInfo] = useState(false);

  const normalized = useMemo(() => courseCode.trim().toUpperCase(), [courseCode]);

  // Fetch course info when course code changes
  useEffect(() => {
    async function fetchCourseInfo() {
      if (!normalized || normalized.length < 3) {
        setCourseInfo(null);
        return;
      }
      setLoadingCourseInfo(true);
      try {
        const course = await api<CourseInfo>(`/course${qs({ courseCode: normalized })}`, "GET");
        setCourseInfo(course);
      } catch (e) {
        // Course not found or doesn't exist yet - that's okay
        setCourseInfo(null);
      } finally {
        setLoadingCourseInfo(false);
      }
    }
    
    // Debounce the API call
    const timeoutId = setTimeout(fetchCourseInfo, 500);
    return () => clearTimeout(timeoutId);
  }, [normalized]);

  async function join() {
    if (!normalized) return toast("Enter a course code.", "error");
    setLoading(true);
    try {
      // Check if user already exists
      const existingUserId = localStorage.getItem("cc_userId");
      const isExistingUser = existingUserId && /^[0-9a-fA-F]{24}$/.test(existingUserId);
      
      if (isExistingUser) {
        // Add course to existing user
        try {
          await api(`/user/add-course${qs({ courseCode: normalized })}`, "POST", undefined, existingUserId);
          setStoredCourse(normalized);
          toast(`Added ${normalized}! Refreshing courses...`, "success");
          // Navigate to feed - Layout will reload courses when courseCode changes
          nav("/feed");
          return;
        } catch (e: any) {
          // If add-course fails, fall through to create new user
          console.log("Could not add course to existing user, creating new user", e);
        }
      }
      
      // Clear any old invalid userIds first
      if (existingUserId && !/^[0-9a-fA-F]{24}$/.test(existingUserId)) {
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
      <h1>Join your course</h1>
      <p className="muted">
        Quick start (demo mode): no passwords. Join your class, build a learning profile, and CourseCupid will suggest study partners and project teammates. 💘📚
      </p>

      <div className="row">
        <label className="label">Course code</label>
        <input
          className="input"
          value={courseCode}
          onChange={(e) => setCourseCode(e.target.value)}
          placeholder="CS471, CS101, MATH200, CS330"
        />
      </div>

      {/* Display course information if available */}
      {loadingCourseInfo && normalized.length >= 3 && (
        <div className="muted" style={{ marginTop: "8px" }}>Loading course info...</div>
      )}

      {courseInfo && !loadingCourseInfo && (
        <div className="card" style={{ 
          marginTop: "16px", 
          padding: "16px"
        }}>
          <h3 style={{ marginTop: 0, marginBottom: "12px", color: "var(--text)" }}>
            {courseInfo.courseName || courseInfo.courseCode}
          </h3>
          
          {courseInfo.professor && (
            <div style={{ marginBottom: "8px", color: "var(--text)" }}>
              <strong style={{ color: "var(--primary2)" }}>Professor:</strong> {courseInfo.professor}
            </div>
          )}
          
          {courseInfo.location && (
            <div style={{ marginBottom: "8px", color: "var(--text)" }}>
              <strong style={{ color: "var(--primary2)" }}>Location:</strong> {courseInfo.location}
            </div>
          )}
          
          {courseInfo.officeHours && (
            <div style={{ marginBottom: "8px", color: "var(--text)" }}>
              <strong style={{ color: "var(--primary2)" }}>Office Hours:</strong> {courseInfo.officeHours}
            </div>
          )}

          {courseInfo.classPolicy && (
            <details style={{ marginTop: "12px", marginBottom: "8px" }}>
              <summary style={{ 
                cursor: "pointer", 
                fontWeight: "bold", 
                color: "var(--primary2)",
                fontSize: "0.95em"
              }}>
                Class Policies
              </summary>
              <div style={{ 
                marginTop: "8px", 
                padding: "12px", 
                background: "var(--card)", 
                borderRadius: "8px",
                whiteSpace: "pre-wrap",
                fontSize: "0.9em",
                color: "var(--text)",
                lineHeight: "1.5",
                border: "1px solid var(--border)"
              }}>
                {courseInfo.classPolicy}
              </div>
            </details>
          )}

          {courseInfo.latePolicy && (
            <details style={{ marginTop: "8px", marginBottom: "8px" }}>
              <summary style={{ 
                cursor: "pointer", 
                fontWeight: "bold", 
                color: "var(--primary2)",
                fontSize: "0.95em"
              }}>
                Late Submission Policy
              </summary>
              <div style={{ 
                marginTop: "8px", 
                padding: "12px", 
                background: "var(--card)", 
                borderRadius: "8px",
                whiteSpace: "pre-wrap",
                fontSize: "0.9em",
                color: "var(--text)",
                lineHeight: "1.5",
                border: "1px solid var(--border)"
              }}>
                {courseInfo.latePolicy}
              </div>
            </details>
          )}

          {courseInfo.syllabusText && (
            <details style={{ marginTop: "8px" }} open>
              <summary style={{ 
                cursor: "pointer", 
                fontWeight: "bold", 
                color: "var(--primary2)",
                fontSize: "0.95em"
              }}>
                Full Course Syllabus
              </summary>
              <div style={{ 
                marginTop: "8px", 
                padding: "16px", 
                background: "var(--card)", 
                borderRadius: "8px",
                whiteSpace: "pre-wrap",
                fontSize: "0.8em",
                color: "var(--text)",
                lineHeight: "1.6",
                border: "1px solid var(--border)",
                maxHeight: "500px",
                overflowY: "auto",
                overflowX: "hidden",
                fontFamily: "monospace"
              }}>
                {courseInfo.syllabusText}
              </div>
              <div style={{ 
                marginTop: "12px", 
                padding: "10px",
                fontSize: "0.85em", 
                color: "var(--muted)",
                fontStyle: "italic",
                background: "rgba(255,122,178,0.1)",
                borderRadius: "6px",
                border: "1px solid rgba(255,122,178,0.2)"
              }}>
                💡 Too much to read? Use the chatbox to ask questions instead!
              </div>
            </details>
          )}
        </div>
      )}

      {!courseInfo && !loadingCourseInfo && normalized.length >= 3 && (
        <div className="muted" style={{ marginTop: "8px", fontSize: "0.9em" }}>
          Course "{normalized}" not found. You can still join, but course information won't be available.
        </div>
      )}

      <button className="btn primary" onClick={join} disabled={loading} style={{ marginTop: "16px" }}>
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
