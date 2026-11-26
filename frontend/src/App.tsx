import { useEffect, useState } from "react";
import {
  NavLink,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { api } from "@/api/client";
import { clearSessionToken } from "@/lib/api";
import { Icons } from "@/lib/icons";
import Board from "@/screens/Board";
import PostIdea from "@/screens/PostIdea";
import SignUp from "@/screens/SignUp";
import LogIn from "@/screens/LogIn";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "flex min-h-11 items-center gap-2 rounded-[var(--brand-radius)] px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-[var(--brand-hover)] text-[var(--brand-fg)]" : "text-[var(--brand-fg-muted)]",
  ].join(" ");

// The app's menu, drawn around every screen except the ones routed outside it below.
function AppShellLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  // undefined while GET /auth/me is pending, null when logged out or the session has expired.
  const [user, setUser] = useState<{ email: string } | null | undefined>(undefined);

  useEffect(() => {
    let current = true;
    api
      .GET("/auth/me")
      .then(({ data, response }) => {
        if (response && response.status === 401) clearSessionToken();
        if (current) setUser(data ?? null);
      })
      .catch(() => {
        if (current) setUser(null);
      });
    return () => {
      current = false;
    };
  }, [location.pathname]);

  // Ends the session on the server first (it needs the token), then drops the local one
  // whatever the answer, and shows the board as a visitor.
  const logOut = async () => {
    try {
      await api.POST("/auth/logout");
    } catch {
      // The server is unreachable: the local session is still dropped below.
    }
    clearSessionToken();
    setUser(null);
    navigate("/board", { replace: true });
  };

  // A visitor (or an expired session) is not redirected from the post form: the screen itself
  // prompts to log in or sign up, and the server refuses the post anyway.

  return (
    <div className="flex min-h-screen flex-col">
      <header
        className="border-b"
        style={{
          backgroundColor: "var(--brand-surface)",
          borderColor: "var(--brand-border)",
        }}
      >
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-6 gap-y-1 px-4 py-2 sm:px-6">
          <p
            className="shrink-0 text-sm font-semibold"
            style={{ fontFamily: "var(--brand-font-heading)" }}
          >
            {"Voting Idea"}
          </p>
          <nav aria-label="App menu" className="flex flex-wrap items-center gap-1">
            <NavLink to="/board" className={navLinkClass}>
              <Icons.Home size={16} />
              {"Ideas Board"}
            </NavLink>
            <NavLink to="/post-idea" className={navLinkClass}>
              <Icons.Plus size={16} />
              {"Post an Idea"}
            </NavLink>
            {user ? null : (
              <>
                <NavLink to="/log-in" className={navLinkClass}>
                  <Icons.User size={16} />
                  {"Log In"}
                </NavLink>
                <NavLink to="/sign-up" className={navLinkClass}>
                  {"Sign Up"}
                </NavLink>
              </>
            )}
          </nav>
          {user ? (
            <div className="flex min-w-0 flex-wrap items-center gap-x-3 text-sm sm:ml-auto">
              <span className="min-w-0 break-all">{`Logged in as ${user.email}`}</span>
              <button type="button" className="min-h-11 px-1 underline" onClick={logOut}>
                {"Log out"}
              </button>
            </div>
          ) : null}
        </div>
      </header>
      <main className="min-w-0 flex-1 overflow-x-hidden">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppShellLayout />}>
        <Route path="/board" element={<Board />} />
        <Route path="/post-idea" element={<PostIdea />} />
      </Route>
      <Route path="/sign-up" element={<SignUp />} />
      <Route path="/log-in" element={<LogIn />} />
      <Route path="*" element={<Navigate to="/board" replace />} />
    </Routes>
  );
}
