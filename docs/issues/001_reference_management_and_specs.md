# [P0 · Issue 1] Reference Management and Asset Specifications

## 1. Objective
Establish a formal, reproducible reference management architecture where concept art, turnaround sheets, and design specifications are permanently tracked alongside 3D assets, rather than passed as ephemeral prompt attachments.

---

## 2. Standardized Directory Architecture
Every high-fidelity asset (creatures, hero props, architectural landmarks) must reside in a dedicated directory with the following structure:

```text
assets/
└── creatures/
    └── <asset_id>/
        ├── references/          # Concept art, turnarounds, anatomical photo references
        │   ├── primary_concept.png
        │   ├── front_turnaround.png
        │   ├── side_turnaround.png
        │   └── rear_turnaround.png
        ├── source/              # High-poly sculpts (.blend), ZBrush files, or raw photogrammetry
        ├── working/             # Active work-in-progress scene files, bakes, UV maps
        ├── exports/             # Game-ready binary glTF (.glb) and LOD exports
        ├── materials/           # PBR texture sets (diff, nor_gl, rough, arm) and shaders
        ├── qa/                  # Diagnostic clay renders, in-engine captures, and critic reports
        └── asset_spec.yaml      # Master contract specification for the asset
```

---

## 3. Asset Specification (`asset_spec.yaml`) Schema
Every asset directory must contain an `asset_spec.yaml` declaring its metadata, targets, and constraints:

```yaml
asset_id: sasquatch_classic
asset_type: organic_creature    # organic_creature | environment_prop | procedural_scatter
quality_tier: hero             # hero | standard | background

reference:
  primary: references/classic_bigfoot_concept.png
  front: references/front_turnaround.png
  side: references/side_turnaround.png
  rear: references/rear_turnaround.png

design:
  species: sasquatch
  style: realistic_grounded
  scale_meters: 2.85
  body_type: massive_humanoid_ape
  posture: forward_leaning_bent_knee
  key_features:
    - conical_sagittal_crest_sloping_backward
    - heavy_supraorbital_brow_shelf
    - broad_flat_simian_nose_closed_lips
    - neckless_trapezius_slope
    - broad_barrel_chest_flat_pectorals
    - long_arms_reaching_past_mid_thigh
    - plantigrade_wide_feet_18_inch

materials:
  fur_color: dark_chestnut_brown
  skin_tone: dark_charcoal_leathery
  eye_reflection: amber_tapetum_lucidum
  roughness_range: [0.70, 0.95]

budget:
  max_triangles: 16000
  target_triangles: 12000
  max_texture_resolution: 2048
  target_fps: 60
  gpu_target: nvidia_gtx_960

requirements:
  match_reference: true
  continuous_anatomy: true
  realistic_materials: true
  gameplay_ready: true

status: in_development        # concept | base_anatomy | sculpted | textured | integrated | approved
```

---

## 4. Implementation Tasks

- [ ] Create folder structure for `assets/creatures/sasquatch/` (`references/`, `source/`, `working/`, `exports/`, `materials/`, `qa/`).
- [ ] Author `assets/creatures/sasquatch/asset_spec.yaml` with the Classic Bigfoot design specs and hardware constraints.
- [ ] Ingest visual reference concept art into `assets/creatures/sasquatch/references/`.
- [ ] Create Python validation utility `scripts/tools/asset_spec_validator.py` that verifies:
  1. All declared reference files exist on disk.
  2. All mandatory YAML keys are populated.
  3. Triangles and texture dimensions adhere to the GTX 960 hardware budget.
- [ ] Update `GEMINI.md` to instruct AI agents to inspect `asset_spec.yaml` prior to initiating any 3D asset work.

---

## 5. Acceptance Criteria
- [ ] Running `python3 scripts/tools/asset_spec_validator.py --spec assets/creatures/sasquatch/asset_spec.yaml` exits with code `0`.
- [ ] All required subdirectories exist under `assets/creatures/sasquatch/`.
- [ ] Spec correctly defines target scale, triangle budget (max 16,000), texture limits (2048), and anatomical markers.
