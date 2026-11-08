# 3D Art Pipeline & Quality Standards: The Black Pines

## Guidelines
- **Workflow**: Antigravity -> Blender MCP -> Detailed 3D Models -> GLB Assets -> Godot Scene -> Godot MCP -> Run Game -> Screenshot -> Inspect -> Iterate.
- **Mesh Construction**:
  - Never generate raw un-beveled primitive geometry for hero assets.
  - Apply edge bevels, chamfers, and subdivision surfaces to catch specular highlights.
- **Materials**:
  - Always pair meshes with full PBR sets (Albedo, Normal OpenGL, Roughness, AO).
  - Use `python3 scripts/tools/fetch_polyhaven_asset.py` to source photorealistic CC0 PBR textures.
- **Export & Transfer**:
  - Export from Blender as `.glb` (glTF 2.0 Binary) to `assets/models/`.
  - Up axis: `+Y`, Forward axis: `-Z`.
- **GTX 960 Hardware Budget**:
  - 1K textures for general props and foliage; 2K textures max for hero models (Cabin, Sasquatch).
  - Total triangle budgets: Cryptid (8k-16k), Cabin (10k-22k), Trees (1.5k-4k), Props (300-2.5k).
  - Maintain 60 FPS target at 1080p.
