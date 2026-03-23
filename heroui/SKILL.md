---
name: heroui
description: HeroUI v3 component library expertise for React (web) and React Native (mobile). Use when code imports @heroui/react, @heroui/styles, or heroui-native, user asks to build UI with HeroUI, or references HeroUI components, theming, or migration from NextUI/HeroUI v2.
---

# HeroUI v3

An open-source UI component library for React (web) and React Native (mobile). Built on Tailwind CSS v4 and React Aria Components. Provides 75+ accessible, customizable web components and 40+ native components.

## Technology Stack

| Platform | Package | Requires |
|----------|---------|----------|
| React (Web) | `@heroui/react`, `@heroui/styles` | React 19+, Tailwind CSS v4 |
| React Native | `heroui-native` | React Native, Uniwind, react-native-reanimated 4.1+, react-native-gesture-handler 2.28+ |

## Quick Setup

### React (Web)

```bash
npm i @heroui/react @heroui/styles
```

```css
/* globals.css — order matters */
@import "tailwindcss";
@import "@heroui/styles";
```

```tsx
import { Button } from "@heroui/react";

function App() {
  return <Button>Click me</Button>;
}
```

### React Native

```bash
npm install heroui-native react-native-reanimated@^4.1.1 react-native-gesture-handler@^2.28.0 react-native-worklets@^0.5.1 react-native-safe-area-context@^5.6.0 react-native-svg@^15.12.1 tailwind-variants@^3.2.2 tailwind-merge@^3.4.0
```

```css
/* global.css */
@import "tailwindcss";
@import "uniwind";
@import "heroui-native/styles";
@source "./node_modules/heroui-native/lib";
```

```tsx
import { HeroUINativeProvider } from "heroui-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { Button } from "heroui-native";

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <HeroUINativeProvider>
        <Button onPress={() => console.log("Pressed!")}>Get Started</Button>
      </HeroUINativeProvider>
    </GestureHandlerRootView>
  );
}
```

For detailed setup instructions, see [react-setup.md](references/react-setup.md) and [native-setup.md](references/native-setup.md).

## Component Architecture

HeroUI v3 uses **compound component composition** with dot notation:

```tsx
<Modal>
  <Button>Open</Button>
  <Modal.Backdrop>
    <Modal.Container>
      <Modal.Dialog>
        <Modal.Header>
          <Modal.Heading>Title</Modal.Heading>
        </Modal.Header>
        <Modal.Body>Content</Modal.Body>
        <Modal.Footer>
          <Button slot="close">Close</Button>
        </Modal.Footer>
      </Modal.Dialog>
    </Modal.Container>
  </Modal.Backdrop>
</Modal>
```

### Three Import Patterns

```tsx
// 1. Compound (recommended)
<Alert>
  <Alert.Icon />
  <Alert.Content>
    <Alert.Title>Success</Alert.Title>
  </Alert.Content>
</Alert>

// 2. With .Root suffix
<Alert.Root>
  <Alert.Icon />
</Alert.Root>

// 3. Named exports
import { AlertRoot, AlertIcon, AlertContent, AlertTitle } from "@heroui/react";
```

### Type Imports

```tsx
import type { ButtonRootProps, AvatarRootProps } from "@heroui/react";
```

## React Web Components (75+)

| Category | Components |
|----------|------------|
| Buttons | Button, ButtonGroup, CloseButton, ToggleButton, ToggleButtonGroup |
| Collections | Dropdown, ListBox, TagGroup |
| Colors | ColorArea, ColorField, ColorPicker, ColorSlider, ColorSwatch, ColorSwatchPicker |
| Controls | Slider, Switch |
| Data Display | Badge, Chip, Table |
| Date & Time | Calendar, DateField, DatePicker, DateRangePicker, RangeCalendar, TimeField |
| Feedback | Alert, Meter, ProgressBar, ProgressCircle, Skeleton, Spinner, Toast |
| Forms | Checkbox, CheckboxGroup, Description, ErrorMessage, FieldError, Fieldset, Form, Input, InputGroup, InputOTP, Label, NumberField, RadioGroup, SearchField, TextField, TextArea |
| Layout | Card, Separator, Surface, Toolbar |
| Media | Avatar |
| Navigation | Accordion, Breadcrumbs, Disclosure, DisclosureGroup, Link, Pagination, Tabs |
| Overlays | AlertDialog, Drawer, Modal, Popover, Tooltip |
| Pickers | Autocomplete, ComboBox, Select |
| Typography | Kbd |
| Utilities | ScrollShadow |

For component anatomy, props, and usage patterns, see [react-components.md](references/react-components.md).

## React Native Components (40+)

| Category | Components |
|----------|------------|
| Buttons | Button, CloseButton, LinkButton |
| Collections | Menu, TagGroup |
| Controls | Slider, Switch, Checkbox |
| Data Display | Chip, Avatar |
| Feedback | Alert, Spinner, Skeleton, SkeletonGroup, Toast |
| Forms | ControlField, Description, FieldError, Input, InputGroup, InputOTP, Label, RadioGroup, SearchField, Select, TextArea, TextField |
| Layout | Card, Separator, Surface, Accordion, ListGroup, Tabs |
| Overlays | BottomSheet, Dialog, Popover |
| Utilities | PressableFeedback, ScrollShadow |

For native component details, see [native-components.md](references/native-components.md).

## Styling System

HeroUI v3 provides three styling approaches:

### 1. BEM Classes

```tsx
<button className="button button--primary button--lg">Click</button>
```

Class pattern: `.{block}`, `.{block}__{element}`, `.{block}--{modifier}`

### 2. Variant Functions (Type-Safe)

```tsx
import { buttonVariants } from "@heroui/styles";

<a className={buttonVariants({ variant: "primary", size: "lg" })} href="/about">
  About
</a>
```

Variant functions are framework-agnostic — usable with Vue, Svelte, vanilla HTML.

### 3. Tailwind CSS Classes + className Prop

```tsx
<Button className="rounded-full shadow-lg">Styled</Button>
```

### Custom Variants

```tsx
import { buttonVariants, tv } from "@heroui/styles";

const myButton = tv({
  extend: buttonVariants,
  base: "font-semibold shadow-md",
  variants: {
    radius: { lg: "rounded-lg", md: "rounded-md" },
  },
});
```

### render Prop for Custom Elements

```tsx
<Button
  render={(domProps, { isPressed }) => (
    <motion.button {...domProps} animate={{ scale: isPressed ? 0.9 : 1 }} />
  )}
>
  Animated
</Button>
```

For theming, CSS variables, dark mode, custom themes, and component-level overrides, see [theming-and-styling.md](references/theming-and-styling.md).

## Common Prop Patterns

### Interactive States (Data Attributes)

| State | Attribute | CSS Pseudo |
|-------|-----------|------------|
| Hover | `[data-hovered="true"]` | `:hover` |
| Pressed | `[data-pressed="true"]` | `:active` |
| Focus | `[data-focus-visible="true"]` | `:focus-visible` |
| Disabled | `[aria-disabled="true"]` | `:disabled` |
| Selected | `[data-selected="true"]` | — |
| Open | `[data-open="true"]` | — |
| Entering | `[data-entering]` | — |
| Exiting | `[data-exiting]` | — |

### Event Handlers

HeroUI uses React Aria's press events, not native click events:

```tsx
<Button onPress={(e) => console.log("pressed")} />
```

### Overlay State Management

```tsx
import { useOverlayState } from "@heroui/react";

const state = useOverlayState({ defaultOpen: false });
// state.isOpen, state.open(), state.close(), state.toggle(), state.setOpen()
```

## Form Validation

```tsx
import { Form, TextField, Button } from "@heroui/react";

<Form validationBehavior="aria" onSubmit={handleSubmit}>
  <TextField name="email" isRequired>
    <Label>Email</Label>
    <Input />
    <FieldError />
  </TextField>
  <Button type="submit">Submit</Button>
</Form>
```

Two validation modes: `"native"` (blocks submission) and `"aria"` (realtime errors).

## Documentation Resources

| Resource | URL |
|----------|-----|
| React Docs | https://www.heroui.com/docs/react/getting-started |
| Native Docs | https://www.heroui.com/docs/native/getting-started |
| All React Components | https://www.heroui.com/docs/react/components |
| All Native Components | https://www.heroui.com/docs/native/components |
| Theme Builder | https://www.heroui.com/themes |
| Migration (v2 to v3) | https://www.heroui.com/docs/react/migration |
