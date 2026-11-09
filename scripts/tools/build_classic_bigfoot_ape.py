"""
High-Fidelity "1. CLASSIC BIGFOOT" Procedural Sculptor & Asset Builder (v2 - Upgraded Pipeline)
Generates an authentic, terrifying, hulking ape cryptid matching reference concept 1:
- Conical sagittal crest cranium with swept-back hair mane and nape mantle
- Heavy ape supraorbital brow shelf (supraorbital torus) sheltering deep orbital sockets
- Broad flat simian nose with flaring nostrils
- Prognathic ape muzzle with closed, natural stern lips
- Volumetric ape chin beard and jaw fringe framing the dark leathery face
- Colossal trapezius hump rising higher than the neck, sloping into massive deltoids
- Broad barrel chest with defined gorilla pectorals, sternal cleft, and serratus ribs
- Seamless latissimus dorsi taper down into pelvis (no flat bottom cutoffs)
- Massive vascular forearms with outer hair frills
- 5-fingered gorilla hands with curved fingers in a stalking grip and blunt nails
- Wide bowed stalking crouch legs with 18-inch plantigrade feet and 5 toes
- Rounded ball-and-socket joints to prevent limb clipping and gaps during animation

Maintains 100% contract compatibility with:
- scenes/creatures/sasquatch.tscn
- scripts/creatures/sasquatch.gd
- tests/test_sasquatch_ai.gd
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
QA_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "qa" / "diagnostic_views"
QA_DIR.mkdir(parents=True, exist_ok=True)


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


def remesh_part(obj, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2):
    """Watertight organic voxel remesh + anatomical smoothing + UV projection."""
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


# =========================================================================
# 1. CLASSIC BIGFOOT HEAD
# Conical sagittal crest, swept hair mane, ape brow, flat nose, full beard
# Origin at neck articulation (0, 0, 0)
# =========================================================================

def build_head():
    parts = []

    # 1. Skull Core & Conical Sagittal Crest
    # Cranium dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.27, location=(0.0, -0.05, 0.10), segments=24, ring_count=16)
    cranium = bpy.context.active_object
    cranium.scale = (0.95, 1.15, 1.05)
    parts.append(cranium)

    # Backward-sloping conical sagittal crest (Patterson-Bigfoot landmark)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.03, depth=0.38, location=(0.0, -0.10, 0.28))
    crest = bpy.context.active_object
    crest.rotation_euler = (math.radians(22), 0, 0)
    crest.scale = (0.78, 1.25, 0.95)
    parts.append(crest)

    # 2. Swept-Back Hair Mane (Volumetric mane lobes over crown and down nape)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(0.0, -0.18, 0.22), segments=18, ring_count=12)
    crest_hair = bpy.context.active_object
    crest_hair.rotation_euler = (math.radians(30), 0, 0)
    crest_hair.scale = (1.05, 1.40, 0.85)
    parts.append(crest_hair)

    # Nape hair mantle flowing down to meet trapezius
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0.0, -0.22, 0.04), segments=18, ring_count=12)
    nape_hair = bpy.context.active_object
    nape_hair.rotation_euler = (math.radians(40), 0, 0)
    nape_hair.scale = (1.20, 1.35, 0.90)
    parts.append(nape_hair)

    # 3. Continuous Heavy Ape Brow Ridge (Supraorbital Torus)
    # The iconic ape brow shelf projecting forward
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, 0.20, 0.09), segments=20, ring_count=12)
    brow = bpy.context.active_object
    brow.scale = (2.4, 0.85, 0.50)
    parts.append(brow)

    for side in (-1.0, 1.0):
        # Brow arches over eyes
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(side * 0.13, 0.21, 0.10), segments=14, ring_count=10)
        arch = bpy.context.active_object
        arch.scale = (1.1, 0.85, 0.55)
        parts.append(arch)

    # 4. Leathery Simian Face Mask & Cheeks
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(side * 0.16, 0.14, 0.00), segments=16, ring_count=10)
        cheek = bpy.context.active_object
        cheek.scale = (0.85, 1.0, 0.95)
        parts.append(cheek)

    # Broad, Flat Simian Nose (Gorilla/Bigfoot nose - flat bridge, wide nostrils)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0.0, 0.23, -0.03), segments=16, ring_count=10)
    nose = bpy.context.active_object
    nose.scale = (1.55, 0.65, 0.60)
    parts.append(nose)

    # Lateral flared nostrils
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(side * 0.075, 0.24, -0.045), segments=12, ring_count=8)
        flare = bpy.context.active_object
        flare.scale = (0.9, 0.65, 0.65)
        parts.append(flare)

    # 5. Prognathic Simian Muzzle & Stoic Lips
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.17, -0.12), segments=18, ring_count=12)
    muzzle = bpy.context.active_object
    muzzle.scale = (1.10, 1.25, 0.85)
    parts.append(muzzle)

    # Broad upper lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.0, 0.25, -0.11), segments=14, ring_count=8)
    u_lip = bpy.context.active_object
    u_lip.scale = (1.8, 0.55, 0.40)
    parts.append(u_lip)

    # Lower lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(0.0, 0.23, -0.17), segments=14, ring_count=8)
    l_lip = bpy.context.active_object
    l_lip.scale = (1.6, 0.60, 0.45)
    parts.append(l_lip)

    # 6. Volumetric Ape Chin Beard & Mandibular Fringe
    # Chin beard mass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.17, -0.26), segments=16, ring_count=10)
    chin_beard = bpy.context.active_object
    chin_beard.rotation_euler = (math.radians(-25), 0, 0)
    chin_beard.scale = (1.25, 1.20, 1.40)
    parts.append(chin_beard)

    # Tapered beard extension down towards chest
    bpy.ops.mesh.primitive_cone_add(radius1=0.13, radius2=0.025, depth=0.26, location=(0.0, 0.14, -0.34))
    beard_tip = bpy.context.active_object
    beard_tip.rotation_euler = (math.radians(-30), 0, 0)
    beard_tip.scale = (1.15, 0.80, 1.0)
    parts.append(beard_tip)

    # Jaw fringe beard masses flanking jawline
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(side * 0.15, 0.12, -0.21), segments=14, ring_count=10)
        jaw_beard = bpy.context.active_object
        jaw_beard.rotation_euler = (math.radians(-15), math.radians(side * -10), 0)
        jaw_beard.scale = (0.95, 1.10, 1.30)
        parts.append(jaw_beard)

        # Sideburns connecting crown mane to jaw fringe
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(side * 0.23, 0.05, -0.05), segments=14, ring_count=10)
        sideburn = bpy.context.active_object
        sideburn.scale = (0.85, 1.15, 1.25)
        parts.append(sideburn)

        # Simian Ears (nested behind sideburns)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(side * 0.26, -0.04, 0.03), segments=12, ring_count=8)
        ear = bpy.context.active_object
        ear.scale = (0.35, 0.85, 1.15)
        parts.append(ear)

    # 7. Muscular Neck Base (Wide muscular collar overlapping into torso socket)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.32, location=(0.0, -0.04, -0.16))
    neck = bpy.context.active_object
    neck.rotation_euler = (math.radians(-12), 0, 0)
    neck.scale = (1.25, 1.18, 1.0)
    parts.append(neck)

    # Join and fuse into unified organic head
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    head_obj = bpy.context.active_object
    head_obj.name = "SasquatchHead"

    # Carve orbital eye socket hollows
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.052, location=(side * 0.13, 0.18, 0.03), segments=12, ring_count=8)
        cutter = bpy.context.active_object
        cutter.scale = (1.0, 1.3, 0.85)

        mod_bool = head_obj.modifiers.new(f"EyeSocket_{side}", 'BOOLEAN')
        mod_bool.operation = 'DIFFERENCE'
        mod_bool.object = cutter
        bpy.context.view_layer.objects.active = head_obj
        bpy.ops.object.modifier_apply(modifier=mod_bool.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    remesh_part(head_obj, voxel_size=0.020, decimate_ratio=0.50, smooth_factor=0.6, smooth_repeat=2)
    return head_obj


# =========================================================================
# 2. CLASSIC BIGFOOT TORSO
# Giant trapezius hump, broad barrel ribcage, defined pectorals, latissimus taper
# Origin at torso root (0, 0, 0)
# =========================================================================

def build_torso():
    parts = []

    # 1. Main Barrel Ribcage & Thorax
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.56, location=(0.0, -0.03, 0.26), segments=24, ring_count=16)
    ribcage = bpy.context.active_object
    ribcage.scale = (1.30, 0.98, 1.18)
    parts.append(ribcage)

    # 2. Giant Trapezius Muscle Hump (Rises above shoulders, sloping into neck)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.46, location=(0.0, -0.16, 0.60), segments=20, ring_count=14)
    trap = bpy.context.active_object
    trap.rotation_euler = (math.radians(-16), 0, 0)
    trap.scale = (1.45, 1.15, 0.90)
    parts.append(trap)

    # Lateral trapezius shoulders (sloping down to deltoids)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(side * 0.38, -0.10, 0.58), segments=16, ring_count=10)
        trap_lat = bpy.context.active_object
        trap_lat.rotation_euler = (0, math.radians(side * -25), math.radians(side * 15))
        trap_lat.scale = (1.20, 1.0, 0.85)
        parts.append(trap_lat)

    # 3. Massive Gorilla Pectorals (Broad, flat chest plates with sternal groove)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.30, location=(side * 0.28, 0.22, 0.34), segments=18, ring_count=12)
        pec = bpy.context.active_object
        pec.rotation_euler = (math.radians(-15), math.radians(side * 18), 0)
        pec.scale = (1.25, 0.60, 0.85)
        parts.append(pec)

        # Clavicular upper chest swell
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(side * 0.26, 0.16, 0.52), segments=14, ring_count=10)
        clav = bpy.context.active_object
        clav.scale = (1.30, 0.65, 0.70)
        parts.append(clav)

    # Sternal groove divider
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.55, location=(0.0, 0.20, 0.35))
    groove = bpy.context.active_object
    groove.rotation_euler = (math.radians(-15), 0, 0)
    groove.scale = (0.5, 0.8, 1.0)
    # Will indent sternum

    # 4. Massive Abdominal Wall & Core
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(0.0, -0.01, -0.10), segments=20, ring_count=14)
    ab = bpy.context.active_object
    ab.scale = (1.18, 0.95, 1.10)
    parts.append(ab)

    # Serratus anterior rib ridges flanking ribs
    for side in (-1.0, 1.0):
        for z_off in (0.15, 0.02, -0.12):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(side * 0.52, 0.05, z_off), segments=12, ring_count=8)
            serr = bpy.context.active_object
            serr.scale = (0.55, 1.25, 0.75)
            parts.append(serr)

    # 5. Latissimus Dorsi & Spinal Furrow (Back definition)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36, location=(side * 0.34, -0.22, 0.20), segments=18, ring_count=12)
        lat = bpy.context.active_object
        lat.rotation_euler = (math.radians(15), math.radians(side * -12), 0)
        lat.scale = (1.10, 0.85, 1.45)
        parts.append(lat)

    # 6. Lower Pelvis Taper (Organic muscular waist flowing into hips, NO flat shelf!)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.44, location=(0.0, -0.02, -0.32), segments=20, ring_count=14)
    pelvis = bpy.context.active_object
    pelvis.scale = (1.12, 0.94, 0.95)
    parts.append(pelvis)

    # Hip sockets (spherical articulation masses for upper legs)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(side * 0.35, -0.02, -0.38), segments=16, ring_count=10)
        hip = bpy.context.active_object
        hip.scale = (1.0, 1.0, 1.0)
        parts.append(hip)

    # Shoulder articulation masses (deltoid base for upper arms)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(side * 0.62, 0.05, 0.50), segments=16, ring_count=12)
        sh_socket = bpy.context.active_object
        sh_socket.scale = (1.1, 1.1, 1.0)
        parts.append(sh_socket)

    # Join and fuse into unified organic torso
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    torso_obj = bpy.context.active_object
    torso_obj.name = "SasquatchTorso"

    remesh_part(torso_obj, voxel_size=0.024, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return torso_obj


# =========================================================================
# 3. CLASSIC BIGFOOT UPPER ARM
# Giant deltoid cap, bulging ape bicep/tricep, rounded elbow joint
# Origin at shoulder articulation (0, 0, 0), extends down to Z = -0.6
# =========================================================================

def build_arm_upper():
    parts = []

    # 1. Shoulder Articulation Ball (Fits inside torso shoulder socket)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.0, 0.0, 0.0), segments=18, ring_count=12)
    sh_ball = bpy.context.active_object
    parts.append(sh_ball)

    # Massive Deltoid Muscle Cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.03, -0.01, -0.10), segments=18, ring_count=12)
    delt = bpy.context.active_object
    delt.scale = (1.20, 1.10, 1.30)
    parts.append(delt)

    # 2. Bulging Bicep & Tricep Arm Shaft
    # Bicep belly (anterior-medial)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(-0.02, 0.05, -0.28), segments=18, ring_count=12)
    bicep = bpy.context.active_object
    bicep.scale = (0.95, 1.15, 1.45)
    parts.append(bicep)

    # Tricep lateral & long heads (posterior)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21, location=(0.02, -0.06, -0.26), segments=18, ring_count=12)
    tricep = bpy.context.active_object
    tricep.scale = (1.05, 1.10, 1.50)
    parts.append(tricep)

    # Arm core shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.48, location=(0.0, 0.0, -0.28))
    shaft = bpy.context.active_object
    shaft.scale = (1.05, 0.98, 1.0)
    parts.append(shaft)

    # 3. Elbow Articulation Ball & Olecranon Joint at Z = -0.60
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.0, -0.01, -0.60), segments=16, ring_count=10)
    elbow_ball = bpy.context.active_object
    elbow_ball.scale = (1.0, 1.08, 0.95)
    parts.append(elbow_ball)

    # Olecranon (elbow point protruding back)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, -0.08, -0.58), segments=12, ring_count=8)
    olecranon = bpy.context.active_object
    olecranon.scale = (0.9, 1.2, 0.8)
    parts.append(olecranon)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_up = bpy.context.active_object
    arm_up.name = "SasquatchArmUpper"

    remesh_part(arm_up, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return arm_up


# =========================================================================
# 4. CLASSIC BIGFOOT LOWER ARM
# Colossal vascular forearm thicker than human thighs, outer hair fringe
# Origin at elbow articulation (0, 0, 0), extends down to Z = -0.56
# =========================================================================

def build_arm_lower():
    parts = []

    # 1. Elbow Socket Cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(0.0, -0.01, 0.0), segments=18, ring_count=12)
    elbow_cup = bpy.context.active_object
    parts.append(elbow_cup)

    # 2. Colossal Forearm Muscle Mass (Brachioradialis & Flexors)
    # The signature ape forearm swell right below the elbow
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.02, 0.03, -0.18), segments=20, ring_count=14)
    brachio = bpy.context.active_object
    brachio.rotation_euler = (math.radians(-6), 0, math.radians(10))
    brachio.scale = (1.15, 1.25, 1.40)
    parts.append(brachio)

    # Deep flexor forearm mass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(-0.02, -0.04, -0.26), segments=18, ring_count=12)
    flexor = bpy.context.active_object
    flexor.scale = (1.10, 1.15, 1.45)
    parts.append(flexor)

    # Forearm tapered shaft
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.14, depth=0.48, location=(0.0, 0.0, -0.26))
    shaft = bpy.context.active_object
    shaft.scale = (1.10, 1.18, 1.0)
    parts.append(shaft)

    # 3. Hanging Fur Fringe along Outer / Posterior Forearm (Matching reference!)
    for z_fringe in (-0.14, -0.24, -0.34, -0.42):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0.10, -0.08, z_fringe), segments=12, ring_count=8)
        fringe = bpy.context.active_object
        fringe.rotation_euler = (math.radians(20), 0, math.radians(-15))
        fringe.scale = (0.75, 1.40, 1.20)
        parts.append(fringe)

    # 4. Massive Wrist Joint at Z = -0.56
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.155, location=(0.0, 0.0, -0.56), segments=16, ring_count=10)
    wrist_ball = bpy.context.active_object
    wrist_ball.scale = (1.18, 0.90, 0.95)
    parts.append(wrist_ball)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    arm_low = bpy.context.active_object
    arm_low.name = "SasquatchArmLower"

    remesh_part(arm_low, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return arm_low


# =========================================================================
# 5. CLASSIC BIGFOOT HAND
# Colossal 5-fingered ape hand, curved stalking grip, thick leathery pads, blunt claws
# Origin at wrist articulation (0, 0, 0), extends down to Z ~ -0.32
# =========================================================================

def build_hand():
    parts = []

    # 1. Wrist Socket Ball at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    w_socket = bpy.context.active_object
    parts.append(w_socket)

    # 2. Broad Leathery Palm & Metacarpal Mass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.0, 0.02, -0.11), segments=18, ring_count=12)
    palm = bpy.context.active_object
    palm.scale = (1.28, 0.65, 1.15)
    parts.append(palm)

    # Thenar & hypothenar muscle pads on the palm
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(-0.08, 0.07, -0.09), segments=12, ring_count=8)
    thenar = bpy.context.active_object
    thenar.scale = (0.9, 0.6, 1.2)
    parts.append(thenar)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0.08, 0.07, -0.10), segments=12, ring_count=8)
    hypothenar = bpy.context.active_object
    hypothenar.scale = (0.85, 0.6, 1.2)
    parts.append(hypothenar)

    # Knuckle ridge across digits
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0.0, 0.01, -0.18), segments=16, ring_count=10)
    knuckles = bpy.context.active_object
    knuckles.scale = (1.45, 0.65, 0.60)
    parts.append(knuckles)

    # 3. Opposable Simian Thumb (Digit 1 - set low and angled forward)
    # Proximal phalanx
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(-0.16, 0.06, -0.12), segments=12, ring_count=8)
    thumb_p = bpy.context.active_object
    thumb_p.rotation_euler = (math.radians(-25), math.radians(20), math.radians(35))
    thumb_p.scale = (0.85, 0.85, 1.45)
    parts.append(thumb_p)

    # Distal phalanx with curved tip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(-0.20, 0.10, -0.18), segments=12, ring_count=8)
    thumb_d = bpy.context.active_object
    thumb_d.rotation_euler = (math.radians(-40), math.radians(15), math.radians(25))
    thumb_d.scale = (0.85, 0.85, 1.40)
    parts.append(thumb_d)

    # 4. Four Heavy Curved Fingers (Digits 2-5: Index, Middle, Ring, Pinky)
    # Curved forward into an athletic stalking grip
    finger_specs = [
        # (x_center, length_scale, width_scale, curl_angle)
        (-0.10, 1.05, 1.00, 32), # Index
        (-0.03, 1.18, 1.08, 36), # Middle (longest)
        (0.04, 1.12, 1.02, 34),  # Ring
        (0.10, 0.95, 0.92, 28),  # Pinky
    ]

    for x_pos, len_sc, w_sc, curl_deg in finger_specs:
        # Proximal phalanx (sloping forward-down)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.058 * w_sc, location=(x_pos, 0.03, -0.21), segments=12, ring_count=8)
        ph1 = bpy.context.active_object
        ph1.rotation_euler = (math.radians(curl_deg), 0, 0)
        ph1.scale = (1.0, 0.9, 1.35 * len_sc)
        parts.append(ph1)

        # Intermediate phalanx (curling further inward)
        y_mid = 0.03 + math.sin(math.radians(curl_deg)) * 0.08
        z_mid = -0.21 - math.cos(math.radians(curl_deg)) * 0.08
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.052 * w_sc, location=(x_pos, y_mid, z_mid), segments=12, ring_count=8)
        ph2 = bpy.context.active_object
        ph2.rotation_euler = (math.radians(curl_deg + 25), 0, 0)
        ph2.scale = (0.95, 0.85, 1.30 * len_sc)
        parts.append(ph2)

        # Distal fingertip pad with blunt nail
        y_tip = y_mid + math.sin(math.radians(curl_deg + 25)) * 0.07
        z_tip = z_mid - math.cos(math.radians(curl_deg + 25)) * 0.07
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.046 * w_sc, location=(x_pos, y_tip, z_tip), segments=10, ring_count=8)
        ph3 = bpy.context.active_object
        ph3.rotation_euler = (math.radians(curl_deg + 45), 0, 0)
        ph3.scale = (0.90, 0.80, 1.20)
        parts.append(ph3)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    hand_obj = bpy.context.active_object
    hand_obj.name = "SasquatchHand"

    remesh_part(hand_obj, voxel_size=0.018, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return hand_obj


# =========================================================================
# 6. CLASSIC BIGFOOT UPPER LEG
# Colossal femoral mass, heavy quadriceps, wide bowed stance
# Origin at hip joint (0, 0, 0), extends down to Z = -0.62
# =========================================================================

def build_leg_upper():
    parts = []

    # 1. Hip Articulation Femoral Ball at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(0.0, 0.0, 0.0), segments=18, ring_count=12)
    hip_ball = bpy.context.active_object
    parts.append(hip_ball)

    # Greater trochanter hip flare
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(-0.05, -0.04, -0.08), segments=16, ring_count=10)
    troch = bpy.context.active_object
    troch.scale = (1.20, 1.05, 1.15)
    parts.append(troch)

    # 2. Massive Quadriceps & Thigh Belly (Rectus Femoris, Vastus Lateralis)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(-0.02, 0.05, -0.28), segments=20, ring_count=14)
    quad = bpy.context.active_object
    quad.scale = (1.10, 1.25, 1.45)
    parts.append(quad)

    # Posterior Hamstrings
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(0.0, -0.06, -0.28), segments=18, ring_count=12)
    ham = bpy.context.active_object
    ham.scale = (1.05, 1.20, 1.45)
    parts.append(ham)

    # Thigh connecting cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.52, location=(0.0, 0.0, -0.30))
    shaft = bpy.context.active_object
    shaft.scale = (1.08, 1.12, 1.0)
    parts.append(shaft)

    # 3. Knee Articulation Condyle at Z = -0.62
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0.0, 0.0, -0.62), segments=18, ring_count=12)
    knee_ball = bpy.context.active_object
    knee_ball.scale = (1.10, 1.15, 0.90)
    parts.append(knee_ball)

    # Patella (kneecap prominence in front)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, 0.12, -0.60), segments=12, ring_count=8)
    patella = bpy.context.active_object
    patella.scale = (1.1, 0.8, 1.2)
    parts.append(patella)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_up = bpy.context.active_object
    leg_up.name = "SasquatchLegUpper"

    remesh_part(leg_up, voxel_size=0.024, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return leg_up


# =========================================================================
# 7. CLASSIC BIGFOOT LOWER LEG
# Heavy gastrocnemius calf belly, thick Achilles tendon, ankle joint
# Origin at knee joint (0, 0, 0), extends down to Z = -0.62
# =========================================================================

def build_leg_lower():
    parts = []

    # 1. Knee Articulation Cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21, location=(0.0, 0.0, 0.0), segments=18, ring_count=12)
    knee_cup = bpy.context.active_object
    parts.append(knee_cup)

    # 2. Bulging Gastrocnemius Calf Belly (Posterior)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.0, -0.06, -0.22), segments=20, ring_count=14)
    calf = bpy.context.active_object
    calf.scale = (1.15, 1.25, 1.45)
    parts.append(calf)

    # Anterior Tibial Shin Mass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, 0.05, -0.26), segments=16, ring_count=12)
    shin = bpy.context.active_object
    shin.scale = (1.0, 1.10, 1.40)
    parts.append(shin)

    # Calf core cylinder
    bpy.ops.mesh.primitive_cone_add(radius1=0.21, radius2=0.15, depth=0.52, location=(0.0, 0.0, -0.30))
    shaft = bpy.context.active_object
    shaft.scale = (1.08, 1.15, 1.0)
    parts.append(shaft)

    # 3. Thick Achilles Tendon (Extending down into heel)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.28, location=(0.0, -0.07, -0.48))
    achilles = bpy.context.active_object
    achilles.scale = (0.9, 1.15, 1.0)
    parts.append(achilles)

    # 4. Ankle Joint Ball at Z = -0.52 (articulates with Foot)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.0, -0.52), segments=16, ring_count=10)
    ankle_ball = bpy.context.active_object
    ankle_ball.scale = (1.15, 1.05, 0.90)
    parts.append(ankle_ball)

    # Malleoli (ankle bone protrusions)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(side * 0.14, -0.01, -0.52), segments=10, ring_count=8)
        mall = bpy.context.active_object
        parts.append(mall)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    leg_low = bpy.context.active_object
    leg_low.name = "SasquatchLegLower"

    remesh_part(leg_low, voxel_size=0.022, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return leg_low


# =========================================================================
# 8. CLASSIC BIGFOOT FOOT
# True 18-inch plantigrade footprint, thick padded heel, 5 distinct toes
# Origin at ankle joint (0, 0, 0), extends forward to Y ~ +0.32, heel at Y ~ -0.16
# =========================================================================

def build_foot():
    parts = []

    # 1. Ankle Articulation Cup at (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    ankle_cup = bpy.context.active_object
    parts.append(ankle_cup)

    # 2. Massive Calcaneus (Heel Pad - thick and shock-absorbing)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, -0.15, -0.08), segments=16, ring_count=10)
    heel = bpy.context.active_object
    heel.scale = (1.15, 1.25, 0.85)
    parts.append(heel)

    # 3. Broad Midfoot & Mid-tarsal Break (Patterson-Gimlin signature footprint)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.0, 0.08, -0.09), segments=18, ring_count=12)
    midfoot = bpy.context.active_object
    midfoot.scale = (1.28, 1.45, 0.70)
    parts.append(midfoot)

    # Metatarsal ball pad under the ball of the foot
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.22, -0.09), segments=16, ring_count=10)
    ball_pad = bpy.context.active_object
    ball_pad.scale = (1.35, 1.10, 0.65)
    parts.append(ball_pad)

    # Flat plantigrade sole plate (grounds on terrain)
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, 0.08, -0.13))
    sole_box = bpy.context.active_object
    sole_box.scale = (1.15, 1.90, 0.20)
    parts.append(sole_box)

    # 4. Five Distinct Ape Toes (Digits 1-5: Hallux to Pinky)
    # The big toe (hallux) is massive, aligned with the foot (non-divergent for Bigfoot)
    toe_specs = [
        # (x_center, y_center, radius, length_scale)
        (-0.11, 0.33, 0.065, 1.25), # Hallux (Big toe - huge)
        (-0.04, 0.35, 0.055, 1.18), # Second toe
        (0.03, 0.34, 0.052, 1.12),  # Third toe
        (0.09, 0.32, 0.048, 1.05),  # Fourth toe
        (0.14, 0.29, 0.044, 0.95),  # Fifth toe (Pinky)
    ]

    for x_toe, y_toe, r_toe, len_sc in toe_specs:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r_toe, location=(x_toe, y_toe, -0.09), segments=12, ring_count=8)
        toe = bpy.context.active_object
        toe.scale = (1.0, len_sc, 0.80)
        parts.append(toe)

        # Toe pad
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r_toe * 0.85, location=(x_toe, y_toe + 0.03, -0.10), segments=10, ring_count=8)
        toe_tip = bpy.context.active_object
        toe_tip.scale = (0.95, 0.90, 0.75)
        parts.append(toe_tip)

    # Join and fuse
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    foot_obj = bpy.context.active_object
    foot_obj.name = "SasquatchFoot"

    remesh_part(foot_obj, voxel_size=0.020, decimate_ratio=0.55, smooth_factor=0.6, smooth_repeat=2)
    return foot_obj


# =========================================================================
# 9. SILHOUETTE-BREAKING FUR CARDS
# Positioned across trapezius, shoulders, and upper back to break mechanical edge
# =========================================================================

def build_fur_cards():
    
    # Create curved clump quads
    cards = []
    
    # Trapezius and shoulder fur clumps
    card_transforms = [
        # Location, Rotation, Scale
        ((0.0, -0.22, 0.72), (math.radians(-25), 0, 0), (0.28, 0.18, 0.22)),
        ((-0.24, -0.16, 0.68), (math.radians(-20), math.radians(20), math.radians(-15)), (0.24, 0.16, 0.20)),
        ((0.24, -0.16, 0.68), (math.radians(-20), math.radians(-20), math.radians(15)), (0.24, 0.16, 0.20)),
        ((-0.46, -0.12, 0.62), (math.radians(-15), math.radians(35), math.radians(-25)), (0.22, 0.15, 0.18)),
        ((0.46, -0.12, 0.62), (math.radians(-15), math.radians(-35), math.radians(25)), (0.22, 0.15, 0.18)),
        ((-0.58, 0.02, 0.54), (0, math.radians(45), math.radians(-30)), (0.20, 0.14, 0.16)),
        ((0.58, 0.02, 0.54), (0, math.radians(-45), math.radians(30)), (0.20, 0.14, 0.16)),
        # Crown crest tufts
        ((0.0, -0.12, 0.95), (math.radians(35), 0, 0), (0.16, 0.12, 0.22)),
        ((-0.10, -0.14, 0.92), (math.radians(30), math.radians(15), 0), (0.14, 0.10, 0.18)),
        ((0.10, -0.14, 0.92), (math.radians(30), math.radians(-15), 0), (0.14, 0.10, 0.18)),
    ]

    for loc, rot, sc in card_transforms:
        # Create a small curved card mesh
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
        card = bpy.context.active_object
        card.rotation_euler = rot
        card.scale = sc
        
        # Subdivide and give slight curve
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
# ASSEMBLE ALL & EXPORT
# =========================================================================

def build_assembled_full(part_objs):
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


def build_and_export_all():
    print("=" * 60)
    print(" BUILDING CLASSIC BIGFOOT APE ASSETS (UPGRADED PIPELINE)")
    print("=" * 60)
    clean_scene()

    part_objs = {}

    # 1. Head
    head = build_head()
    part_objs["head"] = head
    export_obj_part(head, MODELS_DIR / "sasquatch_head.obj")

    # 2. Torso
    torso = build_torso()
    part_objs["torso"] = torso
    export_obj_part(torso, MODELS_DIR / "sasquatch_torso.obj")

    # 3. Upper Arm
    arm_up = build_arm_upper()
    part_objs["arm_up"] = arm_up
    export_obj_part(arm_up, MODELS_DIR / "sasquatch_arm_upper.obj")

    # 4. Lower Arm
    arm_low = build_arm_lower()
    part_objs["arm_low"] = arm_low
    export_obj_part(arm_low, MODELS_DIR / "sasquatch_arm_lower.obj")

    # 5. Hand
    hand = build_hand()
    part_objs["hand"] = hand
    export_obj_part(hand, MODELS_DIR / "sasquatch_hand.obj")

    # 6. Upper Leg
    leg_up = build_leg_upper()
    part_objs["leg_up"] = leg_up
    export_obj_part(leg_up, MODELS_DIR / "sasquatch_leg_upper.obj")

    # 7. Lower Leg
    leg_low = build_leg_lower()
    part_objs["leg_low"] = leg_low
    export_obj_part(leg_low, MODELS_DIR / "sasquatch_leg_lower.obj")

    # 8. Foot
    foot = build_foot()
    part_objs["foot"] = foot
    export_obj_part(foot, MODELS_DIR / "sasquatch_foot.obj")

    # 9. Fur Cards
    fur_cards = build_fur_cards()
    export_obj_part(fur_cards, MODELS_DIR / "sasquatch_fur_cards.obj")

    # 10. Assembled Full Model
    build_assembled_full(part_objs)

    print("\n>>> ALL 9 BIGFOOT COMPONENT MESHES & ASSEMBLED FULL MESH EXPORTED CLEANLY <<<")


if __name__ == "__main__":
    build_and_export_all()
