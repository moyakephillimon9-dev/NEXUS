# NEXUS UI Design Document
**Version:** 0.1.0  
**Status:** Implemented (Foundation)

---

## 1. Design Philosophy

NEXUS must feel like an AI Operating System from the future — not an app, not a dashboard, but a *control centre*. The visual language communicates power, intelligence and precision. Every screen should make the Founder feel they are operating advanced technology.

**Three words:** Holographic. Precise. Alive.

---

## 2. Brand Identity (from official NEXUS brand sheet)

### Logo Mark
The **NX** mark — a combined angular N and X letterform with a blue-to-purple gradient. Used in:
- Sidebar header (SVG, 40×40)
- Auth pages (SVG, 50×50)
- Favicon

### Colour Suite
| Token | Hex | Usage |
|-------|-----|-------|
| Electric Cyan | `#00D4FF` | Primary actions, active states, glows |
| Violet Purple | `#8A2BE2` | Secondary accent, gradients, hover |
| White | `#FFFFFF` | Headings, primary text |
| Dark Navy | `#0D0D14` | Card surfaces |
| Darkest | `#07101A` | Page background |

### Derived Colours
| Token | Value | Usage |
|-------|-------|-------|
| `--gradient` | `135deg #00D4FF → #8A2BE2` | Buttons, active indicators, logo |
| `--cyan-glow` | `rgba(0,212,255,0.20)` | Box shadows, glow effects |
| `--purple-glow` | `rgba(138,43,226,0.20)` | Secondary glows |
| `--card-border` | `rgba(0,212,255,0.12)` | Card default borders |
| `--text` | `#d8e8ff` | Body text |
| `--text-mid` | `#7a8ab0` | Secondary text |
| `--text-muted` | `#3d4d6a` | Placeholders, labels |

### Typography
- **Font:** Inter (Google Fonts) — 400, 500, 600, 700, 800
- **Monospace:** Fira Code — console, clock, code blocks
- **Logo text:** 800 weight, 4px letter-spacing, gradient text

---

## 3. Layout System

### Shell Structure
```
┌─────────────────────────────────────────────┐
│  SIDEBAR (264px fixed)  │  TOPBAR (64px)     │
│                         ├───────────────────┤
│  Logo                   │                   │
│  Navigation             │   MAIN CONTENT    │
│  ─────────              │   (scrollable)    │
│  Owner pill             │                   │
└─────────────────────────┴───────────────────┘
```

### Sidebar
- Width: 264px (collapses to 220px at <1024px)
- Background: `#060e15`
- Right edge: gradient line (cyan→purple) at 35% opacity
- Logo: NX SVG mark + "NEXUS" gradient text
- Nav groups: Control Center, Build, Intelligence, System
- Active item: gradient left border + gradient background wash

### Top Bar
- Height: 64px
- Background: `rgba(7,16,26,0.88)` + `backdrop-filter: blur(24px)`
- Bottom edge: gradient line (cyan→purple) at 40% opacity
- Right: live clock (monospace), AI status pill

### Main Content
- Padding: 32px
- Margin: left 264px, top 64px
- Background inherits body (circuit pattern)

---

## 4. Circuit Board Texture

Applied to `body` background via CSS `url()` SVG data URI:
- Subtle grid lines at 80px intervals (`rgba(0,212,255,0.03)`)
- Small dots at grid intersections (cyan/purple, 5% opacity)
- Radial gradient overlay (cyan, top center, 6% opacity)

This creates the holographic/cyber feel without distracting from content.

---

## 5. Card System

### Default Card
- Background: `#0D0D14`
- Border: `rgba(0,212,255,0.12)` → brightens to `0.28` on hover
- Border-radius: 14px
- Holographic top edge: gradient line appears on hover (fade-in)
- Hover: subtle `translateY(-2px)`, deeper shadow

### Glow Card (`.card-glow`)
- Permanent blue+purple ambient glow
- Used for featured/highlighted content

### Stat Card
- Bottom gradient bar animates in on hover (scaleX 0→1)
- Coloured icon zone (cyan/purple/green/yellow variants)

### Holographic Border
Achieved by an `::before` pseudo-element with gradient background, opacity 0 → 0.6 on hover.

---

## 6. Screens (v0.1.0)

| Route | Screen | Status |
|-------|--------|--------|
| `/setup` | First-time setup | ✅ Built |
| `/login` | Owner login | ✅ Built |
| `/dashboard` | Main control centre | ✅ Built |
| `/chat` | Chat with NEXUS | ✅ Built |
| `/builder` | Project builder | ✅ Built |
| `/projects` | Projects list | ✅ Built |
| `/workers` | AI Workers | ✅ Built |
| `/memory` | Memory timeline | ✅ Built |
| `/reports` | Analytics | ✅ Built |
| `/settings` | Configuration | ✅ Built |
| `/roadmap` | Roadmap | ✅ Built |

---

## 7. What Is NOT Implemented (v0.1.0)

These remain **design/roadmap only** — no fake UI:

- Voice interface (waveform, mic button — logo sheet shows this, planned v0.3)
- Financial dashboard
- Social media management
- Mobile app
- Real-time notifications
- 2FA
- Dark/light theme toggle (dark only)
