import bpy
import math
import random
import os

def create_spike_trap():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 1. Materials
    mat_wood = bpy.data.materials.new(name="Mat_TrapWood")
    mat_wood.use_nodes = True
    bsdf_w = mat_wood.node_tree.nodes.get("Principled BSDF")
    if bsdf_w:
        bsdf_w.inputs["Base Color"].default_value = (0.24, 0.17, 0.12, 1.0)
        bsdf_w.inputs["Roughness"].default_value = 0.85

    mat_metal = bpy.data.materials.new(name="Mat_TrapSpikes")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf_m:
        bsdf_m.inputs["Base Color"].default_value = (0.30, 0.24, 0.22, 1.0)
        bsdf_m.inputs["Metallic"].default_value = 0.8
        bsdf_m.inputs["Roughness"].default_value = 0.5

    objects_to_join = []

    # Planks (3 longitudinal, 2 cross braces)
    plank_configs = [
        ((-0.35, 0.0, 0.025), (0.18, 1.2, 0.05), 0.02),
        ((0.0, 0.0, 0.025), (0.19, 1.18, 0.05), -0.01),
        ((0.35, 0.0, 0.025), (0.18, 1.22, 0.05), 0.03),
        ((0.0, -0.42, 0.065), (1.1, 0.16, 0.04), 0.0),
        ((0.0, 0.42, 0.065), (1.1, 0.16, 0.04), 0.0)
    ]

    for idx, (pos, scale, rot_z) in enumerate(plank_configs):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
        plank = bpy.context.active_object
        plank.name = f"Plank_{idx}"
        plank.scale = scale
        plank.rotation_euler = (0, 0, rot_z)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        plank.data.materials.append(mat_wood)
        objects_to_join.append(plank)

    # 9 Sharp Jagged Spikes
    spike_positions = [
        (-0.35, -0.28, 0.16), (-0.33, 0.15, 0.17), (-0.36, 0.45, 0.16),
        (0.02, -0.35, 0.18), (0.0, 0.0, 0.20), (0.01, 0.38, 0.17),
        (0.34, -0.38, 0.16), (0.36, 0.12, 0.17), (0.33, 0.42, 0.18)
    ]

    for s_idx, (sx, sy, sz) in enumerate(spike_positions):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.03, radius2=0.004, depth=0.25, location=(sx, sy, sz))
        spike = bpy.context.active_object
        spike.name = f"Spike_{s_idx}"
        spike.rotation_euler = (random.uniform(-0.12, 0.12), random.uniform(-0.12, 0.12), random.uniform(0, 3.14))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        spike.data.materials.append(mat_metal)
        objects_to_join.append(spike)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_to_join:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects_to_join[0]
    bpy.ops.object.join()
    trap = bpy.context.active_object
    trap.name = "TrapSpike"

    # Export GLB
    out_dir = "/home/m3tal/apps/the-black-pines/assets/models"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "trap_spike.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Trap Spike to {out_path} ({len(trap.data.vertices)} vertices)")

def create_active_flare():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Flare Materials
    mat_casing = bpy.data.materials.new(name="Mat_FlareCasing")
    mat_casing.use_nodes = True
    bsdf_c = mat_casing.node_tree.nodes.get("Principled BSDF")
    if bsdf_c:
        bsdf_c.inputs["Base Color"].default_value = (0.78, 0.12, 0.08, 1.0) # Bright warning red
        bsdf_c.inputs["Roughness"].default_value = 0.6

    mat_burn = bpy.data.materials.new(name="Mat_FlareBurningHead")
    mat_burn.use_nodes = True
    bsdf_b = mat_burn.node_tree.nodes.get("Principled BSDF")
    if bsdf_b:
        bsdf_b.inputs["Base Color"].default_value = (1.0, 0.9, 0.4, 1.0)
        bsdf_b.inputs["Emission Color"].default_value = (1.0, 0.25, 0.05, 1.0)
        bsdf_b.inputs["Emission Strength"].default_value = 5.0

    objects = []

    # Main flare tube (angled on ground)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.035, depth=0.32, location=(0, 0, 0.035))
    tube = bpy.context.active_object
    tube.name = "FlareTube"
    tube.rotation_euler = (0, 1.45, 0.2) # laying slightly propped on ground
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    tube.data.materials.append(mat_casing)
    objects.append(tube)

    # Burning tip
    tip_loc = (0.15, 0.03, 0.06)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.033, depth=0.06, location=tip_loc)
    tip = bpy.context.active_object
    tip.name = "FlareBurningTip"
    tip.rotation_euler = (0, 1.45, 0.2)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    tip.data.materials.append(mat_burn)
    objects.append(tip)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    flare = bpy.context.active_object
    flare.name = "ActiveFlare"

    out_dir = "/home/m3tal/apps/the-black-pines/assets/models"
    out_path = os.path.join(out_dir, "active_flare.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Active Flare to {out_path} ({len(flare.data.vertices)} vertices)")

if __name__ == "__main__":
    create_spike_trap()
    create_active_flare()
