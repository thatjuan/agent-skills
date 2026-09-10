# React Web Components Reference

## Table of Contents

- [Buttons](#buttons)
- [Collections](#collections)
- [Colors](#colors)
- [Controls](#controls)
- [Data Display](#data-display)
- [Date and Time](#date-and-time)
- [Feedback](#feedback)
- [Forms](#forms)
- [Layout](#layout)
- [Media](#media)
- [Navigation](#navigation)
- [Overlays](#overlays)
- [Pickers](#pickers)
- [Typography](#typography)
- [Utilities](#utilities)
- [Common Patterns](#common-patterns)

All components import from `@heroui/react`. All support `className` and standard HTML attributes.

## Buttons

### Button

Clickable element with multiple variants and states.

```tsx
<Button variant="primary" size="md" onPress={handlePress}>
  Label
</Button>
```

| Prop | Type | Default |
|------|------|---------|
| `variant` | `"primary" \| "secondary" \| "tertiary" \| "outline" \| "ghost" \| "danger"` | `"primary"` |
| `size` | `"sm" \| "md" \| "lg"` | `"md"` |
| `fullWidth` | `boolean` | `false` |
| `isDisabled` | `boolean` | `false` |
| `isPending` | `boolean` | `false` |
| `isIconOnly` | `boolean` | `false` |
| `onPress` | `(e: PressEvent) => void` | — |
| `render` | `DOMRenderFunction` | — |

CSS: `.button`, `.button--primary`, `.button--sm`, `.button--icon-only`

### ButtonGroup

Groups related buttons with consistent styling and spacing.

```tsx
<ButtonGroup>
  <Button>One</Button>
  <Button>Two</Button>
</ButtonGroup>
```

### CloseButton

Specialized button for closing dialogs, modals, or dismissing content.

### ToggleButton

Interactive toggle control for on/off or selected/unselected states.

### ToggleButtonGroup

Groups multiple ToggleButtons; supports single or multiple selection.

## Collections

### Dropdown

Displays a list of actions or options.

```tsx
<Dropdown>
  <Button>Actions</Button>
  <Dropdown.Popover>
    <Dropdown.Menu>
      <Dropdown.Item id="edit">Edit</Dropdown.Item>
      <Dropdown.Item id="delete">Delete</Dropdown.Item>
    </Dropdown.Menu>
  </Dropdown.Popover>
</Dropdown>
```

### ListBox

Displays a list of selectable options.

```tsx
<ListBox selectionMode="single" aria-label="Options">
  <ListBox.Item id="1">Option 1</ListBox.Item>
  <ListBox.Item id="2">Option 2</ListBox.Item>
  <ListBox.Section>
    <ListBox.Header>Group</ListBox.Header>
    <ListBox.Item id="3">Option 3</ListBox.Item>
  </ListBox.Section>
</ListBox>
```

### TagGroup

Focusable list of tags with keyboard navigation, selection, and removal.

## Colors

### ColorPicker

Composable picker synchronizing color value between multiple color components.

### ColorArea

2D gradient area for selecting colors.

### ColorSlider

Slider for adjusting an individual color channel.

### ColorField

Input field for color values with labels, descriptions, and validation.

### ColorSwatch

Visual preview of a color value with accessibility support.

### ColorSwatchPicker

List of color swatches for selecting from a predefined palette.

## Controls

### Slider

Select one or more values within a range.

### Switch

Toggle between boolean states.

```tsx
<Switch>Dark mode</Switch>
```

| Prop | Type |
|------|------|
| `isSelected` | `boolean` |
| `onChange` | `(isSelected: boolean) => void` |
| `isDisabled` | `boolean` |

## Data Display

### Badge

Small indicator for notification counts, status dots, labels. Positioned relative to another element.

### Chip

Small informational badges for labels, statuses, categories.

### Table

Structured data in rows and columns with sorting, selection, column resizing, infinite scrolling, and virtualization.

```tsx
<Table>
  <Table.ScrollContainer>
    <Table.Content aria-label="Users" selectionMode="multiple">
      <Table.Header>
        <Table.Column id="name" isRowHeader>Name</Table.Column>
        <Table.Column id="role">Role</Table.Column>
      </Table.Header>
      <Table.Body>
        <Table.Row id="1">
          <Table.Cell>Alice</Table.Cell>
          <Table.Cell>Admin</Table.Cell>
        </Table.Row>
      </Table.Body>
    </Table.Content>
  </Table.ScrollContainer>
  <Table.Footer>
    <Pagination total={10} />
  </Table.Footer>
</Table>
```

Sub-components: `Table`, `Table.ScrollContainer`, `Table.Content`, `Table.Header`, `Table.Column`, `Table.Body`, `Table.Row`, `Table.Cell`, `Table.Footer`, `Table.ColumnResizer`, `Table.ResizableContainer`, `Table.LoadMore`, `Table.LoadMoreContent`, `Table.Collection`.

| Table.Content Prop | Type |
|--------------------|------|
| `selectionMode` | `"none" \| "single" \| "multiple"` |
| `sortDescriptor` | `SortDescriptor` |
| `onSortChange` | `(descriptor: SortDescriptor) => void` |
| `selectedKeys` | `Selection` |
| `onSelectionChange` | `(keys: Selection) => void` |

| Table.Column Prop | Type |
|-------------------|------|
| `allowsSorting` | `boolean` |
| `isRowHeader` | `boolean` |
| `defaultWidth` | `string \| number` |

| Table Prop | Type | Default |
|------------|------|---------|
| `variant` | `"primary" \| "secondary"` | `"primary"` |

CSS: `.table-root`, `.table__scroll-container`, `.table__content`, `.table__header`, `.table__column`, `.table__body`, `.table__row`, `.table__cell`, `.table__footer`

## Date and Time

### Calendar

Composable date picker with month grid, navigation, and year picker. Built on React Aria Calendar.

### RangeCalendar

Date range picker with month grid. Built on React Aria RangeCalendar.

### DateField

Date input field with labels, descriptions, and validation. Built on React Aria DateField.

### DatePicker

Composable date picker combining DateField and Calendar.

### DateRangePicker

Composable date range picker combining DateField and RangeCalendar.

### TimeField

Time input with labels, descriptions, and validation. Built on React Aria TimeField.

## Feedback

### Alert

Important messages and notifications with status indicators.

```tsx
<Alert>
  <Alert.Icon />
  <Alert.Content>
    <Alert.Title>Success</Alert.Title>
    <Alert.Description>Changes saved.</Alert.Description>
  </Alert.Content>
  <Alert.Close />
</Alert>
```

### Meter

Quantity within a known range or fractional value.

### ProgressBar

Determinate or indeterminate linear progress.

### ProgressCircle

Circular progress indicator.

### Skeleton

Loading placeholder showing expected shape of a component.

### Spinner

Animated loading indicator.

### Toast

Temporary notifications with automatic dismissal and customizable placement.

```tsx
import { ToastQueue } from "@heroui/react";

ToastQueue.add({ title: "Saved", description: "Changes saved." });
```

## Forms

### Form

Wrapper for form validation and submission.

```tsx
<Form validationBehavior="aria" onSubmit={handleSubmit}>
  <TextField name="email" isRequired>
    <Label>Email</Label>
    <Input />
    <FieldError />
  </TextField>
  <Button type="submit">Submit</Button>
</Form>
```

| Prop | Type | Default |
|------|------|---------|
| `validationBehavior` | `"native" \| "aria"` | `"native"` |
| `validationErrors` | `ValidationErrors` | — |
| `onSubmit` | `FormEventHandler` | — |
| `onInvalid` | `FormEventHandler` | — |

### TextField

Composition-friendly text field with label, description, and validation.

```tsx
<TextField name="name" isRequired>
  <Label>Name</Label>
  <Input />
  <Description>Enter your full name</Description>
  <FieldError />
</TextField>
```

### Input

Primitive single-line text input. Accepts standard HTML input attributes.

### TextArea

Primitive multiline text input.

### InputGroup

Groups input with prefix and suffix elements.

```tsx
<InputGroup>
  <InputGroup.Prefix>$</InputGroup.Prefix>
  <Input />
  <InputGroup.Suffix>.00</InputGroup.Suffix>
</InputGroup>
```

### InputOTP

One-time password input for verification codes.

### NumberField

Number input with increment/decrement buttons, validation, and internationalized formatting.

### SearchField

Search input with clear button and search icon.

### Checkbox / CheckboxGroup

```tsx
<CheckboxGroup>
  <Label>Options</Label>
  <Checkbox value="a">Option A</Checkbox>
  <Checkbox value="b">Option B</Checkbox>
</CheckboxGroup>
```

### RadioGroup

```tsx
<RadioGroup name="color">
  <Label>Color</Label>
  <RadioGroup.Radio value="red">Red</RadioGroup.Radio>
  <RadioGroup.Radio value="blue">Blue</RadioGroup.Radio>
</RadioGroup>
```

### Fieldset

Groups related form controls with legends, descriptions, and actions.

### Label

Accessible label associated with form controls.

### Description

Supplementary text for form fields.

### ErrorMessage / FieldError

Display validation error messages.

## Layout

### Card

Flexible container for grouping related content.

```tsx
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer>Footer</Card.Footer>
</Card>
```

### Surface

Container providing surface-level styling and context.

### Separator

Visual divider between content sections.

### Toolbar

Container for interactive controls with arrow key navigation.

## Media

### Avatar

User profile images with customizable fallback content.

```tsx
<Avatar src="/photo.jpg" alt="User" />
```

## Navigation

### Tabs

Organize content into multiple sections.

```tsx
<Tabs>
  <Tabs.List>
    <Tabs.Tab id="1">Tab 1</Tabs.Tab>
    <Tabs.Tab id="2">Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="1">Content 1</Tabs.Panel>
  <Tabs.Panel id="2">Content 2</Tabs.Panel>
</Tabs>
```

### Accordion

Collapsible content panels.

```tsx
<Accordion>
  <Accordion.Item id="1">
    <Accordion.Trigger>Section 1</Accordion.Trigger>
    <Accordion.Panel>Content 1</Accordion.Panel>
  </Accordion.Item>
</Accordion>
```

### Breadcrumbs

Navigation breadcrumbs showing location within a hierarchy.

### Disclosure / DisclosureGroup

Collapsible sections with header and content.

### Link

Styled anchor with built-in icon support.

### Pagination

Page navigation with composable page links, previous/next buttons, and ellipsis.

## Overlays

### Modal

Dialog overlay for focused interactions.

```tsx
<Modal>
  <Button>Open Modal</Button>
  <Modal.Backdrop>
    <Modal.Container size="md" placement="center">
      <Modal.Dialog>
        <Modal.CloseTrigger />
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

| Sub-component | Key Props |
|---------------|-----------|
| `Modal.Backdrop` | `variant: "opaque" \| "blur" \| "transparent"`, `isDismissable`, `isOpen`, `onOpenChange` |
| `Modal.Container` | `size: "xs" \| "sm" \| "md" \| "lg" \| "cover" \| "full"`, `placement: "auto" \| "center" \| "top" \| "bottom"`, `scroll: "inside" \| "outside"` |

### AlertDialog

Modal dialog for critical confirmations requiring explicit user action.

### Drawer

Slide-out panel for supplementary content.

### Popover

Rich content in a portal triggered by a button or custom element.

### Tooltip

Informative text on hover or focus.

```tsx
<Tooltip>
  <Button>Hover me</Button>
  <Tooltip.Content>Tooltip text</Tooltip.Content>
</Tooltip>
```

## Pickers

### Select

Collapsible option list for single or multiple selection.

```tsx
<Select>
  <Label>Country</Label>
  <Select.Trigger>
    <Select.Value placeholder="Pick a country" />
    <Select.Indicator />
  </Select.Trigger>
  <Select.Popover>
    <ListBox>
      <ListBox.Item id="us">United States</ListBox.Item>
      <ListBox.Item id="uk">United Kingdom</ListBox.Item>
    </ListBox>
  </Select.Popover>
  <Description>Select your country</Description>
</Select>
```

| Prop | Type | Default |
|------|------|---------|
| `selectionMode` | `"single" \| "multiple"` | `"single"` |
| `variant` | `"primary" \| "secondary"` | `"primary"` |
| `isDisabled` | `boolean` | — |
| `isRequired` | `boolean` | — |
| `isInvalid` | `boolean` | — |
| `fullWidth` | `boolean` | `false` |

### ComboBox

Text input combined with a listbox for filtering options.

### Autocomplete

Select with filtering, searching, and selecting from a list.

## Typography

### Kbd

Display keyboard shortcuts and key combinations.

```tsx
<Kbd>Ctrl+S</Kbd>
```

## Utilities

### ScrollShadow

Visual shadows indicating scrollable content overflow.

## Common Patterns

### Dynamic Collections

```tsx
<Table.Body items={users}>
  {(user) => (
    <Table.Row id={user.id}>
      <Table.Cell>{user.name}</Table.Cell>
    </Table.Row>
  )}
</Table.Body>
```

### Controlled State

```tsx
const [value, setValue] = useState<Key | null>(null);

<Select value={value} onChange={setValue}>
  {/* ... */}
</Select>
```

### Overlay State Hook

```tsx
const state = useOverlayState({ defaultOpen: false });
// state.isOpen, state.open(), state.close(), state.toggle()
```

### Slot-Based Closing

```tsx
<Button slot="close">Close</Button>
```

Any button with `slot="close"` inside an overlay automatically closes it.

### Full Component Docs

Each component has detailed documentation at:
`https://www.heroui.com/docs/react/components/{component-name}`
