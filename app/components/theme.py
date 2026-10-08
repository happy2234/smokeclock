"""
SmokeClock UI theme — CSS constants for the Gradio dashboard.

Palette (light mode reference):
  Background   var(--background-fill-primary)   white
  Surface      var(--block-background-fill)      white
  Border       var(--border-color-primary)       #e5e7eb
  Text         var(--body-text-color)            #1f2937
  Muted        var(--body-text-color-subdued)    #9ca3af
  Accent       #2a7f62  (restrained teal-green, same in both modes)
  Accent light #e8f4f0  (overridden in dark mode)

Strategy:
  - Use Gradio CSS variables wherever possible so Blocks light/dark theme
    switching automatically propagates.
  - Add :root.dark overrides only for colors that have no direct Gradio
    variable equivalent (custom accent surfaces, badge backgrounds).
  - Never hard-code white/black for body text or card backgrounds.
"""

DASHBOARD_CSS = """
/* ── Base ──────────────────────────────────────────────────────────── */
body, .gradio-container {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}

/* ── Hero ───────────────────────────────────────────────────────────── */
.sc-hero {
    background: var(--block-background-fill);
    border: 1px solid var(--border-color-primary);
    border-left: 4px solid #2a7f62;
    border-radius: 6px;
    padding: 28px 32px 22px 32px;
    margin-bottom: 24px;
}

.sc-hero h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--body-text-color);
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}

.sc-hero .sc-subtitle {
    font-size: 1.1rem;
    color: var(--body-text-color);
    margin: 0 0 16px 0;
    font-weight: 400;
    opacity: 0.85;
}

.sc-hero .sc-tagline {
    font-size: 0.93rem;
    color: var(--body-text-color);
    line-height: 1.55;
    margin-bottom: 16px;
    opacity: 0.8;
}

.sc-badge {
    display: inline-block;
    background: var(--sc-accent-surface, #e8f4f0);
    color: #2a7f62;
    border: 1px solid var(--sc-accent-border, #b8ddd3);
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 10px;
    margin-right: 6px;
}

.sc-pipeline {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    flex-wrap: wrap;
}

.sc-pipeline-step {
    background: var(--background-fill-secondary);
    border: 1px solid var(--border-color-primary);
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 0.8rem;
    color: var(--body-text-color);
    font-weight: 500;
}

.sc-pipeline-arrow {
    color: #2a7f62;
    font-weight: 700;
    font-size: 1rem;
}

/* ── Section headings ────────────────────────────────────────────────── */
.sc-section-heading {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2a7f62;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--sc-accent-surface, #e8f4f0);
    padding-bottom: 6px;
    margin-bottom: 16px;
}

/* ── Metric grid (snapshot) ──────────────────────────────────────────── */
.sc-metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 12px;
}

.sc-metric-card {
    background: var(--block-background-fill);
    border: 1px solid var(--border-color-primary);
    border-radius: 6px;
    padding: 16px 18px 14px 18px;
}

.sc-metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--body-text-color-subdued);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.sc-metric-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--body-text-color);
    line-height: 1.1;
}

.sc-metric-unit {
    font-size: 0.8rem;
    color: var(--body-text-color-subdued);
    margin-top: 3px;
}

.sc-metric-note {
    background: var(--background-fill-secondary);
    border: 1px solid var(--border-color-primary);
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 0.78rem;
    color: var(--body-text-color);
    line-height: 1.5;
    opacity: 0.8;
}

.sc-timestamp {
    font-size: 0.82rem;
    color: var(--body-text-color-subdued);
    margin-bottom: 14px;
}

/* ── Replay result card ──────────────────────────────────────────────── */
.sc-replay-result {
    background: var(--block-background-fill);
    border: 1px solid var(--border-color-primary);
    border-left: 4px solid #2a7f62;
    border-radius: 6px;
    padding: 20px 24px;
    margin-top: 12px;
}

.sc-replay-result h3 {
    font-size: 0.85rem;
    font-weight: 600;
    color: #2a7f62;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 14px 0;
}

.sc-replay-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.sc-replay-item-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--body-text-color-subdued);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}

.sc-replay-item-value {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--body-text-color);
}

.sc-replay-item-unit {
    font-size: 0.75rem;
    color: var(--body-text-color-subdued);
}

.sc-replay-notice {
    font-size: 0.77rem;
    color: var(--body-text-color-subdued);
    border-top: 1px solid var(--border-color-primary);
    margin-top: 14px;
    padding-top: 10px;
    line-height: 1.5;
}

.sc-held-out-badge {
    display: inline-block;
    background: var(--sc-warn-surface, #fff3cd);
    color: var(--sc-warn-text, #856404);
    border: 1px solid var(--sc-warn-border, #ffc107);
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    margin-left: 8px;
    vertical-align: middle;
}

/* ── Evidence / benchmark ────────────────────────────────────────────── */
.sc-evidence-callout {
    background: var(--sc-accent-surface, #e8f4f0);
    border: 1px solid var(--sc-accent-border, #b8ddd3);
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 14px;
}

.sc-evidence-callout .sc-evidence-number {
    font-size: 2.4rem;
    font-weight: 700;
    color: #2a7f62;
    line-height: 1;
}

.sc-evidence-callout .sc-evidence-label {
    font-size: 0.85rem;
    color: var(--sc-accent-text, #1e5c46);
    font-weight: 500;
    margin-top: 2px;
}

.sc-evidence-footnote {
    font-size: 0.76rem;
    color: var(--body-text-color);
    margin-top: 8px;
    line-height: 1.5;
    opacity: 0.85;
}

/* ── Uncertainty section ──────────────────────────────────────────────── */
.sc-uncertainty {
    background: var(--block-background-fill);
    border: 1px solid var(--border-color-primary);
    border-radius: 6px;
    padding: 20px 24px;
}

.sc-uncertainty-badge {
    display: inline-block;
    background: var(--sc-warn-surface, #fff3cd);
    color: var(--sc-warn-text, #856404);
    border: 1px solid var(--sc-warn-border, #ffc107);
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    margin-bottom: 12px;
}

.sc-uncertainty-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}

.sc-uncertainty-item-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--body-text-color-subdued);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}

.sc-uncertainty-item-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--body-text-color);
}

.sc-uncertainty-item-unit {
    font-size: 0.75rem;
    color: var(--body-text-color-subdued);
}

.sc-uncertainty-note {
    font-size: 0.8rem;
    color: var(--body-text-color);
    border-top: 1px solid var(--border-color-primary);
    padding-top: 12px;
    line-height: 1.6;
    opacity: 0.85;
}

/* ── Footer ──────────────────────────────────────────────────────────── */
.sc-footer {
    background: var(--block-background-fill);
    border: 1px solid var(--border-color-primary);
    border-radius: 6px;
    padding: 20px 24px;
    margin-top: 8px;
}

.sc-footer-heading {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #2a7f62;
    margin-bottom: 10px;
}

.sc-footer ol, .sc-footer ul {
    font-size: 0.82rem;
    color: var(--body-text-color);
    padding-left: 20px;
    line-height: 1.8;
    margin: 0 0 10px 0;
}

.sc-footer li {
    color: var(--body-text-color);
}

.sc-footer-caution {
    font-size: 0.76rem;
    color: var(--body-text-color);
    border-top: 1px solid var(--border-color-primary);
    padding-top: 10px;
    margin-top: 4px;
    opacity: 0.8;
}

/* ── General tightening ──────────────────────────────────────────────── */
.gradio-container .prose h2 {
    margin-top: 0 !important;
}

/* Gradio DataFrame tweaks */
.sc-table-wrap table {
    font-size: 0.82rem;
}

/* ══════════════════════════════════════════════════════════════════════
   DARK MODE OVERRIDES
   Gradio 6 sets :root.dark when dark theme is active.
   Override custom surface colors that have no Gradio variable equivalent.
   All text/border already adapts via var(--body-text-color) etc.
   ══════════════════════════════════════════════════════════════════════ */

:root.dark {
    /* Accent surface: teal callout / badge bg in dark mode */
    --sc-accent-surface: #0d2b22;
    --sc-accent-border:  #1a4d38;
    --sc-accent-text:    #6fcfaa;

    /* Warning badge (held-out / research only) in dark mode */
    --sc-warn-surface:   #2d2500;
    --sc-warn-text:      #f5c842;
    --sc-warn-border:    #7a6000;
}

/* Light mode custom property defaults (redundant fallback for clarity) */
:root:not(.dark) {
    --sc-accent-surface: #e8f4f0;
    --sc-accent-border:  #b8ddd3;
    --sc-accent-text:    #1e5c46;

    --sc-warn-surface:   #fff3cd;
    --sc-warn-text:      #856404;
    --sc-warn-border:    #ffc107;
}

/* ── prefers-color-scheme fallback ─────────────────────────────────────
   If Gradio has not yet toggled the .dark class (e.g. SSR or initial
   paint), respect the system preference so the first frame is readable.
   ──────────────────────────────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
    :root:not(.dark):not([class*="light"]) {
        --sc-accent-surface: #0d2b22;
        --sc-accent-border:  #1a4d38;
        --sc-accent-text:    #6fcfaa;
        --sc-warn-surface:   #2d2500;
        --sc-warn-text:      #f5c842;
        --sc-warn-border:    #7a6000;
    }
}
"""


def hero_html() -> str:
    """Return the hero section HTML block."""
    return """
<div class="sc-hero">
  <h1>SmokeClock</h1>
  <p class="sc-subtitle">Wind-aware smoke intelligence for Delhi-NCR</p>
  <p class="sc-tagline">
    Connecting upwind fire activity, atmospheric transport and PM2.5
    to understand what smoke may matter next.
  </p>
  <div>
    <span class="sc-badge">Historical Replay</span>
    <span class="sc-badge">Research Prototype</span>
  </div>
  <div class="sc-pipeline">
    <span class="sc-pipeline-step">Satellite fires</span>
    <span class="sc-pipeline-arrow">→</span>
    <span class="sc-pipeline-step">Wind / transport index</span>
    <span class="sc-pipeline-arrow">→</span>
    <span class="sc-pipeline-step">PM2.5 forecast model</span>
    <span class="sc-pipeline-arrow">→</span>
    <span class="sc-pipeline-step">Chronological evaluation</span>
  </div>
</div>
"""
