#!/usr/bin/env python3
"""
Sasquatch organic BLOCKOUT builder (issue #29, stage: blockout_review).

Builds the creature as a single continuous metaball field converted to mesh,
then voxel-remeshed. Metaballs are used here ONLY to get a continuous,
seam-free organic silhouette for the blockout gate — they are not the final
hero-sculpt method. Proportions target the Classic Bigfoot spec:
2.85 m mass, forward-leaning bent-knee posture, +Y forward, +Z up, X lateral.

Run:  blender --background --python scripts/tools/build_sasquatch_blockout.py
Outputs:
  assets/creatures/sasquatch/source/blockout.blend
  assets/creatures/sasquatch/build/blockout.obj        (generated artifact)
"""

import bpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source"
BUILD_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "build"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# (name, co(x,y,z), radius, stiffness)
# Frame: Z up, Y forward (face/chest direction), X lateral. Feet at z=0.
ELEMENTS = [
    # --- pelvis / hips ---
    ("pelvis",        (0.00, -0.02, 0.98), 0.36, 2.0),
    ("hip_l",         ( 0.26, -0.05, 0.92), 0.25, 2.0),
    ("hip_r",         (-0.26, -0.05, 0.92), 0.25, 2.0),
    ("glute_l",       ( 0.20, -0.28, 1.02), 0.24, 2.0),
    ("glute_r",       (-0.20, -0.28, 1.02), 0.24, 2.0),
    # --- legs (bowed, bent-knee stalk) ---
    ("thigh_l",       ( 0.25, -0.02, 0.62), 0.23, 2.0),
    ("thigh_r",       (-0.25, -0.02, 0.62), 0.23, 2.0),
    ("knee_l",        ( 0.27, -0.18, 0.40), 0.18, 2.0),
    ("knee_r",        (-0.27, -0.18, 0.40), 0.18, 2.0),
    ("calf_l",        ( 0.28, -0.02, 0.24), 0.19, 2.0),
    ("calf_r",        (-0.28, -0.02, 0.24), 0.19, 2.0),
    ("shin_l",        ( 0.28,  0.06, 0.12), 0.14, 2.0),
    ("shin_r",        (-0.28,  0.06, 0.12), 0.14, 2.0),
    ("foot_l",        ( 0.28,  0.30, 0.07), 0.20, 2.0),
    ("foot_r",        (-0.28,  0.30, 0.07), 0.20, 2.0),
    # --- torso: barrel chest, no neck ---
    ("abdomen",       ( 0.00,  0.10, 1.30), 0.38, 2.0),
    ("barrel_chest",  ( 0.00,  0.20, 1.62), 0.46, 2.0),
    ("pec_l",         ( 0.20,  0.42, 1.64), 0.19, 2.0),
    ("pec_r",         (-0.20,  0.42, 1.64), 0.19, 2.0),
    ("lat_l",         ( 0.34,  0.05, 1.55), 0.22, 2.0),
    ("lat_r",         (-0.34,  0.05, 1.55), 0.22, 2.0),
    ("lower_back",    ( 0.00, -0.12, 1.45), 0.36, 2.0),
    # --- trapezius hump (rises above neck line) ---
    ("trap_hump",     ( 0.00, -0.02, 1.98), 0.44, 2.0),
    ("trap_slope_l",  ( 0.38,  0.10, 2.00), 0.26, 2.0),
    ("trap_slope_r",  (-0.38,  0.10, 2.00), 0.26, 2.0),
    ("deltoid_l",     ( 0.58,  0.16, 1.86), 0.28, 2.0),
    ("deltoid_r",     (-0.58,  0.16, 1.86), 0.28, 2.0),
    # --- head / skull ---
    ("skull_base",    ( 0.00,  0.24, 2.18), 0.26, 2.0),
    ("cranium",       ( 0.00,  0.22, 2.38), 0.23, 2.0),
    ("crest",         ( 0.00,  0.05, 2.52), 0.17, 2.0),
    ("brow_l",        ( 0.11,  0.42, 2.42), 0.10, 2.0),
    ("brow_r",        (-0.11,  0.42, 2.42), 0.10, 2.0),
    ("muzzle",        ( 0.00,  0.46, 2.28), 0.14, 2.0),
    ("jaw",           ( 0.00,  0.40, 2.16), 0.16, 2.0),
    # --- arms: long, reaching past mid-thigh ---
    ("upper_arm_l",   ( 0.72,  0.18, 1.62), 0.17, 2.0),
    ("upper_arm_r",   (-0.72,  0.18, 1.62), 0.17, 2.0),
    ("bicep_l",       ( 0.70,  0.34, 1.50), 0.13, 2.0),
    ("bicep_r",       (-0.70,  0.34, 1.50), 0.13, 2.0),
    ("elbow_l",       ( 0.84,  0.10, 1.24), 0.15, 2.0),
    ("elbow_r",       (-0.84,  0.10, 1.24), 0.15, 2.0),
    ("forearm_l",     ( 0.90,  0.16, 0.92), 0.17, 2.0),
    ("forearm_r",     (-0.90,  0.16, 0.92), 0.17, 2.0),
    ("wrist_l",       ( 0.93,  0.22, 0.68), 0.12, 2.0),
    ("wrist_r",       (-0.93,  0.22, 0.68), 0.12, 2.0),
    ("hand_l",        ( 0.93,  0.28, 0.52), 0.14, 2.0),
    ("hand_r",        (-0.93,  0.28, 0.52), 0.14, 2.0),
    ("knuckle_l",     ( 0.94,  0.36, 0.44), 0.09, 2.0),
    ("knuckle_r",     (-0.94,  0.36, 0.44), 0.09, 2.0),
]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mb = bpy.data.metaballs.new("SasquatchBlockoutMeta")
    mb.resolution = 0.045
    mb.render_resolution = 0.02
    mb.threshold = 0.6
    obj = bpy.data.objects.new("SasquatchBlockout", mb)
    bpy.context.scene.collection.objects.link(obj)

    for name, co, radius, stiffness in ELEMENTS:
        el = mb.elements.new()
        el.co = co
        el.radius = radius
        el.stiffness = stiffness

    # Convert metaball field to mesh, then voxel remesh for uniform topology
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active
    obj.name = "SasquatchBlockout"

    obj.data.remesh_voxel_size = 0.035
    bpy.ops.object.voxel_remesh()

    # Gentle organic smoothing
    mod = obj.modifiers.new("BlockoutSmooth", "SMOOTH")
    mod.factor = 0.5
    mod.iterations = 3
    bpy.ops.object.modifier_apply(modifier="BlockoutSmooth")

    # Neutral clay material so diagnostic renders shade consistently
    mat = bpy.data.materials.new("BlockoutClay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.6, 0.55, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    obj.data.materials.append(mat)

    # Ground the model: report bounds for the review manifest
    bpy.context.view_layer.update()
    dims = obj.dimensions
    print(f">>> BLOCKOUT bounds: X={dims.x:.2f} Y={dims.y:.2f} Z={dims.z:.2f} m, "
          f"verts={len(obj.data.vertices)} <<<")

    blend_path = SOURCE_DIR / "blockout.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=str(BUILD_DIR / "blockout.obj"),
                          export_selected_objects=True)
    print(f">>> SAVED {blend_path} and {BUILD_DIR / 'blockout.obj'} <<<")


main()
