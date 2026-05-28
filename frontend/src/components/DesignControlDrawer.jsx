import { useEffect, useState } from "react";
import { Check, Clipboard, RotateCcw, SlidersHorizontal, X } from "lucide-react";
import { UI_OPTIONS, normalizeUiConfig, uiConfigLabel } from "../config/uiConfig.js";

export default function DesignControlDrawer({ open, config, onChange, onClose, onReset }) {
  const normalized = normalizeUiConfig(config);
  const [copied, setCopied] = useCopiedState();

  function update(key, value) {
    onChange(normalizeUiConfig({ ...normalized, [key]: value }));
  }

  async function copyConfig() {
    const payload = JSON.stringify(normalized, null, 2);
    try {
      await navigator.clipboard?.writeText(payload);
    } catch {
      // The in-app browser can block clipboard writes; the JSON preview remains visible below.
    }
    setCopied(true);
  }

  return (
    <>
      <div className={`drawer-scrim ${open ? "open" : ""}`} onMouseDown={onClose} />
      <aside className={`design-drawer ${open ? "open" : ""}`} aria-hidden={!open}>
        <div className="drawer-head">
          <div>
            <p className="eyebrow">UI lock controls</p>
            <h2>Design Drawer</h2>
            <span>{uiConfigLabel(normalized)}</span>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close design drawer">
            <X size={18} />
          </button>
        </div>

        <div className="drawer-section">
          <h3>Preset</h3>
          <OptionGrid
            name="template"
            value={normalized.template}
            options={UI_OPTIONS.template}
            onChange={(value) => update("template", value)}
          />
        </div>

        <div className="drawer-section">
          <h3>Workflow Feel</h3>
          <ControlSelect label="Density" value={normalized.density} options={UI_OPTIONS.density} onChange={(value) => update("density", value)} />
          <ControlSelect label="Navigation" value={normalized.navigation} options={UI_OPTIONS.navigation} onChange={(value) => update("navigation", value)} />
          <ControlSelect label="Issue display" value={normalized.issueDisplay} options={UI_OPTIONS.issueDisplay} onChange={(value) => update("issueDisplay", value)} />
          <ControlSelect label="Sticker preview" value={normalized.stickerPreview} options={UI_OPTIONS.stickerPreview} onChange={(value) => update("stickerPreview", value)} />
        </div>

        <div className="drawer-section">
          <h3>Surface Tokens</h3>
          <ControlSelect label="Panel radius" value={normalized.radius} options={UI_OPTIONS.radius} onChange={(value) => update("radius", value)} />
          <ControlSelect label="Shadow strength" value={normalized.shadow} options={UI_OPTIONS.shadow} onChange={(value) => update("shadow", value)} />
          <ControlSelect label="Font scale" value={normalized.fontScale} options={UI_OPTIONS.fontScale} onChange={(value) => update("fontScale", value)} />
          <ControlSelect label="Table density" value={normalized.tableDensity} options={UI_OPTIONS.tableDensity} onChange={(value) => update("tableDensity", value)} />
          <ControlSelect label="Raw card width" value={normalized.rawCardWidth} options={UI_OPTIONS.rawCardWidth} onChange={(value) => update("rawCardWidth", value)} />
          <ControlSelect label="Accent color" value={normalized.accent} options={UI_OPTIONS.accent} onChange={(value) => update("accent", value)} />
        </div>

        <div className="drawer-section token-preview">
          <h3>Preview</h3>
          <div className="swatch-row">
            <span className="swatch swatch-primary" />
            <span className="swatch swatch-secondary" />
            <span className="swatch swatch-success" />
            <span className="swatch swatch-warning" />
            <span className="swatch swatch-danger" />
          </div>
        </div>

        <div className="drawer-actions">
          <button className="button button-secondary" type="button" onClick={onReset}>
            <RotateCcw size={16} />
            Reset
          </button>
          <button className="button button-primary" type="button" onClick={copyConfig}>
            {copied ? <Check size={16} /> : <Clipboard size={16} />}
            {copied ? "Copied" : "Copy UI Config"}
          </button>
        </div>

        <pre className="config-preview">{JSON.stringify(normalized, null, 2)}</pre>
      </aside>
    </>
  );
}

function ControlSelect({ label, value, options, onChange }) {
  return (
    <label className="control-select">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function OptionGrid({ value, options, onChange }) {
  return (
    <div className="option-grid">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          className={value === option.value ? "active" : ""}
          onClick={() => onChange(option.value)}
        >
          <SlidersHorizontal size={15} />
          {option.label}
        </button>
      ))}
    </div>
  );
}

function useCopiedState() {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return undefined;
    const timeout = window.setTimeout(() => setCopied(false), 1600);
    return () => window.clearTimeout(timeout);
  }, [copied]);

  return [copied, setCopied];
}
