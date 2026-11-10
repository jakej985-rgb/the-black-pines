#!/usr/bin/env python3
"""
Sasquatch Organic Blockout Builder — Iteration 4 (Phase 1 / Issue #29).
Applies targeted proportion corrections from Iteration 3 critique:
- Broadens deltoids and latissimus dorsi by +22% for the iconic gorilla V-taper
- Thickens forearm muscle bellies and outer arm silhouette by +30%
- Enlarges 5-fingered hands with heavy ape fingers in stalking grip
- Widens zygomatic cheekbones, mandible, and chin beard volume for broad ape countenance
- Broadens the sagittal crest ridge (no narrow pinhead cone)
- Deepens anterior barrel chest and core
- Grounds 18-inch plantigrade feet in wide bent-knee stance
"""

import bpy
import bmesh
import math
import sys
from pathlib import Path
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_GLB = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source" / "base_mesh.glb"
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source"
BUILD_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "build"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)


def build_blockout():
    clean_scene()
    print("=" * 60)
    print(" BUILDING CLASSIC BIGFOOT ANATOMICAL BLOCKOUT — ITERATION 4")
    print("=" * 60)

    # 1. Import base mesh
    bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))
    mesh_obj = None
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH' and o.name != 'Icosphere':
            mesh_obj = o
        elif o.type == 'ARMATURE' or o.name == 'Icosphere':
            bpy.data.objects.remove(o, do_unlink=True)

    if not mesh_obj:
        raise RuntimeError("Failed to find base mesh in base_mesh.glb")

    mesh_obj.parent = None
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # In base_mesh.glb, character faces -Y. Rotate 180 deg around Z so it faces +Y (diagnostic front camera)
    mesh_obj.rotation_euler = (0, 0, math.pi)
    bpy.ops.object.transform_apply(rotation=True)

    # Map vertex groups
    vg_map = {vg.name: vg.index for vg in mesh_obj.vertex_groups}

    def get_weight(v, names):
        total = 0.0
        for name in names:
            if name in vg_map:
                idx = vg_map[name]
                for g in v.groups:
                    if g.group == idx:
                        total += g.weight
        return min(total, 1.0)

    # Bone group sets
    HEAD_GROUPS = ['spine.004', 'spine.005']
    UPPER_TRAP_GROUPS = ['spine.003', 'shoulder.L', 'shoulder.R']
    TORSO_GROUPS = ['spine', 'spine.001', 'spine.002', 'spine.003', 'shoulder.L', 'shoulder.R', 'pelvis.L', 'pelvis.R']
    ARM_UP_GROUPS = ['upper_arm.L', 'upper_arm.R']
    ARM_LOW_GROUPS = ['forearm.L', 'forearm.R']
    HAND_GROUPS = ['hand.L', 'hand.R', 'thumb.01.L', 'thumb.01.R', 'thumb.02.L', 'thumb.02.R',
                   'f_index.01.L', 'f_index.01.R', 'f_middle.01.L', 'f_middle.01.R',
                   'f_ring.01.L', 'f_ring.01.R', 'f_pinky.01.L', 'f_pinky.01.R']
    THIGH_GROUPS = ['thigh.L', 'thigh.R']
    SHIN_GROUPS = ['shin.L', 'shin.R']
    FOOT_GROUPS = ['foot.L', 'foot.R', 'toe.L', 'toe.R', 'heel.02.L', 'heel.02.R']

    SCALE_GLOBAL = 1.40
    mesh = mesh_obj.data

    for v in mesh.vertices:
        co = v.co.copy()
        co *= SCALE_GLOBAL

        w_head = get_weight(v, HEAD_GROUPS)
        w_trap = get_weight(v, UPPER_TRAP_GROUPS)
        w_torso = get_weight(v, TORSO_GROUPS)
        w_arm_up = get_weight(v, ARM_UP_GROUPS)
        w_arm_low = get_weight(v, ARM_LOW_GROUPS)
        w_hand = get_weight(v, HAND_GROUPS)
        w_thigh = get_weight(v, THIGH_GROUPS)
        w_shin = get_weight(v, SHIN_GROUPS)
        w_foot = get_weight(v, FOOT_GROUPS)

        # 1. LEGS & CROUCH STANCE (Bent-knee stalking crouch, bowed legs)
        if w_thigh > 0.05 or w_shin > 0.05 or w_foot > 0.05:
            # Stance spread increases smoothly down the leg toward the feet (preserving natural crotch & lower abdomen at hips)
            spread_factor = max(0.0, min(1.0, (1.15 - co.z) / 1.00)) ** 1.5
            lateral_spread = (0.16 if co.x > 0 else -0.16) * spread_factor
            co.x += lateral_spread

            if w_thigh > 0.1:
                co.z -= 0.10 * w_thigh
                co.y += 0.08 * w_thigh
                co.x *= (1.0 + 0.35 * w_thigh)
                co.y *= (1.0 + 0.38 * w_thigh)

            if w_shin > 0.1:
                co.z -= 0.06 * w_shin
                co.y -= 0.05 * w_shin
                co.x *= (1.0 + 0.38 * w_shin)
                if co.y < 0:
                    co.y *= (1.0 + 0.50 * w_shin)

            # 18-inch Plantigrade Foot (wide, long, flat)
            if w_foot > 0.1:
                co.x *= (1.0 + 0.48 * w_foot)
                if co.y > 0:
                    co.y *= (1.0 + 0.75 * w_foot)
                else:
                    co.y *= (1.0 + 0.40 * w_foot)
                if co.z < 0.15:
                    co.z = max(0.01, co.z * 0.58)

        # 2. TORSO & MASSIVE TRAPEZIUS (Colossal gorilla barrel chest, deep core & broad lats)
        if w_torso > 0.05:
            # Major expansion in chest, core, and lats
            co.x *= (1.0 + 0.55 * w_torso)
            if co.y > 0:
                co.y *= (1.0 + 0.50 * w_torso)  # Deep barrel chest and full abdominal depth
            else:
                co.y *= (1.0 + 0.42 * w_torso)  # Heavy back

            # Continuous forward abdominal & chest volume (eliminates waist hollow / shelf)
            if 1.05 < co.z < 2.05 and co.y > 0.0:
                torso_belly = math.sin((co.z - 1.05) / 1.00 * math.pi)
                co.y += 0.12 * torso_belly * w_torso

            # Colossal Trapezius Hump — eliminate neck collar, rise smoothly into skull base
            if co.z > 1.70:
                hump_factor = min(1.0, (co.z - 1.70) / 0.50)
                co.z += 0.15 * hump_factor * w_torso
                if co.y < 0.15:
                    co.z += 0.12 * hump_factor
                    co.y -= 0.05 * hump_factor

        # 3. HEAD & SIMIAN CRANIUM (Broad ape skull on actual head z >= 2.25m)
        if w_head > 0.05:
            co.z -= 0.02 * w_head
            co.y += 0.05 * w_head

            # Broaden cheekbones, mandible, and skull
            co.x *= (1.0 + 0.35 * w_head)

            # Sagittal Crest: wide backward-sloping ape dome (z >= 2.60m)
            if co.z > 2.58:
                crest_prog = min(1.0, (co.z - 2.58) / 0.22)
                co.z += 0.06 * crest_prog * w_head
                co.y -= 0.10 * crest_prog * w_head
                co.x *= (1.0 + 0.10 * crest_prog)  # Keep crest rounded & broad, NOT a pinhead spike!

            # Heavy Supraorbital Brow Shelf (z: 2.50 - 2.65m)
            if 2.50 < co.z < 2.66 and co.y > 0.0:
                brow_prog = math.sin((co.z - 2.50) / 0.16 * math.pi)
                co.y += 0.08 * brow_prog * w_head

            # Prognathic Ape Muzzle (z: 2.30 - 2.48m)
            if 2.30 < co.z < 2.48 and co.y > 0.02:
                muzzle_prog = math.sin((co.z - 2.30) / 0.18 * math.pi)
                co.y += 0.09 * muzzle_prog * w_head
                co.x *= (1.0 + 0.18 * muzzle_prog * w_head)

            # Chin Beard & Throat Fringe (z: 2.22 - 2.38m)
            if 2.22 < co.z < 2.38 and co.y > 0.04:
                beard_prog = min(1.0, (2.38 - co.z) / 0.16)
                co.y += 0.08 * beard_prog * w_head
                co.x *= (1.0 + 0.25 * beard_prog)

        # 4. LONG MUSCULAR ARMS (Forward stalking grip, colossal forearms)
        w_arm_total = w_arm_up + w_arm_low + w_hand
        if w_arm_total > 0.05:
            co.z -= 0.30 * w_arm_total
            co.y += 0.10 * w_arm_total

            # Heavy upper arm & deltoid
            if w_arm_up > 0.1:
                co.x += (0.15 if co.x > 0 else -0.15) * w_arm_up
                co.y *= (1.0 + 0.40 * w_arm_up)

            # Colossal vascular forearm thickness & outer silhouette volume
            if w_arm_low > 0.1:
                co.x += (0.20 if co.x > 0 else -0.20) * w_arm_low
                co.y *= (1.0 + 0.60 * w_arm_low)

            # Heavy grasping hands with ape palm & fingers
            if w_hand > 0.1:
                co.x += (0.12 if co.x > 0 else -0.12) * w_hand
                co.y *= (1.0 + 0.50 * w_hand)
                if co.z < 0.95:
                    co.y += 0.10 * w_hand


        v.co = co

    mesh.update()

    # 5. Voxel Remesh for uniform, continuous, watertight organic geometry
    mesh_obj.data.remesh_voxel_size = 0.018  # 1.8cm uniform organic resolution
    bpy.ops.object.voxel_remesh()

    # Smooth modifier pass to refine anatomical muscle transitions
    mod_smooth = mesh_obj.modifiers.new("BlockoutSmooth", "SMOOTH")
    mod_smooth.factor = 0.50
    mod_smooth.iterations = 3
    bpy.ops.object.modifier_apply(modifier="BlockoutSmooth")

    # Subdivision surface for smooth curvature
    mod_sub = mesh_obj.modifiers.new("BlockoutSubsurf", "SUBSURF")
    mod_sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="BlockoutSubsurf")

    # Ensure ground contact at z = 0
    bpy.context.view_layer.update()
    corners = [mesh_obj.matrix_world @ Vector(c) for c in mesh_obj.bound_box]
    min_z = min(c.z for c in corners)
    mesh_obj.location.z -= min_z
    bpy.ops.object.transform_apply(location=True)

    bpy.ops.object.shade_smooth()

    # Neutral clay material
    mat = bpy.data.materials.new("BlockoutClay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.6, 0.55, 0.5, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)

    bpy.context.view_layer.update()
    dims = mesh_obj.dimensions
    vert_count = len(mesh_obj.data.vertices)
    poly_count = len(mesh_obj.data.polygons)
    print(f">>> BLOCKOUT BOUNDS (Iter 4): X={dims.x:.2f}m Y={dims.y:.2f}m Z={dims.z:.2f}m | verts={vert_count}, polys={poly_count} <<<")

    # Save .blend and export .obj
    blend_path = SOURCE_DIR / "blockout.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    obj_path = BUILD_DIR / "blockout.obj"
    bpy.ops.wm.obj_export(
        filepath=str(obj_path),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
    )
    print(f">>> SAVED: {blend_path}")
    print(f">>> EXPORTED: {obj_path}")


if __name__ == "__main__":
    build_blockout()
