#!/usr/bin/env python3
"""
Procedural Mossy Rock Cluster Optimizer & Builder for Blender 4.2 LTS.
Welds duplicate vertices, smooth-shades, and decimates Poly Haven 'rock_moss_set_01'
into an ultra-clean ~1,800 triangle real-time boulder cluster.
Renders inspection preview and exports 'assets/models/rock_cluster_mossy.glb'.
"""

import math
import sys
from pathlib import Path

try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler
except ImportError:
    print("Execute via 'blender --background --python <script>'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def main():
    print("=== STARTING BLENDER MOSSY ROCK CLUSTER BUILD (V3 - WELDED) ===")
    clear_scene()

    source_gltf = PROJECT_ROOT / "assets/models/polyhaven/rock_moss_set_01/rock_moss_set_01_1k.gltf"
    if not source_gltf.exists():
        print(f"ERROR: Source file not found: {source_gltf}")
        sys.exit(1)

    bpy.ops.import_scene.gltf(filepath=str(source_gltf))

    # Identify individual rock objects from the set
    rocks = {}
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            name_lower = obj.name.lower()
            if "rock01" in name_lower:
                rocks["main"] = obj
            elif "rock02" in name_lower:
                rocks["side"] = obj
            elif "rock03" in name_lower:
                rocks["small"] = obj
            elif "rock04" in name_lower:
                rocks["satellite1"] = obj
            elif "rock06" in name_lower:
                rocks["satellite2"] = obj

    # Remove unused objects
    for obj in list(bpy.context.scene.objects):
        if obj not in rocks.values() and obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    # 1. Weld coincidental vertices to eliminate photogrammetry seam cracks
    # 2. Decimate to target ~1,800 triangles total
    decimate_ratios = {
        "main": 0.04,        # ~450 quads / ~900 tris
        "side": 0.04,        # ~450 quads / ~900 tris
        "small": 0.05,       # ~250 quads / ~500 tris
        "satellite1": 0.02,  # ~100 quads / ~200 tris
        "satellite2": 0.02   # ~100 quads / ~200 tris
    }

    for key, obj in rocks.items():
        # Weld duplicate vertices
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
        bm.to_mesh(obj.data)
        bm.free()

        # Decimate
        ratio = decimate_ratios.get(key, 0.04)
        mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
        mod.ratio = ratio
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)

        # Smooth shading
        for p in obj.data.polygons:
            p.use_smooth = True

    # Position rocks into a natural, grounded formation
    # Main prominent mossy boulder
    main_boulder = rocks.get("main")
    if main_boulder:
        main_boulder.location = Vector((0.0, 0.0, -0.25))  # Embedded into soil
        main_boulder.rotation_euler = Euler((0.15, -0.25, 0.45), "XYZ")
        main_boulder.scale = Vector((1.3, 1.25, 1.1))

    # Flanking medium moss boulder
    side_boulder = rocks.get("side")
    if side_boulder:
        side_boulder.location = Vector((1.25, 0.35, -0.18))
        side_boulder.rotation_euler = Euler((-0.2, 0.35, 1.8), "XYZ")
        side_boulder.scale = Vector((0.95, 0.9, 0.85))

    # Rear weathered stone
    small_boulder = rocks.get("small")
    if small_boulder:
        small_boulder.location = Vector((-1.05, -0.45, -0.15))
        small_boulder.rotation_euler = Euler((0.3, -0.1, -1.2), "XYZ")
        small_boulder.scale = Vector((0.85, 0.9, 0.8))

    # Forefront satellite stones nestled at the base
    sat1 = rocks.get("satellite1")
    if sat1:
        sat1.location = Vector((0.6, -1.0, -0.08))
        sat1.rotation_euler = Euler((0.4, 0.2, 0.8), "XYZ")
        sat1.scale = Vector((0.48, 0.42, 0.36))

    sat2 = rocks.get("satellite2")
    if sat2:
        sat2.location = Vector((-0.9, 0.85, -0.08))
        sat2.rotation_euler = Euler((-0.3, -0.4, 2.1), "XYZ")
        sat2.scale = Vector((0.42, 0.48, 0.4))

    # Calculate total triangles
    total_tris = sum(len(o.data.polygons) * 2 for o in rocks.values())
    print(f"[STATS] Total Rock Cluster Triangles: ~{total_tris} (GTX 960 optimal: < 2,500 tris)")

    # Render Preview
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector((4.2, -4.2, 2.6))
    look_target = Vector((0.15, 0.05, 0.4))
    direction = look_target - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Directional moonlight + flashlight bounce
    sun_data = bpy.data.lights.new(name="Moonlight", type="SUN")
    sun_data.energy = 3.2
    sun_data.color = (0.78, 0.88, 1.0)
    sun_obj = bpy.data.objects.new("Moonlight", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(48), math.radians(-28), math.radians(35))

    fill_data = bpy.data.lights.new(name="Flashlight", type="POINT")
    fill_data.energy = 600.0
    fill_data.color = (0.98, 0.95, 0.88)
    fill_obj = bpy.data.objects.new("Flashlight", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.location = Vector((3.6, -3.0, 2.2))

    preview_path = PROJECT_ROOT / "docs/graphics/previews/blender_rock_cluster_preview.png"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview image: {preview_path}")

    # Select all rocks and export as single clean GLB
    bpy.ops.object.select_all(action="DESELECT")
    for o in rocks.values():
        o.select_set(True)
    bpy.context.view_layer.objects.active = main_boulder

    export_glb_path = PROJECT_ROOT / "assets/models/rock_cluster_mossy.glb"
    export_glb_path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=str(export_glb_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported GLB rock cluster: {export_glb_path} (Size: {export_glb_path.stat().st_size} bytes)")
    print("=== BLENDER MOSSY ROCK CLUSTER BUILD FINISHED ===")


if __name__ == "__main__":
    main()
