#!/usr/bin/env python3
"""
Test script: High-Fidelity Anatomical Classic Bigfoot Head V2
Builds the authentic ape head from Concept Reference 1:
- Conical sagittal crest with hair flowing backward
- Continuous heavy supraorbital brow ridge shelf
- Deep-set orbital eye cavities with reflective amber eyes
- Broad flat simian nose with nostril flare
- Prognathic ape jaw with stoic closed lips
- Full cascading chin beard framing dark leathery face mask
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PREVIEWS_DIR = PROJECT_ROOT / "docs" / "graphics" / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("HeadCollection")
    bpy.context.scene.collection.children.link(col)
    return col


def make_head_ring(z, cx, cy, rx, ry, brow=0.0, nose=0.0, jaw=0.0, beard=0.0, eyes=0.0, crest=0.0, num_verts=32):
    pts = []
    for i in range(num_verts):
        angle = 2.0 * math.pi * i / num_verts
        ca = math.cos(angle)
        sa = math.sin(angle)
        
        r_x = rx
        r_y = ry
        
        # Sagittal crest (back of head, angle ~ 3pi/2)
        if crest > 0 and sa < 0:
            back_factor = max(0.0, -sa) ** 2.2
            r_y += crest * back_factor
            r_x *= (1.0 - 0.28 * back_factor)
            
        # Heavy ape brow shelf (front of head, angle ~ pi/2)
        if brow > 0 and sa > 0:
            front_factor = max(0.0, sa) ** 1.3
            r_y += brow * front_factor
            # Brow shelf overhang extends laterally across supraorbital ridge
            if abs(ca) < 0.75:
                r_y += brow * 0.35 * (1.0 - abs(ca) / 0.75)
            
        # Deep eye sockets (angle ~ 55 deg and 125 deg)
        if eyes > 0 and sa > 0:
            for socket_ang in [math.pi * 0.36, math.pi * 0.64]:
                diff = abs(angle - socket_ang)
                if diff < 0.32:
                    dent = (1.0 - diff / 0.32) ** 2
                    r_y -= eyes * dent
                    
        # Simian nose (front center, angle ~ pi/2)
        if nose > 0 and sa > 0:
            diff = abs(angle - math.pi * 0.5)
            if diff < 0.38:
                bump = (1.0 - diff / 0.38) ** 1.8
                r_y += nose * bump
                r_x += nose * 0.35 * bump
                
        # Prognathic jaw & cascading beard
        if (jaw > 0 or beard > 0) and sa > 0:
            diff = abs(angle - math.pi * 0.5)
            if diff < 0.65:
                beard_bump = (1.0 - diff / 0.65) ** 1.4
                r_y += (jaw + beard) * beard_bump
                
        x = cx + r_x * ca
        y = cy + r_y * sa
        pts.append(Vector((x, y, z)))
    return pts


def build_head_mesh():
    mesh = bpy.data.meshes.new("ClassicBigfootHead")
    bm = bmesh.new()
    num_verts = 32

    # Cross section specifications from top of crest to neck base
    # (z, cx, cy, rx, ry, brow, nose, jaw, beard, eyes, crest)
    ring_specs = [
        # Top sagittal crest cone apex
        (0.48, 0.00, -0.10, 0.08, 0.12, 0.00, 0.00, 0.00, 0.00, 0.00, 0.08),
        # Upper sagittal crest slope
        (0.42, 0.00, -0.09, 0.14, 0.18, 0.00, 0.00, 0.00, 0.00, 0.00, 0.12),
        # Mid cranium / swept hair vault
        (0.35, 0.00, -0.07, 0.18, 0.22, 0.03, 0.00, 0.00, 0.00, 0.00, 0.14),
        # Lower cranium / supraorbital brow root
        (0.28, 0.00, -0.05, 0.21, 0.23, 0.08, 0.00, 0.00, 0.00, 0.00, 0.12),
        # SUPRAORBITAL BROW RIDGE SHELF (heavy protruding ape brow!)
        (0.22, 0.00, -0.03, 0.22, 0.23, 0.14, 0.02, 0.00, 0.00, 0.00, 0.08),
        # ORBITAL CAVITIES (deeply recessed dark eye sockets!)
        (0.16, 0.00, -0.02, 0.21, 0.22, 0.07, 0.06, 0.00, 0.00, 0.12, 0.05),
        # SIMIAN NOSE & MALAR CHEEKBONES (flat wide gorilla snout)
        (0.10, 0.00, -0.01, 0.22, 0.23, 0.02, 0.12, 0.03, 0.00, 0.05, 0.03),
        # NOSTRIL WINGS & PROGNATHIC UPPER JAW
        (0.04, 0.00,  0.00, 0.21, 0.22, 0.00, 0.10, 0.08, 0.02, 0.00, 0.02),
        # CLOSED STOIC APE LIPS & MOUTH
        (-0.02, 0.00, 0.00, 0.20, 0.21, 0.00, 0.04, 0.10, 0.06, 0.00, 0.02),
        # HEAVY LOWER JAW & CHIN BEARD BASE
        (-0.08, 0.00, -0.02, 0.19, 0.21, 0.00, 0.00, 0.08, 0.12, 0.00, 0.03),
        # CASCADING CHIN BEARD (full flowing beard mass!)
        (-0.15, 0.00, -0.04, 0.17, 0.20, 0.00, 0.00, 0.04, 0.15, 0.00, 0.05),
        # LOWER BEARD FRINGE & SUBMENTAL THROAT
        (-0.22, 0.00, -0.06, 0.15, 0.18, 0.00, 0.00, 0.00, 0.12, 0.00, 0.06),
        # NECK COLLAR / BLENDING PIVOT
        (-0.28, 0.00, -0.06, 0.15, 0.16, 0.00, 0.00, 0.00, 0.00, 0.00, 0.04),
    ]

    bm_rings = []
    for spec in ring_specs:
        z, cx, cy, rx, ry, brow, nose, jaw, beard, eyes, crest = spec
        pts = make_head_ring(z, cx, cy, rx, ry, brow=brow, nose=nose, jaw=jaw, beard=beard, eyes=eyes, crest=crest, num_verts=num_verts)
        bm_ring = [bm.verts.new(p) for p in pts]
        bm_rings.append(bm_ring)

    bm.verts.ensure_lookup_table()

    # Bridge rings into quads
    for r in range(len(bm_rings) - 1):
        ring_a = bm_rings[r]
        ring_b = bm_rings[r + 1]
        for i in range(num_verts):
            i_next = (i + 1) % num_verts
            bm.faces.new((ring_a[i], ring_a[i_next], ring_b[i_next], ring_b[i]))

    # Top cap on crest
    top_ring = bm_rings[0]
    c_top = sum((v.co for v in top_ring), Vector((0, 0, 0))) / num_verts + Vector((0, -0.03, 0.04))
    v_top = bm.verts.new(c_top)
    for i in range(num_verts):
        i_next = (i + 1) % num_verts
        bm.faces.new((top_ring[i_next], top_ring[i], v_top))

    # Bottom cap on neck
    bot_ring = bm_rings[-1]
    c_bot = sum((v.co for v in bot_ring), Vector((0, 0, 0))) / num_verts
    v_bot = bm.verts.new(c_bot)
    for i in range(num_verts):
        i_next = (i + 1) % num_verts
        bm.faces.new((bot_ring[i], bot_ring[i_next], v_bot))

    bm.to_mesh(mesh)
    bm.free()

    head_obj = bpy.data.objects.new("ClassicBigfootHead", mesh)
    bpy.context.collection.objects.link(head_obj)

    # Apply Subdivision modifier for smooth organic curvature
    mod_sub = head_obj.modifiers.new("Subdivision", 'SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1
    bpy.context.view_layer.objects.active = head_obj
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    bpy.ops.object.shade_smooth()

    # Add deep-set eye spheres
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.032, location=(side * 0.082, 0.18, 0.16), segments=16, ring_count=12)
        eye_obj = bpy.context.active_object
        eye_obj.name = f"Eye_{'R' if side < 0 else 'L'}"
        eye_obj.scale = (0.85, 0.85, 0.85)

    return head_obj


def main():
    col = clean_scene()
    print("=" * 60)
    print(" BUILDING HIGH-FIDELITY CLASSIC BIGFOOT APE HEAD V2")
    print("=" * 60)

    head_obj = build_head_mesh()
    print(f"[OK] Built head mesh: {len(head_obj.data.vertices)} vertices, {len(head_obj.data.polygons)} polygons")

    # Add neutral clay material
    mat = bpy.data.materials.new("ClayShader")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.75, 0.70, 0.65, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    head_obj.data.materials.append(mat)

    # Eye shader: glossy dark amber reflective pupil
    eye_mat = bpy.data.materials.new("EyeAmberShader")
    eye_mat.use_nodes = True
    eye_bsdf = eye_mat.node_tree.nodes['Principled BSDF']
    eye_bsdf.inputs['Base Color'].default_value = (0.04, 0.02, 0.01, 1.0)
    eye_bsdf.inputs['Roughness'].default_value = 0.05
    eye_bsdf.inputs['Emission Color'].default_value = (0.95, 0.68, 0.18, 1.0)
    eye_bsdf.inputs['Emission Strength'].default_value = 0.45
    for obj in bpy.context.collection.objects:
        if obj.name.startswith("Eye_"):
            obj.data.materials.append(eye_mat)

    # 3-Point Studio Lighting
    # World
    world = bpy.data.worlds.new("HeadWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    wbsdf = world.node_tree.nodes['Background']
    wbsdf.inputs['Color'].default_value = (0.25, 0.25, 0.25, 1.0)
    wbsdf.inputs['Strength'].default_value = 0.8

    # Key light: Front-right elevated, angled down into brow and face
    bpy.ops.object.light_add(type='SUN', location=(1.5, 2.5, 2.5))
    key = bpy.context.active_object
    key.data.energy = 4.0
    dir_key = Vector((0, 0, 0.12)) - key.location
    key.rotation_euler = dir_key.to_track_quat('-Z', 'Y').to_euler()

    # Fill light: Front-left softer
    bpy.ops.object.light_add(type='SUN', location=(-2.0, 2.0, 1.5))
    fill = bpy.context.active_object
    fill.data.energy = 2.0
    dir_fill = Vector((0, 0, 0.12)) - fill.location
    fill.rotation_euler = dir_fill.to_track_quat('-Z', 'Y').to_euler()

    # Rim light: Behind crest
    bpy.ops.object.light_add(type='SUN', location=(0.0, -2.5, 2.0))
    rim = bpy.context.active_object
    rim.data.energy = 3.0
    dir_rim = Vector((0, 0, 0.25)) - rim.location
    rim.rotation_euler = dir_rim.to_track_quat('-Z', 'Y').to_euler()

    # Camera
    cam_data = bpy.data.cameras.new("BustCam")
    cam_data.lens = 85
    cam_obj = bpy.data.objects.new("BustCam", cam_data)
    col.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Camera looking at head front
    cam_obj.location = Vector((0.0, 1.45, 0.12))
    dir_cam = Vector((0.0, 0.05, 0.12)) - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngine") else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    out_front = PREVIEWS_DIR / "blender_test_anatomical_head_front.png"
    scene.render.filepath = str(out_front)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered bust front -> {out_front}")

    # Camera 3/4 perspective
    cam_obj.location = Vector((-0.85, 1.15, 0.22))
    dir_cam = Vector((0.0, 0.05, 0.12)) - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()

    out_34 = PREVIEWS_DIR / "blender_test_anatomical_head_threequarter.png"
    scene.render.filepath = str(out_34)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered bust 3/4 -> {out_34}")

    # Camera Profile Side
    cam_obj.location = Vector((-1.45, 0.0, 0.12))
    dir_cam = Vector((0.0, 0.0, 0.12)) - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()

    out_side = PREVIEWS_DIR / "blender_test_anatomical_head_side.png"
    scene.render.filepath = str(out_side)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered bust side -> {out_side}")


if __name__ == "__main__":
    main()
