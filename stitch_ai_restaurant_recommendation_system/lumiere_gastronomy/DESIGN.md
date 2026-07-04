---
name: Lumiere Gastronomy
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#cbc3d7'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#958ea0'
  outline-variant: '#494454'
  surface-tint: '#d0bcff'
  primary: '#d0bcff'
  on-primary: '#3c0091'
  primary-container: '#a078ff'
  on-primary-container: '#340080'
  inverse-primary: '#6d3bd7'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#ffafd3'
  on-tertiary: '#620040'
  tertiary-container: '#e364a7'
  on-tertiary-container: '#560038'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffd8e7'
  tertiary-fixed-dim: '#ffafd3'
  on-tertiary-fixed: '#3d0026'
  on-tertiary-fixed-variant: '#85145a'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 64px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 40px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max: 1440px
  gutter: 24px
  margin-desktop: 80px
  margin-mobile: 20px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  section-gap: 120px
---

## Brand & Style

The design system is centered on a "Digital Concierge" persona—sophisticated, intuitive, and hyper-modern. It targets a discerning audience that seeks premium culinary experiences facilitated by cutting-edge AI. The visual narrative combines the weightless elegance of **Glassmorphism** with the precision of a high-tech interface.

The emotional response should be one of effortless discovery and luxury. By utilizing deep obsidian foundations paired with ethereal light-refracting surfaces, the UI creates an immersive "night-out" atmosphere. Micro-interactions should feel fluid and viscous, mimicking the movement of high-end optical lenses.

## Colors

The palette is anchored in a multi-layered dark mode. The base is a deep **Midnight Navy (#020617)**, providing the infinite depth required for glass effects to pop. 

- **Primary & Secondary:** A vibrant gradient spanning from **Violet (#8B5CF6)** to **Azure (#06B6D4)** represents the "AI intelligence" layer.
- **Surface Colors:** Surfaces are not solid; they utilize semi-transparent slates with a 50-70% opacity to allow background blurs to bleed through.
- **Functional Colors:** Success states utilize emerald tints, while warnings use a soft amber, always maintained at a high enough luminosity to contrast against the dark base.

## Typography

This design system employs a dual-font strategy. **Outfit** is used for headings to provide a geometric, modern, and slightly "tech-luxe" feel. Its wide apertures and clean lines ensure legibility even in glowing states. 

**Inter** handles all body copy and UI labels, providing the systematic clarity needed for complex data like menus and ratings. For display headings, a tighter letter-spacing is applied to create a high-fashion editorial look. All text should maintain a high contrast ratio against the dark background, primarily using off-whites and cool greys to avoid harsh optical strain.

## Layout & Spacing

The layout philosophy follows a **Fluid-Fixed Hybrid**. Content is housed within a 12-column grid with a maximum width of 1440px, centered on the screen. 

- **Desktop:** Generous section gaps (120px+) to emphasize exclusivity and give the high-quality imagery room to breathe.
- **Gradients as Spacing:** Subtle background radial gradients should be used to anchor different layout sections, acting as soft visual delimiters rather than hard lines.
- **Mobile:** Transition to a single-column layout with 20px side margins. Use horizontal "peek-a-boo" scrolling for restaurant card lists to maintain the horizontal rhythm of the desktop experience.

## Elevation & Depth

Depth is achieved through **Backdrop Filtering** rather than traditional drop shadows. 

1.  **Level 1 (Base):** Deepest background, solid color.
2.  **Level 2 (Cards/Modules):** `backdrop-filter: blur(12px)`; background: `rgba(255, 255, 255, 0.03)`; border: `1px solid rgba(255, 255, 255, 0.1)`.
3.  **Level 3 (Popovers/Modals):** `backdrop-filter: blur(24px)`; background: `rgba(255, 255, 255, 0.08)`; box-shadow: `0 20px 40px rgba(0, 0, 0, 0.4)`.

The "glow" effect is a signature of this system. Interactive elements should have a primary-colored outer glow (`box-shadow: 0 0 20px rgba(139, 92, 246, 0.3)`) when hovered or active, simulating a neon-lit premium establishment.

## Shapes

The design system uses a **Rounded (Level 2)** shape language. This strikes a balance between the clinical sharpness of tech and the organic warmth of the hospitality industry. 

- Standard components (buttons, small cards) use a 0.5rem (8px) radius.
- Large featured restaurant cards and main containers use a 1rem (16px) radius.
- Interactive pills and chips use a fully rounded "stadium" shape to distinguish them from structural elements.

## Components

### Buttons
Primary buttons feature the Violet-to-Azure gradient with white text. Secondary buttons use a "Ghost Glass" style: transparent background, white border (0.1 opacity), and a heavy backdrop blur. On hover, the border opacity increases and a subtle inner glow is applied.

### Glassy Cards
The core of the UI. Cards must have a 1px top-left highlight border (white at 0.2 opacity) to simulate light hitting a glass edge. Backgrounds must never be 100% opaque.

### AI Recommendations (Glow State)
Specialized "AI-picked" cards should feature a pulsating outer border-gradient and a "Lens Flare" micro-animation that traverses the card face every few seconds.

### Inputs
Search bars and filters should feel integrated into the background. Use a dark, semi-transparent fill with a focus state that illuminates the entire border in the primary gradient.

### Chips & Tags
Use low-saturation background tints of the primary colors (e.g., a dark purple tint for "Fine Dining") with high-vibrancy text labels. These indicate cuisine types, price points, and "AI Match" percentages.