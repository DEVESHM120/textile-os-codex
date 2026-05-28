import { useEffect, useMemo, useState } from "react";
import {
  Blocks,
  ClipboardCheck,
  Inbox,
  Settings2,
  Sticker,
} from "lucide-react";
import {
  convertBuyerFile,
  fetchMe,
  generateBulkStickersWithTemplate,
  logout,
} from "./api/client.js";
import { buildUiCssVars, loadUiConfig, saveUiConfig } from "./config/uiConfig.js";
import LabelStudio from "./pages/LabelStudio.jsx";
import Login from "./pages/Login.jsx";
import DesignerDesk from "./pages/DesignerDesk.jsx";
import FtcInbox from "./pages/FtcInbox.jsx";

const navItems = [
  { id: "designer", label: "Designer Desk", icon: ClipboardCheck, roles: ["designer", "admin"] },
  { id: "ftc",      label: "FTC Inbox",     icon: Inbox,          roles: ["ftc_member", "admin"] },
  { id: "sticker",  label: "Sticker Agent", icon: Sticker,        roles: null },
];

export default function App() {
  const [currentUser,     setCurrentUser]     = useState(null);
  const [authChecked,     setAuthChecked]     = useState(false);
  const [view,            setView]            = useState("designer");
  const [uiConfig,        setUiConfig]        = useState(loadUiConfig);
  const [bulkArtifact,    setBulkArtifact]    = useState(null);
  const [convertArtifact, setConvertArtifact] = useState(null);
  const [busy,            setBusy]            = useState("");

  useEffect(() => {
    fetchMe()
      .then(({ user }) => {
        setCurrentUser(user);
        setView(user.role === "ftc_member" ? "ftc" : "designer");
      })
      .catch(() => setCurrentUser(null))
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    saveUiConfig(uiConfig);
  }, [uiConfig]);

  const shellTitle = useMemo(() => {
    if (view === "designer") return "Designer Desk";
    if (view === "ftc")      return "FTC Inbox";
    if (view === "sticker")  return "Sticker Agent";
    return "Textile OS";
  }, [view]);

  const uiCssVars = useMemo(() => buildUiCssVars(uiConfig), [uiConfig]);

  async function runGenerateBulkLabels(payload) {
    setBusy("bulk-labels");
    try {
      const data = await generateBulkStickersWithTemplate(payload);
      setBulkArtifact(data.artifact);
    } finally {
      setBusy("");
    }
  }

  async function runConvertExcel(payload) {
    setBusy("convert");
    try {
      const data = await convertBuyerFile(payload);
      setConvertArtifact(data.artifact);
    } finally {
      setBusy("");
    }
  }

  function renderNavItem(item) {
    const Icon = item.icon;
    if (item.roles && currentUser && !item.roles.includes(currentUser.role)) return null;
    return (
      <button
        key={item.id}
        className={view === item.id ? "active" : ""}
        onClick={() => setView(item.id)}
        title={item.label}
      >
        <Icon size={18} />
        <span>{item.label}</span>
      </button>
    );
  }

  async function handleLogout() {
    try { await logout(); } catch { /* ignore */ }
    setCurrentUser(null);
    setAuthChecked(true);
  }

  if (!authChecked) {
    return <div className="app-loading">Loading…</div>;
  }
  if (!currentUser) {
    return (
      <Login
        onLogin={(user) => {
          setCurrentUser(user);
          setView(user.role === "ftc_member" ? "ftc" : "designer");
        }}
      />
    );
  }

  return (
    <div
      className={`app-shell nav-${uiConfig.navigation} template-${uiConfig.template} density-${uiConfig.density} issue-mode-${uiConfig.issueDisplay}`}
      style={uiCssVars}
      data-template={uiConfig.template}
      data-density={uiConfig.density}
    >
      <aside className="sidebar">
        <div className="brand-block">
          <Blocks size={26} />
          <div>
            <strong>Textile OS</strong>
            <span>Feasibility Platform</span>
          </div>
        </div>
        <nav>
          <div className="nav-section">
            {navItems.map(renderNavItem)}
          </div>
        </nav>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <p className="eyebrow">Textile OS · {currentUser.role.replace(/_/g, " ")}</p>
            <h1>{shellTitle}</h1>
          </div>
          <div className="topbar-actions">
            <div className="status-pill">
              <Settings2 size={15} />
              <span>{currentUser.display_name} · {currentUser.role}</span>
            </div>
            <button className="button button-secondary" type="button" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        </header>

        {view === "designer" && <DesignerDesk currentUser={currentUser} />}

        {view === "ftc" && <FtcInbox currentUser={currentUser} />}

        {view === "sticker" && (
          <LabelStudio
            bulkArtifact={bulkArtifact}
            convertArtifact={convertArtifact}
            bulkBusy={busy === "bulk-labels"}
            convertBusy={busy === "convert"}
            onGenerateBulkStickers={runGenerateBulkLabels}
            onConvertExcel={runConvertExcel}
          />
        )}
      </main>
    </div>
  );
}
