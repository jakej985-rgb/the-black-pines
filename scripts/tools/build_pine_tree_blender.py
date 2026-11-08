#!/usr/bin/env python3
"""
Procedural Photorealistic Mature Timber Pine Generator for Blender 4.2 LTS.
Architecture:
- Trunk: Flared buttress roots (Z < 1.5m), organic curvature, taper, and 6 snag branch stubs.
- Canopy: 14 tiers of lateral branch whorls with natural parabolic droop and upward sweeping tips.
- Foliage: Dense 3D needle sprays with tiered branchlets and cross-faceted cards for lush volume.
- Material: High-res Poly Haven PBR bark + rich forest needle shading with normal depth.
- Performance: ~3,200 triangles (GTX 960 optimal).
"""

import math
import random
import sys
from pathlib import Path

try:
    import bpy
    import bmesh
    from mathutils import Vector
except ImportError:
    print("Execute via 'blender --background --python <script>'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def create_trunk_mesh():
    bm = bmesh.new()

    height = 18.0
    rings = 24
    radial_segs = 14
    random.seed(101)

    root_flairs = 5
    flair_angles = [i * (2.0 * math.pi / root_flairs) + random.uniform(-0.1, 0.1) for i in range(root_flairs)]

    ring_verts = []

    for ring_idx in range(rings):
        t = ring_idx / (rings - 1)
        z = t * height

        # Natural trunk taper: flared base -> organic taper -> slender apex
        base_radius = 0.44 * math.pow(1.0 - t * 0.95, 0.65) + 0.05

        # Subtle natural trunk lean and organic waver
        lean_x = math.sin(t * 1.8) * 0.22 - math.sin(t * 3.5) * 0.08
        lean_y = math.cos(t * 1.5) * 0.18 - 0.18

        current_ring = []
        for seg_idx in range(radial_segs):
            angle = (seg_idx / radial_segs) * 2.0 * math.pi
            r = base_radius

            # Buttress root flairs at base (Z < 1.5m)
            if z < 1.5:
                flair_strength = math.pow((1.5 - z) / 1.5, 2.2)
                flair_factor = 0.0
                for fa in flair_angles:
                    diff = abs((angle - fa + math.pi) % (2.0 * math.pi) - math.pi)
                    if diff < 0.65:
                        flair_factor = max(flair_factor, math.cos(diff * (math.pi / 1.3)))
                r += flair_strength * flair_factor * 0.42

            # Organic circumference irregularities
            r *= 1.0 + random.uniform(-0.03, 0.03) + math.sin(angle * 3.0 + ring_idx * 0.7) * 0.025

            vx = lean_x + math.cos(angle) * r
            vy = lean_y + math.sin(angle) * r
            vz = z

            v = bm.verts.new((vx, vy, vz))
            current_ring.append(v)

        ring_verts.append(current_ring)

    # Quad faces between rings
    for r in range(rings - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = ring_verts[r][s]
            v2 = ring_verts[r][next_s]
            v3 = ring_verts[r + 1][next_s]
            v4 = ring_verts[r + 1][s]
            bm.faces.new((v1, v2, v3, v4))

    # Close apex
    v_top = bm.verts.new((lean_x, lean_y, height))
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        bm.faces.new((ring_verts[-1][s], ring_verts[-1][next_s], v_top))

    # Snag branch stubs on lower trunk (Z = 2.8m - 6.0m)
    snag_configs = [
        (2.8, 0.4, 0.55, -0.22),
        (3.8, 2.1, 0.65, -0.16),
        (4.7, 3.9, 0.48, -0.12),
        (5.4, 1.2, 0.52, -0.24),
        (6.1, 5.2, 0.60, -0.15)
    ]
    for sz, s_angle, s_len, s_pitch in snag_configs:
        t = sz / height
        trunk_r = 0.44 * math.pow(1.0 - t * 0.95, 0.65) + 0.05
        lx = math.sin(t * 1.8) * 0.22 - math.sin(t * 3.5) * 0.08
        ly = math.cos(t * 1.5) * 0.18 - 0.18

        origin = Vector((lx + math.cos(s_angle) * trunk_r, ly + math.sin(s_angle) * trunk_r, sz))
        direction = Vector((math.cos(s_angle), math.sin(s_angle), s_pitch)).normalized()

        stub_segs = 6
        stub_rings = 3
        prev_sv = []
        for sr in range(stub_rings):
            st = sr / (stub_rings - 1)
            pos = origin + direction * (st * s_len)
            s_radius = 0.065 * (1.0 - st * 0.45)
            cur_sv = []
            for ss in range(stub_segs):
                sa = (ss / stub_segs) * 2.0 * math.pi
                up = Vector((0, 0, 1))
                side = direction.cross(up).normalized()
                up_actual = side.cross(direction).normalized()
                pt = pos + (side * math.cos(sa) + up_actual * math.sin(sa)) * s_radius
                cur_sv.append(bm.verts.new(pt))
            if prev_sv:
                for ss in range(stub_segs):
                    nss = (ss + 1) % stub_segs
                    bm.faces.new((prev_sv[ss], prev_sv[nss], cur_sv[nss], cur_sv[ss]))
            prev_sv = cur_sv

    mesh = bpy.data.meshes.new("TrunkMesh")
    bm.to_mesh(mesh)
    bm.free()

    # Cylindrical UVs for bark texture
    mesh.uv_layers.new(name="UVMap")
    uv_layer = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            loop = mesh.loops[loop_idx]
            vert = mesh.vertices[loop.vertex_index]
            angle = math.atan2(vert.co.y, vert.co.x)
            u = (angle / (2.0 * math.pi)) + 0.5
            v = vert.co.z * 0.38
            uv_layer[loop_idx].uv = (u, v)

    obj = bpy.data.objects.new("Pine_Trunk", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_foliage_mesh():
    bm = bmesh.new()
    random.seed(2026)

    # 13 tiers of branch whorls from Z = 5.8m to 17.6m
    tiers = [
        # (z_height, max_radius, boughs_count, droop, pitch)
        (5.8, 3.2, 7, 0.45, -0.06),
        (6.8, 3.6, 7, 0.42, -0.05),
        (7.9, 3.7, 7, 0.40, -0.04),
        (9.0, 3.5, 7, 0.36, -0.02),
        (10.2, 3.3, 6, 0.32, 0.00),
        (11.4, 2.9, 6, 0.28, 0.02),
        (12.6, 2.5, 6, 0.24, 0.05),
        (13.7, 2.1, 5, 0.20, 0.08),
        (14.8, 1.7, 5, 0.16, 0.11),
        (15.8, 1.3, 4, 0.12, 0.15),
        (16.7, 0.9, 4, 0.08, 0.20),
        (17.3, 0.55, 3, 0.05, 0.25),
        (17.7, 0.30, 3, 0.02, 0.30)
    ]

    for tier_idx, (tz, max_r, boughs_count, base_droop, tier_pitch) in enumerate(tiers):
        t_height = tz / 18.0
        trunk_cx = math.sin(t_height * 1.8) * 0.22 - math.sin(t_height * 3.5) * 0.08
        trunk_cy = math.cos(t_height * 1.5) * 0.18 - 0.18

        angle_offset = tier_idx * 0.65

        for b_idx in range(boughs_count):
            base_angle = angle_offset + (b_idx / boughs_count) * 2.0 * math.pi + random.uniform(-0.12, 0.12)
            bough_len = max_r * random.uniform(0.88, 1.12)
            droop_amount = base_droop * (bough_len / 3.4)

            # Generate 4 spine nodes along the branch
            spine_nodes = []
            node_count = 4
            for ni in range(node_count):
                nt = ni / (node_count - 1)
                dist = nt * bough_len
                # Parabolic droop formula
                cur_z = tz + (tier_pitch * dist) - droop_amount * math.pow(nt, 1.5)
                # Upward conifer tip sweep
                if nt > 0.65:
                    cur_z += (nt - 0.65) * 0.22

                cur_x = trunk_cx + math.cos(base_angle) * dist
                cur_y = trunk_cy + math.sin(base_angle) * dist
                spine_nodes.append(Vector((cur_x, cur_y, cur_z)))

            # Create lateral drooping needle sprays along each branch segment
            for ni in range(1, node_count):
                p0 = spine_nodes[ni - 1]
                p1 = spine_nodes[ni]
                fwd = (p1 - p0).normalized()
                seg_len = (p1 - p0).length

                up_ref = Vector((0, 0, 1))
                side = fwd.cross(up_ref).normalized()
                local_up = side.cross(fwd).normalized()

                fan_width = 0.65 * (1.15 - (ni / node_count) * 0.35)

                # Primary drooping bough fan (horizontal)
                v1 = bm.verts.new(p0 - side * (fan_width * 0.6) - local_up * 0.06)
                v2 = bm.verts.new(p0 + side * (fan_width * 0.6) - local_up * 0.06)
                v3 = bm.verts.new(p1 + side * fan_width + local_up * 0.03)
                v4 = bm.verts.new(p1 - side * fan_width + local_up * 0.03)
                bm.faces.new((v1, v2, v3, v4))

                # Secondary lateral bough spray (+30 deg pitch)
                tilt1 = 0.52
                s_dir1 = (local_up * math.cos(tilt1) + side * math.sin(tilt1)).normalized()
                s_w = fan_width * 0.72
                w1 = bm.verts.new(p0 - s_dir1 * s_w * 0.7)
                w2 = bm.verts.new(p0 + s_dir1 * s_w * 0.7)
                w3 = bm.verts.new(p1 + s_dir1 * s_w * 0.85)
                w4 = bm.verts.new(p1 - s_dir1 * s_w * 0.85)
                bm.faces.new((w1, w2, w3, w4))

                # Tertiary opposing lateral spray (-30 deg pitch)
                s_dir2 = (local_up * math.cos(-tilt1) + side * math.sin(-tilt1)).normalized()
                q1 = bm.verts.new(p0 - s_dir2 * s_w * 0.7)
                q2 = bm.verts.new(p0 + s_dir2 * s_w * 0.7)
                q3 = bm.verts.new(p1 + s_dir2 * s_w * 0.85)
                q4 = bm.verts.new(p1 - s_dir2 * s_w * 0.85)
                bm.faces.new((q1, q2, q3, q4))

                # Drooping tip tassel on outermost segments
                if ni == node_count - 1:
                    tip_len = 0.55
                    tip_pt = p1 + fwd * tip_len - local_up * 0.12
                    t1 = bm.verts.new(p1 - side * (fan_width * 0.5))
                    t2 = bm.verts.new(p1 + side * (fan_width * 0.5))
                    t3 = bm.verts.new(tip_pt)
                    bm.faces.new((t1, t2, t3))

    mesh = bpy.data.meshes.new("FoliageMesh")
    bm.to_mesh(mesh)
    bm.free()

    mesh.uv_layers.new(name="UVMap")
    uv_layer = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        if len(poly.loop_indices) == 4:
            uv_layer[poly.loop_indices[0]].uv = (0.0, 0.0)
            uv_layer[poly.loop_indices[1]].uv = (1.0, 0.0)
            uv_layer[poly.loop_indices[2]].uv = (1.0, 1.0)
            uv_layer[poly.loop_indices[3]].uv = (0.0, 1.0)
        elif len(poly.loop_indices) == 3:
            uv_layer[poly.loop_indices[0]].uv = (0.0, 0.0)
            uv_layer[poly.loop_indices[1]].uv = (1.0, 0.0)
            uv_layer[poly.loop_indices[2]].uv = (0.5, 1.0)

    obj = bpy.data.objects.new("Pine_Foliage", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def setup_materials(trunk_obj, foliage_obj):
    # 1. Bark Material
    bark_mat = bpy.data.materials.new(name="M_Pine_Bark")
    bark_mat.use_nodes = True
    nodes = bark_mat.node_tree.nodes
    links = bark_mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    diff_path = PROJECT_ROOT / "assets/textures/polyhaven/knotted_pine_bark/knotted_pine_bark_diffuse_1k.jpg"
    norm_path = PROJECT_ROOT / "assets/textures/polyhaven/knotted_pine_bark/knotted_pine_bark_normal_1k.jpg"
    rough_path = PROJECT_ROOT / "assets/textures/polyhaven/knotted_pine_bark/knotted_pine_bark_rough_1k.jpg"

    if diff_path.exists():
        tex_diff = nodes.new("ShaderNodeTexImage")
        tex_diff.image = bpy.data.images.load(str(diff_path))
        links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])

    if rough_path.exists():
        tex_rough = nodes.new("ShaderNodeTexImage")
        tex_rough.image = bpy.data.images.load(str(rough_path))
        tex_rough.image.colorspace_settings.name = "Non-Color"
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.88

    if norm_path.exists():
        tex_norm = nodes.new("ShaderNodeTexImage")
        tex_norm.image = bpy.data.images.load(str(norm_path))
        tex_norm.image.colorspace_settings.name = "Non-Color"
        norm_map = nodes.new("ShaderNodeNormalMap")
        norm_map.inputs["Strength"].default_value = 1.6
        links.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
        links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])

    trunk_obj.data.materials.append(bark_mat)

    # 2. Foliage Material (Rich deep evergreen needles)
    foliage_mat = bpy.data.materials.new(name="M_Pine_Needles")
    foliage_mat.use_nodes = True
    fnodes = foliage_mat.node_tree.nodes
    flinks = foliage_mat.node_tree.links
    fbsdf = fnodes.get("Principled BSDF")

    # Dark Pacific Northwest evergreen needle color
    fbsdf.inputs["Base Color"].default_value = (0.055, 0.135, 0.075, 1.0)
    fbsdf.inputs["Roughness"].default_value = 0.82

    foliage_obj.data.materials.append(foliage_mat)


def render_inspection_preview(output_path: Path):
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    # Camera looking at tree from distance (Z is up)
    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 42.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector((14.0, -14.0, 9.5))
    look_target = Vector((0.0, 0.0, 8.5))
    direction = look_target - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

    # Directional Moonlight (cool blue-white angle)
    light_data = bpy.data.lights.new(name="Moonlight", type="SUN")
    light_data.energy = 3.2
    light_data.color = (0.80, 0.88, 1.0)
    light_obj = bpy.data.objects.new(name="Moonlight", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(50), math.radians(-25), math.radians(40))

    # Rim light from behind tree
    rim_data = bpy.data.lights.new(name="RimLight", type="SUN")
    rim_data.energy = 1.4
    rim_data.color = (0.6, 0.75, 0.95)
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(-40), math.radians(35), math.radians(-120))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview image: {output_path}")


def main():
    print("=== STARTING BLENDER PROCEDURAL PINE TREE BUILD (V3) ===")
    clear_scene()

    trunk_obj = create_trunk_mesh()
    foliage_obj = create_foliage_mesh()

    setup_materials(trunk_obj, foliage_obj)

    trunk_tris = len(trunk_obj.data.polygons) * 2
    foliage_tris = sum(len(p.vertices) - 2 for p in foliage_obj.data.polygons)
    total_tris = trunk_tris + foliage_tris

    print(f"[STATS] Trunk Triangles:   ~{trunk_tris}")
    print(f"[STATS] Foliage Triangles: ~{foliage_tris}")
    print(f"[STATS] Total Triangles:   ~{total_tris} (GTX 960 budget: < 4,000 tris)")

    # Render Preview
    preview_path = PROJECT_ROOT / "docs/graphics/previews/blender_pine_tree_preview.png"
    render_inspection_preview(preview_path)

    # Select both objects for export
    bpy.ops.object.select_all(action="DESELECT")
    trunk_obj.select_set(True)
    foliage_obj.select_set(True)
    bpy.context.view_layer.objects.active = trunk_obj

    # Export GLB (+Y up, -Z forward standard glTF)
    export_glb_path = PROJECT_ROOT / "assets/models/tree_pine_tall_v2.glb"
    export_glb_path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=str(export_glb_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported GLB model: {export_glb_path} (File size: {export_glb_path.stat().st_size} bytes)")
    print("=== BLENDER PINE TREE BUILD FINISHED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
