# Theming and Styling

## Table of Contents

- [Theming System](#theming-system)
- [Color Variables](#color-variables)
- [Dark Mode](#dark-mode)
- [Custom Themes](#custom-themes)
- [Custom Semantic Colors](#custom-semantic-colors)
- [Component-Level Overrides](#component-level-overrides)
- [Styling Methods](#styling-methods)
- [Variant Functions](#variant-functions)
- [Custom Variants](#custom-variants)
- [BEM Class Reference](#bem-class-reference)
- [Data Attributes for Interactive States](#data-attributes-for-interactive-states)

## Theming System

HeroUI v3 uses CSS variables and BEM classes for theming. Built on Tailwind CSS v4's theme system with automatic light/dark switching and CSS layers.

### Naming Convention

- **Background colors**: Variables without suffix (e.g., `--accent`)
- **Foreground colors**: Variables with `-foreground` suffix (e.g., `--accent-foreground`)

## Color Variables

Override in `:root` or theme selectors:

```css
@import "tailwindcss";
@import "@heroui/styles";

:root {
  --accent: oklch(0.7 0.25 260);
  --success: oklch(0.65 0.15 155);
}
```

### Variable Categories

| Type | Description | Examples |
|------|-------------|---------|
| Base | Non-changing values | `--white`, `--black`, spacing, typography |
| Theme | Shift between light/dark | `--accent`, `--background`, `--foreground` |
| Calculated | Auto-generated states | Hover, focus variants via `@theme` |

### Field Control Variables

Form controls (inputs, checkboxes, radios, OTP slots) use `--field-*` variables. Update these to restyle form components independently from buttons or cards.

## Dark Mode

Toggle via HTML class and data attribute:

```html
<!-- Light -->
<html class="light" data-theme="light">

<!-- Dark -->
<html class="dark" data-theme="dark">
```

## Custom Themes

Define in separate CSS files with light/dark variants:

```css
@layer base {
  [data-theme="ocean"] {
    color-scheme: light;
    --accent: oklch(0.6 0.2 240);
    --background: oklch(0.97 0.01 240);
    --foreground: oklch(0.2 0.02 240);
  }

  [data-theme="ocean-dark"] {
    color-scheme: dark;
    --accent: oklch(0.7 0.18 240);
    --background: oklch(0.15 0.02 240);
    --foreground: oklch(0.95 0.01 240);
  }
}
```

Apply in globals with layer prioritization:

```css
@layer theme, base, components, utilities;

@import "tailwindcss";
@import "@heroui/styles";
@import "./src/themes/ocean.css" layer(theme);
```

## Custom Semantic Colors

Add colors for both light and dark themes, then register with Tailwind:

```css
:root,
[data-theme="light"] {
  --info: oklch(0.6 0.15 210);
  --info-foreground: oklch(0.98 0 0);
}

.dark,
[data-theme="dark"] {
  --info: oklch(0.7 0.12 210);
  --info-foreground: oklch(0.15 0 0);
}

@theme inline {
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
}
```

Usage:

```tsx
<div className="bg-info text-info-foreground">Info message</div>
```

## Component-Level Overrides

Override component styles globally using BEM classes in `@layer components`:

```css
@layer components {
  .button {
    @apply font-semibold tracking-wide;
  }

  .button--primary {
    @apply bg-blue-600 hover:bg-blue-700;
  }

  .accordion__trigger {
    @apply text-lg font-bold;
  }

  .select__trigger {
    @apply rounded-lg border border-border bg-surface p-2;
  }
}
```

## Styling Methods

### 1. className Prop

```tsx
<Button className="rounded-full shadow-lg font-bold">Styled</Button>
```

### 2. Inline Styles

```tsx
<Button style={{ borderRadius: "9999px" }}>Rounded</Button>
```

### 3. CSS Modules

```tsx
import styles from "./MyComponent.module.css";
<Button className={styles.customButton}>Styled</Button>
```

### 4. CSS-in-JS (Styled Components / Emotion)

```tsx
const StyledButton = styled(Button)`
  border-radius: 9999px;
`;
```

### 5. Global Stylesheet

```css
@layer components {
  .table-root {
    @apply relative grid w-full overflow-clip;
  }
  .table__header {
    @apply bg-gray-100;
  }
  .table__row {
    @apply bg-white border-b border-gray-200;
  }
}
```

### 6. Render Props for State-Based Styling

```tsx
<Button>
  {({ isPressed }) => (
    <span className={isPressed ? "text-white" : "text-gray-800"}>
      Press me
    </span>
  )}
</Button>
```

## Variant Functions

Type-safe styling available from `@heroui/styles` or `@heroui/react`:

```tsx
import { buttonVariants } from "@heroui/styles";

// Apply to any element
<a className={buttonVariants({ variant: "primary", size: "lg" })} href="/about">
  About
</a>
```

Available functions: `buttonVariants`, `chipVariants`, `linkVariants`, `spinnerVariants`, and component-specific functions.

### Slot-Based Variant Functions

Some components expose slot functions:

```tsx
const slots = linkVariants();

<a className={slots.base()} href="/about">
  About
  <span className={slots.icon()} />
</a>
```

## Custom Variants

Extend base variant functions with `tv()`:

```tsx
import { buttonVariants, tv } from "@heroui/styles";

const myButton = tv({
  extend: buttonVariants,
  base: "text-md font-semibold shadow-md",
  variants: {
    radius: {
      lg: "rounded-lg",
      md: "rounded-md",
    },
  },
});

<button className={myButton({ variant: "primary", radius: "lg" })}>
  Custom
</button>
```

## BEM Class Reference

### Pattern

- Block: `.button`, `.modal`, `.table-root`
- Element: `.modal__header`, `.table__cell`
- Modifier: `.button--primary`, `.button--lg`, `.modal__backdrop--blur`

### Common Component Classes

| Component | Base | Elements | Modifiers |
|-----------|------|----------|-----------|
| Button | `.button` | — | `--primary`, `--secondary`, `--tertiary`, `--outline`, `--ghost`, `--danger`, `--sm`, `--md`, `--lg`, `--icon-only` |
| Modal | `.modal` | `__trigger`, `__backdrop`, `__container`, `__dialog`, `__header`, `__body`, `__footer`, `__close-trigger` | `__backdrop--opaque`, `__backdrop--blur`, `__backdrop--transparent` |
| Table | `.table-root` | `__scroll-container`, `__content`, `__header`, `__column`, `__body`, `__row`, `__cell`, `__footer` | `--primary`, `--secondary` |
| Select | `.select` | `__trigger`, `__value`, `__indicator`, `__popover` | `--primary`, `--secondary` |
| Card | `.card` | `__header`, `__body`, `__footer`, `__title` | — |
| Accordion | `.accordion` | `__item`, `__trigger`, `__panel` | — |
| Alert | `.alert` | `__icon`, `__content`, `__title`, `__description`, `__close` | — |

## Data Attributes for Interactive States

| State | Data Attribute | CSS Pseudo |
|-------|---------------|------------|
| Hovered | `[data-hovered="true"]` | `:hover` |
| Pressed | `[data-pressed="true"]` | `:active` |
| Focused | `[data-focus-visible="true"]` | `:focus-visible` |
| Disabled | `[aria-disabled="true"]` | `:disabled` |
| Selected | `[data-selected="true"]` | — |
| Open | `[data-open="true"]` | — |
| Entering | `[data-entering]` | — |
| Exiting | `[data-exiting]` | — |
| Invalid | `[data-invalid="true"]` | — |
| Pending | `[data-pending]` | — |
| Placeholder | `[data-placeholder="true"]` | — |
| Allows Sorting | `[data-allows-sorting="true"]` | — |
| Dragging | `[data-dragging="true"]` | — |
| Drop Target | `[data-drop-target="true"]` | — |

### Targeting States in CSS

```css
.button[data-hovered="true"] {
  transform: translateY(-1px);
}

.table__row[data-selected="true"] {
  background-color: var(--accent);
}
```

### Targeting States with Tailwind

```tsx
<Button className="data-[hovered=true]:scale-105 data-[pressed=true]:scale-95">
  Interactive
</Button>
```

### Color Format

OKLCH is the recommended format for color variables:

```css
--accent: oklch(0.7 0.25 260);
```

### Theme Builder

Visual tool at https://www.heroui.com/themes for customizing colors, radius, fonts.
