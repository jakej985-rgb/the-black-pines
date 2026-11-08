# Technical Architecture: The Black Pines

## 1. Architecture Overview
Built on **Godot 4.7** using **GDScript** and the **Forward+** rendering pipeline.

### Directory Structure
```text
the-black-pines/
├── scenes/
│   ├── main/             # Main game entry scenes
│   ├── player/           # First person player character rig
│   ├── world/            # Environments, terrain, lighting, trees
│   ├── creatures/        # Cryptid rigs and AI scenes
│   └── interactables/    # Inspectable clues, pickups, doors, traps
├── scripts/
│   ├── player/           # Player physics, camera, input
│   ├── creatures/        # Finite state machines for AI
│   ├── systems/          # Global managers, audio directors
│   └── interaction/      # Base classes (Interactable, CollectibleItem, InspectableClue)
├── assets/
│   ├── models/           # 3D meshes (glTF / OBJ)
│   ├── materials/        # PBR materials and shaders
│   ├── textures/         # Albedo, normal, roughness maps
│   ├── audio/            # Ambient loops, creature roars, footsteps
│   └── animations/       # Creature animations
├── ui/                   # HUD, menus, inspection dialogs
└── docs/                 # Design & architecture documentation
```

## 2. Interaction Model
- Built around `Interactable` (`scripts/interaction/interactable.gd`) extending `CollisionObject3D`.
- Player camera has a `RayCast3D` scanning ahead for `Interactable` nodes.
- Derived classes:
  - `InspectableClue`: Emits inspection dialogue with lore / observations.
  - `CollectibleItem`: Adds materials into player inventory and frees node.

## 3. Rendering & Horror Lighting Pipeline
- **Volumetric Fog**: Enabled via `WorldEnvironment` to diffuse light from the player's flashlight and moonlight, producing dramatic god rays and concealing distant silhouettes.
- **Directional Light**: Low-energy, cool moonlight (`Color(0.5, 0.62, 0.75)`, energy `0.22`) with shadows to form silhouettes.
- **Flashlight**: SpotLight3D with smooth angular sway interpolation attached to the player camera.
