# NEXUS Theme System
**Version:** 0.1.0

---

## CSS Custom Properties (Design Tokens)

All tokens live in `:root` in `static/css/nexus.css`.

### Brand (source of truth — do not change without updating brand docs)
```css
--cyan:   #00D4FF   /* Electric Cyan  — primary */
--purple: #8A2BE2   /* Violet Purple  — secondary */
--white:  #FFFFFF   /* Pure White     — headings */
--card-bg:#0D0D14   /* Dark Navy      — surfaces */
--bg:     #07101A   /* Darkest        — background */
```

### Gradients
```css
--gradient:   linear-gradient(135deg, #00D4FF, #8A2BE2)   /* main — diagonal */
--gradient-r: linear-gradient(135deg, #8A2BE2, #00D4FF)   /* reversed */
--gradient-h: linear-gradient(90deg,  #00D4FF, #8A2BE2)   /* horizontal */
```

### Glow / Alpha
```css
--cyan-glow:     rgba(0,212,255,0.20)
--purple-glow:   rgba(138,43,226,0.20)
--cyan-border:   rgba(0,212,255,0.22)
--purple-border: rgba(138,43,226,0.22)
--card-border:   rgba(0,212,255,0.12)
--bg-input:      rgba(255,255,255,0.04)
--bg-hover:      rgba(0,212,255,0.06)
```

### Typography scale
| Class / element | Size | Weight | Notes |
|-----------------|------|--------|-------|
| Page heading    | 26px | 700 | `welcome-text` |
| Section title   | 19px | 700 | `section-title` |
| Card title      | 16px | 600 | `card-title` |
| Body            | 15px | 400 | `body` default |
| Label           | 12px | 500 | `form-label`, uppercase |
| Badge / meta    | 11px | 600 | `badge` |
| Console         | 12px | 400 | `font-mono` |

### Spacing scale (px)
4, 8, 12, 14, 16, 18, 20, 22, 24, 28, 32, 40, 44, 48, 64

### Border radius
```css
--radius-sm: 8px    /* buttons, inputs, small chips */
--radius:    14px   /* cards, modals */
--radius-lg: 20px   /* auth card, large panels */
```

---

## Applying the Theme to New Components

1. Use `var(--cyan)` / `var(--purple)` — never hardcode `#00D4FF`.
2. Hover states: add `rgba(0,212,255,0.06)` background wash.
3. Active/selected: use `--gradient` as border-left or bottom bar.
4. Glow: `box-shadow: 0 0 20px var(--cyan-glow)`.
5. Text gradient: apply `.text-gradient` utility class.
6. Never use pure white for body text — use `var(--text)` (#d8e8ff).

---

## Future Themes (planned v0.6)

- **NEXUS Night** — current default (dark, cyan+purple)
- **NEXUS Solar** — amber/gold accent variant (founder can switch in Settings)
- **NEXUS Stealth** — near-black, monochrome with minimal accents

All theme variables will live in `:root[data-theme="night|solar|stealth"]`.
