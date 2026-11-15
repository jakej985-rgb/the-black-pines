# Ranger Station Cabin Refinement — Forest Service / Lived-In / Abandoned

Status: **Direction locked; implementation plan authored; no production asset replacements authorized.**

## Locked art direction

- **Style:** Forest Service ranger station. Practical, institutional, rugged, maintained with limited resources.
- **Furnishing:** Lived-in and fully equipped. Furniture is functional, mismatched only where believable, and arranged for actual work/rest.
- **Condition:** Abandoned after a recent evacuation. Objects remain where the last ranger left them; deterioration is localized and time-consistent, not long-term ruin.
- **Mood:** Cold, damp Pacific Northwest exterior; restrained warm practical light inside; readable silhouettes under flashlight and moonlight.
- **Hardware:** Preserve the documented GTX 960 target. Props generally 300–2,500 triangles, 1K maps maximum; avoid unnecessary unique materials and draw calls.

## Baseline protection

Existing production assets remain immutable during refinement:
- `assets/models/cabin_ranger_station.glb`
- `assets/models/furniture_ranger_desk.glb`
- `assets/models/furniture_woodstove.glb`
- `assets/models/furniture_cot.glb`
- `assets/models/furniture_shelving.glb`
- `assets/models/generator_industrial.glb`
- `assets/models/firewood_cord_stack.glb`
- `scenes/interactables/ranger_station.tscn`
- `scripts/tools/build_cabin_interior.py`
- `scripts/tools/build_cabin_exterior_props.py`

All new outputs go under `working/cabin_refinement/` and are review-only. Never export to `assets/models/` from the refinement scripts. Never change the production scene references in these passes. Each pass records the source hashes, settings, generated assets, and QA result.

## Existing implementation observations

1. The Godot ranger-station scene already references the cabin, desk/chair, stove, cot, shelves, radio, and investigation props.
2. The interior builder is primitive-derived and uses flat material colors. It is a useful blockout source, not a final realism benchmark.
3. The exterior generator/firewood builder has more developed PBR concepts. Verify texture path existence, channel/color-space setup, UV scale, exported materials, dimensions, pivots, and in-engine appearance.
4. The Godot scene uses broad collision shapes for shell and furniture. Runtime checks must verify doorway/window boundaries, stove clearance, furniture footprints, clue reachability, and collision/visual agreement.
5. Repository preview PNGs were discoverable but could not be visually inspected through the source-fetch path during this audit. Capture fresh controlled baselines before edits.

## Pass sequence

### Pass 00 — Baseline inventory and measurement (read-only)
**Inputs:** production cabin GLB, current furniture GLBs, generator/firewood GLBs, ranger station scene, existing builders.

**Work:**
- Record SHA-256, file size, object/mesh/material/texture counts, dimensions, local bounds, and mesh triangle counts.
- Record scene transforms, collision dimensions, interactable locations, and all referenced resources.
- Produce fixed camera baseline captures: exterior front 3/4, porch, interior overview, desk, stove, cot, shelving, generator, wood rack.
- Record Godot version, Blender version, resolution, graphics preset, camera, and lighting state.

**Gate:** no source asset changed; missing dependencies are listed, not silently repaired.

### Pass 01 — Cabin shell, access, and architectural detailing
**Work:** inspect actual interior surfaces before modeling. Confirm floor, walls, ceiling, roof underside, door jamb/threshold, window reveals, glass, porch posts, stairs, roof flashing, chimney penetration, and weather sealing. Add modular trim, corner boards, baseboards, window/door casings, beam details, floorboard variation, and restrained water ingress only where supported by geometry.

**Modeling rules:** real thickness at visible edges; bevel/chamfer hard edges; avoid coplanar overlays and z-fighting; use shared trim materials; maintain consistent world scale and pivots.

**Gate:** interior has no hollow-shell views, missing backfaces, major light leaks, blocked routes, or collision mismatch. Do not proceed to production replacement based on Blender render alone.

### Pass 02 — Interior furnishing and lived-in equipment
Build independent review assets:
- Work/dining table and two practical chairs.
- Filing cabinet and wall-mounted map/notice board.
- Stove tool set, ash bucket, firewood basket.
- Coat hooks, ranger coat, wet boots.
- Mugs, kettle/cookware, food tins, first-aid tin, toolbox.
- Small personal effects and abandoned work-in-progress set dressing.

**Composition:** keep a clear route from entrance to desk, stove, cot, and shelves. Do not bury clues under clutter. The desk remains the primary investigation station; table is a secondary practical surface. Use believable object groupings, not evenly spaced prop rows.

**Condition:** dust and dampness in sheltered corners; boot mud near entrance; hand wear around handles; soot near stove; water staining below windows; recently abandoned food/paperwork. Avoid heavy cobwebs, collapsed furniture, or extensive rot (that would imply long abandonment).

**Gate:** human-scale dimensions, stable contact, no floating/intersecting objects, sensible reach/clearance, readable clues, and asset budgets.

### Pass 03 — Exterior utility yard
Refine as a coherent service zone:
- Existing generator: verify scale, service-panel access, intake/exhaust orientation, rain protection, anti-vibration mounts, anchoring, concrete contact, conduit/cable route, disconnect, labels, and weathering.
- Existing firewood rack: verify log count and believable stacking, rack bracing, split-heartwood variation, bark variation, tarp/cover drainage, ballast placement, and ground contact.
- Add splitting block, axe/wedges, small chip/bark scatter, utility crate, rain barrel, and maintenance bucket only if placement supports the layout.

**Gate:** generator exhaust is not aimed at doors/windows; service side is accessible; wood is protected from ground moisture; props do not block navigation or obscure sightlines.

### Pass 04 — Storytelling, materials, and weathering
- Create a single abandonment narrative: evacuation was recent and hurried, but the station was operational immediately beforehand.
- Add restrained paper clutter, map annotations, a mug, coat/boots, tools left mid-task, and a few supplies.
- PBR review: albedo, tangent-space OpenGL normal, roughness, AO; physically plausible metallic response; texture scale and texel density.
- Keep material variants shared and localized. No global texture-resolution increase.

**Gate:** all detail supports use, wear, weather, or narrative; no arbitrary clutter.

### Pass 05 — Godot integration and runtime QA
- Integrate only after human approval of review exports.
- Preserve current node paths, clue scripts, interaction layers, and scene references.
- Create fitted collision: static shell collision aligned to walkable/solid geometry; compound simple collision for furniture; no decorative micro-collision.
- Test door/window access, entrance route, clue reachability, stove/table/cot clearances, generator interaction/service access, and exterior traversal.
- Test daylight, moonlight, flashlight, fog, wet conditions, and local lantern lighting.
- Capture before/after fixed-angle screenshots and a short traversal recording.
- Measure frame time, draw calls, visible mesh count, texture memory, and import size on the GTX 960 target.

**Gate:** import/parse passes; no missing resources; no interaction regressions; no unacceptable performance regression; Art Director / owner visually approves.

## Reviewable output structure

```
working/cabin_refinement/
  baseline/
    inventory.json
    source_hashes.json
    captures/
  pass01_architecture/
    review.blend
    exports/
    qa.json
    notes.md
  pass02_interior/
    review.blend
    exports/
    qa.json
    notes.md
  pass03_exterior/
    review.blend
    exports/
    qa.json
    notes.md
  pass04_storytelling/
    review.blend
    exports/
    qa.json
    notes.md
  pass05_godot/
    captures/
    performance.json
    qa.md
```

## Acceptance checklist

- [ ] Baseline hashes recorded and production files unchanged.
- [ ] Every new asset has source blend, exported GLB, dimensions, triangle count, materials, and preview.
- [ ] No missing textures/resources or invalid normals.
- [ ] Pivots, transforms, scale, UVs, and collision are checked.
- [ ] No floating props, obvious intersections, clipping, or z-fighting.
- [ ] Player path and all current clues remain reachable.
- [ ] Abandonment reads as recent evacuation, not long-term ruin.
- [ ] Performance remains appropriate for GTX 960 target.
- [ ] Runtime evidence exists for all important views and lighting conditions.
- [ ] Owner approves visual direction before any production asset is replaced.

## Rollback

Because this workflow writes only under `working/cabin_refinement/`, rollback is deletion of that review directory or checkout of the review branch. Production assets and current scene references remain untouched until a separate approved integration change.
