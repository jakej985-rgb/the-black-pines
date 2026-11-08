# The Black Pines (M3TAL: UNKNOWN)

[![Engine](https://img.shields.io/badge/Engine-Godot%204.7%2B-blue.svg)](https://godotengine.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-green.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](#)

> **"It didn't scream... it laughed. A low, rolling vibration in your chest. God help us."**

*The Black Pines* (working title: **M3TAL: UNKNOWN**) is an atmospheric first-person cryptid survival horror game built in **Godot 4.7 Forward+** with GDScript. 

You play as an investigator arriving at the abandoned Black Pine Ranger Station #04 following anomalous reports of vanished forestry wardens and violent livestock attacks deep in the Pacific Northwest backcountry.

---

## Key Features

- **Atmospheric Horror Experience**: Cool night procedural skybox, volumetric fog, directional moonlight silhouettes, and dense pine canopies.
- **Dynamic Horror Audio Director**: Synthesized spatial audio featuring crunching pine needle footsteps, ambient night wind, distant timber creaks, branch snaps, and sub-bass creature vocalizations.
- **Cryptid Stalker AI**: A towering 9-foot beast lurking at the perimeter of the fog with amber reflective eye glints that reacts to flashlight beams and close proximity.
- **Physical Camera & Movement**: Clamped pitch look, stamina-based sprint and jump, physical camera bank/roll on strafes, landing compression, and flashlight sway with volumetric dust motes.
- **Environmental Storytelling & Clues**:
  - Evacuated Ranger Station #04 with notice boards and porch light.
  - Three sets of massive bipedal clawed footprints pressed into the mud.
  - Territorial claw marks carved 10 cm deep into a weathered pine trunk with bleeding sap.
  - Mutilated bull elk kill site with shattered marrow bones, pried ribcage, and dark coagulated gore pool.
  - Abandoned hunter expedition campsite with waterlogged journal, spent cartridges, and emergency road flares.
- **Photorealistic PBR Visual Suite**:
  - 1K scanned PBR materials (Albedo, Normal OpenGL, Roughness, Ambient Occlusion) for forest ground loam, knotted pine bark, weathered cabin wood, and canvas tent fabric.
  - 3D photogrammetry-scanned mountain boulders and moss-covered rock formations.
  - Dedicated perimeter cliff barriers and out-of-bounds fall safety recovery.

---

## Controls

| Action | Key / Input |
|---|---|
| **Move** | `W`, `A`, `S`, `D` |
| **Look** | Mouse |
| **Sprint** | `Shift` (Hold) |
| **Jump** | `Space` |
| **Toggle Flashlight** | `F` |
| **Interact / Inspect / Gather** | `E` |
| **Unlock / Capture Mouse** | `Escape` / Left Click |

---

## Quickstart

### Prerequisites
- [Godot Engine 4.7+](https://godotengine.org/download)

### Run the Game Directly
```bash
./run_game.sh
```
*(Or launch directly with Godot CLI: `godot --path .`)*

### Open in Godot Editor
```bash
./open_editor.sh
```

---

## Project Structure

```text
the-black-pines/
├── project.godot
├── run_game.sh             # Direct launch helper script
├── open_editor.sh          # Editor launcher helper script
├── assets/
│   ├── imported/           # Scanned 3D GLTF models (rocks, tree trunk)
│   ├── materials/          # PBR materials (.tres) and foliage wind shader
│   ├── models/             # 3D Wavefront meshes (cabin, tent, elk carcass, clawed tree)
│   └── textures/           # Scanned 1K PBR textures (bark, mud loam, planks, fabric)
├── scenes/
│   ├── creatures/          # Sasquatch stalker scene & AI
│   ├── interactables/      # Clues, carcass, cabin, camp, and collectible items
│   ├── main/               # Game entry point scene linking world, player & HUD
│   ├── player/             # First-person CharacterBody3D with flashlight & raycast
│   └── world/              # Forest environment, trees, rocks & map boundaries
├── scripts/
│   ├── creatures/          # Cryptid AI logic
│   ├── interaction/        # Interactable, clue inspection & collectible item scripts
│   ├── player/             # Player controller, stamina, footstep & fall recovery
│   └── systems/            # Game manager & audio director
├── ui/                     # Minimalist HUD, crosshair & clue inspection dialog
└── docs/                   # Detailed game design & technical architecture docs
```
