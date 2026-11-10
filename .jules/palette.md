# Palette's UX & Accessibility Journal

## 2026-11-10 - Keyboard focus parity on procedural UI buttons
**Learning:** Procedurally generated UI buttons in Godot controls (such as item list entries or crafting recipe rows) frequently only connect to `mouse_entered` for details inspection. This completely breaks accessibility for keyboard navigation (Tab / UI focus directional keys), leaving keyboard-only players unable to view descriptions or inspect item stats. In addition, setting `tooltip_text` on dynamic buttons provides native desktop hover tooltips and screen-reader hints, including explanatory disabled states on buttons like "Craft".
**Action:** When dynamically instantiating UI `Button` instances that reveal details on hover, always connect both `mouse_entered` and `focus_entered` to the inspector callback and populate `tooltip_text` (including disabled context on action buttons).

## 2026-11-11 - Initial keyboard focus and mutual dialog switching in Godot UI
**Learning:** When Godot modal UI dialogs (such as Inventory or Journal) are opened via key actions, no child control node automatically receives focus by default, causing directional keyboard/gamepad navigation to fail until the user performs a mouse click. Furthermore, independent `_unhandled_input` handlers across dialogs cause them to open simultaneously on top of one another when switching keys (`Tab` and `J`) are pressed.
**Action:** Explicitly call `grab_focus()` on the first interactive item button upon opening a dialog to ensure immediate keyboard accessibility and auto-population of detail labels. Handle cross-dialog hotkeys by closing active dialogs and allowing unhandled events to propagate to sibling dialogs smoothly.
