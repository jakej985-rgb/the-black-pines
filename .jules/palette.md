# Palette's UX & Accessibility Journal

## 2026-11-10 - Keyboard focus parity on procedural UI buttons
**Learning:** Procedurally generated UI buttons in Godot controls (such as item list entries or crafting recipe rows) frequently only connect to `mouse_entered` for details inspection. This completely breaks accessibility for keyboard navigation (Tab / UI focus directional keys), leaving keyboard-only players unable to view descriptions or inspect item stats. In addition, setting `tooltip_text` on dynamic buttons provides native desktop hover tooltips and screen-reader hints, including explanatory disabled states on buttons like "Craft".
**Action:** When dynamically instantiating UI `Button` instances that reveal details on hover, always connect both `mouse_entered` and `focus_entered` to the inspector callback and populate `tooltip_text` (including disabled context on action buttons).

## 2026-11-11 - Initial keyboard focus and mutual dialog switching in Godot UI
**Learning:** When Godot modal UI dialogs (such as Inventory or Journal) are opened via key actions, no child control node automatically receives focus by default, causing directional keyboard/gamepad navigation to fail until the user performs a mouse click. Furthermore, independent `_unhandled_input` handlers across dialogs cause them to open simultaneously on top of one another when switching keys (`Tab` and `J`) are pressed.
**Action:** Explicitly call `grab_focus()` on the first interactive item button upon opening a dialog to ensure immediate keyboard accessibility and auto-population of detail labels. Handle cross-dialog hotkeys by closing active dialogs and allowing unhandled events to propagate to sibling dialogs smoothly.

## 2026-11-12 - Tab cycling shortcuts and category-aware focus retention in TabContainer dialogs
**Learning:** In Godot 4 `TabContainer` interfaces, keyboard navigation is disrupted when navigating between tabs because TabContainer does not provide default bumper/cycling keybinds (`Q`/`E`), and switching tabs leaves focus stranded on elements belonging to inactive tab pages or drops focus entirely. Connecting `tab_changed` to an active-tab focus handler guarantees keyboard and gamepad accessibility stays synchronized with the visible category.
**Action:** Provide `Q`/`E` tab cycling in modal dialog `_unhandled_input` handlers, connect `tab_container.tab_changed` to focus the first interactive item or active tab bar within the selected category, and update footer hints to explicitly guide players.

## 2026-11-13 - Dynamic reticle focus state and modal occlusion hiding in survival horror HUDs
**Learning:** In first-person games with sparse, minimalist HUDs, keeping the reticle static forces players to read peripheral prompt text to verify interactability. Providing micro-feedback directly on the crosshair (subtle expansion and warm chromatic tint when an interactable enters raycast focus) creates instant, non-verbal targeting confirmation. Furthermore, leaving the center crosshair rendered while modal dialogs (inspection sheets, inventory, journal) are active produces visual obstruction over readable text and breaks immersive diegesis.
**Action:** Bind interactable prompt state changes to reticle modulate/dimension properties, and hide the crosshair whenever full-screen or centered modal overlays are active.

## 2026-11-14 - Modal backdrop dimming and mutual exclusivity for inspection panels
**Learning:** Clue inspection popups that lack a full-screen backdrop dimming scrim suffer severe legibility problems in dynamic 3D environments, as varying background luminance (flashlight cones, fog, moonlight) reduces contrast against small text. In addition, without mutual modal exclusivity, inspecting a clue while the inventory or journal is open leads to colliding UI layers and conflicting dismiss hotkeys.
**Action:** Always place an atmospheric dimming scrim behind modal inspection dialogs, ensure opening an inspection closes active dialogs, and allow pressing dialog hotkeys (`Tab`/`J`) to dismiss the active inspection panel seamlessly.
