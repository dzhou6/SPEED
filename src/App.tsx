import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import JoinCourse from "./pages/JoinCourse";
import ProfileBuilder from "./pages/ProfileBuilder";
import MatchFeed from "./pages/MatchFeed";
import PodPage from "./pages/PodPage";
import { useLocalStorage } from "./hooks/useLocalStorage";

// Check if string is a valid MongoDB ObjectId format (24 hex characters)
function isValidObjectId(id: string | null): boolean {
  if (!id) return false;
  // MongoDB ObjectId is 24 hex characters
  return /^[0-9a-fA-F]{24}$/.test(id);
}

function RequireSession({ children }: { children: JSX.Element }) {
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);
  
  // Validate userId is a valid ObjectId format (backend requirement)
  if (!userId || !courseCode || !isValidObjectId(userId)) {
    // Clear invalid session data
    if (userId && !isValidObjectId(userId)) {
      localStorage.removeItem("cc_userId");
      localStorage.removeItem("cc_courseCode");
      localStorage.removeItem("cc_displayName");
    }
    return <Navigate to="/" replace />;
  }
  
  return children;
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<JoinCourse />} />
        <Route
          path="/profile"
          element={
            <RequireSession>
              <ProfileBuilder />
            </RequireSession>
          }
        />
        <Route
          path="/feed"
          element={
            <RequireSession>
              <MatchFeed />
            </RequireSession>
          }
        />
        <Route
          path="/pod"
          element={
            <RequireSession>
              <PodPage />
            </RequireSession>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
