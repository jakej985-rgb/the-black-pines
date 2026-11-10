#!/usr/bin/env python3
"""
Procedural Photorealistic Fallen Nurse Log Generator for Blender 4.2 LTS.
Architecture:
- Trunk: 6.4m weathered fallen timber along X axis with organic sag, taper, and cross-section irregularity.
- Base: Flared root break with splintered heartwood fibers and partial decay cavity.
- Crown: Shattered fracture with jagged snap fibers.
- Branch Stubs: 2 sheared lateral limbs.
- Materials: Poly Haven moss_wood (exterior weathered mossy bark) + fine_grained_wood (interior core wood).
- Target GPU: NVIDIA GeForce GTX 960 (~1,600 triangles).
"""

import math
import random
import sys
from pathlib import Path

try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
except ImportError:
    print("Execute via 'blender --background --python <script>'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def create_fallen_log():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    random.seed(42)

    rings = 24
    radial_segs = 16
    length = 6.4
    x_min = -3.2
    x_max = 3.2

    # Pre-calculate ring positions along X with slight organic waver in Y and Z
    ring_positions = []
    for i in range(rings):
        t = i / (rings - 1)
        x = x_min + t * length
        # Natural trunk waver and slight ground sag in center
        waver_y = math.sin(t * math.pi) * 0.12 + math.sin(t * 3.0 * math.pi) * 0.04
        # Radius tapers from base (0.44m) to snapped tip (0.28m)
        r_base = 0.44 * math.pow(1.0 - t * 0.45, 0.8)
        # Center Z rests on ground: axis height = r_base + slight offset
        z = r_base * 0.92 - math.sin(t * math.pi) * 0.04
        ring_positions.append((x, waver_y, z, r_base, t))

    ring_verts = []

    # Generate rings
    for ring_idx, (x, cy, cz, r, t) in enumerate(ring_positions):
        current_ring = []

        for s in range(radial_segs):
            angle = (s / radial_segs) * 2.0 * math.pi

            # Non-circular organic profile (wider horizontally, flatter on bottom where it hits dirt)
            rx = r * (1.0 + 0.10 * math.cos(2.0 * angle))
            rz = r * (0.92 + 0.08 * math.sin(angle))

            # Bottom flattening against terrain
            local_z = math.sin(angle) * rz
            if local_z < -r * 0.7:
                local_z = -r * 0.7 + (local_z + r * 0.7) * 0.3

            local_y = math.cos(angle) * rx

            # Flared root buttresses at base end (t < 0.20)
            if t < 0.20:
                flare_weight = (1.0 - t / 0.20)
                # 3 root lobes
                root_flair = 0.20 * math.pow(max(0.0, math.cos(3.0 * angle + 0.4)), 2.5) * flare_weight
                local_y += math.cos(angle) * root_flair
                local_z += math.sin(angle) * root_flair

            # Surface bark ridges and organic noise
            noise = (math.sin(angle * 5.0 + t * 8.0) * 0.016 +
                     math.cos(angle * 3.0 - t * 12.0) * 0.012)
            local_y += noise
            local_z += noise

            vx = x
            vy = cy + local_y
            vz = max(0.02, cz + local_z)

            v = bm.verts.new(Vector((vx, vy, vz)))
            current_ring.append(v)

        ring_verts.append(current_ring)

    # Connect rings with quads and precise seamless UV coordinates
    for i in range(rings - 1):
        r1 = ring_verts[i]
        r2 = ring_verts[i + 1]
        v0_coord = (i / (rings - 1)) * 4.5
        v1_coord = ((i + 1) / (rings - 1)) * 4.5

        for s in range(radial_segs):
            s_next = (s + 1) % radial_segs
            u0 = s / radial_segs
            u1 = (s + 1) / radial_segs

            f = bm.faces.new((r1[s], r2[s], r2[s_next], r1[s_next]))
            f.material_index = 0
            f.smooth = True

            # In moss_wood, grain is along Y, so V is log length, U is circumference
            f.loops[0][uv_layer].uv = (u0, v0_coord)
            f.loops[1][uv_layer].uv = (u0, v1_coord)
            f.loops[2][uv_layer].uv = (u1, v1_coord)
            f.loops[3][uv_layer].uv = (u1, v0_coord)

    # 1. Base Cap: Hollowed splintered cavity
    base_center_y = ring_positions[0][1]
    base_center_z = ring_positions[0][2]

    # Inner cavity ring recessed inward (+X)
    cavity_depth = 0.50
    cavity_r = ring_positions[0][3] * 0.55
    cavity_verts = []
    for s in range(radial_segs):
        angle = (s / radial_segs) * 2.0 * math.pi
        cvx = x_min + cavity_depth + random.uniform(-0.06, 0.06)
        cvy = base_center_y + math.cos(angle) * cavity_r
        cvz = max(0.08, base_center_z + math.sin(angle) * cavity_r)
        v = bm.verts.new(Vector((cvx, cvy, cvz)))
        cavity_verts.append(v)

    # Cavity back center point
    cavity_back = bm.verts.new(Vector((x_min + cavity_depth + 0.25, base_center_y, base_center_z)))
    for s in range(radial_segs):
        s_next = (s + 1) % radial_segs
        f = bm.faces.new((cavity_back, cavity_verts[s_next], cavity_verts[s]))
        f.material_index = 1
        f.smooth = True
        f.loops[0][uv_layer].uv = (0.5, 0.5)
        f.loops[1][uv_layer].uv = (0.5 + math.cos((s + 1) / radial_segs * 2 * math.pi) * 0.3,
                                  0.5 + math.sin((s + 1) / radial_segs * 2 * math.pi) * 0.3)
        f.loops[2][uv_layer].uv = (0.5 + math.cos(s / radial_segs * 2 * math.pi) * 0.3,
                                  0.5 + math.sin(s / radial_segs * 2 * math.pi) * 0.3)

    # Intermediate jagged splinter ring extending outward (-X)
    splinter_verts = []
    for s in range(radial_segs):
        angle = (s / radial_segs) * 2.0 * math.pi
        splinter_len = random.choice([0.18, 0.42, 0.15, 0.55, 0.28, 0.48])
        spx = x_min - splinter_len
        spy = base_center_y + math.cos(angle) * (ring_positions[0][3] * 0.88)
        spz = max(0.04, base_center_z + math.sin(angle) * (ring_positions[0][3] * 0.88))
        v = bm.verts.new(Vector((spx, spy, spz)))
        splinter_verts.append(v)

    # Connect outer base ring -> splinter ring -> cavity ring
    base_ring = ring_verts[0]
    for s in range(radial_segs):
        s_next = (s + 1) % radial_segs
        # Outer rim to splinter
        f1 = bm.faces.new((base_ring[s_next], base_ring[s], splinter_verts[s], splinter_verts[s_next]))
        f1.material_index = 1
        f1.smooth = True
        u0 = s / radial_segs
        u1 = (s + 1) / radial_segs
        f1.loops[0][uv_layer].uv = (u1, 0.0)
        f1.loops[1][uv_layer].uv = (u0, 0.0)
        f1.loops[2][uv_layer].uv = (u0, 0.3)
        f1.loops[3][uv_layer].uv = (u1, 0.3)

        # Splinter to cavity
        f2 = bm.faces.new((splinter_verts[s_next], splinter_verts[s], cavity_verts[s], cavity_verts[s_next]))
        f2.material_index = 1
        f2.smooth = True
        f2.loops[0][uv_layer].uv = (u1, 0.3)
        f2.loops[1][uv_layer].uv = (u0, 0.3)
        f2.loops[2][uv_layer].uv = (u0, 0.8)
        f2.loops[3][uv_layer].uv = (u1, 0.8)

    # 2. Crown / Snapped Tip Fracture (at x_max)
    tip_ring = ring_verts[-1]
    tip_cy = ring_positions[-1][1]
    tip_cz = ring_positions[-1][2]
    tip_r = ring_positions[-1][3]

    # Create 6 jagged splinter shards extending past x_max
    shard_count = 6
    shard_verts = []
    for s in range(radial_segs):
        angle = (s / radial_segs) * 2.0 * math.pi
        is_shard = (s % (radial_segs // shard_count) == 0)
        shard_len = random.uniform(0.35, 0.70) if is_shard else random.uniform(0.08, 0.22)
        sx = x_max + shard_len
        sy = tip_cy + math.cos(angle) * (tip_r * 0.72)
        sz = max(0.05, tip_cz + math.sin(angle) * (tip_r * 0.72))
        v = bm.verts.new(Vector((sx, sy, sz)))
        shard_verts.append(v)

    # Inner snapped core point
    core_pt = bm.verts.new(Vector((x_max + 0.12, tip_cy, tip_cz)))

    for s in range(radial_segs):
        s_next = (s + 1) % radial_segs
        u0 = s / radial_segs
        u1 = (s + 1) / radial_segs

        f1 = bm.faces.new((tip_ring[s], tip_ring[s_next], shard_verts[s_next], shard_verts[s]))
        f1.material_index = 1
        f1.smooth = True
        f1.loops[0][uv_layer].uv = (u0, 0.0)
        f1.loops[1][uv_layer].uv = (u1, 0.0)
        f1.loops[2][uv_layer].uv = (u1, 0.4)
        f1.loops[3][uv_layer].uv = (u0, 0.4)

        f2 = bm.faces.new((shard_verts[s], shard_verts[s_next], core_pt))
        f2.material_index = 1
        f2.smooth = True
        f2.loops[0][uv_layer].uv = (u0, 0.4)
        f2.loops[1][uv_layer].uv = (u1, 0.4)
        f2.loops[2][uv_layer].uv = (0.5, 0.9)

    # 3. Add 2 Sheared Broken Branch Stubs
    branch_specs = [
        (-0.9, math.pi * 0.38, 0.58, 0.12),
        (1.4, -math.pi * 0.42, 0.68, 0.14)
    ]

    for bx, b_angle, b_len, b_rad in branch_specs:
        b_segs = 8
        idx = min(range(rings), key=lambda i: abs(ring_positions[i][0] - bx))
        cx, cy, cz, r, t = ring_positions[idx]

        b_dir = Vector((math.sin(0.35), math.cos(b_angle), math.sin(b_angle))).normalized()
        b_origin = Vector((cx, cy + math.cos(b_angle) * (r * 0.9), cz + math.sin(b_angle) * (r * 0.9)))

        b_rings = 3
        b_verts = []
        for bi in range(b_rings):
            bt = bi / (b_rings - 1)
            b_center = b_origin + b_dir * (b_len * bt)
            cur_r = b_rad * (1.0 - bt * 0.22)
            up_v = Vector((0, 0, 1))
            right_v = b_dir.cross(up_v).normalized()
            up_v = right_v.cross(b_dir).normalized()

            ring = []
            for bs in range(b_segs):
                ba = (bs / b_segs) * 2.0 * math.pi
                bpt = b_center + (right_v * math.cos(ba) + up_v * math.sin(ba)) * cur_r
                v = bm.verts.new(bpt)
                ring.append(v)
            b_verts.append(ring)

        for bi in range(b_rings - 1):
            r1 = b_verts[bi]
            r2 = b_verts[bi + 1]
            bv0 = bi / (b_rings - 1) * 1.5
            bv1 = (bi + 1) / (b_rings - 1) * 1.5
            for bs in range(b_segs):
                bs_next = (bs + 1) % b_segs
                bu0 = bs / b_segs
                bu1 = (bs + 1) / b_segs
                f = bm.faces.new((r1[bs], r2[bs], r2[bs_next], r1[bs_next]))
                f.material_index = 0
                f.smooth = True
                f.loops[0][uv_layer].uv = (bu0, bv0)
                f.loops[1][uv_layer].uv = (bu0, bv1)
                f.loops[2][uv_layer].uv = (bu1, bv1)
                f.loops[3][uv_layer].uv = (bu1, bv0)

        # Splintered branch tip
        b_tip_center = bm.verts.new(b_origin + b_dir * (b_len + random.uniform(0.08, 0.16)))
        r_last = b_verts[-1]
        for bs in range(b_segs):
            bs_next = (bs + 1) % b_segs
            f = bm.faces.new((r_last[bs], r_last[bs_next], b_tip_center))
            f.material_index = 1
            f.smooth = True
            f.loops[0][uv_layer].uv = (bs / b_segs, 0.2)
            f.loops[1][uv_layer].uv = ((bs + 1) / b_segs, 0.2)
            f.loops[2][uv_layer].uv = (0.5, 0.8)

    # Convert to mesh
    mesh = bpy.data.meshes.new("FallenLogMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("FallenLog_Weathered", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def setup_materials(log_obj):
    # Material 0: Mossy Weathered Bark
    bark_mat = bpy.data.materials.new(name="M_FallenLog_Bark")
    bark_mat.use_nodes = True
    bnodes = bark_mat.node_tree.nodes
    blinks = bark_mat.node_tree.links
    bbsdf = bnodes.get("Principled BSDF")

    diff_path = PROJECT_ROOT / "assets/textures/polyhaven/moss_wood/moss_wood_diffuse_1k.jpg"
    norm_path = PROJECT_ROOT / "assets/textures/polyhaven/moss_wood/moss_wood_normal_1k.jpg"
    rough_path = PROJECT_ROOT / "assets/textures/polyhaven/moss_wood/moss_wood_rough_1k.jpg"

    if diff_path.exists():
        tex_diff = bnodes.new("ShaderNodeTexImage")
        tex_diff.image = bpy.data.images.load(str(diff_path))
        blinks.new(tex_diff.outputs["Color"], bbsdf.inputs["Base Color"])

    if rough_path.exists():
        tex_rough = bnodes.new("ShaderNodeTexImage")
        tex_rough.image = bpy.data.images.load(str(rough_path))
        tex_rough.image.colorspace_settings.name = "Non-Color"
        blinks.new(tex_rough.outputs["Color"], bbsdf.inputs["Roughness"])
    else:
        bbsdf.inputs["Roughness"].default_value = 0.85

    if norm_path.exists():
        tex_norm = bnodes.new("ShaderNodeTexImage")
        tex_norm.image = bpy.data.images.load(str(norm_path))
        tex_norm.image.colorspace_settings.name = "Non-Color"
        norm_map = bnodes.new("ShaderNodeNormalMap")
        norm_map.inputs["Strength"].default_value = 1.8
        blinks.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
        blinks.new(norm_map.outputs["Normal"], bbsdf.inputs["Normal"])

    log_obj.data.materials.append(bark_mat)

    # Material 1: Heartwood / Splintered Core Wood
    wood_mat = bpy.data.materials.new(name="M_FallenLog_Heartwood")
    wood_mat.use_nodes = True
    wnodes = wood_mat.node_tree.nodes
    wlinks = wood_mat.node_tree.links
    wbsdf = wnodes.get("Principled BSDF")

    wdiff_path = PROJECT_ROOT / "assets/textures/polyhaven/fine_grained_wood/fine_grained_wood_diffuse_1k.jpg"
    wnorm_path = PROJECT_ROOT / "assets/textures/polyhaven/fine_grained_wood/fine_grained_wood_normal_1k.jpg"
    wrough_path = PROJECT_ROOT / "assets/textures/polyhaven/fine_grained_wood/fine_grained_wood_rough_1k.jpg"

    if wdiff_path.exists():
        wtex_diff = wnodes.new("ShaderNodeTexImage")
        wtex_diff.image = bpy.data.images.load(str(wdiff_path))
        wlinks.new(wtex_diff.outputs["Color"], wbsdf.inputs["Base Color"])

    if wrough_path.exists():
        wtex_rough = wnodes.new("ShaderNodeTexImage")
        wtex_rough.image = bpy.data.images.load(str(wrough_path))
        wtex_rough.image.colorspace_settings.name = "Non-Color"
        wlinks.new(wtex_rough.outputs["Color"], wbsdf.inputs["Roughness"])
    else:
        wbsdf.inputs["Roughness"].default_value = 0.78

    if wnorm_path.exists():
        wtex_norm = wnodes.new("ShaderNodeTexImage")
        wtex_norm.image = bpy.data.images.load(str(wnorm_path))
        wtex_norm.image.colorspace_settings.name = "Non-Color"
        wnorm_map = wnodes.new("ShaderNodeNormalMap")
        wnorm_map.inputs["Strength"].default_value = 1.4
        wlinks.new(wtex_norm.outputs["Color"], wnorm_map.inputs["Color"])
        wlinks.new(wnorm_map.outputs["Normal"], wbsdf.inputs["Normal"])

    log_obj.data.materials.append(wood_mat)


def render_preview(output_path: Path):
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 32.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position camera looking at entire log
    cam_obj.location = Vector((0.2, -5.6, 2.4))
    direction = Vector((0.0, 0.0, 0.35)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Warm flashlight key light
    flash_data = bpy.data.lights.new(name="Flashlight", type="SPOT")
    flash_data.energy = 650.0
    flash_data.spot_size = math.radians(65)
    flash_data.color = (1.0, 0.95, 0.88)
    flash_obj = bpy.data.objects.new(name="Flashlight", object_data=flash_data)
    scene.collection.objects.link(flash_obj)
    flash_obj.location = cam_obj.location
    flash_obj.rotation_euler = cam_obj.rotation_euler

    # Cool blue moonlight fill
    moon_data = bpy.data.lights.new(name="Moonlight", type="SUN")
    moon_data.energy = 1.2
    moon_data.color = (0.75, 0.85, 1.0)
    moon_obj = bpy.data.objects.new(name="Moonlight", object_data=moon_data)
    scene.collection.objects.link(moon_obj)
    moon_obj.rotation_euler = (math.radians(55), math.radians(-30), math.radians(45))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview to {output_path}")


def export_glb(log_obj, output_path: Path):
    bpy.ops.object.select_all(action="DESELECT")
    log_obj.select_set(True)
    bpy.context.view_layer.objects.active = log_obj

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported fallen nurse log GLB to {output_path}")


def main():
    clear_scene()
    print("=== BUILDING PROCEDURAL FALLEN NURSE LOG IN BLENDER ===")
    log_obj = create_fallen_log()
    setup_materials(log_obj)

    # Count geometry stats
    poly_count = len(log_obj.data.polygons)
    vert_count = len(log_obj.data.vertices)
    print(f"[STATS] Polygons: {poly_count}, Vertices: {vert_count} (Triangles: ~{poly_count * 2})")

    # Render inspection preview
    preview_path = PROJECT_ROOT / "docs/graphics/previews/blender_fallen_log_preview.png"
    render_preview(preview_path)

    # Export GLB
    glb_path = PROJECT_ROOT / "assets/models/fallen_log_weathered.glb"
    export_glb(log_obj, glb_path)
    print("=== FALLEN NURSE LOG GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
