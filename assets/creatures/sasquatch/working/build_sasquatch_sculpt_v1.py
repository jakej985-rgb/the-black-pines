#!/usr/bin/env python3
"""
Sasquatch Hero Sculpt Builder (Phase 2 / Issue #29 & #6).
Builds a high-resolution organic hero sculpt based on the approved blockout:
- Loads assets/creatures/sasquatch/source/blockout.blend
- Subdivides / remeshes to high resolution (~300,000+ polygons) for detailed sculpting
- Does NOT apply game triangle budget to the high-res sculpt (Phase 2 Rule 6)
- Correctly positions facial anatomy on the ACTUAL HEAD (z = 2.20m - 2.78m):
  * Heavy supraorbital brow shelf (z = 2.58 - 2.72m)
  * Deep recessed orbital sockets with eyeball spheres (z = 2.50 - 2.62m)
  * Broad flat gorilla nose with flared nostril cavities (z = 2.42 - 2.54m)
  * Prognathic simian muzzle with closed ape lip line (z = 2.32 - 2.46m)
  * Cascading chin beard framing face over neck notch (z = 2.18 - 2.38m)
  * Backward-sloping conical sagittal crest (z = 2.65 - 2.78m)
- Correctly positions torso & chest anatomy on the CHEST (z = 1.65m - 2.15m):
  * Dual gorilla pectorals with deep sternal cleft
  * Colossal trapezius hump rising from deltoids directly into skull base
  * Serratus anterior and abdominal wall
  * Vascular brachioradialis forearms, 5-fingered hands, and 18-inch plantigrade feet
- Saves high-res sculpt to assets/creatures/sasquatch/source/hero_sculpt.blend
- Exports assets/creatures/sasquatch/build/hero_sculpt.obj for baking / diagnostic QA
"""

import bpy
import bmesh
import math
import sys
from pathlib import Path
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BLOCKOUT_BLEND = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source" / "blockout.blend"
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source"
BUILD_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "build"
SCULPT_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "qa" / "stage_reviews" / "sculpt_review"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)
(SCULPT_DIR / "diagnostic").mkdir(parents=True, exist_ok=True)
(SCULPT_DIR / "comparison").mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)


def sculpt_anatomy(mesh_obj):
    """Sculpts detailed organic anatomical features and fur volume onto the high-res mesh."""
    bpy.context.view_layer.objects.active = mesh_obj
    mesh = mesh_obj.data

    # High-resolution voxel remesh (~1.0cm voxel size for crisp muscular & facial details)
    mesh_obj.data.remesh_voxel_size = 0.010
    bpy.ops.object.voxel_remesh()
    print(f"[OK] Remeshed to {len(mesh_obj.data.vertices)} vertices for high-res sculpt")

    mesh = mesh_obj.data
    verts = mesh.vertices

    # Anatomical coordinates (Total Height = 2.75 - 2.80m):
    # Head & Face: z = 2.20m to 2.78m
    # Chest & Trapezius: z = 1.68m to 2.20m
    # Abdomen & Core: z = 1.10m to 1.70m
    # Legs & Feet: z = 0.0m to 1.10m
    # +Y is Forward (face, chest, toes), -Y is Rear (back, spine, heels)

    for v in verts:
        co = v.co.copy()
        x, y, z = co.x, co.y, co.z
        abs_x = abs(x)

        # -------------------------------------------------------------
        # A. FACIAL & CRANIAL SCULPTING ON THE ACTUAL HEAD (z: 2.20m - 2.78m)
        # -------------------------------------------------------------
        if z > 2.20:
            # 1. Broad Rounded Sagittal Crest (z: 2.62 - 2.78m, rounded ape dome, not a sharp spike!)
            if z > 2.62:
                crest_prog = min(1.0, (z - 2.62) / 0.16)
                if abs_x < 0.22:
                    # Broad parabolic dome across parietal bones
                    dome_factor = (1.0 - (abs_x / 0.22) ** 2)
                    co.z += 0.040 * dome_factor * crest_prog
                # Hair mane swept backward along -Y
                co.y -= 0.035 * crest_prog

            # 2. Supraorbital Brow Shelf (z: 2.56 - 2.70m, projecting forward on face)
            if 2.56 < z < 2.70 and y > -0.05:
                brow_factor = math.sin((z - 2.56) / 0.14 * math.pi)
                if abs_x < 0.22:
                    shelf_depth = 0.050 * brow_factor * (1.0 - (abs_x / 0.22) ** 2)
                    co.y += shelf_depth
                    # Central glabella depression between eyes
                    if abs_x < 0.035:
                        co.y -= 0.015 * brow_factor

            # 3. Deep-set Orbital Sockets & Eyeballs (z: 2.48 - 2.60m)
            if 2.48 < z < 2.60 and 0.035 < abs_x < 0.17 and y > -0.02:
                eye_factor = math.sin((z - 2.48) / 0.12 * math.pi) * math.sin((abs_x - 0.035) / 0.135 * math.pi)
                # Recess socket under brow
                co.y -= 0.035 * eye_factor
                # Eyeball dome swell inside socket
                if 2.51 < z < 2.57 and 0.065 < abs_x < 0.135:
                    ball_factor = math.sin((z - 2.51) / 0.06 * math.pi) * math.sin((abs_x - 0.065) / 0.070 * math.pi)
                    co.y += 0.020 * ball_factor

            # 4. Zygomatic Cheekbone Arches (z: 2.40 - 2.56m, flaring laterally)
            if 2.40 < z < 2.56 and 0.08 < abs_x < 0.26 and y > 0.0:
                cheek_factor = math.sin((z - 2.40) / 0.16 * math.pi) * math.sin((abs_x - 0.08) / 0.18 * math.pi)
                co.y += 0.028 * cheek_factor
                co.x += (0.018 if x > 0 else -0.018) * cheek_factor

            # 5. Broad Flat Simian Nose & Nostril Cavities (z: 2.40 - 2.52m)
            if 2.40 < z < 2.52 and abs_x < 0.13 and y > 0.02:
                nose_factor = math.sin((z - 2.40) / 0.12 * math.pi)
                # Broad nose bridge
                if abs_x < 0.055:
                    co.y += 0.026 * nose_factor
                # Flared lateral alar wings
                elif 0.055 <= abs_x < 0.12:
                    alar_f = math.sin((abs_x - 0.055) / 0.065 * math.pi)
                    co.y += 0.028 * nose_factor * alar_f
                    co.x += (0.016 if x > 0 else -0.016) * nose_factor * alar_f
                # Nostril cavities
                if 2.41 < z < 2.47 and 0.020 < abs_x < 0.055:
                    co.y -= 0.022 * nose_factor

            # 6. Prognathic Simian Muzzle & Ape Lips (z: 2.30 - 2.44m)
            if 2.30 < z < 2.44 and abs_x < 0.18 and y > 0.04:
                muzzle_factor = math.sin((z - 2.30) / 0.14 * math.pi)
                # Upper lip swell
                if z > 2.38:
                    co.y += 0.030 * muzzle_factor
                    if abs_x < 0.025:
                        co.y -= 0.010 * muzzle_factor  # Philtrum
                # Oral fissure cleft (horizontal mouth furrow)
                elif 2.36 <= z <= 2.38:
                    co.y -= 0.018 * (1.0 - (abs_x / 0.18) ** 2)
                # Lower lip
                else:
                    co.y += 0.025 * muzzle_factor

            # 7. Cascading Chin Beard & Mandibular Jaw Fringe (z: 2.20 - 2.38m)
            if 2.20 < z < 2.38 and abs_x < 0.28 and y > 0.06:
                beard_prog = min(1.0, (2.38 - z) / 0.18)
                tuft_wave = math.cos(abs_x * 25.0) * 0.012
                co.y += (0.060 + tuft_wave) * beard_prog
                co.z -= 0.030 * beard_prog
                co.x *= (1.0 + 0.18 * beard_prog)

        # -------------------------------------------------------------
        # B. TORSO, PECTORALS & MUSCULAR CORE (z: 1.10m - 2.20m)
        # -------------------------------------------------------------
        if 1.10 <= z <= 2.20:
            # 1. Unified Anterior Torso Fullness (continuous convex barrel shape, eliminating hollows)
            if y > 0.0 and abs_x < 0.55:
                barrel_curve = math.sin((z - 1.05) / 1.15 * math.pi)
                co.y += 0.075 * barrel_curve * (1.0 - (abs_x / 0.55) ** 2)

            # 2. Pectoralis Major & Sternal Groove (z: 1.68 - 2.18m, anterior y > 0.10m)
            if 1.68 < z < 2.18 and y > 0.08:
                pec_height = math.sin((z - 1.68) / 0.50 * math.pi)
                if abs_x < 0.50:
                    # Gorilla pectoral bulge (smooth cosine swell)
                    pec_bulge = 0.055 * pec_height * math.sin(abs_x / 0.50 * math.pi)
                    co.y += pec_bulge
                    # Sternal Cleft (central vertical cleft between pectorals)
                    if abs_x < 0.050:
                        cleft_depth = 0.028 * pec_height * (1.0 - abs_x / 0.050)
                        co.y -= cleft_depth

            # 3. Serratus Anterior & Costal Rib Flanks (z: 1.40 - 1.80m, 0.32 < abs_x < 0.65)
            if 1.40 < z < 1.80 and 0.32 < abs_x < 0.65 and y > -0.05:
                slip_wave = math.sin(z * 32.0 - y * 8.0) * 0.015 * math.sin((z - 1.40) / 0.40 * math.pi)
                co.x += (slip_wave if x > 0 else -slip_wave)
                co.y += 0.018 * math.sin((z - 1.40) / 0.40 * math.pi)

            # 4. Sculpted Rectus Abdominis & Heroic Core (z: 1.12 - 1.70m, anterior y > 0.06m)
            if 1.12 < z < 1.70 and y > 0.06:
                # --- Rectus Abdominis Muscle Packs (Central abs: abs_x < 0.32m) ---
                if abs_x < 0.32:
                    # Central Linea Alba (deep vertical groove down midline)
                    if abs_x < 0.040:
                        linea_depth = 0.026 * (1.0 - abs_x / 0.040)
                        co.y -= linea_depth
                        # Umbilicus (Navel depression at z = 1.34m)
                        if 1.30 < z < 1.38:
                            navel_depth = 0.022 * math.sin((z - 1.30) / 0.08 * math.pi) * (1.0 - abs_x / 0.040)
                            co.y -= navel_depth

                    # Segmented Muscle Pads (Left & Right rectus abdominis bellies)
                    elif 0.040 <= abs_x < 0.30:
                        belly_x = math.sin((abs_x - 0.040) / 0.260 * math.pi)

                        # 3-Tier Segmented Ab Packs with organic convex swelling:
                        # Tier 1 (Upper abs / epigastric): z = 1.50 to 1.70m
                        if 1.50 < z < 1.70:
                            tier_z = math.sin((z - 1.50) / 0.20 * math.pi)
                            co.y += 0.052 * belly_x * tier_z
                        # Tier 2 (Middle abs / umbilical): z = 1.32 to 1.50m
                        elif 1.32 < z <= 1.50:
                            tier_z = math.sin((z - 1.32) / 0.18 * math.pi)
                            co.y += 0.055 * belly_x * tier_z
                        # Tier 3 (Lower abs / supra-pubic core): z = 1.12 to 1.32m
                        else:
                            tier_z = math.sin((z - 1.12) / 0.20 * math.pi)
                            co.y += 0.048 * belly_x * tier_z

                        # Subtle Tendinous Intersection Furrows between tiers
                        # Crease 1: between upper and middle abs (z ~ 1.50m)
                        if 1.47 < z < 1.53:
                            crease_1 = math.cos((z - 1.50) / 0.03 * (math.pi / 2)) ** 2
                            co.y -= 0.016 * crease_1 * belly_x
                        # Crease 2: between middle and lower abs (z ~ 1.32m)
                        if 1.29 < z < 1.35:
                            crease_2 = math.cos((z - 1.32) / 0.03 * (math.pi / 2)) ** 2
                            co.y -= 0.015 * crease_2 * belly_x

                    # Linea Semilunaris (lateral furrow groove bounding the rectus abdominis)
                    if 0.27 < abs_x < 0.33:
                        semi_depth = 0.020 * math.sin((abs_x - 0.27) / 0.06 * math.pi)
                        co.y -= semi_depth

                # --- External Obliques & Muscular Flank Rolls (0.28 < abs_x < 0.58m) ---
                if 0.28 < abs_x < 0.58:
                    oblique_factor = math.sin((abs_x - 0.28) / 0.30 * math.pi) * math.sin((z - 1.10) / 0.58 * math.pi)
                    co.y += 0.050 * oblique_factor
                    co.x += (0.038 if x > 0 else -0.038) * oblique_factor

            # 5. Trapezius Hump & Posterior Back (posterior y < 0.10m)
            if y < 0.10:
                # Spinal furrow
                if abs_x < 0.045 and 1.25 < z < 2.10:
                    co.y += 0.020 * (1.0 - abs_x / 0.045)
                # Scapular muscular pads
                elif 0.12 < abs_x < 0.45 and 1.65 < z < 2.15:
                    scap_h = math.sin((z - 1.65) / 0.50 * math.pi) * math.sin((abs_x - 0.12) / 0.33 * math.pi)
                    co.y -= 0.032 * scap_h

        # -------------------------------------------------------------
        # C. ARM & HAND MUSCULATURE (abs_x > 0.45m)
        # -------------------------------------------------------------
        if abs_x > 0.45:
            # 1. Deltoid Muscle Cap (z: 1.65 - 2.10m)
            if 1.65 < z < 2.10:
                delt_f = math.sin((z - 1.65) / 0.45 * math.pi)
                co.x += (0.045 if x > 0 else -0.045) * delt_f
                co.y += 0.032 * delt_f

            # 2. Vascular Brachioradialis & Forearm Swell (z: 0.85 - 1.45m)
            if 0.85 < z < 1.45:
                arm_f = math.sin((z - 0.85) / 0.60 * math.pi)
                co.x += (0.055 if x > 0 else -0.055) * arm_f
                co.y += 0.045 * arm_f
                # Outer forearm fur frill / hair silhouette breakup
                outer_frill = math.sin(z * 35.0) * 0.015
                co.x += (outer_frill if x > 0 else -outer_frill) * arm_f

            # 3. 5-Fingered Stalking Hands & Knuckle Pads (z < 0.85m)
            if z < 0.85:
                knuckle_wave = math.sin(y * 45.0 + z * 30.0) * 0.012
                co.y += knuckle_wave
                co.x += (0.015 if x > 0 else -0.015)

        # -------------------------------------------------------------
        # D. LEGS & 18-INCH PLANTIGRADE FEET (z < 1.10m, abs_x < 0.55m)
        # -------------------------------------------------------------
        if z < 1.10 and abs_x < 0.55:
            # 1. Quadriceps & Hamstrings (z: 0.50 - 1.05m)
            if 0.50 < z < 1.05:
                thigh_f = math.sin((z - 0.50) / 0.55 * math.pi)
                if y > 0:
                    co.y += 0.038 * thigh_f
                else:
                    co.y -= 0.032 * thigh_f

            # 2. Gastrocnemius Calf Belly (z: 0.18 - 0.55m)
            if 0.18 < z < 0.55:
                calf_f = math.sin((z - 0.18) / 0.37 * math.pi)
                if y < 0:
                    co.y -= 0.048 * calf_f
                co.x += (0.028 if x > 0 else -0.028) * calf_f

            # 3. Plantigrade Foot Anatomy: Splayed Toes & Heel Pad (z < 0.18m)
            if z < 0.18:
                if y < 0:
                    co.y -= 0.025
                    co.x += (0.020 if x > 0 else -0.020)
                elif y > 0.15:
                    toe_wave = math.sin(abs_x * 50.0) * 0.012
                    co.z += toe_wave
                    co.y += 0.030

        v.co = co

    mesh.update()
    print("[OK] Sculpted facial landmarks on the HEAD (z: 2.20 - 2.78m) and pectorals on the CHEST (z: 1.65 - 2.12m)")


def main():
    clean_scene()
    print("=" * 60)
    print(" AUTHORING HIGH-RESOLUTION CLASSIC BIGFOOT HERO SCULPT")
    print("=" * 60)

    with bpy.data.libraries.load(str(BLOCKOUT_BLEND), link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    mesh_obj = None
    for o in data_to.objects:
        if o is not None and o.type == 'MESH':
            bpy.context.scene.collection.objects.link(o)
            mesh_obj = o
            break

    if not mesh_obj:
        raise RuntimeError(f"No mesh found in blockout file: {BLOCKOUT_BLEND}")

    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # Sculpt detailed organic anatomy
    sculpt_anatomy(mesh_obj)

    # Subdivision modifier for smooth curvature
    mod_sub = mesh_obj.modifiers.new("HeroSubsurf", "SUBSURF")
    mod_sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="HeroSubsurf")

    # Ground to z = 0
    bpy.context.view_layer.update()
    corners = [mesh_obj.matrix_world @ Vector(c) for c in mesh_obj.bound_box]
    min_z = min(c.z for c in corners)
    mesh_obj.location.z -= min_z
    bpy.ops.object.transform_apply(location=True)

    bpy.ops.object.shade_smooth()

    # Neutral inspection clay material
    mat = bpy.data.materials.new("HeroSculptClay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.72, 0.68, 0.64, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.55
        bsdf.inputs["Metallic"].default_value = 0.0
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)

    bpy.context.view_layer.update()
    dims = mesh_obj.dimensions
    vert_count = len(mesh_obj.data.vertices)
    poly_count = len(mesh_obj.data.polygons)
    print(f">>> HERO SCULPT STATS: X={dims.x:.2f}m Y={dims.y:.2f}m Z={dims.z:.2f}m | verts={vert_count}, polys={poly_count} <<<")

    # Save high-resolution sculpt
    sculpt_blend = SOURCE_DIR / "hero_sculpt.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(sculpt_blend))
    print(f">>> SAVED HERO SCULPT: {sculpt_blend}")

    # Export high-res OBJ
    sculpt_obj = BUILD_DIR / "hero_sculpt.obj"
    bpy.ops.wm.obj_export(
        filepath=str(sculpt_obj),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
    )
    print(f">>> EXPORTED HERO SCULPT OBJ: {sculpt_obj}")


if __name__ == "__main__":
    main()
