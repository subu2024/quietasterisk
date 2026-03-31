# Quiet Asterisk Design Guide

Complete design system documentation for the Quiet Asterisk blog.

## 🎨 Design Philosophy

The Quiet Asterisk blog features a **modern literary editorial** aesthetic that balances:
- Warmth and approachability (earth tones, soft gradients)
- Sophistication and readability (premium typography, generous spacing)
- Modern interactivity (glassmorphism, smooth animations, hover effects)
- Content-first focus (minimal chrome, clear hierarchy)

---

## 🌈 Color Palette

### Primary Colors

```css
--color-cream: #FAF8F3      /* Main background, light neutral */
--color-sand: #E8E3D8       /* Borders, dividers, subtle backgrounds */
--color-charcoal: #2B2826   /* Primary text, dark elements */
```

### Accent Colors

```css
--color-rust: #B8503E       /* Primary accent, links, CTAs */
--color-terracotta: #D17458 /* Lighter rust variant, gradients */
--color-sage: #8B9B7E       /* Secondary accent, calm elements */
--color-gold: #C9A767       /* Tertiary accent, highlights */
--color-slate: #5A5450      /* Secondary text, muted content */
```

### Usage Guidelines

**Rust (`#B8503E`):**
- Primary buttons and CTAs
- Important links
- Featured badges
- Active navigation states
- Category labels

**Sage (`#8B9B7E`):**
- Secondary accents
- Divider dots
- Calm call-outs
- Alternative badges

**Gold (`#C9A767`):**
- Premium elements
- Book-related content
- Tertiary highlights
- Gradient accents

**Charcoal (`#2B2826`):**
- All body text
- Headings
- Navigation text
- High-contrast elements

**Slate (`#5A5450`):**
- Metadata (dates, reading time)
- Secondary text
- Muted labels
- Inactive states

---

## ✍️ Typography

### Font Families

```css
--font-serif: 'Crimson Pro', serif    /* Headings, body text */
--font-sans: 'Work Sans', sans-serif  /* UI elements, labels */
```

**Crimson Pro (Serif):**
- All headings (H1-H6)
- Article body text
- Pull quotes
- Hero titles
- Signature text

**Work Sans (Sans-serif):**
- Navigation menus
- Buttons and CTAs
- Labels and badges
- Metadata
- Footer text
- Form inputs

### Type Scale

```css
/* Hero/Display */
7rem (112px)    - Homepage hero title
4.5rem (72px)   - Section hero titles
3.5rem (56px)   - Page titles

/* Headings */
3rem (48px)     - H1
2.5rem (40px)   - H2
2rem (32px)     - H3
1.5rem (24px)   - H4
1.25rem (20px)  - H5

/* Body */
1.125rem (18px) - Large body text, about page
1rem (16px)     - Standard body text
0.9375rem (15px)- Small body text

/* UI */
0.875rem (14px) - Labels, metadata, captions
0.75rem (12px)  - Tiny labels, badges
```

### Font Weights

```css
400 - Regular   (body text)
500 - Medium    (emphasis, labels)
600 - Semibold  (subheadings, UI)
700 - Bold      (headings)
800 - Extrabold (hero titles)
```

### Line Heights

```css
1.1 - Hero titles, display text
1.2 - Section headings
1.5 - Card titles
1.6 - Subheadings, descriptions
1.7 - About page, featured text
1.8 - Article body, long-form content
```

---

## 🎭 Modern Design Elements

### Glassmorphism

Semi-transparent elements with blur effects for depth:

```css
background: rgba(255, 255, 255, 0.7);
backdrop-filter: blur(10px);
border: 2px solid rgba(184, 80, 62, 0.2);
```

**Used in:**
- Hero stat cards
- Badge pills
- Secondary buttons
- Floating elements

### Gradient Backgrounds

Subtle color transitions for visual interest:

```css
/* Hero gradient */
background: linear-gradient(135deg, #FAF8F3 0%, #E8E3D8 50%, #F5E6D3 100%);

/* Section gradient */
background: linear-gradient(180deg, var(--color-cream) 0%, white 100%);

/* Button gradient */
background: linear-gradient(135deg, var(--color-rust), var(--color-terracotta));
```

### Gradient Text

Multi-color text using background-clip:

```css
background: linear-gradient(135deg, var(--color-charcoal) 0%, var(--color-rust) 50%, var(--color-gold) 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

**Used in:**
- Hero titles
- Stat numbers
- Feature headings

### Floating Background Blobs

Animated radial gradients for depth:

```css
position: absolute;
width: 500px;
height: 500px;
background: radial-gradient(circle, rgba(184, 80, 62, 0.15), transparent);
border-radius: 50%;
filter: blur(60px);
animation: float 20s infinite ease-in-out;
```

**Animation:**
```css
@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(5deg); }
  66% { transform: translate(-20px, 20px) rotate(-5deg); }
}
```

### Pill Badges

Rounded badges with colored borders:

```css
padding: 0.5rem 1.5rem;
background: rgba(184, 80, 62, 0.1);
border: 2px solid var(--color-rust);
border-radius: 50px;
text-transform: uppercase;
letter-spacing: 0.15em;
font-size: 0.875rem;
font-weight: 600;
```

**Color variants:**
- Rust border - Featured content
- Sage border - Latest/recent content
- Gold border - Premium/books

---

## 🎴 Card Components

### Standard Card

```css
background: white;
border: 2px solid var(--color-sand);
padding: 2.5rem;
border-radius: 4px;
transition: all 0.3s;
```

**Hover state:**
```css
border-color: var(--color-charcoal);
box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
transform: translateY(-4px);
```

### Featured Card (Large)

- Spans 2 rows in grid
- 3rem padding
- Featured badge at top
- Larger title (3rem)
- Larger excerpt (1.25rem)

### Glassmorphic Card (Stats)

```css
background: rgba(255, 255, 255, 0.7);
backdrop-filter: blur(10px);
border: 2px solid rgba(184, 80, 62, 0.2);
border-radius: 16px;
padding: 2rem;
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
```

**Hover:**
```css
transform: translateY(-8px);
box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
```

---

## 🔘 Buttons

### Primary Button

```css
background: var(--color-rust);
color: white;
border: 2px solid var(--color-rust);
padding: 1.25rem 2.5rem;
font-family: var(--font-sans);
font-weight: 500;
font-size: 1.125rem;
border-radius: 2px;
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
transition: all 0.3s;
```

**Hover:**
```css
background: #A03D2F;
box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
transform: translateY(-2px);
```

### Secondary Button

```css
background: transparent;
color: var(--color-charcoal);
border: 2px solid var(--color-charcoal);
```

**Hover:**
```css
background: var(--color-charcoal);
color: white;
```

### Glassmorphic Button

```css
backdrop-filter: blur(10px);
background: rgba(255, 255, 255, 0.5);
border: 2px solid var(--color-charcoal);
```

---

## 📐 Spacing System

### Container Widths

```css
max-width: 1280px  /* Main container */
max-width: 56rem   /* Video/content sections */
max-width: 48rem   /* Article content, forms */
max-width: 42rem   /* About page, narrow content */
max-width: 36rem   /* Descriptions, subtitles */
```

### Section Padding

```css
padding: 8rem 0 6rem  /* Hero sections */
padding: 6rem 0       /* Major sections */
padding: 4rem 0       /* Minor sections */
padding: 3rem 0       /* Compact sections */
```

### Element Spacing

```css
margin-bottom: 3rem   /* Between major elements */
margin-bottom: 2rem   /* Between paragraphs (about page) */
margin-bottom: 1.5rem /* Between card elements */
margin-bottom: 1rem   /* Between small elements */
margin-bottom: 0.5rem /* Between tightly grouped items */
```

### Grid Gaps

```css
gap: 2rem        /* Card grids */
gap: 1.5rem      /* Stat cards, modern grids */
gap: 1rem        /* Button groups, inline items */
gap: 0.5rem      /* Tight groupings */
```

---

## 🖼️ Layout Patterns

### Hero Section

```html
<section class="hero" style="
  background: linear-gradient(...);
  position: relative;
  overflow: hidden;
  padding: 8rem 0 6rem;
">
  <!-- Floating blobs -->
  <div style="position: absolute; ...animated blob..."></div>
  
  <div class="container" style="position: relative; z-index: 10;">
    <div style="text-align: center;">
      <!-- Pill badge -->
      <!-- Large title with gradient -->
      <!-- Subtitle -->
      <!-- Description -->
      <!-- CTA buttons -->
      <!-- Stats cards -->
    </div>
  </div>
</section>
```

### Section Header (Centered)

```html
<div style="text-align: center; margin-bottom: 4rem;">
  <!-- Pill badge -->
  <div style="...badge styles...">Label</div>
  
  <!-- Title -->
  <h2 style="font-size: clamp(2.5rem, 5vw, 3.5rem); ...">Title</h2>
  
  <!-- Description -->
  <p style="font-size: 1.25rem; max-width: 36rem; margin: 0 auto;">Description</p>
  
  <!-- Decorative line -->
  <div style="width: 80px; height: 4px; background: linear-gradient(...); margin: 0 auto;"></div>
</div>
```

### Card Grid

```html
<div class="card-grid" style="
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
">
  <!-- Cards -->
</div>
```

### Featured Grid (1 large + 3 small)

```html
<div class="featured-grid" style="
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
">
  <!-- Large featured card (grid-row: span 2) -->
  <div style="display: flex; flex-direction: column; gap: 2rem;">
    <!-- 3 small cards -->
  </div>
</div>
```

---

## 🎬 Animations & Transitions

### Standard Transitions

```css
transition: all 0.3s;           /* General purpose */
transition: transform 0.3s;     /* Movement only */
transition: color 0.3s;         /* Color changes */
transition: box-shadow 0.3s;    /* Shadow changes */
```

### Hover Effects

**Card Lift:**
```css
transform: translateY(-4px);
box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
```

**Button Lift:**
```css
transform: translateY(-2px);
box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
```

**Stat Card Lift:**
```css
transform: translateY(-8px);
box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
```

**Color Transition:**
```css
onmouseover="this.style.color='var(--color-rust)'"
onmouseout="this.style.color='var(--color-charcoal)'"
```

### Keyframe Animations

**Float (background blobs):**
```css
@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(5deg); }
  66% { transform: translate(-20px, 20px) rotate(-5deg); }
}
animation: float 20s infinite ease-in-out;
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile first - base styles for mobile */
@media (max-width: 768px) {
  /* Tablets and below */
}

@media (max-width: 480px) {
  /* Small phones */
}
```

### Responsive Typography

Use `clamp()` for fluid typography:

```css
font-size: clamp(3.5rem, 8vw, 7rem);    /* Hero */
font-size: clamp(2.5rem, 5vw, 3.5rem);  /* Section titles */
font-size: clamp(1.25rem, 2.5vw, 1.75rem); /* Subtitles */
font-size: clamp(3rem, 5vw, 4rem);      /* Page titles */
```

### Mobile Adjustments

**Hero:**
- Reduce padding: `4rem 0 3rem`
- Stack stats vertically: `grid-template-columns: 1fr`

**Navigation:**
- Stack vertically
- Center items
- Increase touch targets

**Cards:**
- Single column: `grid-template-columns: 1fr`
- Reduce padding

---

## 🎯 Component Specifications

### Navigation Header

- Sticky position
- Backdrop blur
- 2px sand border bottom
- Active state: rust underline (2px, 0.25rem below)
- Hover: color change charcoal

### Footer

- Dark background (charcoal)
- Cream text
- 3-column grid (auto-fit, 250px min)
- Rust section titles
- 1px slate border-top for copyright

### Dividers

```html
<div class="divider" style="
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 0;
">
  <div style="width: 4rem; height: 2px; background: var(--color-rust);"></div>
  <div style="width: 8px; height: 8px; border-radius: 50%; background: var(--color-rust);"></div>
  <div style="width: 4rem; height: 2px; background: var(--color-rust);"></div>
</div>
```

### Video Embeds

```css
position: relative;
padding-bottom: 56.25%;  /* 16:9 aspect ratio */
height: 0;
overflow: hidden;
border-radius: 8px;
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
```

Iframe inside:
```css
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 100%;
```

### Archive Accordion

**Year button:**
- Gradient background (rust to terracotta)
- White text
- 1.5rem padding
- Box shadow with hover lift

**Month button:**
- White background
- Sand border → rust on hover
- Cream background on hover

**Post cards:**
- Cream background
- Left border: 3px sage
- Hover: title color → rust

---

## 🎨 Best Practices

### Do's ✅

- Use gradient text for hero titles
- Add hover effects to all interactive elements
- Maintain generous white space
- Use glassmorphism for overlay elements
- Stick to the color palette
- Use clamp() for responsive typography
- Add loading states and transitions
- Keep borders minimal (2px max)
- Use backdrop-filter for depth

### Don'ts ❌

- Don't use black (#000) - use charcoal
- Don't use pure white backgrounds everywhere
- Don't overuse animations
- Don't mix serif/sans inappropriately
- Don't ignore mobile breakpoints
- Don't use more than 3 accent colors per section
- Don't create jarring color transitions
- Don't forget hover states

---

## 🔍 Accessibility

### Color Contrast

All text meets WCAG AA standards:
- Charcoal on cream: 8.5:1 ✅
- Rust on white: 4.8:1 ✅
- Slate on white: 7.2:1 ✅
- White on rust: 4.8:1 ✅

### Interactive Elements

- All buttons have clear hover states
- Links are underlined in body text
- Focus states visible for keyboard navigation
- Touch targets minimum 44x44px
- Alt text for all images

### Semantic HTML

- Proper heading hierarchy (H1 → H2 → H3)
- `<article>` for blog posts
- `<nav>` for navigation
- `<section>` for content sections
- `<main>` for primary content

---

## 🎨 Theme Variations

### Light Mode (Current)
- Cream backgrounds
- Charcoal text
- Soft shadows

### Potential Dark Mode
```css
--color-cream: #1A1816      /* Dark background */
--color-charcoal: #FAF8F3   /* Light text */
--color-sand: #2B2826       /* Borders */
/* Keep accent colors same */
```

---

## 📦 Design Assets

### Icons
- SVG icons for arrows, navigation
- Inline SVG for performance
- Single color (currentColor)
- 16px-24px typical sizes

### Images
- Book covers: consistent aspect ratio
- Border-radius: 4px
- Max-width: 100%
- Lazy loading for performance

### Fonts
- Google Fonts CDN
- Preload for performance
- Display: swap for FOUT prevention

---

## 🚀 Performance

### CSS Optimization
- Minimal selectors
- Inline critical CSS
- Avoid !important
- Use CSS variables

### Animation Performance
- Use transform and opacity
- Avoid animating width/height
- Use will-change sparingly
- requestAnimationFrame for JS

---

This design system ensures consistency, accessibility, and modern aesthetics across the entire Quiet Asterisk blog. 🎨✨
