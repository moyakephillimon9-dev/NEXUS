"""
NEXUS
Design AI — UI/UX Specification Engine

Module ID : DESIGN-001
Version   : 1.0.0

Generates a professional UI/UX design specification,
colour palette, typography guide, and (for web projects)
a production-ready CSS stylesheet based on the project
goal and research context.
"""

import os
from datetime import datetime


# ------------------------------------------------------------------ #
# Colour Palettes                                                       #
# ------------------------------------------------------------------ #

_PALETTES: dict = {
    "calculator":   {
        "primary":    "#1A1A2E",
        "secondary":  "#16213E",
        "accent":     "#0F3460",
        "highlight":  "#E94560",
        "text":       "#EAEAEA",
        "bg":         "#0F0F1A",
        "tone":       "Dark Professional",
    },
    "todo_app":     {
        "primary":    "#2D6A4F",
        "secondary":  "#40916C",
        "accent":     "#52B788",
        "highlight":  "#F4A261",
        "text":       "#1B1B1B",
        "bg":         "#F8F9FA",
        "tone":       "Clean Productivity",
    },
    "web_app":      {
        "primary":    "#3A0CA3",
        "secondary":  "#4361EE",
        "accent":     "#4CC9F0",
        "highlight":  "#F72585",
        "text":       "#1A1A1A",
        "bg":         "#FFFFFF",
        "tone":       "Modern Enterprise",
    },
    "rest_api":     {
        "primary":    "#023E8A",
        "secondary":  "#0077B6",
        "accent":     "#00B4D8",
        "highlight":  "#F77F00",
        "text":       "#212529",
        "bg":         "#F0F4F8",
        "tone":       "Technical Precision",
    },
    "desktop_gui":  {
        "primary":    "#22223B",
        "secondary":  "#4A4E69",
        "accent":     "#9A8C98",
        "highlight":  "#C9ADA7",
        "text":       "#22223B",
        "bg":         "#F2E9E4",
        "tone":       "Elegant Desktop",
    },
    "data_analyzer":{
        "primary":    "#212529",
        "secondary":  "#495057",
        "accent":     "#20C997",
        "highlight":  "#FD7E14",
        "text":       "#212529",
        "bg":         "#F8F9FA",
        "tone":       "Data Clarity",
    },
    "game":         {
        "primary":    "#6A0572",
        "secondary":  "#AB83A1",
        "accent":     "#FF6B6B",
        "highlight":  "#FFE66D",
        "text":       "#FFFFFF",
        "bg":         "#1A0A1E",
        "tone":       "Vibrant Play",
    },
    "inventory":    {
        "primary":    "#1D3557",
        "secondary":  "#457B9D",
        "accent":     "#A8DADC",
        "highlight":  "#E63946",
        "text":       "#1D3557",
        "bg":         "#F1FAEE",
        "tone":       "Business Trust",
    },
    "generic":      {
        "primary":    "#264653",
        "secondary":  "#2A9D8F",
        "accent":     "#E9C46A",
        "highlight":  "#E76F51",
        "text":       "#212529",
        "bg":         "#FAFAFA",
        "tone":       "Balanced Neutral",
    },
}


# ------------------------------------------------------------------ #
# Layout Templates                                                      #
# ------------------------------------------------------------------ #

_LAYOUTS: dict = {
    "calculator": {
        "type":       "Single Page",
        "regions":    ["Display Panel", "Button Grid (4×5)", "History Sidebar"],
        "navigation": "None",
        "responsive": False,
    },
    "todo_app": {
        "type":       "Two Panel",
        "regions":    ["Sidebar (Filters)", "Main List", "Task Detail Panel"],
        "navigation": "Sidebar",
        "responsive": True,
    },
    "web_app": {
        "type":       "Full Application",
        "regions":    ["Top Navigation", "Hero / Banner", "Content Grid", "Footer"],
        "navigation": "Top Bar + Sidebar",
        "responsive": True,
    },
    "rest_api": {
        "type":       "API Documentation",
        "regions":    ["Endpoint Explorer", "Request Builder", "Response Viewer", "Auth Panel"],
        "navigation": "Left Sidebar",
        "responsive": True,
    },
    "desktop_gui": {
        "type":       "Native Desktop",
        "regions":    ["Menu Bar", "Toolbar", "Main Content Area", "Status Bar"],
        "navigation": "Menu Bar",
        "responsive": False,
    },
    "data_analyzer": {
        "type":       "Dashboard",
        "regions":    ["Filter Bar", "KPI Cards", "Chart Area", "Data Table"],
        "navigation": "Top Tabs",
        "responsive": True,
    },
    "game": {
        "type":       "Full Screen",
        "regions":    ["Game Area", "HUD Overlay", "Inventory Panel", "Menu Screen"],
        "navigation": "In-Game Menu",
        "responsive": False,
    },
    "inventory": {
        "type":       "Enterprise Dashboard",
        "regions":    ["Sidebar Navigation", "Summary Cards", "Data Grid", "Detail Drawer"],
        "navigation": "Left Sidebar",
        "responsive": True,
    },
    "generic": {
        "type":       "Standard Layout",
        "regions":    ["Header", "Main Content", "Footer"],
        "navigation": "Top Bar",
        "responsive": True,
    },
}


def _generate_css(palette: dict, layout: dict) -> str:
    return f"""\
/* NEXUS Design AI — Auto-generated Stylesheet */
/* Tone: {palette['tone']} | Layout: {layout['type']} */

:root {{
  --color-primary:   {palette['primary']};
  --color-secondary: {palette['secondary']};
  --color-accent:    {palette['accent']};
  --color-highlight: {palette['highlight']};
  --color-text:      {palette['text']};
  --color-bg:        {palette['bg']};
  --font-main:       'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono:       'JetBrains Mono', 'Fira Code', monospace;
  --radius:          8px;
  --shadow:          0 4px 24px rgba(0,0,0,0.08);
  --transition:      0.2s ease;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: var(--font-main);
  background:  var(--color-bg);
  color:       var(--color-text);
  line-height: 1.6;
}}

/* ── Typography ─────────────────────────────────────── */
h1, h2, h3, h4 {{ font-weight: 700; line-height: 1.2; }}
h1 {{ font-size: clamp(1.8rem, 4vw, 2.8rem); }}
h2 {{ font-size: clamp(1.4rem, 3vw, 2rem); }}
h3 {{ font-size: 1.2rem; }}
p  {{ max-width: 70ch; }}

/* ── Buttons ─────────────────────────────────────────── */
.btn {{
  display:       inline-flex;
  align-items:   center;
  gap:           0.5rem;
  padding:       0.6rem 1.4rem;
  border-radius: var(--radius);
  border:        none;
  cursor:        pointer;
  font-size:     0.95rem;
  font-weight:   600;
  transition:    var(--transition);
}}
.btn-primary {{
  background: var(--color-primary);
  color:      #fff;
}}
.btn-primary:hover {{ filter: brightness(1.15); }}
.btn-accent {{
  background: var(--color-accent);
  color:      #fff;
}}
.btn-outline {{
  background: transparent;
  border:     2px solid var(--color-primary);
  color:      var(--color-primary);
}}

/* ── Cards ───────────────────────────────────────────── */
.card {{
  background:    #fff;
  border-radius: calc(var(--radius) * 1.5);
  box-shadow:    var(--shadow);
  padding:       1.5rem;
}}

/* ── Forms ───────────────────────────────────────────── */
input, textarea, select {{
  width:         100%;
  padding:       0.6rem 0.9rem;
  border:        1.5px solid #dee2e6;
  border-radius: var(--radius);
  font-family:   var(--font-main);
  font-size:     0.95rem;
  transition:    var(--transition);
}}
input:focus, textarea:focus, select:focus {{
  outline:      none;
  border-color: var(--color-accent);
  box-shadow:   0 0 0 3px color-mix(in srgb, var(--color-accent) 20%, transparent);
}}

/* ── Layout ──────────────────────────────────────────── */
.container      {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
.grid           {{ display: grid; gap: 1.5rem; }}
.grid-2         {{ grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
.grid-3         {{ grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
.flex           {{ display: flex; align-items: center; gap: 1rem; }}
.flex-between   {{ display: flex; justify-content: space-between; align-items: center; }}

/* ── Navigation ──────────────────────────────────────── */
nav {{
  background: var(--color-primary);
  padding:    1rem 1.5rem;
  display:    flex;
  justify-content: space-between;
  align-items:     center;
}}
nav a {{ color: #fff; text-decoration: none; font-weight: 600; }}

/* ── Utilities ───────────────────────────────────────── */
.text-accent  {{ color: var(--color-accent); }}
.text-highlight {{ color: var(--color-highlight); }}
.mt-1 {{ margin-top: 0.5rem; }}
.mt-2 {{ margin-top: 1rem; }}
.mt-3 {{ margin-top: 1.5rem; }}
.mt-4 {{ margin-top: 2rem; }}
.p-1  {{ padding: 0.5rem; }}
.p-2  {{ padding: 1rem; }}
.p-3  {{ padding: 1.5rem; }}
.hidden {{ display: none; }}

/* ── Responsive ──────────────────────────────────────── */
@media (max-width: 768px) {{
  .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
  nav {{ flex-direction: column; gap: 0.5rem; }}
}}
"""


class DesignAI:
    """
    NEXUS UI/UX Designer.

    Generates colour palettes, typography guides, layout
    specifications, and production-ready CSS based on the
    project type detected by Research AI.

    Responsibilities
    ----------------
    • Colour palette selection
    • Layout specification
    • CSS stylesheet generation
    • Design spec document (Markdown)
    """

    def __init__(self, shared_memory, deployment_root: str = "deployments"):
        self.memory          = shared_memory
        self.deployment_root = deployment_root
        print("[Design AI] Connected to Shared Memory.")

    def start(self):
        print("[Design AI] UI/UX Specification Engine Ready.")

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Design AI] Project not found.")
            return

        print(f"[Design AI] Generating design: {task_id}")

        project_type = project.get("project_type", "generic")
        palette      = _PALETTES.get(project_type, _PALETTES["generic"])
        layout       = _LAYOUTS.get(project_type, _LAYOUTS["generic"])
        css          = _generate_css(palette, layout)

        # Write to deployment folder
        goal_slug = project.get("goal", "project").lower().replace(" ", "_")[:40]
        folder    = os.path.join(self.deployment_root, f"{task_id}_{goal_slug}")
        os.makedirs(os.path.join(folder, "static"), exist_ok=True)

        css_path  = os.path.join(folder, "static", "style.css")
        spec_path = os.path.join(folder, "design_spec.md")

        with open(css_path, "w") as f:
            f.write(css)

        spec = f"""# Design Specification
## {project.get('goal')}

**Generated by NEXUS Design AI** | {datetime.utcnow().isoformat()}

---

## Colour Palette

| Token       | Hex       | Usage          |
|-------------|-----------|----------------|
| Primary     | `{palette['primary']}`  | Main brand colour |
| Secondary   | `{palette['secondary']}` | Supporting elements |
| Accent      | `{palette['accent']}`   | Interactive elements |
| Highlight   | `{palette['highlight']}` | Calls to action |
| Text        | `{palette['text']}`     | Body text |
| Background  | `{palette['bg']}`       | Page background |

**Design Tone:** {palette['tone']}

---

## Typography

- **Primary Font:** Inter, Segoe UI, system-ui (sans-serif)
- **Mono Font:** JetBrains Mono, Fira Code (monospace)
- **H1:** clamp(1.8rem, 4vw, 2.8rem) — Bold
- **H2:** clamp(1.4rem, 3vw, 2rem) — Bold
- **Body:** 0.95rem — Regular, max-width 70ch

---

## Layout

- **Type:** {layout['type']}
- **Regions:** {', '.join(layout['regions'])}
- **Navigation:** {layout['navigation']}
- **Responsive:** {'Yes' if layout['responsive'] else 'No'}

---

## Design Principles

1. **Clarity** — Users should understand the interface in under 5 seconds.
2. **Consistency** — Use the same colour tokens and spacing throughout.
3. **Accessibility** — Minimum 4.5:1 contrast ratio for all text.
4. **Performance** — No render-blocking resources; CSS under 50 KB.
5. **Mobile First** — Design for small screens, then scale up.

---

## Components

- **Buttons:** `.btn`, `.btn-primary`, `.btn-accent`, `.btn-outline`
- **Cards:** `.card` with `--shadow` and `--radius`
- **Forms:** Styled `input`, `textarea`, `select` with focus ring
- **Grid:** `.grid-2`, `.grid-3` for responsive layouts
- **Utilities:** `.flex`, `.flex-between`, spacing `.mt-*`, `.p-*`

---

*CSS file generated at: `static/style.css`*
"""

        with open(spec_path, "w") as f:
            f.write(spec)

        design_report = {
            "generated_at":  datetime.utcnow().isoformat(),
            "project_type":  project_type,
            "palette":       palette,
            "layout":        layout,
            "css_file":      css_path,
            "spec_file":     spec_path,
            "css_size_bytes": len(css),
        }

        project["design"] = design_report
        project["status"] = "DESIGN_COMPLETE"
        self.memory.write(key, project)

        print(f"[Design AI] Tone      : {palette['tone']}")
        print(f"[Design AI] Layout    : {layout['type']}")
        print(f"[Design AI] CSS       : {css_path} ({len(css)} bytes)")
        print(f"[Design AI] Spec      : {spec_path}")
