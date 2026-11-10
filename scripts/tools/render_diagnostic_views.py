#!/usr/bin/env python3
"""
Automated Diagnostic Studio (Blender)
Renders 5-angle neutral untextured clay diagnostic views (Front, Side, Rear, 3/4, Bust)
for asset anatomy and silhouette review in compliance with Issue 003.
"""

import argparse
import json
import struct
import sys
from pathlib import Path

# If executed directly by Python, spawn Blender with this script
if __name__ == "__main__" and "bpy" not in sys.modules:
    parser = argparse.ArgumentParser(description="Render 5-angle diagnostic clay views in Blender.")
    parser.add_argument("--asset", default="sasquatch", help="Asset ID under assets/creatures/")
    parser.add_argument("--source", default=None, help="Path to .blend, .obj, or directory of .objs to render")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    asset_dir = project_root / "assets" / "creatures" / args.asset
    out_dir = asset_dir / "qa" / "diagnostic_views"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "blender",
        "--background",
        "--python", str(Path(__file__).resolve()),
        "--",
        "--asset", args.asset,
        "--out", str(out_dir)
    ]
    if args.source:
        cmd.extend(["--source", str(Path(args.source).resolve())])

    manifest_path = out_dir / "diagnostic_render_manifest.json"
    manifest_path.unlink(missing_ok=True)

    import subprocess
    print(f"[EXEC] {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)

    expected_views = [
        "render_front.png",
        "render_side.png",
        "render_rear.png",
        "render_threequarter.png",
        "render_bust.png",
    ]
    failed = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not manifest.get("completed") or manifest.get("asset") != args.asset:
            failed.append("diagnostic_render_manifest.json (invalid)")
        elif set(expected_views) - set(manifest.get("views", [])):
            failed.append("diagnostic_render_manifest.json (missing views)")
    except (OSError, json.JSONDecodeError):
        failed.append("diagnostic_render_manifest.json (missing)")

    for name in expected_views:
        path = out_dir / name
        try:
            with path.open("rb") as f:
                header = f.read(24)
            valid_png = (
                len(header) == 24
                and header[:8] == b"\x89PNG\r\n\x1a\n"
                and header[12:16] == b"IHDR"
            )
            width, height = struct.unpack(">II", header[16:24]) if valid_png else (0, 0)
            if not valid_png or width != 1280 or height != 1280:
                failed.append(f"{name} ({path.stat().st_size if path.exists() else 0} bytes)")
        except OSError:
            failed.append(f"{name} (missing)")

    if failed:
        print(f"[FAIL] Diagnostic render QA failed: {', '.join(failed)}")
        sys.exit(1)
    print(f"[PASS] Diagnostic render QA verified {len(expected_views)} PNG views at 1280x1280.")
    sys.exit(0)

# =========================================================================
# BLENDER INTERNAL EXECUTION
# =========================================================================
import bpy
from mathutils import Vector

# Parse script args after "--"
argv = sys.argv
if "--" in argv:
    script_args = argv[argv.index("--") + 1:]
else:
    script_args = []

import argparse
b_parser = argparse.ArgumentParser()
b_parser.add_argument("--asset", default="sasquatch")
b_parser.add_argument("--out", required=True)
b_parser.add_argument("--source", default=None)
parsed = b_parser.parse_args(script_args)

out_dir = Path(parsed.out)
out_dir.mkdir(parents=True, exist_ok=True)
project_root = Path(__file__).resolve().parent.parent.parent

# 1. Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
main_col = bpy.data.collections.new("DiagnosticCollection")
bpy.context.scene.collection.children.link(main_col)

# 2. Load Mesh Geometry
imported_objects = []

if parsed.source:
    source_path = Path(parsed.source)
    if not source_path.exists():
        raise RuntimeError(f"Diagnostic source does not exist: {source_path}")

    if source_path.is_dir():
        obj_files = sorted(source_path.glob("*.obj"))
        if not obj_files:
            raise RuntimeError(f"No .obj files found in diagnostic source directory: {source_path}")
        for obj_file in obj_files:
            bpy.ops.wm.obj_import(filepath=str(obj_file))
        imported_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    elif source_path.suffix.lower() == ".obj":
        bpy.ops.wm.obj_import(filepath=str(source_path))
        imported_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    elif source_path.suffix.lower() in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=str(source_path))
        for a in bpy.context.selected_objects:
            if a.type == 'ARMATURE':
                a.rotation_quaternion = (1, 0, 0, 0)
                a.rotation_euler = (0, 0, 0)
                a.location = (0, 0, 0)
        bpy.context.view_layer.update()
        imported_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    elif source_path.suffix.lower() == ".blend":
        with bpy.data.libraries.load(str(source_path), link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        for obj in data_to.objects:
            if obj is not None and obj.type == 'MESH':
                main_col.objects.link(obj)
        imported_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    else:
        raise RuntimeError(f"Unsupported diagnostic source type: {source_path}")

    if not imported_objects:
        raise RuntimeError(f"No mesh objects found in diagnostic source: {source_path}")
else:
    # Look for exported full mesh or assembled parts in assets/models/
    full_obj = project_root / "assets" / "models" / f"{parsed.asset}_full.obj"
    if full_obj.exists():
        bpy.ops.wm.obj_import(filepath=str(full_obj))
        imported_objects = list(bpy.context.selected_objects)
    else:
        # Load component parts assembled according to Godot hierarchy
        models_dir = project_root / "assets" / "models"
        part_specs = [
            ("sasquatch_torso.obj", Vector((0, 0, 0))),
            ("sasquatch_head.obj", Vector((0, 0.1, 0.75))), # Adjusted for Blender coords
            ("sasquatch_arm_upper.obj", Vector((-0.62, -0.05, 0.5))),
            ("sasquatch_arm_upper.obj", Vector((0.62, -0.05, 0.5)), Vector((-1, 1, 1))),
            ("sasquatch_arm_lower.obj", Vector((-0.62, -0.07, -0.1))),
            ("sasquatch_arm_lower.obj", Vector((0.62, -0.07, -0.1)), Vector((-1, 1, 1))),
            ("sasquatch_hand.obj", Vector((-0.62, -0.09, -0.66))),
            ("sasquatch_hand.obj", Vector((0.62, -0.09, -0.66)), Vector((-1, 1, 1))),
            ("sasquatch_leg_upper.obj", Vector((-0.35, -0.02, -0.3))),
            ("sasquatch_leg_upper.obj", Vector((0.35, -0.02, -0.3)), Vector((-1, 1, 1))),
            ("sasquatch_leg_lower.obj", Vector((-0.35, -0.04, -0.92))),
            ("sasquatch_leg_lower.obj", Vector((0.35, -0.04, -0.92)), Vector((-1, 1, 1))),
            ("sasquatch_foot.obj", Vector((-0.35, 0.01, -1.44))),
            ("sasquatch_foot.obj", Vector((0.35, 0.01, -1.44)), Vector((-1, 1, 1))),
        ]
        for spec in part_specs:
            fname = spec[0]
            loc = spec[1]
            scale = spec[2] if len(spec) > 2 else Vector((1, 1, 1))
            fpath = models_dir / fname
            if fpath.exists():
                bpy.ops.wm.obj_import(filepath=str(fpath))
                objs = list(bpy.context.selected_objects)
                for o in objs:
                    o.location = loc
                    o.scale = scale
                    imported_objects.append(o)

# 3. Create Neutral Matte Clay Material
clay_mat = bpy.data.materials.new("DiagnosticClay")
clay_mat.use_nodes = True
nodes = clay_mat.node_tree.nodes
links = clay_mat.node_tree.links
nodes.clear()

node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
node_bsdf.inputs['Base Color'].default_value = (0.75, 0.75, 0.75, 1.0)
node_bsdf.inputs['Roughness'].default_value = 0.50
node_bsdf.inputs['Metallic'].default_value = 0.0
links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

for o in imported_objects:
    if o.type == 'MESH':
        o.data.materials.clear()
        o.data.materials.append(clay_mat)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_smooth()

# 4. Compute Bounding Center & Dimensions
if imported_objects:
    bbox_corners = [o.matrix_world @ Vector(corner) for o in imported_objects if o.type == 'MESH' for corner in o.bound_box]
    if bbox_corners:
        min_x = min(c.x for c in bbox_corners)
        max_x = max(c.x for c in bbox_corners)
        min_y = min(c.y for c in bbox_corners)
        max_y = max(c.y for c in bbox_corners)
        min_z = min(c.z for c in bbox_corners)
        max_z = max(c.z for c in bbox_corners)
        center = Vector(((min_x + max_x) * 0.5, (min_y + max_y) * 0.5, (min_z + max_z) * 0.5))
        height = max_z - min_z
    else:
        center = Vector((0, 0, 1.4))
        height = 2.85
else:
    center = Vector((0, 0, 1.4))
    height = 2.85

# 5. Environment & 3-Point Neutral Daylight Lighting
world = bpy.data.worlds.new("DiagnosticWorld")
bpy.context.scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
wnodes.clear()
wout = wnodes.new('ShaderNodeOutputWorld')
wbg = wnodes.new('ShaderNodeBackground')
wbg.inputs['Color'].default_value = (0.35, 0.35, 0.35, 1.0) # Neutral ambient fill
wbg.inputs['Strength'].default_value = 0.8
wlinks.new(wbg.outputs['Background'], wout.inputs['Surface'])

# Key Light (Front-right, elevated, shining onto face & chest)
bpy.ops.object.light_add(type='SUN', location=(center.x + 3.0, center.y + 4.0, center.z + 5.0))
key_sun = bpy.context.active_object
key_sun.data.energy = 3.5
key_sun.data.color = (1.0, 1.0, 1.0)
direction_key = center - key_sun.location
key_sun.rotation_euler = direction_key.to_track_quat('-Z', 'Y').to_euler()

# Fill Light (Front-left, softer)
bpy.ops.object.light_add(type='SUN', location=(center.x - 3.5, center.y + 4.0, center.z + 3.0))
fill_sun = bpy.context.active_object
fill_sun.data.energy = 2.0
fill_sun.data.color = (0.95, 0.95, 1.0)
direction_fill = center - fill_sun.location
fill_sun.rotation_euler = direction_fill.to_track_quat('-Z', 'Y').to_euler()

# Rim / Back Light (Behind, high angle)
bpy.ops.object.light_add(type='SUN', location=(center.x, center.y - 4.5, center.z + 4.5))
rim_sun = bpy.context.active_object
rim_sun.data.energy = 2.5
rim_sun.data.color = (1.0, 1.0, 0.95)
direction_rim = center - rim_sun.location
rim_sun.rotation_euler = direction_rim.to_track_quat('-Z', 'Y').to_euler()

# 6. Camera Setup
cam_data = bpy.data.cameras.new("DiagnosticCam")
cam_data.lens = 85 # 85mm portrait telephoto to minimize perspective distortion
cam_obj = bpy.data.objects.new("DiagnosticCam", cam_data)
main_col.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Camera Distance based on creature height
dist = max(height * 2.2, 5.0)

# Render Settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngine") else 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 1280
scene.render.film_transparent = False

# Five Diagnostic Camera Angles: Front, Side, Rear, Threequarter, and Bust Closeup
# In Blender native: +Y is Forward (chest/face), -Y is Rear (back/spine), +Z is Up (head)
views = {
    # Front View: Camera in front of chest/face (+Y)
    "render_front.png": (Vector((center.x, center.y + dist, center.z)), Vector((center.x, center.y, center.z))),
    # True Profile Side View: 90 deg lateral
    "render_side.png": (Vector((center.x - dist, center.y, center.z)), Vector((center.x, center.y, center.z))),
    # Rear View: 180 deg behind back (-Y)
    "render_rear.png": (Vector((center.x, center.y - dist, center.z)), Vector((center.x, center.y, center.z))),
    # 3/4 Dynamic Perspective View
    "render_threequarter.png": (Vector((center.x - dist * 0.72, center.y + dist * 0.72, center.z + 0.3)), Vector((center.x, center.y, center.z))),
    # Close-up Bust Portrait (Head, Brow, Face Mask, Beard, Pectorals)
    "render_bust.png": (Vector((center.x - 0.25, center.y + 1.85, center.z + 0.75)), Vector((center.x, center.y + 0.15, center.z + 0.75))),
}

for filename, (cam_pos, target_pos) in views.items():
    cam_obj.location = cam_pos
    
    # Point camera precisely at target position
    direction = target_pos - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    scene.render.filepath = str(out_dir / filename)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered {filename} -> {scene.render.filepath}")

manifest = {
    "asset": parsed.asset,
    "source": parsed.source or f"assets/models/{parsed.asset}_full.obj",
    "completed": True,
    "views": list(views.keys()),
}
(out_dir / "diagnostic_render_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f">>> ALL {len(views)} DIAGNOSTIC VIEWS RENDERED CLEANLY <<<")
