import { NavLink, Navigate, Outlet, Route, Routes } from "react-router-dom";

import { Icons } from "@/lib/icons";
import Board from "@/screens/Board";
import PostIdea from "@/screens/PostIdea";
import SignUp from "@/screens/SignUp";
import LogIn from "@/screens/LogIn";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "flex items-center gap-2 rounded-[var(--brand-radius)] px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-[var(--brand-hover)] text-[var(--brand-fg)]" : "text-[var(--brand-fg-muted)]",
  ].join(" ");

// The app's menu, drawn around every screen except the ones routed outside it below.
function AppShellLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header
        className="border-b"
        style={{
          backgroundColor: "var(--brand-surface)",
          borderColor: "var(--brand-border)",
        }}
      >
        <div className="flex items-center gap-6 px-6 py-2">
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
            <NavLink to="/log-in" className={navLinkClass}>
              <Icons.User size={16} />
              {"Log In"}
            </NavLink>
            <NavLink to="/sign-up" className={navLinkClass}>
              {"Sign Up"}
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="flex-1 overflow-auto">
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
