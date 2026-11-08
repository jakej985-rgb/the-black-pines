import bpy
import bmesh
import math
import random
import os

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def build_ranger_desk_and_chair(out_dir):
    reset_scene()

    mat_oak = create_pbr_material("Mat_RangerOak", (0.28, 0.19, 0.12, 1.0), roughness=0.70)
    mat_brass = create_pbr_material("Mat_DeskBrass", (0.75, 0.60, 0.22, 1.0), roughness=0.35, metallic=0.90)

    objects = []

    # 1. Desk Top (1.40m wide, 0.78m deep, 0.05m thick at height 0.76m)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.735, 0))
    top = bpy.context.active_object
    top.scale = (1.40, 0.05, 0.78)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bevel = top.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    top.data.materials.append(mat_oak)
    objects.append(top)

    # 2. Left and Right Pedestals (Drawers)
    for px in [-0.48, 0.48]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.35, 0))
        ped = bpy.context.active_object
        ped.scale = (0.36, 0.70, 0.72)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ped.data.materials.append(mat_oak)
        objects.append(ped)

        # 3 Drawer faceplates with brass pulls
        for dy in [0.18, 0.38, 0.58]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, dy, 0.365))
            df = bpy.context.active_object
            df.scale = (0.32, 0.17, 0.015)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            df.data.materials.append(mat_oak)
            objects.append(df)

            # Brass pull handle
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.08, location=(px, dy, 0.38))
            handle = bpy.context.active_object
            handle.rotation_euler = (0, 1.5708, 0)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            handle.data.materials.append(mat_brass)
            objects.append(handle)

    # 3. Center Kneehole Back Panel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.42, -0.32))
    panel = bpy.context.active_object
    panel.scale = (0.60, 0.55, 0.02)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    panel.data.materials.append(mat_oak)
    objects.append(panel)

    # 4. Matching Ranger Chair (tucked into desk)
    chair_z = 0.55
    # Chair seat
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.44, chair_z))
    seat = bpy.context.active_object
    seat.scale = (0.44, 0.04, 0.42)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    seat.data.materials.append(mat_oak)
    objects.append(seat)

    # 4 Chair legs
    for lx in [-0.18, 0.18]:
        for lz in [chair_z - 0.17, chair_z + 0.17]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.44, location=(lx, 0.22, lz))
            leg = bpy.context.active_object
            leg.data.materials.append(mat_oak)
            objects.append(leg)

    # Chair backrest posts & slats
    for bx in [-0.18, 0.18]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.48, location=(bx, 0.68, chair_z + 0.17))
        post = bpy.context.active_object
        post.data.materials.append(mat_oak)
        objects.append(post)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.86, chair_z + 0.17))
    crest = bpy.context.active_object
    crest.scale = (0.42, 0.08, 0.025)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    crest.data.materials.append(mat_oak)
    objects.append(crest)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Furniture_RangerDesk"

    out_path = os.path.join(out_dir, "furniture_ranger_desk.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Ranger Desk & Chair -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_potbelly_woodstove(out_dir):
    reset_scene()

    mat_iron = create_pbr_material("Mat_CastIronStove", (0.18, 0.18, 0.20, 1.0), roughness=0.65, metallic=0.75)
    mat_hearth = create_pbr_material("Mat_HearthPlate", (0.14, 0.14, 0.15, 1.0), roughness=0.85)

    objects = []

    # 1. Hearth Base Plate (0.90m x 0.90m steel plate)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.015, 0))
    hearth = bpy.context.active_object
    hearth.scale = (0.90, 0.03, 0.90)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    hearth.data.materials.append(mat_hearth)
    objects.append(hearth)

    # 2. 4 Curved Iron Feet
    for fx in [-0.26, 0.26]:
        for fz in [-0.26, 0.26]:
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.045, radius2=0.02, depth=0.14, location=(fx, 0.10, fz))
            foot = bpy.context.active_object
            foot.data.materials.append(mat_iron)
            objects.append(foot)

    # 3. Potbelly Barrel Body (rounded cylindrical belly)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.32, depth=0.45, location=(0, 0.40, 0))
    belly = bpy.context.active_object
    belly.data.materials.append(mat_iron)
    objects.append(belly)

    # Upper tapered drum
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.32, radius2=0.22, depth=0.32, location=(0, 0.76, 0))
    upper = bpy.context.active_object
    upper.data.materials.append(mat_iron)
    objects.append(upper)

    # 4. Firebox Door with Draft Slider
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.44, 0.31))
    door = bpy.context.active_object
    door.scale = (0.24, 0.28, 0.04)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    door.data.materials.append(mat_iron)
    objects.append(door)

    # 5. Flue Pipe rising 2.2m to ceiling
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=2.0, location=(0, 1.90, 0))
    pipe = bpy.context.active_object
    pipe.data.materials.append(mat_iron)
    objects.append(pipe)

    # Pipe collar damper
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.105, depth=0.06, location=(0, 1.40, 0))
    damper = bpy.context.active_object
    damper.data.materials.append(mat_iron)
    objects.append(damper)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Furniture_Woodstove"

    out_path = os.path.join(out_dir, "furniture_woodstove.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Potbelly Woodstove -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_cot_and_bedding(out_dir):
    reset_scene()

    mat_frame = create_pbr_material("Mat_CotTimber", (0.35, 0.25, 0.16, 1.0), roughness=0.80)
    mat_canvas = create_pbr_material("Mat_CotCanvas", (0.65, 0.60, 0.48, 1.0), roughness=0.90)
    mat_wool = create_pbr_material("Mat_WoolBlanket", (0.24, 0.32, 0.22, 1.0), roughness=0.95) # USFS forest green wool
    mat_pack = create_pbr_material("Mat_CanvasRucksack", (0.42, 0.35, 0.24, 1.0), roughness=0.85)

    objects = []

    # 1. Folding Timber Cot Frame (1.95m long, 0.80m wide, 0.42m high)
    # Side rails
    for rx in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, 0.40, 0))
        rail = bpy.context.active_object
        rail.scale = (0.05, 0.05, 1.95)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        rail.data.materials.append(mat_frame)
        objects.append(rail)

    # 3 pairs of scissor legs
    for lz in [-0.75, 0.0, 0.75]:
        for lx in [-0.36, 0.36]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, 0.20, lz))
            leg = bpy.context.active_object
            leg.scale = (0.04, 0.40, 0.04)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            leg.data.materials.append(mat_frame)
            objects.append(leg)

    # 2. Taut Canvas Bed Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.40, 0))
    canvas = bpy.context.active_object
    canvas.scale = (0.72, 0.015, 1.90)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    canvas.data.materials.append(mat_canvas)
    objects.append(canvas)

    # 3. Folded USFS Wool Blanket draped at foot of cot
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.47, 0.55))
    blanket = bpy.context.active_object
    blanket.scale = (0.70, 0.12, 0.65)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    blanket.data.materials.append(mat_wool)
    objects.append(blanket)

    # 4. Canvas Rucksack resting against side of cot
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.50, 0.22, -0.40))
    pack = bpy.context.active_object
    pack.scale = (0.24, 0.42, 0.35)
    pack.rotation_euler = (0.1, 0, -0.15)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    pack.data.materials.append(mat_pack)
    objects.append(pack)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Furniture_Cot"

    out_path = os.path.join(out_dir, "furniture_cot.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Ranger Cot & Bedding -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_utility_shelving(out_dir):
    reset_scene()

    mat_pine = create_pbr_material("Mat_ShelfPine", (0.32, 0.22, 0.14, 1.0), roughness=0.82)
    mat_metal = create_pbr_material("Mat_SuppliesMetal", (0.45, 0.46, 0.48, 1.0), roughness=0.45, metallic=0.85)

    objects = []

    # 1. 4 Upright Corner Posts (1.80m tall)
    w_shelf, d_shelf, h_shelf = 1.30, 0.42, 1.80
    for px in [-w_shelf*0.5 + 0.03, w_shelf*0.5 - 0.03]:
        for pz in [-d_shelf*0.5 + 0.03, d_shelf*0.5 - 0.03]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, h_shelf*0.5, pz))
            post = bpy.context.active_object
            post.scale = (0.05, h_shelf, 0.05)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            post.data.materials.append(mat_pine)
            objects.append(post)

    # 2. 4 Horizontal Shelves
    for sy in [0.15, 0.65, 1.15, 1.65]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sy, 0))
        shelf = bpy.context.active_object
        shelf.scale = (w_shelf, 0.035, d_shelf)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        shelf.data.materials.append(mat_pine)
        objects.append(shelf)

    # 3. Emergency Canned Rations on Middle Shelf
    for cx in [-0.40, -0.22, -0.04, 0.14, 0.32]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=0.14, location=(cx, 0.74, 0.0))
        can = bpy.context.active_object
        can.data.materials.append(mat_metal)
        objects.append(can)

    # 4. Kerosene Lantern & Metal First Aid Box on Upper Shelf
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.35, 1.28, 0.0))
    f_aid = bpy.context.active_object
    f_aid.scale = (0.28, 0.18, 0.20)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    f_aid.data.materials.append(mat_metal)
    objects.append(f_aid)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.30, location=(0.30, 1.32, 0.0))
    lantern = bpy.context.active_object
    lantern.data.materials.append(mat_metal)
    objects.append(lantern)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Furniture_Shelving"

    out_path = os.path.join(out_dir, "furniture_shelving.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Utility Shelving -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_shortwave_radio(out_dir):
    reset_scene()

    mat_chassis = create_pbr_material("Mat_RadioChassis", (0.20, 0.24, 0.22, 1.0), roughness=0.55, metallic=0.7) # Military olive-drab steel
    mat_faceplate = create_pbr_material("Mat_RadioFaceplate", (0.12, 0.13, 0.14, 1.0), roughness=0.45)
    mat_dial = create_pbr_material("Mat_BacklitDial", (0.85, 0.88, 0.75, 1.0), roughness=0.3)
    mat_chrome = create_pbr_material("Mat_RadioChrome", (0.85, 0.86, 0.88, 1.0), roughness=0.2, metallic=0.95)

    objects = []

    # 1. Main Radio Housing Cabinet (0.52m wide, 0.28m high, 0.34m deep)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.14, 0))
    cabinet = bpy.context.active_object
    cabinet.scale = (0.52, 0.28, 0.34)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bevel = cabinet.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    cabinet.data.materials.append(mat_chassis)
    objects.append(cabinet)

    # 2. Recessed Front Faceplate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.14, 0.175))
    face = bpy.context.active_object
    face.scale = (0.48, 0.24, 0.015)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    face.data.materials.append(mat_faceplate)
    objects.append(face)

    # 3. Illuminated Analog Frequency Tuning Scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.08, 0.18, 0.185))
    scale_dial = bpy.context.active_object
    scale_dial.scale = (0.26, 0.09, 0.01)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    scale_dial.data.materials.append(mat_dial)
    objects.append(scale_dial)

    # 4. Large Rotary Tuning Knob
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.038, depth=0.03, location=(0.14, 0.18, 0.19))
    knob = bpy.context.active_object
    knob.rotation_euler = (1.5708, 0, 0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    knob.data.materials.append(mat_chrome)
    objects.append(knob)

    # 5. Microphone Handset on Side Cradle
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.30, 0.12, 0.12))
    mic = bpy.context.active_object
    mic.scale = (0.05, 0.14, 0.06)
    mic.rotation_euler = (0.2, 0, -0.1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mic.data.materials.append(mat_chassis)
    objects.append(mic)

    # 6. Telescopic Antenna rising 0.85m
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.007, depth=0.85, location=(-0.22, 0.68, -0.12))
    ant = bpy.context.active_object
    ant.data.materials.append(mat_chrome)
    objects.append(ant)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Prop_ShortwaveRadio"

    out_path = os.path.join(out_dir, "prop_shortwave_radio.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Shortwave Radio -> {out_path} ({len(final_obj.data.vertices)} verts)")

if __name__ == "__main__":
    out_dir = "/home/m3tal/apps/the-black-pines/assets/models"
    os.makedirs(out_dir, exist_ok=True)
    build_ranger_desk_and_chair(out_dir)
    build_potbelly_woodstove(out_dir)
    build_cot_and_bedding(out_dir)
    build_utility_shelving(out_dir)
    build_shortwave_radio(out_dir)
