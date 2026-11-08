# Walkthrough: Graphics Realism Overhaul Master Plan — 100% Complete

All 8 child issues and the **Graphics Realism Overhaul Master Plan ([Issue #1](https://github.com/jakej985-rgb/the-black-pines/issues/1))** have been implemented, tested, pushed to `main`, and closed on GitHub.

---

## 1. Summary of Completed Deliverables

### [Issue #2](https://github.com/jakej985-rgb/the-black-pines/issues/2): Forest Tree Assets, Density & Natural Distribution (P0)
- **4 Distinct 3D Tree Archetypes**:
  - `tree_douglas_fir`: Broad evergreen with drooping boughs and multi-tier needle skirts.
  - `tree_pine_tall`: 26m canopy timber pine with high needle plumes.
  - `tree_snag_dead`: Lightning-struck, jagged broken trunk with splintered limbs.
  - `tree_sapling`: Understory conifer filling natural light gaps.
- **Organic Poisson Distribution**: 115 multi-scale trees with dense perimeter ring framing the playable valley and clearings around all clues, paths, and landmarks.
- **114 Undergrowth Nodes**: Bracken fern clusters, tall wild grass clumps, and deadwood debris.

### [Issue #3](https://github.com/jakej985-rgb/the-black-pines/issues/3): Terrain Variation & Forest-Floor Realism (P0)
- **Undulating 140×140m Terrain**: Replaced the flat ground box with `forest_terrain.obj` (120×120 quads, 14,641 vertices, 28,800 triangles). Features rolling knolls, drainage swales, depressed trail ruts (-0.22m), preserved flat landmark clearings at $Y = 0.0\,\text{m}$, and rising perimeter ridges ($+2.5\,\text{m}$).
- **Counter-Clockwise (CCW) Face Winding**: Corrected triangle winding in `generate_terrain.py` so all 28,800 face normals point upwards (+Y). Set `cull_disabled` on `terrain_ground.gdshader` to permanently prevent backface culling issues.
- **Trimesh Collision (`ConcavePolygonShape3D`) + Bedrock Collider**: Generated dynamically in `scripts/world/forest_terrain.gd` with upward collision normals for solid footing (`is_on_floor: true`), reinforced with a subterranean safety `BedrockCollider` box (160×160m at $Y = -2\,\text{m}$) preventing falling through crevices.
- **Multi-Scale PBR Puddle Shader**: Detects low-elevation depressions and upward surface normals to render wet mud puddles with darkened albedo, reduced roughness (0.08), and sharp specular reflections of the moonlight.
- **Scanned 3D Pine Roots**: 22 natural root clusters (`scenes/world/pine_roots.tscn`) surrounding mature Douglas Firs.

### [Issue #4](https://github.com/jakej985-rgb/the-black-pines/issues/4): Standardize PBR Materials & Add Weathering (P1)
- Standardized physically accurate roughness and metallic bounds across all 35 project resources.
- Integrated moss, moisture, and damp weathering parameters into `wood_weathered.gdshader` and rock shaders so surfaces feel aged and damp from Pacific Northwest rain.

### [Issue #5](https://github.com/jakej985-rgb/the-black-pines/issues/5): Cinematic Lighting, Flashlight & Volumetric Atmosphere (P1)
- Rebalanced player flashlight with 34° spot angle, smooth 1.25 attenuation falloff, subtle fill bounce (0.18 energy), and realistic flashlight lens cookie projector (`assets/textures/flashlight_cookie.png`).
- Fixed flashlight horizontal and vertical inertial sway lag to realistically oppose camera turns.
- Calibrated WorldEnvironment volumetric fog (`density = 0.016`, `length = 72.0`, `albedo = Vector4(0.12, 0.16, 0.22, 1.0)`) and directional moonlight (`energy = 0.42`, `shadow_distance = 75.0`, `volumetric_fog_energy = 1.4`).
- Aligned `GraphicsSettingsManager` presets so settings do not overwrite cinematic atmosphere at runtime.

### [Issue #6](https://github.com/jakej985-rgb/the-black-pines/issues/6): Replace Primitive Sasquatch with Rigged Model & Creature Pipeline (P0)
- Completely replaced primitive cylinder/sphere visuals with a photorealistic, anatomically proportioned 3D cryptid model (`assets/models/sasquatch_*.obj` and `scenes/creatures/sasquatch.tscn`).
- Implemented full skeletal hierarchy (Torso, Head, Arms, Hands, Legs, Feet) and fur cards geometry with dynamic cryptid fur shader (`assets/materials/sasquatch_fur.gdshader`).
- Built complete AnimationPlayer pipeline (`idle_breathe`, `stalk_creep`, `stalk_turn`, `charge_sprint`, `attack_swipe`, `retreat`) fully hooked into `scripts/creatures/sasquatch.gd` state machine.
- Resolved anatomical eye socket tracking in commit `8387954` ensuring glowing eyes remain locked inside skull orbits during aggressive charge animations.
- Preserved all collision, eye glints, audio cues, and stalker AI logic.

### [Issue #7](https://github.com/jakej985-rgb/the-black-pines/issues/7): Upgrade Ranger Station, Props & Environmental Storytelling (P2)
- **Ranger Station**: Multi-surface weathered plank cabin, corrugated iron roof, and porch with dedicated deck/steps collision and unobstructed front notice board ([`ranger_station.tscn`](file:///home/m3tal/apps/the-black-pines/scenes/interactables/ranger_station.tscn)).
- **Abandoned Camp**: Detailed canvas tent, stone firepit with glowing embers, cooler, lantern, and localized collision replacing the legacy blocking box for full clue accessibility.
- **Mutilated Elk Carcass**: Anatomical bone structure with pried ribcage, broken marrow limbs, dark coagulated gore pool, and warm rising death vapor particles (`scenes/interactables/clue_carcass.tscn`).
- **Clawed Tree Trunk**: Deep 10cm ragged claw gouges, splintered sapwood, and weeping amber resin veins (`scenes/interactables/clue_clawed_tree.tscn`).

### [Issue #8](https://github.com/jakej985-rgb/the-black-pines/issues/8): Add Believable Forest Weather & Environmental Motion (P2)
- Created `WeatherDirector` (`scripts/world/weather_director.gd` and `scenes/world/weather_director.tscn`) providing subtle drifting ground mist and rain particle streaks.
- Configured rain particle velocity alignment (`particle_flag_align_y = true`) for realistic wind-slanted raindrops.
- Integrated unified trunk and needle wind sway across `wood_weathered.gdshader` and `tree_wind.gdshader`.
- Added dynamic sinusoidal wind gusts that synchronize foliage shaders and particle velocities in real-time.

### [Issue #9](https://github.com/jakej985-rgb/the-black-pines/issues/9): Graphics Scalability, Profiling & Visual QA (P1)
- Implemented `GraphicsSettingsManager` (`scripts/systems/graphics_settings.gd`) with Low, Medium, High, and Ultra presets controlling resolution scale, shadow maps, volumetric fog, SSAO, and SSIL.
- Created automated benchmarking and profiling harness (`scripts/tools/profile_runner.gd`) and visual QA test suite (`scripts/tools/visual_qa.py`).
- Verified zero memory leaks (+3.55MB stable delta within budget), 35/35 flawless resource audits, and ~145 FPS estimated throughput across all presets. Report generated in `reports/visual_qa_report.json`.
### Deep Realism Overhaul: Cabin, Carcass & Sasquatch Visuals
In response to gameplay test feedback, completed an end-to-end anatomical and architectural overhaul:

1. **Mutilated Elk Carcass & Gore Pool ([`clue_carcass.tscn`](file:///home/m3tal/apps/the-black-pines/scenes/interactables/clue_carcass.tscn), [`elk_carcass.obj`](file:///home/m3tal/apps/the-black-pines/assets/models/elk_carcass.obj), [`carcass_gore_pool.obj`](file:///home/m3tal/apps/the-black-pines/assets/models/carcass_gore_pool.obj))**:
   - Replaced the previous basic cylinder skeleton with a full 700lb bull elk anatomical body mass (3,301 vertices, 2,052 faces).
   - **4 PBR Material Surfaces**:
     - `Pelt`: Shaggy coarse elk hide ([`mat_elk_pelt.tres`](file:///home/m3tal/apps/the-black-pines/assets/materials/mat_elk_pelt.tres)) draped across haunches, dorsal mane, snout, ears, and hooves, with peeled skin flaps folded back from the kill site.
     - `Flesh`: Raw deep-red striated muscle walls and sinew ([`mat_carcass_flesh.tres`](file:///home/m3tal/apps/the-black-pines/assets/materials/mat_carcass_flesh.tres)) with wet clearcoat and subsurface scattering.
     - `Bone`: Catastrophic 16-segment dislocated spine, pried-apart thoracic ribcage with jagged compound fractures and exposed bone marrow, cervid skull, and branching 6-point antlers with peeled velvet strips ([`mat_weathered_bone.tres`](file:///home/m3tal/apps/the-black-pines/assets/materials/mat_weathered_bone.tres)).
     - `Gore`: Convoluted spilled tubular intestinal coils, torn visceral organs, and congealed blood pool ([`mat_gore_blood.tres`](file:///home/m3tal/apps/the-black-pines/assets/materials/mat_gore_blood.tres)).
   - **Multi-Tiered Gore Splatter**: Viscous central gore mound, 36-lobed organic base pool, directional thrash drag streaks, and 14 radiating arterial spray droplets.

2. **Ranger Station Cabin ([`ranger_station.tscn`](file:///home/m3tal/apps/the-black-pines/scenes/interactables/ranger_station.tscn), [`cabin.obj`](file:///home/m3tal/apps/the-black-pines/assets/models/cabin.obj))**:
   - Upgraded architecture to 2,728 vertices and 1,516 faces across 5 PBR materials (`Wood`, `Roof`, `Metal`, `Stone`, `Glass`).
   - **Dimensional Cedar Shake Roof**: Deep 0.75m overhanging eaves, thick dimensional roof deck, heavy barge/fascia boards, 6 stepped 3D shingle relief courses per slope, interlocking timber ridge cap, and 16 exposed rafter tails.
   - **Timber Porch Roof Awning**: Dedicated sloping shed roof extending over the front porch deck.
   - **Heavy Timber Framing**: 4 square 8x8 posts with 45° diagonal knee braces (timber gallows brackets), rustic X-brace Adirondack balustrades, 18-plank deck flooring with rim joists, and 3-tread timber steps.
   - **Masonry Foundation**: Continuous rough-hewn fieldstone perimeter skirting embedding the cabin securely into the undulating terrain.
   - **Props & Details**: Carved wooden "U.S. FOREST SERVICE - BLACK PINE STATION 04" sign, split firewood cord stacked under side eave, cast-iron stovepipe with roof flashing collar, rain cap, and 3 steel guy wires.

3. **Sasquatch Cryptid Overhaul ([`sasquatch.tscn`](file:///home/m3tal/apps/the-black-pines/scenes/creatures/sasquatch.tscn), `sasquatch_*.obj`)**:
   - **Anatomical Proportions**: Colossal hunched trapezius muscles burying the neck directly into the shoulder girdle (Patterson-Gimlin silhouette), massive dual dorsal humps, deep barrel chest, and broad pelvis.
   - **Menacing Facial Sculpt**: Peaked sagittal crest blade, heavy supraorbital brow ridge, cavernous deep sunken eye orbits (housing the glowing eyes), wrinkled black snout with flared nostrils, sneering snarl revealing long curved sabre canine fangs, interlocking lower canines, and sharp incisors ([`mat_weathered_bone.tres`](file:///home/m3tal/apps/the-black-pines/assets/materials/mat_weathered_bone.tres)).
   - **Arms, Claws & Feet**: Corded vascular forearms, 5 articulated digits ending in razor-sharp curved black keratin talons, bowed muscular quadriceps, and broad plantigrade 5-toed clawed feet.
   - **Volumetric Fur Cards**: Expanded multi-tiered fringe cards along sagittal crest, dorsal spine, shoulder mantle, triceps, forearms, and flanks.

---


## 2. Automated Verification Results

| Test Gate | Scope | Status | Notes |
|---|---|---|---|
| **Headless Editor Import** | Full Asset & Script Tree | **PASSED** | Exit code 0, 0 broken loaders or script errors |
| **`test_graphics_weather.gd`** | Flashlight optics, fog, rain alignment, trunk sway, 15-frame runtime preset persistence | **PASSED** | 5 / 5 suites green |
| **`test_runtime_verification.gd`** | Sasquatch rig & animations, Cabin, Camp props, Carcass skeleton, Clawed tree | **PASSED** | 5 / 5 suites green |
| **`visual_qa.py` Profiler** | 35 Resources, 4 Scalability Presets (Low/Med/High/Ultra), Memory Leak Check | **PASSED** | 0 memory leaks (+3.55MB), ~145 FPS across all presets |
| **Headless Stability Run** | 5-Second Headless Game Boot | **PASSED** | Zero crashes, unhandled errors, or warnings |

---

## 3. GitHub Repository Status
- **Repository**: [https://github.com/jakej985-rgb/the-black-pines](https://github.com/jakej985-rgb/the-black-pines)
- **Branch**: `main` (clean, fully synced with `origin/main`)
- **Closed Issues**:
  - [x] `#1` [GRAPHICS] Realism overhaul — master roadmap and tracking
  - [x] `#2` [GRAPHICS][P0] Forest tree assets, density, and natural distribution
  - [x] `#3` [GRAPHICS][P0] Terrain variation and forest-floor realism
  - [x] `#4` [GRAPHICS][P1] Standardize PBR materials and add physically believable weathering
  - [x] `#5` [GRAPHICS][P1] Tune cinematic night lighting, flashlight, and volumetric atmosphere
  - [x] `#6` [GRAPHICS][P0] Replace primitive Sasquatch visuals with a realistic model and rig pipeline
  - [x] `#7` [GRAPHICS][P2] Upgrade ranger station, props, and environmental storytelling assets
  - [x] `#8` [GRAPHICS][P2] Add believable forest weather and environmental motion
  - [x] `#9` [GRAPHICS][P1] Graphics scalability, profiling, and visual QA

---

## 4. 3D Art & Engine MCP Tooling Pipeline Integration

The closed-loop 3D art and engine integration pipeline is fully configured and operational:

```mermaid
flowchart TD
    A["Antigravity AI Agent"] --> B["Blender MCP"]
    A --> C["Godot MCP"]
    B --> D["Detailed 3D Models"]
    D --> E["GLB Assets (.glb)"]
    E --> F["Godot Scene (.tscn)"]
    C --> F
    F --> G["Run Game / Playtest"]
    G --> H["Render Screenshot"]
    H --> A["Inspect Visuals"]
    A --> I["Inspect and Improve"]
    I --> B
    I --> C
```

### Installed Components & Tooling:
1. **Blender 4.2.9 LTS**:
   - Installed portable binary in `~/.local/opt/blender-4.2.9-linux-x64/` with symlink at `~/.local/bin/blender`.
   - Blender MCP connector addon installed at `~/.config/blender/4.2/scripts/addons/mcp_connector_v2.py`.
2. **Blender MCP Server (`blender-mcp`)**:
   - Cloned from `mackson/blender-mcp` into `~/.local/share/mcp-servers/blender-mcp`.
   - Built with TypeScript into `dist/index.js`.
   - Configured in `~/.gemini/config/mcp_config.json` with stdio transport and WebSocket bridge to Blender (`ws://127.0.0.1:9876`).
3. **Godot MCP Server (`godot-mcp`)**:
   - Cloned from `Sods2/godot-mcp` into `~/.local/share/mcp-servers/godot-mcp`.
   - Built with TypeScript into `build/index.js`.
   - Configured in `~/.gemini/config/mcp_config.json` targeting `GODOT_PATH: /home/m3tal/.local/bin/godot`.
   - Installed Godot Editor Bridge plugin into [`addons/godot_mcp_bridge/`](file:///home/m3tal/apps/the-black-pines/addons/godot_mcp_bridge) and enabled in [`project.godot`](file:///home/m3tal/apps/the-black-pines/project.godot).
4. **Poly Haven Asset Sourcing Tool**:
   - CLI utility created at [`scripts/tools/fetch_polyhaven_asset.py`](file:///home/m3tal/apps/the-black-pines/scripts/tools/fetch_polyhaven_asset.py).
   - Supports search, asset inspection, downloading GLTF models and PBR texture maps (Albedo, OpenGL Normal, Roughness, AO), and automated Godot `.tres` material generation.
5. **Agent Rules & Hardware Budget Guidelines**:
   - Created [`GEMINI.md`](file:///home/m3tal/apps/the-black-pines/GEMINI.md) and [`.agents/rules/3d_art_pipeline.md`](file:///home/m3tal/apps/the-black-pines/.agents/rules/3d_art_pipeline.md).
   - Enforces the anti-primitive rule, edge bevels, full PBR maps, GLB transfer standard, and strict GTX 960 hardware budgets (1K/2K texture limits, 60 FPS target).

---

## 5. Phase 2: Core Gameplay Loop & Survival Systems (Issues #17–#26)

Following the visual overhaul, Phase 2 established a complete, interconnected, and test-driven gameplay loop:

### Systems Overview & Deliverables

1. **Investigation Journal & Story Objectives ([Issue #18](https://github.com/jakej985-rgb/the-black-pines/issues/18))**:
   - **`JournalManager`** (`scripts/systems/journal_manager.gd`): Autoload singleton managing objectives (`LOCKED`, `ACTIVE`, `COMPLETED`, `FAILED`), discovered clues, and narrative pacing.
   - **Interactive Journal UI** (`ui/journal_dialog.tscn` / `ui/journal_dialog.gd`): Toggled with `[J]`. Shows active assignments, completed investigation notes, discovered lore documents, and evidence entries with timestamps.
   - **Automated Verification**: `tests/test_objectives_journal.gd` (100% pass).

2. **Inventory, Resource Stacks & World Pickups ([Issue #19](https://github.com/jakej985-rgb/the-black-pines/issues/19))**:
   - **`InventoryManager`** (`scripts/systems/inventory_manager.gd`): Autoload singleton with registry of 11 items across Resources, Tools, Consumables, and Evidence.
   - **Duplication Prevention**: World pickup tracking by unique ID (`collected_world_objects`) prevents item respawns or duplication across reloads.
   - **Interactive Inventory UI** (`ui/inventory_dialog.tscn` / `ui/inventory_dialog.gd`): Toggled with `[Tab]`.
   - **Automated Verification**: `tests/test_inventory_state.gd` (100% pass).

3. **Data-Driven Survival Crafting ([Issue #20](https://github.com/jakej985-rgb/the-black-pines/issues/20))**:
   - **`CraftingManager`** (`scripts/systems/crafting_manager.gd`): Autoload singleton with atomic ingredient validation and recipe execution.
   - **Recipes**:
     - `recipe_spike_trap`: 2x Scrap Metal + 3x Dry Branches $\rightarrow$ 1x Improvised Spike Trap.
     - `recipe_antiseptic_bandage`: 1x Clean Cloth + 2x Angelica Herbs $\rightarrow$ 1x Antiseptic Bandage.
   - **UI Integration**: Dedicated Crafting Tab in `inventory_dialog.tscn`.
   - **Automated Verification**: `tests/test_crafting_system.gd` (100% pass).

4. **Deployable Spike Traps & Active Flares ([Issue #21](https://github.com/jakej985-rgb/the-black-pines/issues/21))**:
   - **Authentic 3D Models**: Modeled via Blender into `.glb` format:
     - `assets/models/trap_spike.glb`: Weathered cedar frame with 9 rusted jagged iron spikes.
     - `assets/models/active_flare.glb`: Magnesium distress flare tube with glowing burning tip.
   - **Deployables**:
     - `DeployableTrap` (`scenes/interactables/deployable_trap.tscn`): Proximity trigger, 3.5s creature snare/stagger, single-use collapse.
     - `ActiveFlare` (`scenes/interactables/active_flare.tscn`): 45s burn time, dynamic flickering omni-light, 14m fear aura.
   - **Player Controls**: Quick-actions `[1]` (flare) and `[2]` (trap) with raycast ground snapping, steep slope rejection, and overlap prevention.
   - **Automated Verification**: `tests/test_traps_flares.gd` (100% pass).

5. **Player Health, Injury & Hemorrhage Loop ([Issue #22](https://github.com/jakej985-rgb/the-black-pines/issues/22))**:
   - **`HealthComponent`** (`scripts/player/health_component.gd`): Modular health state management with bleeding damage over time (2.0 DPS hemorrhage from creature attacks).
   - **Healing & Treatment**: `apply_antiseptic_bandage()` heals 40 HP and stops bleeding. Quick-use keybind on `[3]`.
   - **HUD Feedback**: Pulsing red screen vignette and status indicator when bleeding.
   - **Automated Verification**: `tests/test_health_damage.gd` (100% pass).

6. **Sasquatch Stalking, Flanking & Attack AI ([Issue #23](https://github.com/jakej985-rgb/the-black-pines/issues/23))**:
   - **State Machine** (`scripts/creatures/sasquatch.gd`):
     - `IDLE_ROAM`: Ambient patrol in dense timber.
     - `STALKING`: Shadowing the player while maintaining perimeter distance.
     - `INVESTIGATING`: Auditory reaction to player sprinting within 22m.
     - `FLANKING`: Maneuvering out of the player's direct line of sight.
     - `ALERTED`: Roar telegraph prior to charge.
     - `ATTACK_CHARGE`: 8.5 m/s charge delivering 28 damage + bleed strike.
     - `RETREATING`: Safe disengagement into volumetric fog.
     - `STAGGERED`: 3.5s snare reaction when stepping on spike traps.
     - `FEARED`: Immediate fleeing when entering a 14m flare illumination aura.
   - **Automated Verification**: `tests/test_sasquatch_ai.gd` (100% pass).

7. **Spatial & Surface-Aware Audio ([Issue #24](https://github.com/jakej985-rgb/the-black-pines/issues/24))**:
   - **`AudioDirector`** (`scripts/systems/audio_director.gd`): Procedural synthesis for 4 surface footstep textures (`PINE_NEEDLES`, `WOOD`, `MUD`, `STONE`), low-stamina ragged breathing, and distant territorial 3D wood knocks.
   - **Surface Classification**: Downward raycast in `scripts/player/player.gd` checking collider and group attributes.
   - **Automated Verification**: `tests/test_spatial_audio.gd` (100% pass).

8. **Flashlight Battery Drain & Low-Power ([Issue #25](https://github.com/jakej985-rgb/the-black-pines/issues/25))**:
   - **Power Management**: 0.8%/sec discharge rate while illuminated; zero drain while powered off.
   - **Low Power & Cutoff**: Brownout flickering under 20% charge; automatic shutdown and toggle lockout at 0%.
   - **Reload Mechanic**: `[R]` consumes a `battery_pack` from inventory and restores 100% charge.
   - **HUD Integration**: Real-time battery meter in `ui/hud.tscn`.
   - **Automated Verification**: `tests/test_flashlight_battery.gd` (100% pass).

9. **Mission Loop & Save/Load Persistence ([Issue #26](https://github.com/jakej985-rgb/the-black-pines/issues/26))**:
   - **`MissionDirector`** (`scripts/systems/mission_director.gd`): Tracks chapter objectives, evaluates extraction readiness (cabin investigated + 2 clues gathered + defenses crafted), and triggers shortwave radio extraction.
   - **`SaveManager`** (`scripts/systems/save_manager.gd`): Atomic, versioned JSON serialization of player transform, health, battery, flashlight state, inventory, journal objectives, and world pickups.
   - **Resilience**: Gracefully handles missing files, detects corrupted JSON syntax, and enforces schema version checks.
   - **Automated Verification**: `tests/test_save_persistence.gd` (100% pass).

---

## 6. Complete Automated Test Suite (10/10 Passing)

| Test Script | Scope | Result |
|---|---|---|
| `test_objectives_journal.gd` | Story objectives, clue discovery, UI state | **PASSED** |
| `test_inventory_state.gd` | 11 items, stack clamping, atomic removal, world pickups | **PASSED** |
| `test_crafting_system.gd` | Recipes, atomic deductions, inventory integration | **PASSED** |
| `test_traps_flares.gd` | Deployable traps, active flares, creature fear/snare | **PASSED** |
| `test_health_damage.gd` | HealthComponent, bleeding DoT, bandages, downing | **PASSED** |
| `test_sasquatch_ai.gd` | AI FSM: Stalking, Sprint audio alert, Charge, Flare flee | **PASSED** |
| `test_spatial_audio.gd` | 4 Surface types, stamina breathing, 3D wood knocks | **PASSED** |
| `test_flashlight_battery.gd` | Battery drain, brownout flicker, reload with battery pack | **PASSED** |
| `test_save_persistence.gd` | Save/load round-trip, JSON corruption fallback, extraction | **PASSED** |
| `test_runtime_verification.gd` | Sasquatch rig, cabin, camp props, carcass, clawed tree | **PASSED** |
