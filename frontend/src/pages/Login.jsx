import { useState } from "react";
import { login } from "../api/client.js";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [busy,     setBusy]     = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = await login({ username: username.trim(), password });
      onLogin(data.user);
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-logo">
          <span className="login-logo-icon">🧵</span>
          <h1 className="login-title">Textile OS</h1>
          <p className="login-subtitle">Fabric Feasibility &amp; FTC Approval</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="designer1 / ftc1 / admin"
              autoFocus
              disabled={busy}
            />
          </div>
          <div className="form-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={busy}
            />
          </div>

          {error && <p className="login-error">{error}</p>}

          <button className="btn btn-primary login-btn" type="submit" disabled={busy || !username}>
            {busy ? "Signing in…" : "Sign In"}
          </button>
        </form>

        <p className="login-hint">
          Default credentials: designer1 / designer123 · ftc1 / ftcmember123
        </p>
      </div>
    </div>
  );
}
