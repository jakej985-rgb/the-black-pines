#!/usr/bin/env python3
"""
Photorealistic Western Sword Fern Processor for Blender 4.2 LTS.
Architecture:
- Imports Poly Haven fern_02 assets.
- Sets up PBR materials with RGBA Albedo (alpha scissor / clip), Tangent Normal, Roughness, and Translucency.
- Centers cluster at (0, 0, 0) resting on ground.
- Renders an inspection preview.
- Exports assets/models/fern_cluster_sword.glb.
"""

import math
import sys
from pathlib import Path

try:
    import bpy
    from mathutils import Vector
except ImportError:
    print("Execute via 'blender --background --python <script>'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def main():
    clear_scene()
    print("=== PROCESSING WESTERN SWORD FERN IN BLENDER ===")

    gltf_path = PROJECT_ROOT / "assets/models/polyhaven/fern_02/fern_02_1k.gltf"
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))

    # Keep fern_02_a (compact lush cluster ~784 polys) or fern_02_d
    # Let's inspect objects
    target_obj = None
    for obj in list(bpy.context.scene.objects):
        if obj.name == "fern_02_a":
            target_obj = obj
        else:
            # Remove other variants from export scene
            bpy.data.objects.remove(obj, do_unlink=True)

    if not target_obj:
        print("ERROR: fern_02_a not found!")
        sys.exit(1)

    # Center target object at ground origin
    bpy.ops.object.select_all(action="DESELECT")
    target_obj.select_set(True)
    bpy.context.view_layer.objects.active = target_obj

    # Apply transform so origin is at bottom center
    target_obj.location = Vector((0, 0, 0))
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    # Put bottom of bounds at Z = 0
    bbox_min_z = min(v.co.z for v in target_obj.data.vertices)
    for v in target_obj.data.vertices:
        v.co.z -= bbox_min_z
    # Center XY
    avg_x = sum(v.co.x for v in target_obj.data.vertices) / len(target_obj.data.vertices)
    avg_y = sum(v.co.y for v in target_obj.data.vertices) / len(target_obj.data.vertices)
    for v in target_obj.data.vertices:
        v.co.x -= avg_x
        v.co.y -= avg_y

    target_obj.data.update()

    # Setup PBR Material with RGBA Albedo & Alpha Clip
    mat = target_obj.data.materials[0] if target_obj.data.materials else bpy.data.materials.new(name="M_Fern_Sword")
    mat.use_nodes = True
    mat.blend_method = 'CLIP'
    mat.shadow_method = 'CLIP'
    mat.alpha_threshold = 0.45

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    rgba_path = PROJECT_ROOT / "assets/textures/polyhaven/fern_02/fern_02_albedo_1k.png"
    norm_path = PROJECT_ROOT / "assets/models/polyhaven/fern_02/textures/fern_02_nor_gl_1k.jpg"
    arm_path = PROJECT_ROOT / "assets/models/polyhaven/fern_02/textures/fern_02_arm_1k.jpg"

    # Albedo + Alpha
    if rgba_path.exists():
        tex_albedo = nodes.new("ShaderNodeTexImage")
        tex_albedo.image = bpy.data.images.load(str(rgba_path))
        links.new(tex_albedo.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(tex_albedo.outputs["Alpha"], bsdf.inputs["Alpha"])

    # Normal Map
    if norm_path.exists():
        tex_norm = nodes.new("ShaderNodeTexImage")
        tex_norm.image = bpy.data.images.load(str(norm_path))
        tex_norm.image.colorspace_settings.name = "Non-Color"
        norm_map = nodes.new("ShaderNodeNormalMap")
        norm_map.inputs["Strength"].default_value = 1.2
        links.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
        links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])

    # Roughness
    if arm_path.exists():
        tex_arm = nodes.new("ShaderNodeTexImage")
        tex_arm.image = bpy.data.images.load(str(arm_path))
        tex_arm.image.colorspace_settings.name = "Non-Color"
        sep_color = nodes.new("ShaderNodeSeparateColor")
        links.new(tex_arm.outputs["Color"], sep_color.inputs["Color"])
        # Green channel in ARM is Roughness
        links.new(sep_color.outputs["Green"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.65

    # Scale to realistic 0.75m diameter cluster
    target_obj.scale = Vector((1.2, 1.2, 1.2))
    bpy.ops.object.transform_apply(scale=True)

    # Render inspection preview
    scene = bpy.context.scene
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 55.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector((0.7, -1.2, 0.75))
    direction = Vector((0.0, 0.0, 0.20)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Flashlight spot
    flash_data = bpy.data.lights.new(name="Flashlight", type="SPOT")
    flash_data.energy = 80.0
    flash_data.spot_size = math.radians(60)
    flash_data.color = (0.98, 0.95, 0.88)
    flash_obj = bpy.data.objects.new(name="Flashlight", object_data=flash_data)
    scene.collection.objects.link(flash_obj)
    flash_obj.location = cam_obj.location
    flash_obj.rotation_euler = cam_obj.rotation_euler

    # Moonlight fill
    moon_data = bpy.data.lights.new(name="Moonlight", type="SUN")
    moon_data.energy = 1.0
    moon_data.color = (0.75, 0.85, 1.0)
    moon_obj = bpy.data.objects.new(name="Moonlight", object_data=moon_data)
    scene.collection.objects.link(moon_obj)
    moon_obj.rotation_euler = (math.radians(50), math.radians(-25), math.radians(40))

    preview_path = PROJECT_ROOT / "docs/graphics/previews/blender_fern_preview.png"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered fern preview to {preview_path}")

    # Export GLB
    glb_path = PROJECT_ROOT / "assets/models/fern_cluster_sword.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported fern cluster GLB to {glb_path}")
    print("=== WESTERN SWORD FERN GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
