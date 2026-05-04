# Design System (Minimalist Black & White)

## 1. Visual Theme & Atmosphere

This design system is built on confident minimalism — a black-and-white interface where every element has a clear purpose and nothing exists purely for decoration.

The entire experience is based on a strict duality:
- deep black (`#121212`)
- pure white (`#ffffff`)

There are no unnecessary mid-tones or visual noise.

Typography relies on geometric sans-serif fonts with a clean and engineered feel:
- headings are bold and authoritative
- body text is highly readable and functional

The interface makes heavy use of:
- **pill-shaped elements (999px border-radius)**
- **card-based layouts**
- **subtle shadows**
- **compact, information-dense spacing**

---

## 2. Color Palette & Roles

See `apps\web\assets\css\main.css` for color palette of the project. Use this for building interfaces, don't make up the new colors 
without any need.

### Principle
- No gradients
- Only solid colors

---

## 3. Typography Rules

### Font Family
- Primary: `system-ui`, `Inter`, `DM Sans`

### Hierarchy

| Role | Size | Weight | Line Height |
|------|------|--------|------------|
| Hero | 52px | 700 | 1.23 |
| Section Heading | 36px | 700 | 1.22 |
| Card Title | 32px | 700 | 1.25 |
| Subheading | 24px | 700 | 1.33 |
| Small Heading | 20px | 700 | 1.40 |
| UI Text | 18px | 500 | 1.33 |
| Body | 16px | 400-500 | 1.25-1.50 |
| Caption | 14px | 400 | 1.4 |
| Micro | 12px | 400 | 1.6 |

### Principles
- Headings are always bold
- Body text is medium or regular weight
- No decorative typography

---

## 4. Component Stylings

### Buttons

**Primary**
- Background: Black
- Text: White
- Padding: 10px 12px
- Radius: 999px

**Secondary**
- Background: White
- Text: Black
- Hover: `#e2e2e2`
- Radius: 999px

**Chip**
- Background: `#efefef`
- Radius: 999px

**Floating Action**
- Background: White
- Shadow: `rgba(0,0,0,0.16)`
- Radius: 999px

---

### Cards
- Radius: 8px (standard), 12px (featured)
- Shadow: `rgba(0,0,0,0.12)`
- No borders

---

### Inputs
- Border: 1px solid black
- Radius: 8px
- Background: white

---

### Navigation
- Sticky top bar
- Minimal design
- Pill-style navigation elements

---

## 5. Layout Principles

### Spacing
- Base unit: 8px
- Scale: 4px → 32px

### Container
- Max width: ~1136px

### Philosophy
- Efficiency over airiness
- High information density

---

## 6. Depth & Elevation

| Level | Treatment |
|------|----------|
| 0 | No shadow |
| 1 | `rgba(0,0,0,0.12)` |
| 2 | `rgba(0,0,0,0.16)` |
| 3 | Floating elements |
| 4 | Inset (pressed state) |

---

## 7. Nuxt UI Usage Guidelines

### Core Principle

When building the interface, **prefer using Nuxt UI components whenever possible**.

### Rules

- Do NOT create custom components if:
  - an equivalent exists in Nuxt UI
  - it can be adapted via props, slots, or styling

### When Custom Markup is Allowed

Use plain HTML + CSS (or Tailwind) only if:
- the required component does not exist in Nuxt UI
- the behavior is too specific or complex
- a unique layout cannot be achieved with existing components

### Anti-patterns

- ❌ Rebuilding buttons from scratch
- ❌ Duplicating Nuxt UI logic
- ❌ Mixing too many custom and library components inconsistently

### Goal

- UI consistency
- faster development
- easier maintenance

---

## 8. Do's and Don'ts

### Do
- Use black and white as the primary palette
- Use pill-shaped buttons and controls
- Keep layouts compact
- Use subtle shadows

### Don't
- Do not use gradients
- Do not introduce unnecessary colors
- Do not create overly spacious layouts
- Do not use heavy shadows

---

## 9. Responsive Behavior

### Breakpoints

| Name | Width |
|------|------|
| Mobile | 320–600px |
| Tablet | 768–1119px |
| Desktop | 1120px+ |

### Rules
- Layouts stack vertically on smaller screens
- Buttons must be at least 44px height
- Grids collapse into single column

---

## 10. Agent Prompt Guide

### Principles
- Be explicit about colors (`#121212`, `#ffffff`)
- Always specify border-radius for buttons (999px)
- Keep layouts compact and structured
- Prefer consistency over creativity