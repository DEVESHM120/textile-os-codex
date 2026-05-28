const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include", ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || `Request failed: ${response.status}`);
  }
  return body;
}

export async function fetchSampleCard() {
  return request("/api/samples/cloth-card");
}

export async function createWorkflow({ text, filename, file }) {
  if (file) {
    const form = new FormData();
    form.append("file", file);
    return request("/api/workflows", { method: "POST", body: form });
  }
  return request("/api/workflows", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, filename }),
  });
}

export async function createAiSummary(workflowId) {
  return request(`/api/workflows/${workflowId}/ai-summary`, { method: "POST" });
}

export async function generateLabels(workflowId) {
  return request(`/api/workflows/${workflowId}/generate-labels`, { method: "POST" });
}

export async function generateBulkStickers({ masterFile, templateFile, sheetName }) {
  const form = new FormData();
  form.append("master", masterFile);
  if (templateFile) {
    form.append("template", templateFile);
  }
  if (sheetName) {
    form.append("sheet_name", sheetName);
  }
  return request("/api/stickers/generate-bulk", { method: "POST", body: form });
}

export async function fetchWorkflows() {
  return request("/api/workflows");
}

export async function fetchWorkflow(workflowId) {
  return request(`/api/workflows/${workflowId}`);
}

export function artifactDownloadUrl(path) {
  return `${API_BASE}${path}`;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function fetchMe() {
  return request("/api/auth/me");
}

export async function login({ username, password }) {
  return request("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export async function logout() {
  return request("/api/auth/logout");
}

// ── Designer ──────────────────────────────────────────────────────────────────

export async function fetchDesignerSubmissions() {
  return request("/api/designer/submissions");
}

export async function fetchDesignerSubmission(subId) {
  return request(`/api/designer/submissions/${subId}`);
}

export async function submitClothCard({ file, text, filename }) {
  if (file) {
    const form = new FormData();
    form.append("file", file);
    return request("/api/designer/submit", { method: "POST", body: form });
  }
  return request("/api/designer/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, filename }),
  });
}

export async function recheckSubmission(subId) {
  return request(`/api/designer/recheck/${subId}`, { method: "POST" });
}

export async function sendToFtc(subId, note) {
  return request(`/api/designer/send/${subId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note }),
  });
}

// ── FTC ───────────────────────────────────────────────────────────────────────

export async function fetchFtcInbox(statusFilter) {
  const qs = statusFilter ? `?status=${statusFilter}` : "";
  return request(`/api/ftc/inbox${qs}`);
}

export async function fetchAllFtcSubmissions() {
  return request("/api/ftc/inbox/all");
}

export async function fetchFtcSubmission(subId) {
  return request(`/api/ftc/submissions/${subId}`);
}

export async function postFtcFeedback(subId, body, fieldRef) {
  return request(`/api/ftc/feedback/${subId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body, field_ref: fieldRef }),
  });
}

export async function approveFtcSubmission(subId, notes) {
  return request(`/api/ftc/approve/${subId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes }),
  });
}

// ── Messages ──────────────────────────────────────────────────────────────────

export async function fetchMessages(subId) {
  return request(`/api/messages/${subId}`);
}

export async function postMessage(subId, body, fieldRef) {
  return request(`/api/messages/${subId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body, field_ref: fieldRef }),
  });
}

// ── Sticker Convert ───────────────────────────────────────────────────────────

export async function convertBuyerFile({ convertFile, sheetName }) {
  const form = new FormData();
  form.append("file", convertFile);
  if (sheetName) form.append("sheet_name", sheetName);
  return request("/api/stickers/convert", { method: "POST", body: form });
}

// ── Sticker Templates ─────────────────────────────────────────────────────────

export async function fetchStickerTemplates() {
  return request("/api/sticker-templates");
}

export async function uploadStickerTemplate({ file, name, description }) {
  const form = new FormData();
  form.append("file", file);
  if (name) form.append("name", name);
  if (description) form.append("description", description);
  return request("/api/sticker-templates", { method: "POST", body: form });
}

export async function deleteStickerTemplate(templateId) {
  return request(`/api/sticker-templates/${templateId}`, { method: "DELETE" });
}

export async function generateBulkStickersWithTemplate({ masterFile, templateId, sheetName }) {
  const form = new FormData();
  form.append("master", masterFile);
  if (templateId != null) form.append("template_id", String(templateId));
  if (sheetName) form.append("sheet_name", sheetName);
  return request("/api/stickers/generate-bulk", { method: "POST", body: form });
}
