import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

const DEMO_ACCOUNTS = [
  { email: "alice@ajaia.dev", name: "Alice Johnson" },
  { email: "bob@ajaia.dev", name: "Bob Martinez" },
  { email: "carol@ajaia.dev", name: "Carol Chen" },
];
const DEMO_PASSWORD = "demo1234";

export function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const signIn = async (e?: FormEvent, override?: { email: string; password: string }) => {
    e?.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(override?.email ?? email, override?.password ?? password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sign in failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login">
      <section className="login__card">
        <div className="brand brand--lg">
          <span className="brand__mark" aria-hidden>
            <svg viewBox="0 0 24 24" width="22" height="22">
              <path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" fill="currentColor" />
            </svg>
          </span>
          <span className="brand__name">Ajaia Docs</span>
        </div>
        <p className="muted">Sign in to create and share documents.</p>

        <form onSubmit={signIn} className="stack">
          <label className="field">
            <span>Email</span>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="btn btn--primary btn--block" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="demo-accounts">
          <h3 className="section-label">Demo accounts (password: {DEMO_PASSWORD})</h3>
          {DEMO_ACCOUNTS.map((account) => (
            <button
              key={account.email}
              className="demo-account"
              disabled={submitting}
              onClick={() => signIn(undefined, { email: account.email, password: DEMO_PASSWORD })}
            >
              <strong>{account.name}</strong>
              <span>{account.email}</span>
            </button>
          ))}
          <p className="muted small">Tip: open a private window as a second user to test sharing.</p>
        </div>
      </section>
    </main>
  );
}
