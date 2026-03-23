# React Native Components Reference

## Table of Contents

- [Provider](#provider)
- [Buttons](#buttons)
- [Collections](#collections)
- [Controls](#controls)
- [Data Display](#data-display)
- [Feedback](#feedback)
- [Forms](#forms)
- [Layout](#layout)
- [Navigation](#navigation)
- [Overlays](#overlays)
- [Utilities](#utilities)
- [Common Patterns](#common-patterns)

All components import from `heroui-native` or granular paths like `heroui-native/button`.

## Provider

The app root requires `HeroUINativeProvider` wrapped in `GestureHandlerRootView`:

```tsx
import { HeroUINativeProvider } from "heroui-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";

<GestureHandlerRootView style={{ flex: 1 }}>
  <HeroUINativeProvider>
    {/* App */}
  </HeroUINativeProvider>
</GestureHandlerRootView>
```

## Buttons

### Button

Interactive pressable component.

```tsx
import { Button } from "heroui-native";

<Button onPress={() => console.log("pressed")}>Label</Button>
```

### CloseButton

Button for closing dialogs, modals, or dismissing content.

### LinkButton

Ghost-variant button with no highlight feedback for inline link-style interactions.

## Collections

### Menu

Floating context menu with positioning, selection groups, and multiple presentation modes.

### TagGroup

Compound component for displaying and managing selectable tags with optional removal.

## Controls

### Slider

Draggable input for selecting a value or range within a bounded interval. Supports `Slider.Output` composition.

### Switch

Toggle control for on/off states.

### Checkbox

Selectable control toggling between checked and unchecked.

## Data Display

### Chip

Compact capsule-shaped element.

### Avatar

User avatar with support for images, text initials, or fallback icons.

## Feedback

### Alert

Important messages with status indicators.

### Spinner

Animated loading indicator.

### Skeleton / SkeletonGroup

Loading placeholders with shimmer or pulse animation. `SkeletonGroup` coordinates multiple skeletons with centralized animation control.

### Toast

Temporary notifications at top or bottom of screen.

## Forms

### TextField

Text input with label, description, and error handling.

```tsx
import { TextField } from "heroui-native";

<TextField label="Name" placeholder="Enter name" />
```

### Input

Styled single-line text input with border and background.

### TextArea

Multiline text input with styled border and background.

### InputGroup

Groups input with optional prefix and suffix decorators.

### InputOTP

One-time password input with individual character slots, animations, and validation.

### SearchField

Compound search input for filtering and querying.

### Select

Option list triggered by a button. Supports single and multi-selection modes.

### NumberField

Not available in native — use Input with numeric keyboard.

### RadioGroup

Radio buttons where only one option can be selected.

### Checkbox

(See Controls section)

### ControlField

Combines label, description, and control (Switch or Checkbox) into a single pressable area.

### Label

Text component for labeling form fields with required indicators and validation states.

### Description

Text for providing accessible descriptions and helper text.

### FieldError

Validation error message with smooth animations.

## Layout

### Card

Card container with flexible layout sections.

```tsx
import { Card } from "heroui-native";

<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>Content</Card.Body>
</Card>
```

### Surface

Container providing elevation and background styling.

### Separator

Simple visual divider.

### Accordion

Collapsible content panels.

### ListGroup

Surface-based container grouping related list items with consistent layout.

### Tabs

Tabbed views with animated transitions and indicators.

## Overlays

### Dialog

Modal overlay with animated transitions and gesture-based dismissal.

### BottomSheet

Slides up from bottom with animated transitions and swipe-to-dismiss. Requires `react-native-screens` (optional `@gorhom/bottom-sheet`).

### Popover

Floating content panel anchored to a trigger element with placement options.

### Toast

Temporary notifications at top or bottom of screen.

## Utilities

### PressableFeedback

Container providing visual feedback for press interactions with automatic scale animation.

### ScrollShadow

Dynamic gradient shadows on scrollable content based on scroll position and overflow.

## Common Patterns

### Granular Imports

```tsx
import { Button } from "heroui-native/button";
import { Card } from "heroui-native/card";
```

### Tailwind Styling via Uniwind

```tsx
<View className="flex-1 justify-center items-center bg-background">
  <Button>Styled</Button>
</View>
```

### Full Component Docs

Each component has detailed documentation at:
`https://www.heroui.com/docs/native/components/{component-name}`
