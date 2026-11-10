"""
Test script to refine the anatomical modeling of the Classic Bigfoot:
- Separates trapezius into dual lateral masses on the back (Y < 0), unblocking head and throat
- Defines clean simian facial features: heavy brow shelf, deep eye sockets, flat wide ape nose, closed lips, cascading chin beard
- Eliminates snowman-sphere segmentation on limbs with continuous muscular sweeps
- Renders 5 diagnostic clay views (Front, Side, Rear, 3/4, Bust)
"""

import bpy
import math
from pathlib import Path
from mathutils import Vector, Euler

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
QA_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "qa" / "diagnostic_views"
QA_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)


def remesh_part(obj, voxel_size=0.020, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()

    mod_sm = obj.modifiers.new("Smooth", 'SMOOTH')
    mod_sm.factor = smooth_factor
    mod_sm.iterations = smooth_repeat
    bpy.ops.object.modifier_apply(modifier="Smooth")

    if decimate_ratio < 0.99:
        mod_dec = obj.modifiers.new("Decimate", 'DECIMATE')
        mod_dec.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()


def export_obj_part(obj, filepath):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
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


# =========================================================================
# 1. HEAD
# =========================================================================

def build_head():
    parts = []

    # 1. Cranium dome & conical sagittal crest
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.0, -0.04, 0.12), segments=20, ring_count=14)
    cranium = bpy.context.active_object
    cranium.scale = (0.92, 1.15, 1.05)
    parts.append(cranium)

    # Conical sagittal crest (sloping back at 25 degrees)
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.02, depth=0.36, location=(0.0, -0.10, 0.28))
    crest = bpy.context.active_object
    crest.rotation_euler = (math.radians(24), 0, 0)
    crest.scale = (0.75, 1.25, 0.95)
    parts.append(crest)

    # 2. Swept-back hair mane & nape mantle (dorsal hair bulk)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.0, -0.16, 0.20), segments=16, ring_count=10)
    crest_hair = bpy.context.active_object
    crest_hair.rotation_euler = (math.radians(30), 0, 0)
    crest_hair.scale = (1.0, 1.35, 0.85)
    parts.append(crest_hair)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(0.0, -0.18, 0.05), segments=16, ring_count=10)
    nape_hair = bpy.context.active_object
    nape_hair.rotation_euler = (math.radians(35), 0, 0)
    nape_hair.scale = (1.10, 1.25, 0.90)
    parts.append(nape_hair)

    # 3. Continuous Heavy Ape Brow Ridge (Supraorbital Torus)
    # Projects forward over orbits
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0.0, 0.18, 0.10), segments=18, ring_count=10)
    brow = bpy.context.active_object
    brow.scale = (2.3, 0.80, 0.50)
    parts.append(brow)

    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(side * 0.13, 0.19, 0.11), segments=14, ring_count=8)
        arch = bpy.context.active_object
        arch.scale = (1.05, 0.80, 0.55)
        parts.append(arch)

    # 4. Leathery Simian Face Mask & Cheeks
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(side * 0.15, 0.14, 0.02), segments=14, ring_count=8)
        cheek = bpy.context.active_object
        cheek.scale = (0.85, 0.95, 0.90)
        parts.append(cheek)

    # Broad, Flat Simian Nose (Gorilla nose - wide, flat bridge, flared nostrils)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.070, location=(0.0, 0.22, -0.01), segments=14, ring_count=10)
    nose = bpy.context.active_object
    nose.scale = (1.50, 0.65, 0.60)
    parts.append(nose)

    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.042, location=(side * 0.070, 0.23, -0.025), segments=10, ring_count=6)
        flare = bpy.context.active_object
        flare.scale = (0.9, 0.60, 0.60)
        parts.append(flare)

    # 5. Prognathic Simian Muzzle & Stoic Lips (Closed mouth)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.16, -0.09), segments=16, ring_count=10)
    muzzle = bpy.context.active_object
    muzzle.scale = (1.05, 1.20, 0.85)
    parts.append(muzzle)

    # Upper lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(0.0, 0.24, -0.08), segments=12, ring_count=6)
    u_lip = bpy.context.active_object
    u_lip.scale = (1.7, 0.50, 0.35)
    parts.append(u_lip)

    # Lower lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.058, location=(0.0, 0.22, -0.13), segments=12, ring_count=6)
    l_lip = bpy.context.active_object
    l_lip.scale = (1.5, 0.55, 0.40)
    parts.append(l_lip)

    # 6. Ape Chin Beard & Mandibular Fringe (Matching concept 1)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, 0.16, -0.21), segments=14, ring_count=10)
    chin_beard = bpy.context.active_object
    chin_beard.rotation_euler = (math.radians(-25), 0, 0)
    chin_beard.scale = (1.20, 1.15, 1.35)
    parts.append(chin_beard)

    # Tapered beard extension down
    bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.02, depth=0.22, location=(0.0, 0.13, -0.28))
    beard_tip = bpy.context.active_object
    beard_tip.rotation_euler = (math.radians(-30), 0, 0)
    beard_tip.scale = (1.10, 0.75, 1.0)
    parts.append(beard_tip)

    # Flanking jaw fringe
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(side * 0.14, 0.11, -0.16), segments=12, ring_count=8)
        jaw_b = bpy.context.active_object
        jaw_b.rotation_euler = (math.radians(-15), math.radians(side * -10), 0)
        jaw_b.scale = (0.90, 1.05, 1.25)
        parts.append(jaw_b)

        # Sideburns
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(side * 0.21, 0.04, -0.02), segments=12, ring_count=8)
        s_burn = bpy.context.active_object
        s_burn.scale = (0.80, 1.10, 1.20)
        parts.append(s_burn)

        # Ears
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(side * 0.24, -0.04, 0.04), segments=10, ring_count=6)
        ear = bpy.context.active_object
        ear.scale = (0.35, 0.85, 1.15)
        parts.append(ear)

    # 7. Anatomical Neck Base (Slender, plugs into torso, DOES NOT engulf chin)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.24, location=(0.0, -0.04, -0.14))
    neck = bpy.context.active_object
    neck.rotation_euler = (math.radians(-10), 0, 0)
    neck.scale = (1.15, 1.10, 1.0)
    parts.append(neck)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    head_obj = bpy.context.active_object
    head_obj.name = "SasquatchHead"

    # Carve orbital eye sockets
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.050, location=(side * 0.13, 0.16, 0.03), segments=12, ring_count=8)
        cutter = bpy.context.active_object
        cutter.scale = (1.0, 1.3, 0.85)

        mod_bool = head_obj.modifiers.new(f"EyeSocket_{side}", 'BOOLEAN')
        mod_bool.operation = 'DIFFERENCE'
        mod_bool.object = cutter
        bpy.context.view_layer.objects.active = head_obj
        bpy.ops.object.modifier_apply(modifier=mod_bool.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    remesh_part(head_obj, voxel_size=0.018, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return head_obj


# =========================================================================
# 2. TORSO
# =========================================================================

def build_torso():
    parts = []

    # 1. Main Barrel Ribcage & Thorax
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.54, location=(0.0, -0.02, 0.24), segments=22, ring_count=14)
    ribcage = bpy.context.active_object
    ribcage.scale = (1.28, 0.94, 1.15)
    parts.append(ribcage)

    # 2. Dual Lateral Trapezius Muscle Masses (On BACK and SIDES only, Y < 0)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(side * 0.28, -0.16, 0.54), segments=16, ring_count=10)
        trap_lat = bpy.context.active_object
        trap_lat.rotation_euler = (math.radians(-10), math.radians(side * -20), math.radians(side * 12))
        trap_lat.scale = (1.25, 0.85, 0.90)
        parts.append(trap_lat)

        # Clavicular shoulder swell (flanking shoulders)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(side * 0.44, 0.02, 0.48), segments=14, ring_count=8)
        clav_sh = bpy.context.active_object
        clav_sh.scale = (1.10, 0.85, 0.80)
        parts.append(clav_sh)

    # Upper thoracic spine ridge (back center)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.45, location=(0.0, -0.22, 0.44))
    spine_ridge = bpy.context.active_object
    spine_ridge.scale = (0.75, 0.70, 1.0)
    parts.append(spine_ridge)

    # 3. Massive Gorilla Pectorals (Broad, flat chest plates with sternal groove)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(side * 0.26, 0.22, 0.32), segments=18, ring_count=12)
        pec = bpy.context.active_object
        pec.rotation_euler = (math.radians(-12), math.radians(side * 16), 0)
        pec.scale = (1.25, 0.55, 0.80)
        parts.append(pec)

        # Upper pectoral shelf
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(side * 0.24, 0.18, 0.46), segments=14, ring_count=8)
        u_pec = bpy.context.active_object
        u_pec.scale = (1.20, 0.60, 0.65)
        parts.append(u_pec)

    # 4. Abdomen & Serratus Ribs
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.46, location=(0.0, 0.00, -0.08), segments=18, ring_count=12)
    ab = bpy.context.active_object
    ab.scale = (1.15, 0.92, 1.05)
    parts.append(ab)

    for side in (-1.0, 1.0):
        for z_off in (0.12, 0.00, -0.12):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(side * 0.48, 0.05, z_off), segments=10, ring_count=6)
            serr = bpy.context.active_object
            serr.scale = (0.50, 1.20, 0.70)
            parts.append(serr)

    # 5. Latissimus Dorsi & Lower Waist Taper (NO flat bottom cutoff)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(side * 0.32, -0.18, 0.16), segments=16, ring_count=10)
        lat = bpy.context.active_object
        lat.rotation_euler = (math.radians(12), math.radians(side * -10), 0)
        lat.scale = (1.05, 0.80, 1.35)
        parts.append(lat)

    # Lower Pelvis & Waist Taper
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(0.0, -0.01, -0.28), segments=18, ring_count=12)
    pelvis = bpy.context.active_object
    pelvis.scale = (1.10, 0.90, 0.90)
    parts.append(pelvis)

    # Hip articulation spheres
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(side * 0.35, -0.02, -0.34), segments=14, ring_count=8)
        hip = bpy.context.active_object
        parts.append(hip)

    # Shoulder articulation spheres
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(side * 0.62, 0.02, 0.46), segments=16, ring_count=10)
        sh_sc = bpy.context.active_object
        parts.append(sh_sc)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    torso_obj = bpy.context.active_object
    torso_obj.name = "SasquatchTorso"

    remesh_part(torso_obj, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return torso_obj


# =========================================================================
# 3. UPPER ARM
# =========================================================================

def build_arm_upper():
    parts = []

    # Shoulder ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    sh_ball = bpy.context.active_object
    parts.append(sh_ball)

    # Deltoid muscle cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.02, 0.0, -0.08), segments=16, ring_count=10)
    delt = bpy.context.active_object
    delt.scale = (1.15, 1.05, 1.25)
    parts.append(delt)

    # Continuous tapered arm shaft (bicep/tricep)
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.16, depth=0.48, location=(0.0, 0.0, -0.28))
    shaft = bpy.context.active_object
    shaft.scale = (1.05, 1.10, 1.0)
    parts.append(shaft)

    # Bicep swell (anterior)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(-0.02, 0.04, -0.28), segments=14, ring_count=8)
    bicep = bpy.context.active_object
    bicep.scale = (0.9, 1.15, 1.35)
    parts.append(bicep)

    # Tricep swell (posterior)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.02, -0.05, -0.26), segments=14, ring_count=8)
    tricep = bpy.context.active_object
    tricep.scale = (0.95, 1.10, 1.40)
    parts.append(tricep)

    # Elbow ball at Z = -0.60
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, -0.01, -0.60), segments=14, ring_count=8)
    elbow_b = bpy.context.active_object
    parts.append(elbow_b)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_up = bpy.context.active_object
    arm_up.name = "SasquatchArmUpper"
    remesh_part(arm_up, voxel_size=0.020, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return arm_up


# =========================================================================
# 4. LOWER ARM
# =========================================================================

def build_arm_lower():
    parts = []

    # Elbow cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, -0.01, 0.0), segments=16, ring_count=10)
    parts.append(bpy.context.active_object)

    # Brachioradialis / forearm muscle swell below elbow
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21, location=(0.02, 0.03, -0.16), segments=18, ring_count=12)
    forearm_m = bpy.context.active_object
    forearm_m.scale = (1.10, 1.20, 1.35)
    parts.append(forearm_m)

    # Continuous tapered shaft down to wrist
    bpy.ops.mesh.primitive_cone_add(radius1=0.19, radius2=0.13, depth=0.46, location=(0.0, 0.0, -0.26))
    shaft = bpy.context.active_object
    shaft.scale = (1.08, 1.12, 1.0)
    parts.append(shaft)

    # Outer hair fringe (posterior ulna)
    for z_f in (-0.16, -0.26, -0.36):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0.09, -0.07, z_f), segments=10, ring_count=6)
        fringe = bpy.context.active_object
        fringe.scale = (0.7, 1.3, 1.1)
        parts.append(fringe)

    # Wrist joint at Z = -0.56
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.145, location=(0.0, 0.0, -0.56), segments=14, ring_count=8)
    wrist_b = bpy.context.active_object
    wrist_b.scale = (1.15, 0.88, 0.90)
    parts.append(wrist_b)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_low = bpy.context.active_object
    arm_low.name = "SasquatchArmLower"
    remesh_part(arm_low, voxel_size=0.020, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return arm_low


# =========================================================================
# 5. HAND
# =========================================================================

def build_hand():
    parts = []

    # Wrist ball at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, 0.0, 0.0), segments=14, ring_count=8)
    parts.append(bpy.context.active_object)

    # Broad leathery ape palm
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.02, -0.10), segments=16, ring_count=10)
    palm = bpy.context.active_object
    palm.scale = (1.25, 0.60, 1.10)
    parts.append(palm)

    # Knuckle ridge
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, 0.01, -0.16), segments=14, ring_count=8)
    knuckles = bpy.context.active_object
    knuckles.scale = (1.40, 0.60, 0.55)
    parts.append(knuckles)

    # Thumb (Digit 1 - opposable, set low)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.060, location=(-0.15, 0.05, -0.11), segments=10, ring_count=6)
    t1 = bpy.context.active_object
    t1.rotation_euler = (math.radians(-25), math.radians(18), math.radians(30))
    t1.scale = (0.85, 0.85, 1.40)
    parts.append(t1)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.050, location=(-0.19, 0.09, -0.16), segments=10, ring_count=6)
    t2 = bpy.context.active_object
    t2.rotation_euler = (math.radians(-35), math.radians(12), math.radians(20))
    t2.scale = (0.85, 0.85, 1.30)
    parts.append(t2)

    # 4 curved fingers (Digits 2-5)
    finger_specs = [
        (-0.09, 1.00, 32), # Index
        (-0.03, 1.12, 36), # Middle
        (0.04, 1.08, 34),  # Ring
        (0.10, 0.92, 28),  # Pinky
    ]
    for x_pos, len_sc, curl_deg in finger_specs:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(x_pos, 0.03, -0.19), segments=10, ring_count=6)
        ph1 = bpy.context.active_object
        ph1.rotation_euler = (math.radians(curl_deg), 0, 0)
        ph1.scale = (0.95, 0.85, 1.30 * len_sc)
        parts.append(ph1)

        y_m = 0.03 + math.sin(math.radians(curl_deg)) * 0.07
        z_m = -0.19 - math.cos(math.radians(curl_deg)) * 0.07
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.048, location=(x_pos, y_m, z_m), segments=10, ring_count=6)
        ph2 = bpy.context.active_object
        ph2.rotation_euler = (math.radians(curl_deg + 25), 0, 0)
        ph2.scale = (0.90, 0.80, 1.25 * len_sc)
        parts.append(ph2)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    hand_obj = bpy.context.active_object
    hand_obj.name = "SasquatchHand"
    remesh_part(hand_obj, voxel_size=0.016, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return hand_obj


# =========================================================================
# 6. UPPER LEG (Continuous muscular thigh)
# =========================================================================

def build_leg_upper():
    parts = []

    # Femoral hip ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    parts.append(bpy.context.active_object)

    # Continuous tapered quad/hamstring thigh cylinder
    bpy.ops.mesh.primitive_cone_add(radius1=0.23, radius2=0.18, depth=0.54, location=(0.0, 0.01, -0.30))
    thigh_shaft = bpy.context.active_object
    thigh_shaft.scale = (1.08, 1.18, 1.0)
    parts.append(thigh_shaft)

    # Anterior quad belly curve
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21, location=(-0.01, 0.06, -0.26), segments=16, ring_count=10)
    quad_b = bpy.context.active_object
    quad_b.scale = (1.05, 1.15, 1.35)
    parts.append(quad_b)

    # Knee joint condyle at Z = -0.62
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, 0.0, -0.62), segments=16, ring_count=10)
    knee_b = bpy.context.active_object
    knee_b.scale = (1.08, 1.12, 0.90)
    parts.append(knee_b)

    # Patella plate
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0.0, 0.11, -0.60), segments=12, ring_count=6)
    patella = bpy.context.active_object
    patella.scale = (1.1, 0.7, 1.1)
    parts.append(patella)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_up = bpy.context.active_object
    leg_up.name = "SasquatchLegUpper"
    remesh_part(leg_up, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return leg_up


# =========================================================================
# 7. LOWER LEG (Continuous gastrocnemius & Achilles)
# =========================================================================

def build_leg_lower():
    parts = []

    # Knee cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    parts.append(bpy.context.active_object)

    # Continuous tapered calf cone
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.14, depth=0.50, location=(0.0, -0.01, -0.28))
    calf_shaft = bpy.context.active_object
    calf_shaft.scale = (1.06, 1.18, 1.0)
    parts.append(calf_shaft)

    # Posterior calf muscle belly (gastrocnemius)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0.0, -0.06, -0.20), segments=16, ring_count=10)
    calf_b = bpy.context.active_object
    calf_b.scale = (1.10, 1.20, 1.35)
    parts.append(calf_b)

    # Achilles tendon taper into ankle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.24, location=(0.0, -0.06, -0.44))
    achilles = bpy.context.active_object
    achilles.scale = (0.9, 1.15, 1.0)
    parts.append(achilles)

    # Ankle joint at Z = -0.52
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.0, -0.52), segments=14, ring_count=8)
    ankle_b = bpy.context.active_object
    ankle_b.scale = (1.12, 1.02, 0.90)
    parts.append(ankle_b)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_low = bpy.context.active_object
    leg_low.name = "SasquatchLegLower"
    remesh_part(leg_low, voxel_size=0.020, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return leg_low


# =========================================================================
# 8. FOOT (18-inch plantigrade with 5 toes)
# =========================================================================

def build_foot():
    parts = []

    # Ankle cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.0, 0.0), segments=14, ring_count=8)
    parts.append(bpy.context.active_object)

    # Calcaneus heel pad
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, -0.14, -0.07), segments=14, ring_count=8)
    heel = bpy.context.active_object
    heel.scale = (1.15, 1.20, 0.85)
    parts.append(heel)

    # Broad midfoot & ball pad
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.08, -0.08), segments=16, ring_count=10)
    midfoot = bpy.context.active_object
    midfoot.scale = (1.25, 1.40, 0.70)
    parts.append(midfoot)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.22, -0.08), segments=14, ring_count=8)
    ball_pad = bpy.context.active_object
    ball_pad.scale = (1.30, 1.05, 0.65)
    parts.append(ball_pad)

    # Grounded sole plate
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, 0.08, -0.12))
    sole = bpy.context.active_object
    sole.scale = (1.10, 1.85, 0.18)
    parts.append(sole)

    # 5 distinct toes
    toe_specs = [
        (-0.10, 0.32, 0.060, 1.20), # Big toe
        (-0.03, 0.34, 0.052, 1.15),
        (0.03, 0.33, 0.048, 1.10),
        (0.08, 0.31, 0.044, 1.02),
        (0.13, 0.28, 0.040, 0.92),  # Pinky toe
    ]
    for x_t, y_t, r_t, l_sc in toe_specs:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r_t, location=(x_t, y_t, -0.08), segments=10, ring_count=6)
        toe = bpy.context.active_object
        toe.scale = (1.0, l_sc, 0.80)
        parts.append(toe)

    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    foot_obj = bpy.context.active_object
    foot_obj.name = "SasquatchFoot"
    remesh_part(foot_obj, voxel_size=0.018, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return foot_obj


# =========================================================================
# 9. FUR CARDS
# =========================================================================

def build_fur_cards():
    cards = []
    card_transforms = [
        ((0.0, -0.20, 0.70), (math.radians(-25), 0, 0), (0.28, 0.18, 0.22)),
        ((-0.24, -0.16, 0.66), (math.radians(-20), math.radians(20), math.radians(-15)), (0.24, 0.16, 0.20)),
        ((0.24, -0.16, 0.66), (math.radians(-20), math.radians(-20), math.radians(15)), (0.24, 0.16, 0.20)),
        ((-0.46, -0.10, 0.58), (math.radians(-15), math.radians(35), math.radians(-25)), (0.22, 0.15, 0.18)),
        ((0.46, -0.10, 0.58), (math.radians(-15), math.radians(-35), math.radians(25)), (0.22, 0.15, 0.18)),
        ((0.0, -0.10, 0.92), (math.radians(35), 0, 0), (0.16, 0.12, 0.22)),
    ]
    for loc, rot, sc in card_transforms:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
        card = bpy.context.active_object
        card.rotation_euler = rot
        card.scale = sc
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.object.mode_set(mode='OBJECT')
        cards.append(card)

    bpy.context.view_layer.objects.active = cards[0]
    for c in cards:
        c.select_set(True)
    bpy.ops.object.join()
    fur_obj = bpy.context.active_object
    fur_obj.name = "SasquatchFurCards"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    return fur_obj


# =========================================================================
# ASSEMBLE FULL MODEL IN-MEMORY
# =========================================================================

def assemble_and_export_full(part_objs):
    part_specs = [
        ("torso", part_objs["torso"], Vector((0, 0, 0)), Vector((1, 1, 1))),
        ("head", part_objs["head"], Vector((0, 0.10, 0.75)), Vector((1, 1, 1))),
        ("arm_up_l", part_objs["arm_up"], Vector((-0.62, -0.05, 0.50)), Vector((1, 1, 1))),
        ("arm_up_r", part_objs["arm_up"], Vector((0.62, -0.05, 0.50)), Vector((-1, 1, 1))),
        ("arm_low_l", part_objs["arm_low"], Vector((-0.62, -0.07, -0.10)), Vector((1, 1, 1))),
        ("arm_low_r", part_objs["arm_low"], Vector((0.62, -0.07, -0.10)), Vector((-1, 1, 1))),
        ("hand_l", part_objs["hand"], Vector((-0.62, -0.09, -0.66)), Vector((1, 1, 1))),
        ("hand_r", part_objs["hand"], Vector((0.62, -0.09, -0.66)), Vector((-1, 1, 1))),
        ("leg_up_l", part_objs["leg_up"], Vector((-0.35, -0.02, -0.30)), Vector((1, 1, 1))),
        ("leg_up_r", part_objs["leg_up"], Vector((0.35, -0.02, -0.30)), Vector((-1, 1, 1))),
        ("leg_low_l", part_objs["leg_low"], Vector((-0.35, -0.04, -0.92)), Vector((1, 1, 1))),
        ("leg_low_r", part_objs["leg_low"], Vector((0.35, -0.04, -0.92)), Vector((-1, 1, 1))),
        ("foot_l", part_objs["foot"], Vector((-0.35, 0.01, -1.44)), Vector((1, 1, 1))),
        ("foot_r", part_objs["foot"], Vector((0.35, 0.01, -1.44)), Vector((-1, 1, 1))),
    ]
    bpy.ops.object.select_all(action='DESELECT')
    dupes = []
    for name, orig_obj, loc, sc in part_specs:
        dupe = orig_obj.copy()
        dupe.data = orig_obj.data.copy()
        bpy.context.collection.objects.link(dupe)
        dupe.location = loc
        dupe.scale = sc
        dupes.append(dupe)
        dupe.select_set(True)

    bpy.context.view_layer.objects.active = dupes[0]
    bpy.ops.object.join()
    full_obj = bpy.context.active_object
    full_obj.name = "SasquatchFull"
    export_obj_part(full_obj, MODELS_DIR / "sasquatch_full.obj")
    return full_obj


def main():
    clean_scene()
    print("=" * 60)
    print(" ANATOMY PASS: BUILDING REFINED APE SASQUATCH")
    print("=" * 60)

    part_objs = {}

    head = build_head()
    part_objs["head"] = head
    export_obj_part(head, MODELS_DIR / "sasquatch_head.obj")

    torso = build_torso()
    part_objs["torso"] = torso
    export_obj_part(torso, MODELS_DIR / "sasquatch_torso.obj")

    arm_up = build_arm_upper()
    part_objs["arm_up"] = arm_up
    export_obj_part(arm_up, MODELS_DIR / "sasquatch_arm_upper.obj")

    arm_low = build_arm_lower()
    part_objs["arm_low"] = arm_low
    export_obj_part(arm_low, MODELS_DIR / "sasquatch_arm_lower.obj")

    hand = build_hand()
    part_objs["hand"] = hand
    export_obj_part(hand, MODELS_DIR / "sasquatch_hand.obj")

    leg_up = build_leg_upper()
    part_objs["leg_up"] = leg_up
    export_obj_part(leg_up, MODELS_DIR / "sasquatch_leg_upper.obj")

    leg_low = build_leg_lower()
    part_objs["leg_low"] = leg_low
    export_obj_part(leg_low, MODELS_DIR / "sasquatch_leg_lower.obj")

    foot = build_foot()
    part_objs["foot"] = foot
    export_obj_part(foot, MODELS_DIR / "sasquatch_foot.obj")

    fur_cards = build_fur_cards()
    export_obj_part(fur_cards, MODELS_DIR / "sasquatch_fur_cards.obj")

    full = assemble_and_export_full(part_objs)
    print(">>> COMPLETED ANATOMY REFINEMENT & EXPORT <<<")


if __name__ == "__main__":
    main()
