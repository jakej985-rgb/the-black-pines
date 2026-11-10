"""
High-Fidelity "1. CLASSIC BIGFOOT" Sculpted Ape Head Prototype
Builds the authentic ape head from concept 1:
- Conical sagittal crest with flowing swept-back hair mane
- Full beard and jaw hair framing a dark wrinkled simian face
- Continuous heavy ape brow ridge
- Broad flat simian nose with flaring nostrils
- Stoic closed ape lips
- Deep orbital eye sockets with dark intelligent primate eyes
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
PREVIEWS_DIR = PROJECT_ROOT / "docs" / "graphics" / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)


def add_hair_clump(loc, rot, scale, radius=0.08, depth=0.28):
    """Creates a sculpted organic hair lock tapering to a point."""
    bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0.015, depth=depth, location=loc)
    cone = bpy.context.active_object
    cone.rotation_euler = rot
    cone.scale = scale
    return cone


def build_classic_bigfoot_head():
    clean_scene()
    parts = []

    # 1. Base Cranial Dome & Sagittal Cone
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.0, -0.05, 0.08), segments=16, ring_count=12)
    cranium = bpy.context.active_object
    cranium.scale = (0.95, 1.10, 1.0)
    parts.append(cranium)

    # Conical crest peak sloping back
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.04, depth=0.32, location=(0.0, -0.08, 0.24))
    crest = bpy.context.active_object
    crest.rotation_euler = (math.radians(18), 0, 0)
    crest.scale = (0.75, 1.15, 1.0)
    parts.append(crest)

    # 2. Swept-Back Hair Mane (Cascading hair locks along crest and back of head)
    mane_specs = [
        # Center crest ridge locks
        ((0.0, -0.02, 0.38), (math.radians(35), 0, 0), (0.7, 1.1, 1.2), 0.07, 0.30),
        ((0.0, -0.14, 0.32), (math.radians(45), 0, 0), (0.8, 1.1, 1.3), 0.08, 0.32),
        ((0.0, -0.24, 0.22), (math.radians(55), 0, 0), (0.9, 1.1, 1.3), 0.09, 0.35),
        ((0.0, -0.28, 0.08), (math.radians(65), 0, 0), (1.0, 1.1, 1.4), 0.10, 0.38),
        # Flanking crest locks (Left & Right)
        ((-0.10, -0.06, 0.32), (math.radians(30), math.radians(-15), math.radians(-10)), (0.7, 1.0, 1.1), 0.065, 0.28),
        (( 0.10, -0.06, 0.32), (math.radians(30), math.radians( 15), math.radians( 10)), (0.7, 1.0, 1.1), 0.065, 0.28),
        ((-0.15, -0.16, 0.24), (math.radians(40), math.radians(-20), math.radians(-15)), (0.8, 1.0, 1.2), 0.075, 0.30),
        (( 0.15, -0.16, 0.24), (math.radians(40), math.radians( 20), math.radians( 15)), (0.8, 1.0, 1.2), 0.075, 0.30),
        ((-0.18, -0.22, 0.10), (math.radians(50), math.radians(-25), math.radians(-15)), (0.85, 1.0, 1.3), 0.085, 0.34),
        (( 0.18, -0.22, 0.10), (math.radians(50), math.radians( 25), math.radians( 15)), (0.85, 1.0, 1.3), 0.085, 0.34),
        # Temporal hair clumps
        ((-0.22, 0.02, 0.18), (math.radians(20), math.radians(-30), math.radians(-20)), (0.7, 0.9, 1.1), 0.06, 0.25),
        (( 0.22, 0.02, 0.18), (math.radians(20), math.radians( 30), math.radians( 20)), (0.7, 0.9, 1.1), 0.06, 0.25),
    ]

    for loc, rot, scl, rad, dep in mane_specs:
        parts.append(add_hair_clump(loc, rot, scl, radius=rad, depth=dep))

    # 3. Continuous Heavy Ape Brow Ridge (Supraorbital Torus)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.0, 0.21, 0.10), segments=16, ring_count=10)
    brow = bpy.context.active_object
    brow.scale = (2.2, 0.70, 0.50)
    parts.append(brow)

    # Brow overhang crest (accentuates dark shadowed eye sockets)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(side * 0.13, 0.22, 0.11), segments=12, ring_count=8)
        brow_peak = bpy.context.active_object
        brow_peak.scale = (1.2, 0.7, 0.5)
        parts.append(brow_peak)

    # 4. Bare Simian Face Mask (Cheeks, temples, nasal bridge)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(side * 0.16, 0.15, 0.01), segments=12, ring_count=8)
        cheek = bpy.context.active_object
        cheek.scale = (0.85, 0.95, 0.95)
        parts.append(cheek)

    # Flat wide simian nose
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.0, 0.26, -0.02), segments=12, ring_count=8)
    nose = bpy.context.active_object
    nose.scale = (1.45, 0.70, 0.65)
    parts.append(nose)

    # Flaring nostrils
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(side * 0.068, 0.27, -0.04), segments=10, ring_count=8)
        flare = bpy.context.active_object
        flare.scale = (0.9, 0.7, 0.7)
        parts.append(flare)

    # Deep orbital socket recesses (Carve sockets by scaling geometry)
    # 5. Stoic Ape Muzzle & Lips
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.19, -0.12), segments=16, ring_count=12)
    muzzle = bpy.context.active_object
    muzzle.scale = (1.1, 1.25, 0.85)
    parts.append(muzzle)

    # Prominent upper lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.0, 0.28, -0.105), segments=12, ring_count=8)
    u_lip = bpy.context.active_object
    u_lip.scale = (1.75, 0.6, 0.45)
    parts.append(u_lip)

    # Lower lip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(0.0, 0.26, -0.175), segments=12, ring_count=8)
    l_lip = bpy.context.active_object
    l_lip.scale = (1.55, 0.65, 0.50)
    parts.append(l_lip)

    # 6. Heavy Beard & Mandibular Hair (Full ape beard matching reference!)
    beard_specs = [
        # Chin center beard tufts
        ((0.0, 0.21, -0.26), (math.radians(-25), 0, 0), (0.9, 0.9, 1.2), 0.09, 0.32),
        ((0.0, 0.16, -0.34), (math.radians(-35), 0, 0), (0.95, 0.9, 1.3), 0.095, 0.36),
        # Flanking jaw / sideburn beard locks
        ((-0.12, 0.18, -0.24), (math.radians(-20), math.radians(10), math.radians(15)), (0.8, 0.85, 1.1), 0.08, 0.28),
        (( 0.12, 0.18, -0.24), (math.radians(-20), math.radians(-10), math.radians(-15)), (0.8, 0.85, 1.1), 0.08, 0.28),
        ((-0.18, 0.12, -0.20), (math.radians(-15), math.radians(15), math.radians(20)), (0.85, 0.9, 1.2), 0.085, 0.30),
        (( 0.18, 0.12, -0.20), (math.radians(-15), math.radians(-15), math.radians(-20)), (0.85, 0.9, 1.2), 0.085, 0.30),
        # Sideburn hair clumps connecting to temple
        ((-0.24, 0.08, -0.06), (math.radians(10), math.radians(20), math.radians(25)), (0.8, 0.9, 1.1), 0.08, 0.26),
        (( 0.24, 0.08, -0.06), (math.radians(10), math.radians(-20), math.radians(-25)), (0.8, 0.9, 1.1), 0.08, 0.26),
    ]

    for loc, rot, scl, rad, dep in beard_specs:
        parts.append(add_hair_clump(loc, rot, scl, radius=rad, depth=dep))

    # 7. Muscular Neck Cowl expanding down to merge seamlessly into trapezius
    bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.34, location=(0.0, -0.03, -0.16))
    neck = bpy.context.active_object
    neck.rotation_euler = (math.radians(-14), 0, 0)
    neck.scale = (1.2, 1.15, 1.0)
    parts.append(neck)

    # Simian Ears
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(side * 0.27, -0.02, 0.04), segments=10, ring_count=8)
        ear = bpy.context.active_object
        ear.scale = (0.35, 0.9, 1.2)
        parts.append(ear)

    # 8. Organic Voxel Remesh & Polish
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    head_obj = bpy.context.active_object
    head_obj.name = "ClassicBigfootHead_Sculpted"

    # Remesh at high fidelity
    head_obj.data.remesh_voxel_size = 0.018
    bpy.ops.object.voxel_remesh()

    # Biological surface smoothing
    mod_smooth = head_obj.modifiers.new("Smooth", 'SMOOTH')
    mod_smooth.factor = 0.50
    mod_smooth.iterations = 2
    bpy.ops.object.modifier_apply(modifier="Smooth")

    # Decimate to target budget (~3,200 polys for hero head)
    mod_dec = head_obj.modifiers.new("Decimate", 'DECIMATE')
    mod_dec.ratio = 0.35
    bpy.ops.object.modifier_apply(modifier="Decimate")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.shade_smooth()
    print(f"[OK] Sculpted Bigfoot Head: {len(head_obj.data.vertices)} verts, {len(head_obj.data.polygons)} polys")

    # 9. Setup Photorealistic PBR Material
    mat_fur = bpy.data.materials.new("ClassicBigfootFur")
    mat_fur.use_nodes = True
    bsdf = mat_fur.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.22, 0.13, 0.08, 1.0) # Warm rich chestnut
    bsdf.inputs["Roughness"].default_value = 0.85
    head_obj.data.materials.append(mat_fur)

    # Add realistic dark primate eyes inside the orbital sockets (±0.13, 0.21, 0.03)
    mat_eye = bpy.data.materials.new("PrimateEye")
    mat_eye.use_nodes = True
    bsdf_e = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_e.inputs["Base Color"].default_value = (0.04, 0.025, 0.018, 1.0) # Deep dark brown iris
    bsdf_e.inputs["Roughness"].default_value = 0.03 # Wet glossy cornea
    bsdf_e.inputs["Metallic"].default_value = 0.05
    # Subtle tapetum lucidum retro-reflection
    bsdf_e.inputs["Emission Color"].default_value = (0.95, 0.72, 0.22, 1.0)
    bsdf_e.inputs["Emission Strength"].default_value = 0.25

    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(side * 0.13, 0.21, 0.03), segments=12, ring_count=8)
        eye = bpy.context.active_object
        eye.data.materials.append(mat_eye)

    # Studio Lighting (emulating concept 1 sunlight through Pacific Northwest pines)
    sun = bpy.data.lights.new("Sun", type='SUN')
    sun.energy = 4.0
    sun.color = (1.0, 0.94, 0.85)
    sun_o = bpy.data.objects.new("Sun", sun)
    bpy.context.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(-35), math.radians(25), math.radians(-30))

    fill = bpy.data.lights.new("Fill", type='SUN')
    fill.energy = 1.4
    fill.color = (0.6, 0.75, 0.70)
    fill_o = bpy.data.objects.new("Fill", fill)
    bpy.context.collection.objects.link(fill_o)
    fill_o.rotation_euler = (math.radians(-30), math.radians(-40), math.radians(135))

    rim = bpy.data.lights.new("Rim", type='SUN')
    rim.energy = 3.5
    rim.color = (1.0, 0.85, 0.70)
    rim_o = bpy.data.objects.new("Rim", rim)
    bpy.context.collection.objects.link(rim_o)
    rim_o.rotation_euler = (math.radians(35), math.radians(15), math.radians(165))

    # Camera looking directly at the face
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 65.0
    cam_o = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam_o)
    cam_o.location = (0.0, 1.45, 0.06)

    dir_vec = Vector((0.0, 0.0, 0.04)) - cam_o.location
    cam_o.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_o

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    out_path = PREVIEWS_DIR / "blender_test_sculpted_head.png"
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered prototype head to {out_path}")


if __name__ == "__main__":
    build_classic_bigfoot_head()
