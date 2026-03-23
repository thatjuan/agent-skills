# React (Web) Setup

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [CSS Configuration](#css-configuration)
- [Selective Imports](#selective-imports)
- [Framework Integration](#framework-integration)

## Requirements

- React 19+
- Tailwind CSS v4

## Installation

```bash
# npm
npm i @heroui/styles @heroui/react

# pnpm
pnpm add @heroui/styles @heroui/react

# yarn
yarn add @heroui/styles @heroui/react

# bun
bun add @heroui/styles @heroui/react
```

## CSS Configuration

Add to `globals.css` (import order matters):

```css
@import "tailwindcss";
@import "@heroui/styles";
```

### Selective Import with Layer Control

```css
@layer theme, base, components, utilities;

@import "tailwindcss";
@import "@heroui/styles/base" layer(base);
@import "@heroui/styles/themes/default" layer(theme);
@import "@heroui/styles/components" layer(components);
```

### Component-Specific Imports

```css
@import "@heroui/styles/components/button.css" layer(components);
@import "@heroui/styles/components/accordion.css" layer(components);
```

### Headless Mode (Custom Styles Only)

```css
@import "tailwindcss";
@import "@heroui/styles/base/base.css";

.button {
  /* custom button styles */
}
```

## Selective Imports

Components are importable from the main package:

```tsx
import { Button, Modal, Table } from "@heroui/react";
```

Variant functions are available from either package:

```tsx
import { buttonVariants } from "@heroui/styles";
// or
import { buttonVariants } from "@heroui/react";
```

Use `@heroui/styles` to avoid React dependencies (for Vue, Svelte, etc.).

## Framework Integration

### Next.js

```tsx
import Link from "next/link";
import { buttonVariants } from "@heroui/styles";

<Link className={buttonVariants({ variant: "primary" })} href="/dashboard">
  Dashboard
</Link>
```

### React Router

```tsx
import { Link } from "react-router-dom";
import { buttonVariants } from "@heroui/styles";

<Link className={buttonVariants({ variant: "primary" })} to="/dashboard">
  Dashboard
</Link>
```

### Vue / Svelte / Other Frameworks

```ts
import { buttonVariants } from "@heroui/styles";

const primaryButton = buttonVariants({ variant: "primary" });
// Apply in template
```

### HTML Setup

```html
<html class="light" data-theme="light">
  <body class="bg-background text-foreground">
    <!-- App content -->
  </body>
</html>
```
