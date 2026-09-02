---
name: Academic Professional
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#44474c'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#74777d'
  outline-variant: '#c4c6cd'
  surface-tint: '#4f6073'
  primary: '#041627'
  on-primary: '#ffffff'
  primary-container: '#1a2b3c'
  on-primary-container: '#8192a7'
  inverse-primary: '#b7c8de'
  secondary: '#0060ac'
  on-secondary: '#ffffff'
  secondary-container: '#68abff'
  on-secondary-container: '#003e73'
  tertiary: '#0e171d'
  on-tertiary: '#ffffff'
  tertiary-container: '#222b32'
  on-tertiary-container: '#89929b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d2e4fb'
  primary-fixed-dim: '#b7c8de'
  on-primary-fixed: '#0b1d2d'
  on-primary-fixed-variant: '#38485a'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#a4c9ff'
  on-secondary-fixed: '#001c39'
  on-secondary-fixed-variant: '#004883'
  tertiary-fixed: '#dbe4ed'
  tertiary-fixed-dim: '#bfc8d0'
  on-tertiary-fixed: '#141d23'
  on-tertiary-fixed-variant: '#3f484f'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  h1-desktop:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h1-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Source Sans 3
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Source Sans 3
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  caption:
    fontFamily: Source Sans 3
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max-width: 1200px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is rooted in the "Academic Modernist" aesthetic. It prioritizes clarity, authority, and focus, mirroring the environment of a premium university library or a high-end research portal. The interface is designed to fade into the background, allowing the educational content to remain the primary focus.

**Style Pillars:**
- **Minimalism:** Use generous whitespace to reduce cognitive load during study sessions.
- **Structured Hierarchy:** Clear distinction between navigational elements and core academic content.
- **Trust & Reliability:** A stable, "fixed" feel that avoids trendy motion or transient visual effects.
- **Editorial Quality:** High-contrast text on clean surfaces to ensure maximum legibility for long-form note-taking and reading.

## Colors

The palette is restrained and intentional, utilizing "Institutional Navy" and "Scholarly Blue" to evoke a sense of tradition and modern technology combined.

- **Primary (#1A2B3C):** Used for headlines, iconography, and high-emphasis text. It provides a grounded, authoritative feel.
- **Secondary/Accent (#4A90E2):** A muted blue used sparingly for interactive elements, primary call-to-actions, and progress indicators.
- **Neutral Background (#F8F9FA):** A soft off-white that reduces eye strain compared to pure white, serving as the primary canvas for the application.
- **Surface (#FFFFFF):** Pure white is reserved for cards, input fields, and content containers to create a "layered paper" effect.
- **Status Colors:** Use standard success (Green), warning (Amber), and error (Red) in desaturated tones to match the professional temperament.

## Typography

This design system utilizes a dual-sans-serif approach to balance interface precision with reading comfort.

- **Headlines (Inter):** Leverages the geometric clarity of Inter for structural elements and titles. H1s should feel "strong" and "prominent," acting as the anchor for the page.
- **Body Text (Source Sans 3):** Chosen for its exceptional legibility in long paragraphs. The line height is intentionally generous (1.5–1.6) to facilitate sustained reading without fatigue.
- **Scale:** Maintain a strict vertical rhythm. All text should be aligned to a 4px baseline grid to maintain academic order.

## Layout & Spacing

The layout philosophy follows a **Fixed-Fluid Hybrid** model. While the sidebar and navigational elements are fixed, the content area scales gracefully within a 1200px maximum width to ensure line lengths remain optimal for reading.

- **Grid:** A 12-column grid is used for desktop layouts.
- **Rhythm:** Spacing is strictly based on increments of 8px (8, 16, 24, 32, 48, 64).
- **Margins:** Desktop margins are wide (40px) to create a "framed" look, similar to a published paper.
- **Mobile Adaptivity:** On mobile, margins reduce to 16px, and multi-column card layouts stack vertically.

## Elevation & Depth

This design system avoids heavy shadows and floating effects in favor of **Tonal Layering and Thin Outlines**.

- **Surfaces:** Depth is communicated by placing White (#FFFFFF) cards on top of the Off-White (#F8F9FA) background.
- **Borders:** A 1px solid border (#E1E4E8) is the primary method of defining containment.
- **Shadows:** Use a single "Soft Lift" shadow for active cards or hover states only: `0px 2px 4px rgba(26, 43, 60, 0.05)`. Avoid large, diffused shadows.
- **Depth Levels:**
    - Level 0: Background (#F8F9FA).
    - Level 1: Content Surfaces/Cards (#FFFFFF) with 1px border.
    - Level 2: Modals or Popovers with a slightly more pronounced shadow but no change in border style.

## Shapes

The shape language is "Professional-Soft." It moves away from the harshness of sharp corners to provide a modern feel, but stops well short of the playfulness of pill shapes.

- **Standard Radius:** 8px (0.5rem) for cards, buttons, and input fields.
- **Small Radius:** 4px (0.25rem) for tags, checkboxes, and small utility buttons.
- **Interactive Elements:** Ensure consistent corner rounding across all form factors to maintain the system's "integrated" feel.

## Components

### Buttons
- **Primary:** Background #4A90E2, Text #FFFFFF. Solid fill, 8px radius.
- **Secondary:** Border 1px solid #1A2B3C, Text #1A2B3C, Background transparent.
- **Ghost:** Text #1A2B3C, no border or background until hover (use #F8F9FA on hover).

### Cards
- White background, 1px #E1E4E8 border, 8px radius.
- Padding should be generous (typically 24px or 32px) to maintain the "spacious" academic feel.

### Form Fields
- Inputs use the #FFFFFF background with a 1px #E1E4E8 border.
- On focus, the border changes to #4A90E2 with a subtle 2px outer glow of the same color at 20% opacity.

### Tabs
- Horizontal orientation.
- Active state indicated by the Primary Navy (#1A2B3C) text and a 2px bottom border (indicator) in Muted Blue (#4A90E2).
- Inactive states use Tertiary Gray (#6C757D) with no bottom border.

### Chips & Tags
- Used for categories or metadata.
- Light gray background (#F1F3F5) with Dark Navy text. Rounded 4px.

### Navigation
- Vertical sidebar for application-level navigation using the Primary Navy background with low-opacity white text, or a clean white sidebar with navy text for a lighter feel.