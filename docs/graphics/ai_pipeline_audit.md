# AI Creature Art Pipeline — Phase 0 Audit

Date: 2026-11-09. Issues: #28 (master), #29, #30, #31, reopened #6, #11, #16.
Proof case: Classic Bigfoot, `assets/creatures/sasquatch/references/classic_bigfoot_concept.png`.

## 1. Current pipeline (verified)

- `scripts/tools/build_classic_bigfoot_continuous.py` (v3, latest) and
  `build_classic_bigfoot_ape.py` (v2) generate the creature as a **single
  continuous quad mesh** via `loft_polygon_rings()` — hand-placed polygon
  rings skinned into quads — then voxel-remesh + smooth. Output:
  `assets/models/sasquatch_*.obj` (9 separate part OBJs for the legacy scene)
  and `assets/creatures/sasquatch/source/base_mesh.glb`.
- `scenes/creatures/sasquatch.tscn` composes 9 separate OBJ meshes
  (torso, head, arms x2, hands, legs x2, feet) + fur cards. Animation is
  **value tracks rotating/scaling visual nodes — no Skeleton3D/skinning**.
- `scripts/tools/render_diagnostic_views.py` renders 5 clay views
  (front/side/rear/three-quarter/bust) into `qa/diagnostic_views/` with a
  manifest check. `visual_qa.py` does Godot headless import + profiling.
  `asset_spec_validator.py` validates `asset_spec.yaml` structure.
- Rules (`.agents/rules/3d_art_pipeline.md`, `GEMINI.md`) already forbid
  primitive hero meshes and require asset_spec + reference dirs. The v3
  builder complies *technically* (continuous quads, no intersections) but
  the result still reads as crude/childlike — lofted rings cannot produce
  believable organic anatomy (no muscle bellies, tendon shapes, or
  asymmetry) and there is **no visual critique loop** feeding corrections.

## 2. Failure points

1. **No likeness feedback loop.** Renders exist but nothing compares them
   to the reference or converts mismatch into targeted fixes. Iterations
   were driven by code changes, not visual findings.
2. **Loft-ring modeling ceiling.** Parametric ring-lofting produces smooth
   but anatomically wrong forms; every "fix" is a guess at vertex offsets.
3. **No stage gates.** Intermediate/test renders live in the same
   `qa/diagnostic_views/` tree; nothing records pass/revise/reject, so a
   rejected mesh can silently become the production asset.
4. **No skeleton.** Scene animates parts independently; issue #11 requires
   evaluating Skeleton3D/skinning.
5. **Triangle budget applied at generation time** (spec `max_triangles:
   16000` enforced by decimate inside the builder), which conflicts with
   #31's requirement that sculpt stage be unconstrained.

## 3. Tool availability (verified on this machine)

| Tool | Status |
|---|---|
| Blender 4.2.9 LTS (`~/.local/bin/blender`) | Available; headless `--background --python` works. bpy incl. metaballs, voxel remesh, multires. |
| Blender MCP | Addon `mcp_connector_v2` installed in Blender config; MCP server config exists only in `~/.gemini/config/mcp_config.json` (Gemini CLI), **not wired into Devin** (`mcp_list_servers` = empty). Headless bpy scripts are the reliable path here. |
| Godot | `godot` binary on PATH; headless import + `-s` script capture works (`visual_qa.py`). |
| Godot MCP | Server files exist at `~/.local/share/mcp-servers/godot-mcp` but not configured for Devin. |
| Image-to-3D (Tripo/Meshy/Shap-E/Trellis) | **Not available.** No models, no API keys, no local install. |
| ComfyUI + Ollama (docker/artwork) | **Rejected by user** — GTX 960 too weak for useful generation; containers stopped, pull aborted. Only SD1.5 + gemma3:4b were present anyway; no image-to-3D nodes. |
| Vision model for critique | This agent **cannot view images** (text-only) and no viable local vision model exists. **Human review is the required critique mechanism** at every gate, per #30. |
| GPU | GTX 960 4GB — rules out local diffusion/3D-gen; fine for Blender renders. |

## 4. Proposed production workflow

Given no image-to-3D tool and no agent vision, the honest path is:

1. **Blockout (now):** Blender metaball-field sculpt → mesh conversion →
   voxel remesh. Metaballs produce genuinely organic, continuous forms
   (no primitive intersections/seams) and are scriptable for repeatable
   proportion iteration. This is a *blockout* technique, not the final
   hero method — it exists to pass the silhouette gate.
2. **Silhouette gate:** 5-view clay renders + silhouette sheet vs
   reference checklist. **Human review required** — the agent cannot
   verify likeness.
3. **Hero sculpt (after approval):** interactive Blender sculpting
   (multires + dyntopo + sculpt brushes) is the only route to believable
   anatomy available on this machine. This needs a human with Blender,
   or an approved alternative (e.g. licensed base mesh). Documented as
   the key dependency.
4. **Retopo/UV/bake → materials/fur → Skeleton3D rig → Godot import**,
   each behind the stage gates in `pipeline_state.yaml`.

## 5. Files to modify / create

- `assets/creatures/sasquatch/pipeline_state.yaml` — stage gate state (new)
- `scripts/tools/asset_stage_gate.py` — gate CLI (new)
- `scripts/tools/build_sasquatch_blockout.py` — metaball blockout (new)
- `scripts/tools/render_comparison_set.py` — reference-vs-render sheets (new)
- `assets/creatures/sasquatch/references/TARGET_CHECKLIST.md` (new)
- `docs/graphics/ai_pipeline_audit.md` — this file
- Later: `build_classic_bigfoot_continuous.py` (retopo stage),
  `scenes/creatures/sasquatch.tscn` + rig (only after approvals)

## 6. Risks / dependencies

- **Human-in-the-loop is mandatory** at blockout_review and sculpt_review;
  the agent cannot see renders. gemma3:4b critique is best-effort only.
- Metaball blockout may not reach "recognizably Classic Bigfoot" alone;
  expect proportion iteration cycles with human feedback.
- No image-to-3D shortcut exists; do not add paid/API dependencies without
  user approval.
- GTX 960 budget (16k tris) applies only at retopo stage, not blockout/sculpt.
