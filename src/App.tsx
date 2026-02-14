import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import JoinCourse from "./pages/JoinCourse";
import ProfileBuilder from "./pages/ProfileBuilder";
import MatchFeed from "./pages/MatchFeed";
import PodPage from "./pages/PodPage";
import { useLocalStorage } from "./hooks/useLocalStorage";

function RequireSession({ children }: { children: JSX.Element }) {
  const [userId] = useLocalStorage<string | null>("cc_userId", null);
  const [courseCode] = useLocalStorage<string | null>("cc_courseCode", null);
  if (!userId || !courseCode) return <Navigate to="/" replace />;
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
