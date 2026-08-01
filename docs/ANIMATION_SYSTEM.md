# NEXUS Animation System
**Version:** 0.1.0

---

## Philosophy

Animations must feel **purposeful and alive** — never decorative noise. Every animation either:
1. Communicates state (loading, online, working, complete)
2. Provides spatial context (page enter, card hover, element appear)
3. Reinforces the brand (holographic, cyber, alive)

All transitions use `ease` or `ease-out`. Avoid `linear` except for rotating loaders.

---

## Keyframes (defined in nexus.css)

### `fadeUp`
```css
from { opacity: 0; transform: translateY(16px); }
to   { opacity: 1; transform: translateY(0); }
```
**Used on:** Page content sections, cards, messages. Duration 0.4s.
**Variants:** `.fade-up`, `.fade-up-2` (0.5s, 0.1s delay), `.fade-up-3` (0.6s, 0.2s delay)

### `fadeIn`
```css
from { opacity: 0; } to { opacity: 1; }
```
**Used on:** Body page transition, overlay elements. Duration 0.3s.

### `pulse-green`
```css
50% { box-shadow: 0 0 0 5px rgba(0,255,153,0); }
```
**Used on:** AI status dot (Online state). Duration 2.5s infinite.

### `pulse-cyan`
```css
50% { box-shadow: 0 0 0 6px rgba(0,212,255,0); }
```
**Used on:** AI status dot (Working state), active project dots. Duration 1s infinite.

### `dot-bounce`
```css
40% { transform: scale(1); opacity: 1; }
0%,80%,100% { transform: scale(0.55); opacity: 0.35; }
```
**Used on:** Thinking indicator dots (3 dots, staggered delays). Duration 1.2s infinite.

### `float`
```css
50% { transform: translateY(-8px); }
```
**Used on:** NEXUS logo mark on chat welcome screen. Duration 4s ease-in-out infinite.

### `glow-pulse`
```css
50% { opacity: 1; } 0%,100% { opacity: 0.5; }
```
**Used on:** Auth page logo glow ring.

### `scanlines` (`.scanlines::after`)
Repeating horizontal lines at 4px pitch, 3% opacity.
**Used on:** Optional body class for full CRT scan-line effect.

---

## Transition Catalogue

| Element | Property | Duration | Easing | Effect |
|---------|----------|----------|--------|--------|
| `.card` | `border-color`, `box-shadow` | 0.2s | ease | Border brightens on hover |
| `.card::before` | `opacity` | 0.2s | ease | Holographic top line appears |
| `.stat-card` | `transform`, `box-shadow` | 0.15s | ease | Lift `-3px` |
| `.stat-card::after` | `transform: scaleX` | 0.3s | ease | Gradient bottom bar sweeps in |
| `.nav-item` | `background`, `color`, `border` | 0.2s | ease | Subtle wash + text brightens |
| `.launch-card` | `transform`, `box-shadow` | 0.2s | ease | Lift `-4px` + deepen shadow |
| `.launch-card::after` | `transform: scaleX` | 0.3s | ease | Bottom gradient sweeps from center |
| `.worker-card::before` | `opacity` | 0.3s | ease | Top gradient line appears |
| `.btn-primary` | `box-shadow`, `transform` | 0.2s | ease | Glow intensifies, lifts `-1px` |
| `.project-card` | `transform`, `border-color` | 0.2s | ease | Slide right `+3px` |
| `.chat-input-box` | `border-color`, `box-shadow` | 0.2s | ease | Focus glow ring |
| `.build-type` | `transform`, `border-color` | 0.2s | ease | Lift `-3px` |
| `.build-type::before` | `opacity` | 0.2s | ease | Gradient wash appears |
| `.chat-suggestion` | `background`, `border`, `box-shadow` | 0.2s | ease | Cyan highlight |
| `.sidebar-logo-icon` | `filter` (drop-shadow) | 0.2s | ease | Glow intensifies |

---

## JS Animations (nexus.js)

### Chat message appear
Each new `.msg` div gets `.fade-up` class via CSS `animation` — no JS needed.

### Thinking dots
Pure CSS `dot-bounce` on three `<span>` elements with staggered animation-delay.

### SSE streaming
Tokens appended one by one via EventSource, creating a typewriter effect naturally.

### Pipeline progress bar
`element.style.width = pct + '%'` — CSS `transition: width 0.5s ease` handles smoothness.

### Builder console
`scrollTop = scrollHeight` on each new log line keeps the console pinned to bottom.

---

## Future Animations (planned)

### v0.2 — Pipeline visualisation
- Animated flow diagram showing which stage is active
- Worker icons pulse when active
- Stage-complete checkmark animate in

### v0.3 — Voice waveform (from brand sheet)
- Real-time audio waveform SVG when mic is active (like the brand image shows)
- Speaking animation on NEXUS avatar when responding

### v0.4 — Splash screen
- Animated NEXUS logo on first load
- Blue energy particle burst
- Fade transition to dashboard

### v0.5 — Holographic grid
- Subtle 3D perspective grid in background
- Pans slowly as mouse moves (parallax)
