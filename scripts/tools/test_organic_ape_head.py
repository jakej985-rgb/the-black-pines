"""
Organic Anatomical Ape Head Deformation for "1. CLASSIC BIGFOOT"
Deforms a subdivided sphere into authentic ape-man cranial and facial anatomy:
- Conical sagittal crest with swept-back hair volume
- Heavy supraorbital brow ridge with glabellar depression
- Deep-set orbital eye sockets
- Flat wide simian nose with flaring nostrils
- Prognathic ape muzzle with closed, stern lips
- Volumetric chin beard and jaw fringe framing a dark leathery face
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


def build_organic_ape_head():
    clean_scene()

    # Create a high-res base sphere: 48 segments, 36 rings
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0.0, 0.0, 0.0), segments=48, ring_count=36)
    head_obj = bpy.context.active_object
    mesh = head_obj.data

    # Anatomical vertex sculpting in Blender space (+Y forward, +Z up, +X right)
    for v in mesh.vertices:
        x, y, z = v.co

        # 1. Conical Sagittal Crest (Gorilla/Bigfoot cranial peak)
        # Taper upper skull into a conical sagittal crest sloping backwards
        if z > 0.05:
            height_factor = (z - 0.05) / 0.23
            # Taper width
            v.co.x *= (1.0 - height_factor * 0.45)
            # Slope back
            v.co.y -= height_factor * 0.08
            # Heighten crest peak
            crest_ridge = math.exp(-((x / 0.08) ** 2))
            v.co.z += height_factor * 0.12 * crest_ridge

        # 2. Prognathic Simian Muzzle (Ape jaw jutting forward)
        # In lower half of face (z < 0.05, y > 0)
        if y > 0.0 and z < 0.05:
            muzzle_mask = math.exp(-((x / 0.18) ** 2) - (((z + 0.12) / 0.16) ** 2))
            v.co.y += 0.14 * muzzle_mask

        # 3. Heavy Supraorbital Torus (Ape Brow Ridge)
        # Across the forehead: z around 0.08 to 0.14, y > 0.15
        if y > 0.10 and -0.02 < z < 0.20:
            brow_mask = math.exp(-((x / 0.24) ** 2) - (((z - 0.09) / 0.05) ** 2))
            # Brow shelf sticks forward
            v.co.y += 0.095 * brow_mask
            # Slight central glabellar dip between left and right brow arches
            arch_shape = 1.0 - 0.25 * math.exp(-((x / 0.04) ** 2))
            v.co.y += 0.03 * brow_mask * arch_shape

        # 4. Deep-set Orbital Eye Sockets
        # Recessed under brow: x around ±0.12, z around 0.03, y > 0.12
        for side in (-1.0, 1.0):
            dist_sq = ((x - side * 0.12) / 0.065) ** 2 + ((z - 0.035) / 0.045) ** 2
            if dist_sq < 3.0 and y > 0.08:
                socket_recess = math.exp(-dist_sq)
                v.co.y -= 0.085 * socket_recess

        # 5. Broad Flat Simian Nose
        # Center of face: x around 0, z around -0.02, y > 0.18
        nose_dist_sq = (x / 0.09) ** 2 + ((z + 0.02) / 0.05) ** 2
        if nose_dist_sq < 3.0 and y > 0.12:
            nose_bulge = math.exp(-nose_dist_sq)
            v.co.y += 0.075 * nose_bulge
            # Nostril wings flare out
            flare_mask = math.exp(-(((abs(x) - 0.065) / 0.035) ** 2) - (((z + 0.04) / 0.03) ** 2))
            v.co.y += 0.045 * flare_mask
            v.co.x += math.copysign(0.025 * flare_mask, x)

        # 6. Stoic Ape Mouth & Closed Lips
        # Closed horizontal mouth cleft at z around -0.14
        mouth_dist_sq = (x / 0.15) ** 2 + ((z + 0.14) / 0.03) ** 2
        if mouth_dist_sq < 3.0 and y > 0.15:
            lip_cleft = math.exp(-mouth_dist_sq)
            # Indent mouth line
            v.co.y -= 0.035 * lip_cleft
        # Upper lip bulge above cleft
        u_lip_sq = (x / 0.13) ** 2 + ((z + 0.10) / 0.025) ** 2
        if u_lip_sq < 3.0 and y > 0.15:
            v.co.y += 0.040 * math.exp(-u_lip_sq)
        # Lower lip bulge below cleft
        l_lip_sq = (x / 0.12) ** 2 + ((z + 0.17) / 0.025) ** 2
        if l_lip_sq < 3.0 and y > 0.15:
            v.co.y += 0.035 * math.exp(-l_lip_sq)

        # 7. Volumetric Chin Beard & Jaw Mass (Matching reference concept!)
        # Jaw and chin: z < -0.15, extending down and forward
        if z < -0.10:
            chin_depth = (-0.10 - z) / 0.18
            beard_mask = math.exp(-((x / 0.18) ** 2))
            # Chin beard extends down and forward
            v.co.z -= chin_depth * 0.12 * beard_mask
            v.co.y += chin_depth * 0.08 * beard_mask

        # 8. Thick Muscular Neck Base (Expanding to meet trapezius)
        if z < -0.05:
            neck_factor = (-0.05 - z) / 0.23
            v.co.x *= (1.0 + neck_factor * 0.40)
            # Neck extends back into trapezius
            if y < 0.0:
                v.co.y -= neck_factor * 0.18

        # 9. Natural Hair Silhouette Waves (Adds organic hair lock variation to back and crest)
        if y < 0.05 or z > 0.10:
            # Flowing hair displacement
            wave1 = math.sin(x * 24.0 + z * 12.0) * 0.008
            wave2 = math.cos(y * 18.0 + z * 16.0) * 0.006
            v.co.x += wave1
            v.co.y += wave2
            v.co.z += wave1 * 0.5

    # Update mesh normals and geometry
    mesh.update()

    # Add Subdivision Surface for silky organic curvature
    mod_sub = head_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    # Add subtle organic smooth
    mod_sm = head_obj.modifiers.new("Smooth", 'SMOOTH')
    mod_sm.factor = 0.35
    mod_sm.iterations = 2
    bpy.ops.object.modifier_apply(modifier="Smooth")

    # Decimate to hit budget (~3,000 polys for head)
    mod_dec = head_obj.modifiers.new("Decimate", 'DECIMATE')
    mod_dec.ratio = 0.45
    bpy.ops.object.modifier_apply(modifier="Decimate")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()

    print(f"[OK] Sculpted Organic Ape Head: {len(mesh.vertices)} verts, {len(mesh.polygons)} polys")

    # PBR Material
    mat_fur = bpy.data.materials.new("ClassicBigfootFur")
    mat_fur.use_nodes = True
    bsdf = mat_fur.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.24, 0.14, 0.08, 1.0) # Warm rich chestnut
    bsdf.inputs["Roughness"].default_value = 0.82
    head_obj.data.materials.append(mat_fur)

    # Realistic Primate Eyes (Dark glossy cornea tucked deep in sockets)
    mat_eye = bpy.data.materials.new("PrimateEye")
    mat_eye.use_nodes = True
    bsdf_e = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_e.inputs["Base Color"].default_value = (0.04, 0.025, 0.018, 1.0)
    bsdf_e.inputs["Roughness"].default_value = 0.02
    bsdf_e.inputs["Metallic"].default_value = 0.05
    # Subtle tapetum retro-reflection
    bsdf_e.inputs["Emission Color"].default_value = (0.95, 0.75, 0.25, 1.0)
    bsdf_e.inputs["Emission Strength"].default_value = 0.20

    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(side * 0.12, 0.155, 0.035), segments=16, ring_count=12)
        eye = bpy.context.active_object
        eye.data.materials.append(mat_eye)

    # Studio Lighting (Sunlight filtered through pines)
    sun = bpy.data.lights.new("Sun", type='SUN')
    sun.energy = 4.2
    sun.color = (1.0, 0.94, 0.85)
    sun_o = bpy.data.objects.new("Sun", sun)
    bpy.context.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(-32), math.radians(22), math.radians(-25))

    fill = bpy.data.lights.new("Fill", type='SUN')
    fill.energy = 1.3
    fill.color = (0.65, 0.78, 0.72)
    fill_o = bpy.data.objects.new("Fill", fill)
    bpy.context.collection.objects.link(fill_o)
    fill_o.rotation_euler = (math.radians(-28), math.radians(-38), math.radians(140))

    rim = bpy.data.lights.new("Rim", type='SUN')
    rim.energy = 3.8
    rim.color = (1.0, 0.82, 0.65)
    rim_o = bpy.data.objects.new("Rim", rim)
    bpy.context.collection.objects.link(rim_o)
    rim_o.rotation_euler = (math.radians(35), math.radians(12), math.radians(165))

    # Camera looking at head 3/4 front angle
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 65.0
    cam_o = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam_o)
    cam_o.location = (0.25, 1.40, 0.04) # Slightly off-center 3/4 perspective

    dir_vec = Vector((0.0, 0.0, -0.02)) - cam_o.location
    cam_o.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_o

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    out_path = PREVIEWS_DIR / "blender_test_organic_ape_head.png"
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered organic ape head to {out_path}")


if __name__ == "__main__":
    build_organic_ape_head()
