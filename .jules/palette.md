# Palette's UX & Accessibility Journal

## 2026-11-10 - Keyboard focus parity on procedural UI buttons
**Learning:** Procedurally generated UI buttons in Godot controls (such as item list entries or crafting recipe rows) frequently only connect to `mouse_entered` for details inspection. This completely breaks accessibility for keyboard navigation (Tab / UI focus directional keys), leaving keyboard-only players unable to view descriptions or inspect item stats. In addition, setting `tooltip_text` on dynamic buttons provides native desktop hover tooltips and screen-reader hints, including explanatory disabled states on buttons like "Craft".
**Action:** When dynamically instantiating UI `Button` instances that reveal details on hover, always connect both `mouse_entered` and `focus_entered` to the inspector callback and populate `tooltip_text` (including disabled context on action buttons).
