"""
Procedural 3D Cryptid Asset Builder for The Black Pines - Iteration 08
Builds the iconic "1. CLASSIC BIGFOOT" (The Forest Giant):
- 8.5 ft (2.6m) massive bipedal relict hominid silhouette
- Coordinate system in Blender: +Y is FORWARD (face/chest/toes), -Y is BACK (spine/hump/heel), +Z is UP
- Exported via OBJ (+Y up, -Z forward) matching Godot Forward+ 100%
- Conical sagittal crest cranium sloping backwards into peak
- Heavy ape brow ridge shelf over deep-set orbital sockets (matching Godot eyes at ±0.13, 0.05, -0.28)
- Broad flat simian nose and stoic ape muzzle with closed natural lips
- Broad barrel chest with flat, powerful muscular pectoral plates
- Massive forearms and broad 5-fingered hands with blunt ape nails
- 18-inch plantigrade feet with mid-tarsal break and 5 broad toes
- Fuses anatomical volumes with voxel remeshing + smoothing for organic musculature

Maintains 100% contract compatibility with:
- scenes/creatures/sasquatch.tscn
- scripts/creatures/sasquatch.gd
- tests/test_sasquatch_ai.gd
"""

import bpy
import bmesh
import math
import random
from pathlib import Path
from mathutils import Vector, Matrix, Euler

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
PREVIEWS_DIR = PROJECT_ROOT / "docs" / "graphics" / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.textures):
        bpy.data.textures.remove(block)
    for block in list(bpy.data.images):
        bpy.data.images.remove(block)


def remesh_and_optimize(obj, voxel_size=0.032, decimate_ratio=0.35, smooth_factor=0.5, smooth_repeat=2):
    """
    Fuses all intersecting mesh volumes into a watertight organic manifold,
    smooths anatomical transitions, projects UVs, and optimizes polycount.
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 1. Voxel remesh to organically weld volumes
    obj.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()

    # 2. Smooth modifier for organic biological muscle & skin flow
    mod_smooth = obj.modifiers.new("AnatomicalSmooth", 'SMOOTH')
    mod_smooth.factor = smooth_factor
    mod_smooth.iterations = smooth_repeat
    bpy.ops.object.modifier_apply(modifier="AnatomicalSmooth")

    # 3. Decimate to hit strict GTX 960 performance budget
    if decimate_ratio < 0.99:
        mod_dec = obj.modifiers.new("BudgetDecimate", 'DECIMATE')
        mod_dec.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier="BudgetDecimate")

    # 4. Smart UV Projection
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.shade_smooth()


# =========================================================================
# 1. CLASSIC BIGFOOT HEAD
# Conical sagittal crest, heavy ape brow, flat wide simian nose, stoic jaw
# Origin at neck articulation (0, 0, 0)
# +Y is FORWARD (face), -Y is BACK (cranium), +Z is UP
# =========================================================================

def build_sasquatch_head_object():
    clean_scene()
    parts = []

    # 1. Cranium core (Ellipsoid dome)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(0.0, -0.04, 0.06), segments=16, ring_count=12)
    s_cranium = bpy.context.active_object
    s_cranium.scale = (0.95, 1.05, 0.95)
    parts.append(s_cranium)

    # Conical Sagittal Crest Peak (Sloping backward into distinctive Bigfoot cone)
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.05, depth=0.30, location=(0.0, -0.06, 0.22))
    cone_crest = bpy.context.active_object
    cone_crest.rotation_euler = (math.radians(16), 0, 0)
    cone_crest.scale = (0.75, 1.15, 1.0)
    parts.append(cone_crest)

    # 2. Continuous Ape Brow Ridge (Supraorbital Torus above eyes)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, 0.20, 0.09), segments=16, ring_count=10)
    brow_mid = bpy.context.active_object
    brow_mid.scale = (2.2, 0.70, 0.50)
    parts.append(brow_mid)

    # 3. Leathery Midface & Cheekbones
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(side * 0.16, 0.14, 0.01), segments=12, ring_count=8)
        cheek = bpy.context.active_object
        cheek.scale = (0.8, 1.0, 0.9)
        parts.append(cheek)

    # 4. Broad Flat Simian Nose (Iconic Bigfoot feature)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.0, 0.26, -0.02), segments=12, ring_count=8)
    nose = bpy.context.active_object
    nose.scale = (1.4, 0.7, 0.7)
    parts.append(nose)

    # Nostril wings
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(side * 0.065, 0.27, -0.04), segments=10, ring_count=8)
        flare = bpy.context.active_object
        flare.scale = (0.9, 0.7, 0.7)
        parts.append(flare)

    # 5. Stoic Ape Muzzle & Natural Closed Lips (No cartoon fangs)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.18, -0.12), segments=16, ring_count=12)
    muzzle = bpy.context.active_object
    muzzle.scale = (1.1, 1.3, 0.85)
    parts.append(muzzle)

    # Upper Lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.0, 0.27, -0.11), segments=12, ring_count=8)
    u_lip = bpy.context.active_object
    u_lip.scale = (1.7, 0.6, 0.45)
    parts.append(u_lip)

    # Lower Lip & Chin
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.0, 0.25, -0.18), segments=12, ring_count=8)
    l_lip = bpy.context.active_object
    l_lip.scale = (1.5, 0.7, 0.55)
    parts.append(l_lip)

    # Heavy Mandible & Chin Beard
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, 0.12, -0.23), segments=14, ring_count=10)
    chin = bpy.context.active_object
    chin.scale = (1.15, 1.25, 0.8)
    parts.append(chin)

    # 6. Muscular Neck Cowl expanding down to merge into torso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.30, location=(0.0, -0.04, -0.14))
    neck = bpy.context.active_object
    neck.rotation_euler = (math.radians(-12), 0, 0)
    neck.scale = (1.2, 1.1, 1.0)
    parts.append(neck)

    # Leathery Ears
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(side * 0.26, -0.02, 0.04), segments=10, ring_count=8)
        ear = bpy.context.active_object
        ear.scale = (0.35, 0.9, 1.2)
        parts.append(ear)

    # Join and fuse into unified organic head mesh
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    head_obj = bpy.context.active_object
    head_obj.name = "SasquatchHead"

    remesh_and_optimize(head_obj, voxel_size=0.022, decimate_ratio=0.45, smooth_factor=0.55, smooth_repeat=2)
    return head_obj


# =========================================================================
# 2. CLASSIC BIGFOOT TORSO
# Massive barrel chest, flat muscular pecs, hunched trapezius, sloping shoulders
# Origin at torso root (0, 0, 0)
# +Y is FORWARD (chest), -Y is BACK (spine/hump), +Z is UP
# =========================================================================

def build_sasquatch_torso_object():
    clean_scene()
    parts = []

    # 1. Main Ribcage & Thorax (Broad barrel chest)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.52, location=(0.0, -0.05, 0.26), segments=18, ring_count=14)
    ribcage = bpy.context.active_object
    ribcage.scale = (1.25, 0.92, 1.15)
    parts.append(ribcage)

    # 2. Abdomen & Waist
    bpy.ops.mesh.primitive_cylinder_add(radius=0.44, depth=0.54, location=(0.0, -0.02, -0.14))
    abdomen = bpy.context.active_object
    abdomen.scale = (1.18, 0.88, 1.0)
    parts.append(abdomen)

    # 3. Massive Trapezius Hump (The iconic neckless slope in back)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(0.0, -0.22, 0.50), segments=16, ring_count=12)
    trap = bpy.context.active_object
    trap.scale = (1.30, 0.85, 0.95)
    parts.append(trap)

    # 4. Upper Trapezius Neck Collar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.30, location=(0.0, -0.06, 0.60))
    neck_cowl = bpy.context.active_object
    neck_cowl.rotation_euler = (math.radians(-14), 0, 0)
    neck_cowl.scale = (1.15, 0.95, 1.0)
    parts.append(neck_cowl)

    # 5. Flat, Broad Muscular Pectorals (Anatomical ape chest slabs - NOT balls!)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_cube_add(size=0.30, location=(side * 0.22, 0.26, 0.30))
        pec = bpy.context.active_object
        pec.rotation_euler = (math.radians(12), math.radians(side * -14), math.radians(side * 5))
        pec.scale = (1.10, 0.45, 0.85)
        parts.append(pec)

    # 6. Latissimus Dorsi & Broad Back Wings
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(side * 0.42, -0.10, 0.18), segments=14, ring_count=10)
        lat = bpy.context.active_object
        lat.scale = (0.80, 0.95, 1.35)
        parts.append(lat)

    # 7. Broad Deltoid Clavicle Bases
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(side * 0.54, -0.04, 0.46), segments=14, ring_count=10)
        delt_base = bpy.context.active_object
        delt_base.scale = (1.10, 0.95, 0.95)
        parts.append(delt_base)

    # Join and fuse into unified organic torso
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    torso_obj = bpy.context.active_object
    torso_obj.name = "SasquatchTorso"

    remesh_and_optimize(torso_obj, voxel_size=0.036, decimate_ratio=0.32, smooth_factor=0.6, smooth_repeat=3)
    return torso_obj


# =========================================================================
# 3. CLASSIC BIGFOOT UPPER ARM
# Heavy deltoid, thick bicep/tricep, hanging fur taper
# Origin at shoulder articulation (0, 0, 0)
# =========================================================================

def build_sasquatch_arm_upper_object():
    clean_scene()
    parts = []

    # Deltoid shoulder head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.0, 0.0, 0.0), segments=16, ring_count=12)
    delt = bpy.context.active_object
    delt.scale = (1.1, 1.0, 1.0)
    parts.append(delt)

    # Upper arm shaft (Bicep / Brachialis)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.55, location=(0.01, 0.01, -0.28))
    arm_shaft = bpy.context.active_object
    arm_shaft.scale = (1.05, 1.15, 1.0)
    parts.append(arm_shaft)

    # Posterior tricep bulge (towards -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.0, -0.06, -0.24), segments=12, ring_count=8)
    tricep = bpy.context.active_object
    tricep.scale = (0.9, 1.0, 1.3)
    parts.append(tricep)

    # Elbow joint
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.0, -0.58), segments=12, ring_count=8)
    elbow = bpy.context.active_object
    parts.append(elbow)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_up = bpy.context.active_object
    arm_up.name = "SasquatchArmUpper"

    remesh_and_optimize(arm_up, voxel_size=0.030, decimate_ratio=0.35, smooth_factor=0.5, smooth_repeat=2)
    return arm_up


# =========================================================================
# 4. CLASSIC BIGFOOT LOWER ARM (FOREARM)
# Thick vascular forearm, long reaching arm proportions
# Origin at elbow articulation (0, 0, 0)
# =========================================================================

def build_sasquatch_arm_lower_object():
    clean_scene()
    parts = []

    # Forearm proximal elbow interface
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.0, 0.0), segments=14, ring_count=10)
    elbow_int = bpy.context.active_object
    parts.append(elbow_int)

    # Muscular Brachioradialis & Forearm belly
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.52, location=(0.01, 0.01, -0.26))
    forearm = bpy.context.active_object
    forearm.scale = (1.05, 1.12, 1.0)
    parts.append(forearm)

    # Shaggy fur taper along ulna (towards -Y and outer side)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.46, location=(0.08, -0.04, -0.28))
    ulna_fur = bpy.context.active_object
    ulna_fur.scale = (0.7, 1.1, 1.0)
    parts.append(ulna_fur)

    # Thick Wrist joint
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0.0, 0.0, -0.54), segments=12, ring_count=8)
    wrist = bpy.context.active_object
    parts.append(wrist)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_low = bpy.context.active_object
    arm_low.name = "SasquatchArmLower"

    remesh_and_optimize(arm_low, voxel_size=0.028, decimate_ratio=0.35, smooth_factor=0.5, smooth_repeat=2)
    return arm_low


# =========================================================================
# 5. CLASSIC BIGFOOT HAND
# Broad leathery ape hand, thick calloused fingers, blunt dark ape nails
# Origin at wrist articulation (0, 0, 0)
# Palm faces forward (+Y), fingers hang down (-Z)
# =========================================================================

def build_sasquatch_hand_object():
    clean_scene()
    parts = []

    # Broad, heavy palm block
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, 0.01, -0.11))
    palm = bpy.context.active_object
    palm.scale = (1.1, 0.55, 1.0)
    parts.append(palm)

    # 5 Thick Ape Fingers
    fingers = [
        (-0.13, 0.04, -0.08,  0.42, 0.14), # Opposable Thumb
        (-0.08, 0.02, -0.22,  0.08, 0.17), # Index
        (-0.01, 0.02, -0.24,  0.00, 0.19), # Middle
        ( 0.06, 0.02, -0.23, -0.08, 0.17), # Ring
        ( 0.12, 0.02, -0.20, -0.15, 0.14)  # Pinky
    ]

    for fx, fy, fz, ang_x, f_len in fingers:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=f_len, location=(fx, fy, fz - f_len * 0.5))
        cyl = bpy.context.active_object
        cyl.rotation_euler = (math.radians(8), math.radians(ang_x * 57.3), 0)
        parts.append(cyl)

        # Fingertip pad
        tip_z = fz - f_len
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, location=(fx + math.sin(ang_x)*0.03, fy + 0.02, tip_z), segments=8, ring_count=6)
        tip = bpy.context.active_object
        parts.append(tip)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    hand_obj = bpy.context.active_object
    hand_obj.name = "SasquatchHand"

    remesh_and_optimize(hand_obj, voxel_size=0.020, decimate_ratio=0.45, smooth_factor=0.5, smooth_repeat=2)
    return hand_obj


# =========================================================================
# 6. CLASSIC BIGFOOT UPPER LEG (THIGH)
# Powerful bowed bipedal femur, heavy quadriceps, thick fur
# Origin at hip articulation (0, 0, 0)
# =========================================================================

def build_sasquatch_leg_upper_object():
    clean_scene()
    parts = []

    # Hip articulation
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(0.0, 0.0, 0.0), segments=14, ring_count=10)
    hip = bpy.context.active_object
    parts.append(hip)

    # Quadriceps & Femur thigh shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.58, location=(0.02, 0.02, -0.28))
    thigh = bpy.context.active_object
    thigh.scale = (1.05, 1.15, 1.0)
    parts.append(thigh)

    # Posterior Hamstring bulge (towards -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0.0, -0.08, -0.26), segments=12, ring_count=8)
    hamstring = bpy.context.active_object
    hamstring.scale = (0.9, 1.0, 1.35)
    parts.append(hamstring)

    # Massive Knee joint
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, 0.0, -0.60), segments=12, ring_count=8)
    knee = bpy.context.active_object
    parts.append(knee)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_up = bpy.context.active_object
    leg_up.name = "SasquatchLegUpper"

    remesh_and_optimize(leg_up, voxel_size=0.034, decimate_ratio=0.35, smooth_factor=0.5, smooth_repeat=2)
    return leg_up


# =========================================================================
# 7. CLASSIC BIGFOOT LOWER LEG (CALF & SHIN)
# Columnar bipedal calf, thick bone structure
# Origin at knee articulation (0, 0, 0)
# =========================================================================

def build_sasquatch_leg_lower_object():
    clean_scene()
    parts = []

    # Knee interface
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, 0.0, 0.0), segments=12, ring_count=8)
    knee_int = bpy.context.active_object
    parts.append(knee_int)

    # Columnar Shin & Tibia
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.50, location=(0.0, -0.01, -0.25))
    shin = bpy.context.active_object
    shin.scale = (1.0, 1.1, 1.0)
    parts.append(shin)

    # Bulging Gastrocnemius (Posterior calf towards -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.0, -0.08, -0.19), segments=12, ring_count=8)
    calf = bpy.context.active_object
    calf.scale = (0.95, 1.05, 1.3)
    parts.append(calf)

    # Ankle malleoli
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, 0.0, -0.50), segments=12, ring_count=8)
    ankle = bpy.context.active_object
    parts.append(ankle)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_low = bpy.context.active_object
    leg_low.name = "SasquatchLegLower"

    remesh_and_optimize(leg_low, voxel_size=0.030, decimate_ratio=0.35, smooth_factor=0.5, smooth_repeat=2)
    return leg_low


# =========================================================================
# 8. CLASSIC BIGFOOT FOOT
# Iconic 18-inch (0.46m) footprint, mid-tarsal break, 5 broad toes
# Origin at ankle articulation (0, 0, 0)
# Toes extend forward (+Y), heel is backward (-Y)
# =========================================================================

def build_sasquatch_foot_object():
    clean_scene()
    parts = []

    # Calcaneus / Heel Pad (towards -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, -0.12, -0.05), segments=12, ring_count=8)
    heel = bpy.context.active_object
    heel.scale = (1.05, 1.15, 0.8)
    parts.append(heel)

    # Mid-tarsal sole bridge
    bpy.ops.mesh.primitive_cube_add(size=0.22, location=(0.0, 0.08, -0.06))
    sole = bpy.context.active_object
    sole.scale = (1.15, 1.45, 0.45)
    parts.append(sole)

    # Metatarsal ball (towards +Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.22, -0.06), segments=12, ring_count=8)
    ball = bpy.context.active_object
    ball.scale = (1.25, 0.85, 0.55)
    parts.append(ball)

    # 5 Splayed broad toes with blunt toenails (pointing +Y)
    toes = [
        (-0.11, 0.31, -0.07, 0.04, 0.11), # Big toe
        (-0.05, 0.33, -0.07, 0.02, 0.12),
        ( 0.01, 0.34, -0.07, 0.00, 0.12),
        ( 0.07, 0.33, -0.07,-0.02, 0.11),
        ( 0.12, 0.31, -0.07,-0.05, 0.09)  # Pinky toe
    ]

    for tx, ty, tz, ang_x, t_len in toes:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=t_len, location=(tx, ty + t_len * 0.5, tz))
        toe_cyl = bpy.context.active_object
        toe_cyl.rotation_euler = (math.radians(8), 0, math.radians(ang_x * 57.3))
        parts.append(toe_cyl)

        # Toe tip
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, location=(tx + math.sin(ang_x)*0.02, ty + t_len, tz), segments=8, ring_count=6)
        toe_tip = bpy.context.active_object
        parts.append(toe_tip)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    foot_obj = bpy.context.active_object
    foot_obj.name = "SasquatchFoot"

    remesh_and_optimize(foot_obj, voxel_size=0.022, decimate_ratio=0.40, smooth_factor=0.5, smooth_repeat=2)
    return foot_obj


# =========================================================================
# 9. CLASSIC BIGFOOT FUR CARDS (Silhouette hair fringe)
# =========================================================================

def build_sasquatch_fur_cards_object():
    clean_scene()
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    random.seed(1967) # 1967: Patterson-Gimlin film year
    card_origins = [
        (0.0, -0.28, 0.58), (0.0, -0.32, 0.44), (0.0, -0.26, 0.30),
        (-0.52, -0.12, 0.52), (-0.60, -0.08, 0.44), (-0.44, -0.16, 0.54),
        ( 0.52, -0.12, 0.52), ( 0.60, -0.08, 0.44), ( 0.44, -0.16, 0.54),
    ]

    for ox, oy, oz in card_origins:
        dx = random.uniform(-0.06, 0.06)
        dy = random.uniform(-0.14, -0.08)
        dz = random.uniform(-0.16, -0.22)
        w = random.uniform(0.12, 0.18)

        v0 = bm.verts.new((ox - w*0.5, oy, oz))
        v1 = bm.verts.new((ox + w*0.5, oy, oz))
        v2 = bm.verts.new((ox + w*0.3 + dx, oy + dy, oz + dz))
        v3 = bm.verts.new((ox - w*0.3 + dx, oy + dy, oz + dz))

        f = bm.faces.new([v0, v1, v2, v3])
        f.material_index = 0
        f.smooth = True
        f.loops[0][uv_layer].uv = Vector((0.0, 0.0))
        f.loops[1][uv_layer].uv = Vector((1.0, 0.0))
        f.loops[2][uv_layer].uv = Vector((1.0, 1.0))
        f.loops[3][uv_layer].uv = Vector((0.0, 1.0))

    mesh = bpy.data.meshes.new("SasquatchFurCards_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("SasquatchFurCards", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def export_obj_from_object(obj, filepath):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Blender +Y -> OBJ -Z (Godot forward)
    # Blender +Z -> OBJ +Y (Godot up)
    bpy.ops.wm.obj_export(
        filepath=str(filepath),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_uv=True,
        export_normals=True,
        export_materials=False,
        apply_modifiers=True
    )
    print(f"[OK] Exported {filepath.name} ({len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys)")


def setup_studio_lighting():
    # Key light: warm sunlight in front (+Y)
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.94, 0.85)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(-38), math.radians(22), math.radians(-35))

    # Fill light: cool misty bounce
    fill_data = bpy.data.lights.new("Fill", type='SUN')
    fill_data.energy = 1.3
    fill_data.color = (0.62, 0.76, 0.70)
    fill_obj = bpy.data.objects.new("Fill", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(-38), math.radians(130))

    # Rim light: auburn hair rim highlight behind (-Y)
    rim_data = bpy.data.lights.new("Rim", type='SUN')
    rim_data.energy = 3.0
    rim_data.color = (1.0, 0.82, 0.65)
    rim_obj = bpy.data.objects.new("Rim", rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(35), math.radians(12), math.radians(168))


def render_studio_camera(output_path, cam_pos, cam_target, lens=45.0, res_x=1024, res_y=768):
    cam_data = bpy.data.cameras.new("StudioCam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("StudioCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    dir_vec = Vector(cam_target) - Vector(cam_pos)
    rot_quat = dir_vec.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.filepath = str(output_path)

    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview to {output_path}")

    bpy.data.objects.remove(cam_obj)
    bpy.data.cameras.remove(cam_data)


def main():
    print("=== BUILDING ORGANIC '1. CLASSIC BIGFOOT' HERO ASSETS IN BLENDER ===")

    # 1. Build and export all 9 components with clean origins for Godot articulation
    obj_head = build_sasquatch_head_object()
    export_obj_from_object(obj_head, MODELS_DIR / "sasquatch_head.obj")

    obj_torso = build_sasquatch_torso_object()
    export_obj_from_object(obj_torso, MODELS_DIR / "sasquatch_torso.obj")

    obj_arm_up = build_sasquatch_arm_upper_object()
    export_obj_from_object(obj_arm_up, MODELS_DIR / "sasquatch_arm_upper.obj")

    obj_arm_low = build_sasquatch_arm_lower_object()
    export_obj_from_object(obj_arm_low, MODELS_DIR / "sasquatch_arm_lower.obj")

    obj_hand = build_sasquatch_hand_object()
    export_obj_from_object(obj_hand, MODELS_DIR / "sasquatch_hand.obj")

    obj_leg_up = build_sasquatch_leg_upper_object()
    export_obj_from_object(obj_leg_up, MODELS_DIR / "sasquatch_leg_upper.obj")

    obj_leg_low = build_sasquatch_leg_lower_object()
    export_obj_from_object(obj_leg_low, MODELS_DIR / "sasquatch_leg_lower.obj")

    obj_foot = build_sasquatch_foot_object()
    export_obj_from_object(obj_foot, MODELS_DIR / "sasquatch_foot.obj")

    obj_fur = build_sasquatch_fur_cards_object()
    export_obj_from_object(obj_fur, MODELS_DIR / "sasquatch_fur_cards.obj")

    # 2. Studio Render Scene in Blender native space
    clean_scene()
    print("=== ASSEMBLING UNIFIED CLASSIC BIGFOOT STUDIO SCENE ===")

    # Setup PBR Chestnut Fur Material
    mat_fur = bpy.data.materials.new("ClassicBigfootFur")
    mat_fur.use_nodes = True
    bsdf = mat_fur.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.24, 0.13, 0.08, 1.0) # Warm chestnut brown
    bsdf.inputs["Roughness"].default_value = 0.84
    bsdf.inputs["Metallic"].default_value = 0.0

    def import_and_place(filepath, loc, rot_offset=(0,0,0), name="Part"):
        bpy.ops.wm.obj_import(filepath=str(filepath))
        obj = bpy.context.selected_objects[0]
        obj.name = name
        obj.location = loc
        # Keep Blender's coordinate conversion and apply pose rotation offset
        obj.rotation_euler.x += rot_offset[0]
        obj.rotation_euler.y += rot_offset[1]
        obj.rotation_euler.z += rot_offset[2]
        obj.data.materials.clear()
        obj.data.materials.append(mat_fur)
        return obj

    parts = []
    t = import_and_place(MODELS_DIR / "sasquatch_torso.obj", (0.0, 0.0, 1.55), name="Torso")
    parts.append(t)

    h = import_and_place(MODELS_DIR / "sasquatch_head.obj", (0.0, 0.08, 2.30), name="Head")
    parts.append(h)

    for side in (-1.0, 1.0):
        au = import_and_place(MODELS_DIR / "sasquatch_arm_upper.obj",
                              (side * 0.62, -0.05, 2.05),
                              rot_offset=(math.radians(-10), 0, math.radians(side * -8)),
                              name=f"ArmUp_{side}")
        parts.append(au)

        al = import_and_place(MODELS_DIR / "sasquatch_arm_lower.obj",
                              (side * 0.62, -0.07, 1.45),
                              rot_offset=(math.radians(-16), 0, math.radians(side * -5)),
                              name=f"ArmLow_{side}")
        parts.append(al)

        hnd = import_and_place(MODELS_DIR / "sasquatch_hand.obj",
                               (side * 0.62, -0.09, 0.89),
                               rot_offset=(math.radians(-12), 0, math.radians(side * -5)),
                               name=f"Hand_{side}")
        parts.append(hnd)

        lu = import_and_place(MODELS_DIR / "sasquatch_leg_upper.obj",
                              (side * 0.35, -0.02, 1.25),
                              rot_offset=(math.radians(6), 0, math.radians(side * 4)),
                              name=f"LegUp_{side}")
        parts.append(lu)

        ll = import_and_place(MODELS_DIR / "sasquatch_leg_lower.obj",
                              (side * 0.35, -0.04, 0.63),
                              rot_offset=(math.radians(-10), 0, 0),
                              name=f"LegLow_{side}")
        parts.append(ll)

        ft = import_and_place(MODELS_DIR / "sasquatch_foot.obj",
                              (side * 0.35, 0.01, 0.11),
                              rot_offset=(0, 0, math.radians(side * -6)),
                              name=f"Foot_{side}")
        parts.append(ft)

    # Eyes
    mat_eye = bpy.data.materials.new("BigfootEye")
    mat_eye.use_nodes = True
    bsdf_eye = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_eye.inputs["Base Color"].default_value = (0.05, 0.03, 0.02, 1.0)
    bsdf_eye.inputs["Roughness"].default_value = 0.04
    bsdf_eye.inputs["Emission Color"].default_value = (0.95, 0.72, 0.22, 1.0)
    bsdf_eye.inputs["Emission Strength"].default_value = 0.35

    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.038, location=(side * 0.13, 0.26, 2.35))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_eye)
        parts.append(eye)

    setup_studio_lighting()

    # 1. Full Body Hero Render (Camera in front at +Y=4.6 looking toward origin)
    render_studio_camera(
        PREVIEWS_DIR / "blender_sasquatch_classic_full.png",
        cam_pos=(0.0, 4.6, 1.45),
        cam_target=(0.0, 0.0, 1.35),
        lens=42.0,
        res_x=1024, res_y=768
    )

    # 2. Bust Close-up Render (Camera at +Y=1.65 looking at head)
    render_studio_camera(
        PREVIEWS_DIR / "blender_sasquatch_classic_bust.png",
        cam_pos=(0.0, 1.65, 2.32),
        cam_target=(0.0, 0.0, 2.25),
        lens=55.0,
        res_x=1024, res_y=768
    )

    print("=== FINISHED BUILDING ORGANIC '1. CLASSIC BIGFOOT' ===")


if __name__ == "__main__":
    main()
