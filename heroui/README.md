# heroui

> HeroUI v3 component library expertise for React (web) and React Native (mobile). Covers 75+ web components and 40+ native components built on Tailwind CSS v4 and React Aria Components.

## What it does

`heroui` turns your agent into a HeroUI v3 specialist. It knows:

- **Setup for both platforms** — React web (`@heroui/react` + `@heroui/styles`) and React Native (`heroui-native` + Uniwind + Reanimated 4.1+)
- **The full component catalog** — 75+ web components and 40+ native components with their anatomy, props, and composition patterns
- **Theming and styling** — CSS variables, dark mode, custom themes, semantic colors, BEM classes, variant functions, data attributes
- **Compound component patterns** — how HeroUI composes (e.g., `<Modal>` + `<ModalHeader>` + `<ModalBody>` + `<ModalFooter>`)
- **Framework integration** — Next.js App Router, React Router, Vue, Svelte, Expo Router
- **Migration paths** — from NextUI or HeroUI v2

It triggers automatically when code imports `@heroui/react`, `@heroui/styles`, or `heroui-native`.

## When to use it

Invoke this skill when you hear:

- *"Build a dashboard page with HeroUI."*
- *"How do I theme HeroUI to match our brand colors?"*
- *"Compose a multi-step form with HeroUI inputs and a modal confirmation."*
- *"I'm on HeroUI v2 — how do I upgrade to v3?"*
- *"Set up HeroUI in my React Native + Expo app."*
- *"Why isn't dark mode switching in my HeroUI app?"*

## Example walkthrough

**Prompt**

> Set up HeroUI in my Next.js App Router app with a dark-mode toggle and our brand primary color (#0066FF).

**What the skill produces**

**1. Install**

```bash
npm i @heroui/react @heroui/styles
```

**2. `app/globals.css`** (order matters)

```css
@import "tailwindcss";
@import "@heroui/styles";

@theme {
  --color-primary: #0066ff;
  --color-primary-foreground: #ffffff;
}
```

**3. `app/providers.tsx`**

```tsx
"use client";
import { HeroUIProvider } from "@heroui/react";
import { ThemeProvider } from "next-themes";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <HeroUIProvider>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </HeroUIProvider>
  );
}
```

**4. `app/layout.tsx`**

```tsx
import { Providers } from "./providers";
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body><Providers>{children}</Providers></body>
    </html>
  );
}
```

**5. Theme toggle component**

```tsx
"use client";
import { Button } from "@heroui/react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return (
    <Button isIconOnly variant="flat" onPress={() => setTheme(theme === "dark" ? "light" : "dark")}>
      {theme === "dark" ? "☾" : "☀"}
    </Button>
  );
}
```

The skill also explains the **order-matters** pitfall (Tailwind import must come before HeroUI styles) and why `suppressHydrationWarning` is needed with `next-themes`.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill heroui
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Quick setup, component architecture, component index, styling system, common patterns |
| `references/react-setup.md` | React web installation, CSS configuration, selective imports, framework integration (Next.js, React Router, Vue, Svelte) |
| `references/native-setup.md` | React Native installation, peer dependencies, Uniwind setup, provider configuration, granular imports |
| `references/react-components.md` | Complete reference — anatomy, props, and usage for all 75+ web components |
| `references/native-components.md` | Complete reference for all 40+ native components |
| `references/theming-and-styling.md` | CSS variables, dark mode, custom themes, semantic colors, BEM classes, variant functions, data attributes |

## Tips

- **Watch the CSS import order.** `@import "tailwindcss"` must come before `@import "@heroui/styles"`. Reversed order silently breaks theming.
- **Use compound components as designed.** HeroUI's `<Modal>` expects `<ModalContent>` + `<ModalHeader>` etc. — don't try to flatten them, accessibility hooks depend on the composition.
- **Theme via CSS variables, not prop overrides.** Changing `--color-primary` in your theme block cascades to every component. Overriding per-component is a smell.
- **React Native setup is heavier.** The native package needs several peer deps at specific versions (Reanimated 4.1+, Gesture Handler 2.28+). Follow the skill's install list exactly — mismatched versions are the #1 setup failure.

## Related skills

- [`stitch-design`](https://github.com/thatjuan/agent-skills) — for high-fidelity screen generation before component implementation
- [`react-components`](https://github.com/thatjuan/agent-skills) — for converting Stitch designs into modular React components
