export const UI_STORAGE_KEY = "textile-ui-config-v1";

export const UI_OPTIONS = {
  template: [
    { value: "mill", label: "Mill Ops Console" },
    { value: "dual", label: "Dual Tool Skin" },
    { value: "command", label: "Command Center" },
  ],
  density: [
    { value: "spacious", label: "Spacious" },
    { value: "operator", label: "Operator Dense" },
    { value: "compact", label: "Compact" },
  ],
  navigation: [
    { value: "top", label: "Top workflow tabs" },
    { value: "sidebar", label: "Left sidebar" },
    { value: "hybrid", label: "Hybrid sidebar + tabs" },
  ],
  radius: [
    { value: "4", label: "4px" },
    { value: "6", label: "6px" },
    { value: "8", label: "8px" },
    { value: "12", label: "12px" },
  ],
  shadow: [
    { value: "none", label: "None" },
    { value: "soft", label: "Soft" },
    { value: "medium", label: "Medium" },
  ],
  fontScale: [
    { value: "13", label: "13px" },
    { value: "14", label: "14px" },
    { value: "15", label: "15px" },
  ],
  tableDensity: [
    { value: "compact", label: "Compact" },
    { value: "regular", label: "Regular" },
  ],
  issueDisplay: [
    { value: "stacked", label: "Stacked cards" },
    { value: "rows", label: "Table rows" },
    { value: "split", label: "Split severity columns" },
  ],
  rawCardWidth: [
    { value: "50", label: "50%" },
    { value: "60", label: "60%" },
    { value: "70", label: "70%" },
  ],
  stickerPreview: [
    { value: "table", label: "Table only" },
    { value: "table-stats", label: "Table + stats" },
    { value: "visual", label: "Table + visual preview" },
  ],
  accent: [
    { value: "green", label: "Green" },
    { value: "blue", label: "Blue" },
    { value: "teal", label: "Teal" },
  ],
};

export const DEFAULT_UI_CONFIG = {
  template: "mill",
  density: "operator",
  navigation: "sidebar",
  radius: "8",
  shadow: "soft",
  fontScale: "14",
  tableDensity: "compact",
  issueDisplay: "stacked",
  rawCardWidth: "60",
  stickerPreview: "table-stats",
  accent: "green",
};

const TEMPLATE_TOKENS = {
  mill: {
    ink: "#1e2728",
    muted: "#64706f",
    line: "#d8dedb",
    panel: "#ffffff",
    canvas: "#eef3f0",
    sidebar: "#172322",
    sidebarText: "#f6faf7",
    sidebarMuted: "#a9bab4",
    surfaceAlt: "#f7faf8",
    pill: "#edf4f2",
  },
  dual: {
    ink: "#1f2937",
    muted: "#667085",
    line: "#d5dce5",
    panel: "#ffffff",
    canvas: "#f1f5f7",
    sidebar: "#111827",
    sidebarText: "#f8fafc",
    sidebarMuted: "#9ca3af",
    surfaceAlt: "#f8fafc",
    pill: "#edf4ff",
  },
  command: {
    ink: "#e8edf5",
    muted: "#99a6ba",
    line: "#30384a",
    panel: "#151b26",
    canvas: "#0f141d",
    sidebar: "#090d13",
    sidebarText: "#f8fafc",
    sidebarMuted: "#8e9bb0",
    surfaceAlt: "#1d2533",
    pill: "#202a3a",
  },
};

const ACCENTS = {
  green: { primary: "#315b4f", secondary: "#1f6f78", success: "#3d7f58" },
  blue: { primary: "#285d9c", secondary: "#4277b8", success: "#2c7a61" },
  teal: { primary: "#166b6c", secondary: "#0f7a88", success: "#2f7d65" },
};

const DENSITY_TOKENS = {
  spacious: { pageGap: "22px", panelPadding: "22px", rowPadding: "12px", controlHeight: "42px" },
  operator: { pageGap: "16px", panelPadding: "16px", rowPadding: "9px", controlHeight: "38px" },
  compact: { pageGap: "12px", panelPadding: "12px", rowPadding: "7px", controlHeight: "34px" },
};

const SHADOWS = {
  none: "none",
  soft: "0 12px 34px rgba(28, 48, 48, 0.08)",
  medium: "0 18px 46px rgba(18, 28, 34, 0.16)",
};

export function normalizeUiConfig(config = {}) {
  const normalized = { ...DEFAULT_UI_CONFIG, ...config };
  for (const [key, options] of Object.entries(UI_OPTIONS)) {
    if (!options.some((option) => option.value === normalized[key])) {
      normalized[key] = DEFAULT_UI_CONFIG[key];
    }
  }
  return normalized;
}

export function loadUiConfig() {
  if (typeof window === "undefined") return DEFAULT_UI_CONFIG;
  try {
    const stored = window.localStorage.getItem(UI_STORAGE_KEY);
    return normalizeUiConfig(stored ? JSON.parse(stored) : DEFAULT_UI_CONFIG);
  } catch {
    return DEFAULT_UI_CONFIG;
  }
}

export function saveUiConfig(config) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(UI_STORAGE_KEY, JSON.stringify(normalizeUiConfig(config)));
}

export function buildUiCssVars(config) {
  const normalized = normalizeUiConfig(config);
  const template = TEMPLATE_TOKENS[normalized.template];
  const accent = ACCENTS[normalized.accent];
  const density = DENSITY_TOKENS[normalized.density];
  const tablePadding = normalized.tableDensity === "compact" ? "7px 9px" : "10px 12px";
  const rawCardWidth = `${normalized.rawCardWidth}%`;
  const issueColumns =
    normalized.issueDisplay === "split"
      ? "repeat(2, minmax(0, 1fr))"
      : normalized.issueDisplay === "rows"
        ? "1fr"
        : "repeat(auto-fit, minmax(260px, 1fr))";

  return {
    "--ink": template.ink,
    "--muted": template.muted,
    "--line": template.line,
    "--panel": template.panel,
    "--canvas": template.canvas,
    "--forest": accent.primary,
    "--teal": accent.secondary,
    "--green": accent.success,
    "--sidebar": template.sidebar,
    "--sidebar-text": template.sidebarText,
    "--sidebar-muted": template.sidebarMuted,
    "--surface-alt": template.surfaceAlt,
    "--pill": template.pill,
    "--shadow": SHADOWS[normalized.shadow],
    "--radius": `${normalized.radius}px`,
    "--font-size-base": `${normalized.fontScale}px`,
    "--page-gap": density.pageGap,
    "--panel-padding": density.panelPadding,
    "--row-padding": density.rowPadding,
    "--control-height": density.controlHeight,
    "--table-padding": tablePadding,
    "--raw-card-width": rawCardWidth,
    "--issue-columns": issueColumns,
  };
}

export function uiConfigLabel(config) {
  const normalized = normalizeUiConfig(config);
  const template = UI_OPTIONS.template.find((option) => option.value === normalized.template)?.label;
  const density = UI_OPTIONS.density.find((option) => option.value === normalized.density)?.label;
  return `${template} / ${density}`;
}
