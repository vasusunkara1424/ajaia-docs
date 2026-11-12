import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import { Avatar } from "../ui/Avatar";

export function AppHeader({ children }: { children?: ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <header className="app-header">
      <Link to="/" className="brand" aria-label="Ajaia Docs home">
        <span className="brand__mark" aria-hidden>
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" fill="currentColor" />
          </svg>
        </span>
        <span className="brand__name">Ajaia Docs</span>
      </Link>
      <div className="app-header__center">{children}</div>
      {user && (
        <div className="app-header__user">
          <Avatar name={user.name} />
          <span className="app-header__name">{user.name}</span>
          <button className="btn btn--ghost btn--sm" onClick={logout}>
            Sign out
          </button>
        </div>
      )}
    </header>
  );
}
