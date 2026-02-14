import { ReactNode, useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ToastHost from "./Toast";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { api, qs } from "../api/client";
import type { UserCoursesResponse, CourseInfo } from "../api/types";

export default function Layout({ children }: { children: ReactNode }) {
  const nav = useNavigate();
  const location = useLocation();
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode, setCourseCode] = useLocalStorage<string | null>("cc_courseCode", null);
  const [userCourses, setUserCourses] = useState<UserCoursesResponse | null>(null);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [theme, setTheme] = useLocalStorage<"light" | "dark">("cc_theme", "dark");

  // Load user's courses if logged in - reload when userId or courseCode changes
  const loadCourses = useCallback(async () => {
    if (!userId || !/^[0-9a-fA-F]{24}$/.test(userId)) {
      setUserCourses(null);
      return;
    }
    setLoadingCourses(true);
    try {
      const courses = await api<UserCoursesResponse>("/user/courses", "GET", undefined, userId);
      setUserCourses(courses);
      console.log("Loaded user courses:", courses);
    } catch (e) {
      // User might not have courses yet
      console.error("Error loading courses:", e);
      setUserCourses(null);
    } finally {
      setLoadingCourses(false);
    }
  }, [userId]);

  useEffect(() => {
    loadCourses();
  }, [loadCourses, courseCode, location.pathname]); // Reload when courseCode or route changes

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(theme === "dark" ? "light" : "dark");
  }

  function switchCourse(newCourseCode: string) {
    if (newCourseCode === courseCode) return;
    setCourseCode(newCourseCode);
    // Navigate to feed to reload data for new course
    if (location.pathname !== "/") {
      nav("/feed", { replace: true });
    }
  }

  const showCourseSwitcher = userId && userCourses && userCourses.courseCodes.length > 0 && location.pathname !== "/";

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo">💘</div>
          <div style={{ flex: 1 }}>
            <div className="title">CourseCupid / StackMatch</div>
            <div className="subtitle">Hackathon pod matchmaking MVP</div>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {showCourseSwitcher && (
              <>
                <select
                  value={courseCode || ""}
                  onChange={(e) => switchCourse(e.target.value)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: "8px",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                    color: "var(--text)",
                    fontSize: "13px",
                    cursor: "pointer"
                  }}
                >
                  {userCourses.courseCodes && userCourses.courseCodes.length > 0 ? (
                    // Always show all courseCodes, use course details if available
                    userCourses.courseCodes.map((code) => {
                      // Find course details if available
                      const courseDetail = userCourses.courses?.find(c => c.courseCode === code);
                      return (
                        <option key={code} value={code}>
                          {code}{courseDetail?.courseName ? ` - ${courseDetail.courseName}` : ""}
                        </option>
                      );
                    })
                  ) : (
                    <option value="">No courses</option>
                  )}
                </select>
                <button
                  className="link"
                  onClick={() => {
                    loadCourses(); // Refresh courses list
                    nav("/");
                  }}
                  style={{ fontSize: "12px", padding: "4px 8px" }}
                >
                  + Add Course
                </button>
              </>
            )}
            <button
              onClick={toggleTheme}
              className="btn"
              style={{
                padding: "6px 10px",
                fontSize: "16px",
                minWidth: "40px"
              }}
              title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {theme === "dark" ? "☀️" : "🌙"}
            </button>
          </div>
        </div>
      </header>

      <main className="container">{children}</main>
      <ToastHost />
    </div>
  );
}
