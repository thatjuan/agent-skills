# React Native Setup

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [CSS Configuration](#css-configuration)
- [Provider Setup](#provider-setup)
- [Granular Imports](#granular-imports)
- [Optional Dependencies](#optional-dependencies)
- [Platform Support](#platform-support)

## Requirements

- React Native
- Uniwind (Tailwind CSS for React Native)
- Mandatory peer dependencies (see Installation)

## Installation

### Step 1: Install HeroUI Native

```bash
npm install heroui-native
```

### Step 2: Install Mandatory Peer Dependencies

```bash
npm install react-native-reanimated@^4.1.1 react-native-gesture-handler@^2.28.0 react-native-worklets@^0.5.1 react-native-safe-area-context@^5.6.0 react-native-svg@^15.12.1 tailwind-variants@^3.2.2 tailwind-merge@^3.4.0
```

### Step 3: Set Up Uniwind

Follow the [Uniwind installation docs](https://uniwind.dev) for Tailwind CSS React Native integration.

### Step 4: Configure global.css

```css
@import "tailwindcss";
@import "uniwind";
@import "heroui-native/styles";
@source "./node_modules/heroui-native/lib";
```

## Provider Setup

Wrap the app with `HeroUINativeProvider` and `GestureHandlerRootView`:

```tsx
import { HeroUINativeProvider } from "heroui-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <HeroUINativeProvider>
        {/* App content */}
      </HeroUINativeProvider>
    </GestureHandlerRootView>
  );
}
```

## Granular Imports

Granular imports reduce bundle size:

```tsx
import { HeroUINativeProvider } from "heroui-native/provider";
import { Button } from "heroui-native/button";
import { Card } from "heroui-native/card";
```

General imports also work:

```tsx
import { Button, Card } from "heroui-native";
```

Available granular export paths: `provider`, `provider-raw`, individual component names, `portal`, `toast`, `utils`, `hooks`.

## Optional Dependencies

| Package | Version | Required For |
|---------|---------|--------------|
| `react-native-screens` | ^4.16.0 | BottomSheet, Dialog, Menu, Popover, Select, Toast |
| `@gorhom/bottom-sheet` | ^5.2.8 | BottomSheet, Menu/Popover/Select with bottom-sheet presentation |

## Platform Support

HeroUI Native targets **iOS and Android only**. For web development, use `@heroui/react` instead.
