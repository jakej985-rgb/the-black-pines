import bpy
import bmesh
import math
import random
import os

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, color, roughness=0.7, metallic=0.0, transmission=0.0, texture_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if texture_path and os.path.exists(texture_path):
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = bpy.data.images.load(texture_path)
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        else:
            bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
    return mat

def export_glb(out_path, obj_name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        o.select_set(True)
    if bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
        bpy.ops.object.join()
        final_obj = bpy.context.active_object
        final_obj.name = obj_name
        # Apply all transforms prior to export
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True, export_yup=True)
        print(f"[Blender] Exported {obj_name} -> {out_path} ({len(final_obj.data.vertices)} verts)")

# =============================================================================
# 1. CABIN INTERIOR FURNITURE (Z-up, -Y front, +Y back)
# =============================================================================

def build_ranger_desk_and_chair(out_dir):
    reset_scene()
    mat_oak = create_pbr_material("Mat_RangerOak", (0.28, 0.19, 0.12, 1.0), roughness=0.70)
    mat_brass = create_pbr_material("Mat_DeskBrass", (0.75, 0.60, 0.22, 1.0), roughness=0.35, metallic=0.90)

    # 1. Desk Top (1.40m wide in X, 0.78m deep in Y, 0.05m thick in Z, top at Z = 0.76m)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.735))
    top = bpy.context.active_object
    top.scale = (1.40, 0.78, 0.05)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    top.data.materials.append(mat_oak)

    # 2. Left and Right Pedestals with Drawers
    for px in [-0.48, 0.48]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.355))
        ped = bpy.context.active_object
        ped.scale = (0.36, 0.72, 0.71)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ped.data.materials.append(mat_oak)

        # 3 Drawer faceplates facing front (-Y is front)
        for dz in [0.18, 0.38, 0.58]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.365, dz))
            df = bpy.context.active_object
            df.scale = (0.32, 0.015, 0.17)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            df.data.materials.append(mat_oak)

            # Brass cup pull handle
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.08, location=(px, -0.38, dz))
            handle = bpy.context.active_object
            handle.rotation_euler = (0, 1.5708, 0)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            handle.data.materials.append(mat_brass)

    # 3. Center Kneehole Back Modesty Panel (at +Y back)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.32, 0.42))
    panel = bpy.context.active_object
    panel.scale = (0.60, 0.02, 0.55)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    panel.data.materials.append(mat_oak)

    # 4. Ranger Chair (tucked into desk kneehole on the front side, -Y)
    chair_y = -0.55
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, chair_y, 0.44))
    seat = bpy.context.active_object
    seat.scale = (0.44, 0.42, 0.04)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    seat.data.materials.append(mat_oak)

    # 4 Chair legs
    for lx in [-0.18, 0.18]:
        for ly in [chair_y - 0.17, chair_y + 0.17]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.44, location=(lx, ly, 0.22))
            leg = bpy.context.active_object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            leg.data.materials.append(mat_oak)

    # Chair backrest posts & crest rail
    for bx in [-0.18, 0.18]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.48, location=(bx, chair_y - 0.17, 0.68))
        post = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        post.data.materials.append(mat_oak)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, chair_y - 0.17, 0.88))
    crest = bpy.context.active_object
    crest.scale = (0.42, 0.025, 0.08)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    crest.data.materials.append(mat_oak)

    export_glb(os.path.join(out_dir, "furniture_ranger_desk.glb"), "Furniture_RangerDesk")

def build_potbelly_woodstove(out_dir):
    reset_scene()
    mat_iron = create_pbr_material("Mat_CastIron", (0.14, 0.14, 0.15, 1.0), roughness=0.62, metallic=0.88)
    mat_hearth = create_pbr_material("Mat_HearthPlate", (0.18, 0.17, 0.16, 1.0), roughness=0.75, metallic=0.70)

    # 1. Heavy Hearth Base Plate (0.90m x 0.90m steel plate at Z = 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.015))
    hearth = bpy.context.active_object
    hearth.scale = (0.90, 0.90, 0.03)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    hearth.data.materials.append(mat_hearth)

    # 2. 4 Curved Iron Feet
    for fx in [-0.26, 0.26]:
        for fy in [-0.26, 0.26]:
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.045, radius2=0.02, depth=0.14, location=(fx, fy, 0.10))
            foot = bpy.context.active_object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            foot.data.materials.append(mat_iron)

    # 3. Potbelly Barrel Body (upright along Z)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.32, depth=0.45, location=(0, 0, 0.40))
    belly = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    belly.data.materials.append(mat_iron)

    # Upper tapered drum
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.32, radius2=0.22, depth=0.32, location=(0, 0, 0.76))
    upper = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    upper.data.materials.append(mat_iron)

    # 4. Firebox Door with Draft Slider (facing front, -Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.31, 0.44))
    door = bpy.context.active_object
    door.scale = (0.24, 0.04, 0.28)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    door.data.materials.append(mat_iron)

    # 5. Flue Pipe rising upright along Z to 2.4m
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=1.60, location=(0, 0, 1.70))
    pipe = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    pipe.data.materials.append(mat_iron)

    # Damper ring
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.105, depth=0.06, location=(0, 0, 1.40))
    damper = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    damper.data.materials.append(mat_iron)

    export_glb(os.path.join(out_dir, "furniture_woodstove.glb"), "Furniture_Woodstove")

def build_cot_and_bedding(out_dir):
    reset_scene()
    mat_timber = create_pbr_material("Mat_CotTimber", (0.28, 0.18, 0.11, 1.0), roughness=0.80)
    mat_canvas = create_pbr_material("Mat_CotCanvas", (0.58, 0.54, 0.42, 1.0), roughness=0.88)
    mat_blanket = create_pbr_material("Mat_WoolBlanket", (0.16, 0.24, 0.18, 1.0), roughness=0.92) # USFS Olive drab wool
    mat_pack = create_pbr_material("Mat_FieldPack", (0.35, 0.32, 0.24, 1.0), roughness=0.85)

    # 1. Folding Timber Cot Frame (1.95m long in Y, 0.82m wide in X, 0.40m high in Z)
    # Side rails
    for rx in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=1.95, location=(rx, 0, 0.40))
        rail = bpy.context.active_object
        rail.rotation_euler = (1.5708, 0, 0) # along Y
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        rail.data.materials.append(mat_timber)

    # End cross-bars
    for ry in [-0.95, 0.95]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.80, location=(0, ry, 0.40))
        bar = bpy.context.active_object
        bar.rotation_euler = (0, 1.5708, 0) # along X
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bar.data.materials.append(mat_timber)

    # 3 Sets of X-Legs (front, middle, back)
    for ly in [-0.75, 0.0, 0.75]:
        for ang in [-0.55, 0.55]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.022, depth=0.48, location=(0, ly, 0.20))
            leg = bpy.context.active_object
            leg.rotation_euler = (0, ang, 0)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            leg.data.materials.append(mat_timber)

    # 2. Heavy Taut Canvas Bed Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.40))
    canvas = bpy.context.active_object
    canvas.scale = (0.74, 1.88, 0.015)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    canvas.data.materials.append(mat_canvas)

    # 3. Folded USFS Wool Blanket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.25, 0.44))
    blanket = bpy.context.active_object
    blanket.scale = (0.70, 1.10, 0.065)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    blanket.data.materials.append(mat_blanket)

    # 4. Canvas Rucksack Placed at Head of Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.72, 0.48))
    pack = bpy.context.active_object
    pack.scale = (0.42, 0.30, 0.16)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    pack.data.materials.append(mat_pack)

    export_glb(os.path.join(out_dir, "furniture_cot.glb"), "Furniture_Cot")

def build_utility_shelving(out_dir):
    reset_scene()
    mat_pine = create_pbr_material("Mat_ShelfPine", (0.32, 0.22, 0.14, 1.0), roughness=0.82)
    mat_metal = create_pbr_material("Mat_SuppliesMetal", (0.45, 0.46, 0.48, 1.0), roughness=0.45, metallic=0.85)

    # 1. 4 Upright Corner Posts (1.80m tall in Z)
    w_shelf, d_shelf, h_shelf = 1.30, 0.42, 1.80
    for px in [-w_shelf*0.5 + 0.03, w_shelf*0.5 - 0.03]:
        for py in [-d_shelf*0.5 + 0.03, d_shelf*0.5 - 0.03]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, h_shelf*0.5))
            post = bpy.context.active_object
            post.scale = (0.05, 0.05, h_shelf)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            post.data.materials.append(mat_pine)

    # 2. 4 Horizontal Shelves
    for sz in [0.15, 0.65, 1.15, 1.65]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, sz))
        shelf = bpy.context.active_object
        shelf.scale = (w_shelf, d_shelf, 0.035)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        shelf.data.materials.append(mat_pine)

    # 3. Emergency Canned Rations on Middle Shelf (Z = 0.65)
    for cx in [-0.40, -0.20, 0.0, 0.20, 0.40]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=0.14, location=(cx, 0.0, 0.74))
        can = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        can.data.materials.append(mat_metal)

    # 4. Metal First Aid Box on Upper Shelf (Z = 1.15)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.35, 0.0, 1.28))
    f_aid = bpy.context.active_object
    f_aid.scale = (0.28, 0.20, 0.18)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    f_aid.data.materials.append(mat_metal)

    # Kerosene lantern
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.28, location=(0.30, 0.0, 1.31))
    lantern = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    lantern.data.materials.append(mat_metal)

    export_glb(os.path.join(out_dir, "furniture_shelving.glb"), "Furniture_Shelving")

def build_shortwave_radio(out_dir):
    reset_scene()
    mat_chassis = create_pbr_material("Mat_RadioChassis", (0.20, 0.24, 0.22, 1.0), roughness=0.55, metallic=0.7)
    mat_faceplate = create_pbr_material("Mat_RadioFaceplate", (0.12, 0.13, 0.14, 1.0), roughness=0.45)
    mat_dial = create_pbr_material("Mat_BacklitDial", (0.85, 0.88, 0.75, 1.0), roughness=0.3)
    mat_chrome = create_pbr_material("Mat_RadioChrome", (0.85, 0.86, 0.88, 1.0), roughness=0.2, metallic=0.95)

    # 1. Main Radio Housing Cabinet (0.52m wide in X, 0.34m deep in Y, 0.28m high in Z; base at Z = 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.14))
    cabinet = bpy.context.active_object
    cabinet.scale = (0.52, 0.34, 0.28)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    cabinet.data.materials.append(mat_chassis)

    # 2. Recessed Front Faceplate (-Y is front)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.175, 0.14))
    face = bpy.context.active_object
    face.scale = (0.48, 0.015, 0.24)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    face.data.materials.append(mat_faceplate)

    # 3. Illuminated Analog Frequency Tuning Scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.08, -0.185, 0.18))
    scale_dial = bpy.context.active_object
    scale_dial.scale = (0.26, 0.01, 0.09)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    scale_dial.data.materials.append(mat_dial)

    # 4. Rotary Tuning Knobs
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.038, depth=0.03, location=(0.14, -0.19, 0.18))
    knob = bpy.context.active_object
    knob.rotation_euler = (1.5708, 0, 0) # facing -Y
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    knob.data.materials.append(mat_chrome)

    # 5. Microphone Handset on Side Cradle
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.30, -0.12, 0.12))
    mic = bpy.context.active_object
    mic.scale = (0.05, 0.06, 0.14)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mic.data.materials.append(mat_chassis)

    # 6. Telescopic Antenna rising upright along Z to 0.85m
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.007, depth=0.70, location=(-0.22, 0.12, 0.63))
    ant = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ant.data.materials.append(mat_chrome)

    export_glb(os.path.join(out_dir, "prop_shortwave_radio.glb"), "Prop_ShortwaveRadio")

# =============================================================================
# 2. INVESTIGATION DOCUMENTS & CLUES (Z-up, -Y front / viewer, +Y wall)
# =============================================================================

def build_evacuation_notice(out_dir, tex_dir):
    reset_scene()
    tex_path = os.path.join(tex_dir, "prop_doc_evacuation_notice.png")
    mat_plaque = create_pbr_material("Mat_PlaqueWood", (0.22, 0.16, 0.11, 1.0), roughness=0.85)
    mat_paper = create_pbr_material("Mat_EvacPaper", (0.90, 0.88, 0.82, 1.0), roughness=0.90, texture_path=tex_path)
    mat_tack = create_pbr_material("Mat_RustedIron", (0.28, 0.22, 0.20, 1.0), roughness=0.55, metallic=0.75)

    # Plaque backing: centered at origin, width 0.52m in X, height 0.72m in Z, thickness 0.035m in Y
    # Back of plaque at Y = +0.0175 (against wall), Front at Y = -0.0175 (facing viewer)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    plaque = bpy.context.active_object
    plaque.scale = (0.52, 0.035, 0.72)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    plaque.data.materials.append(mat_plaque)

    # Paper Sheet on front face (at Y = -0.020, facing -Y towards the viewer)
    # UV mapping: (0, 0) bottom-left, (1, 1) top-right
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    w, h = 0.44, 0.62
    y_paper = -0.020

    # Vertices (X, Y, Z) - paper facing -Y towards viewer
    # Counter-clockwise when viewed from -Y looking towards +Y:
    # bottom-right -> bottom-left -> top-left -> top-right
    v0 = bm.verts.new(( w*0.5, y_paper, -h*0.5)) # bottom-right
    v1 = bm.verts.new((-w*0.5, y_paper, -h*0.5)) # bottom-left
    v2 = bm.verts.new((-w*0.5, y_paper,  h*0.5)) # top-left
    v3 = bm.verts.new(( w*0.5, y_paper,  h*0.5)) # top-right

    face = bm.faces.new([v0, v1, v2, v3])
    for loop in face.loops:
        if loop.vert == v0: loop[uv_layer].uv = (1.0, 0.0)
        elif loop.vert == v1: loop[uv_layer].uv = (0.0, 0.0)
        elif loop.vert == v2: loop[uv_layer].uv = (0.0, 1.0)
        elif loop.vert == v3: loop[uv_layer].uv = (1.0, 1.0)

    p_mesh = bpy.data.meshes.new("PaperMesh")
    bm.to_mesh(p_mesh)
    bm.free()
    p_obj = bpy.data.objects.new("EvacPaper", p_mesh)
    bpy.context.collection.objects.link(p_obj)
    p_obj.data.materials.append(mat_paper)

    # 4 Rusted iron tacks at corners
    for tx in [-0.20, 0.20]:
        for tz in [-0.28, 0.28]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.015, location=(tx, y_paper - 0.005, tz))
            tack = bpy.context.active_object
            tack.rotation_euler = (1.5708, 0, 0) # along Y
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            tack.data.materials.append(mat_tack)

    export_glb(os.path.join(out_dir, "prop_evacuation_notice.glb"), "Prop_EvacuationNotice")

def build_field_journal(out_dir, tex_dir):
    reset_scene()
    tex_path = os.path.join(tex_dir, "prop_doc_field_journal.png")
    mat_leather = create_pbr_material("Mat_JournalLeather", (0.16, 0.10, 0.07, 1.0), roughness=0.78)
    mat_paper = create_pbr_material("Mat_JournalPaper", (0.88, 0.84, 0.74, 1.0), roughness=0.90, texture_path=tex_path)
    mat_ribbon = create_pbr_material("Mat_BookmarkRibbon", (0.50, 0.10, 0.08, 1.0), roughness=0.6)

    # Lying flat on desk: width in X (0.52m), depth in Y (0.38m), height in Z (0.025m)
    # 1. Leather Binder Cover (base at Z = 0)
    for (side_x, rot_y) in [(-0.14, 0.06), (0.14, -0.06)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side_x, 0, 0.006))
        c = bpy.context.active_object
        c.scale = (0.26, 0.38, 0.012)
        c.rotation_euler = (0, rot_y, 0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        c.data.materials.append(mat_leather)

    # Spine
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.38, location=(0, 0, 0.006))
    spine = bpy.context.active_object
    spine.rotation_euler = (1.5708, 0, 0) # along Y
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    spine.data.materials.append(mat_leather)

    # 2. Open Pages with UV mapping (facing +Z upward towards reader)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    # Left page quad: X in [-0.25, -0.01], Y in [-0.17, 0.17], Z = 0.016
    v0 = bm.verts.new((-0.25, -0.17, 0.016))
    v1 = bm.verts.new((-0.01, -0.17, 0.014))
    v2 = bm.verts.new((-0.01,  0.17, 0.014))
    v3 = bm.verts.new((-0.25,  0.17, 0.016))
    f_left = bm.faces.new([v0, v1, v2, v3])
    for loop in f_left.loops:
        if loop.vert == v0: loop[uv_layer].uv = (0.02, 0.02)
        elif loop.vert == v1: loop[uv_layer].uv = (0.48, 0.02)
        elif loop.vert == v2: loop[uv_layer].uv = (0.48, 0.98)
        elif loop.vert == v3: loop[uv_layer].uv = (0.02, 0.98)

    # Right page quad: X in [0.01, 0.25], Y in [-0.17, 0.17], Z = 0.016
    v4 = bm.verts.new((0.01, -0.17, 0.014))
    v5 = bm.verts.new((0.25, -0.17, 0.016))
    v6 = bm.verts.new((0.25,  0.17, 0.016))
    v7 = bm.verts.new((0.01,  0.17, 0.014))
    f_right = bm.faces.new([v4, v5, v6, v7])
    for loop in f_right.loops:
        if loop.vert == v4: loop[uv_layer].uv = (0.52, 0.02)
        elif loop.vert == v5: loop[uv_layer].uv = (0.98, 0.02)
        elif loop.vert == v6: loop[uv_layer].uv = (0.98, 0.98)
        elif loop.vert == v7: loop[uv_layer].uv = (0.52, 0.98)

    p_mesh = bpy.data.meshes.new("JournalPages")
    bm.to_mesh(p_mesh)
    bm.free()
    p_obj = bpy.data.objects.new("JournalPages", p_mesh)
    bpy.context.collection.objects.link(p_obj)
    p_obj.data.materials.append(mat_paper)

    # Crimson Bookmark ribbon lying across right page
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.06, 0.02, 0.020))
    ribbon = bpy.context.active_object
    ribbon.scale = (0.016, 0.40, 0.003)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ribbon.data.materials.append(mat_ribbon)

    export_glb(os.path.join(out_dir, "prop_field_journal.glb"), "Prop_FieldJournal")

def build_topomap(out_dir, tex_dir):
    reset_scene()
    tex_path = os.path.join(tex_dir, "prop_doc_topomap.png")
    mat_map = create_pbr_material("Mat_TopoPaper", (0.84, 0.82, 0.72, 1.0), roughness=0.92, texture_path=tex_path)
    mat_pin = create_pbr_material("Mat_BrassPin", (0.85, 0.65, 0.20, 1.0), roughness=0.35, metallic=0.9)

    # Pinned vertically on wall (facing -Y towards room/viewer)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    w, h = 0.90, 0.64
    y_map = 0.0

    v0 = bm.verts.new(( w*0.5, y_map, -h*0.5))
    v1 = bm.verts.new((-w*0.5, y_map, -h*0.5))
    v2 = bm.verts.new((-w*0.5, y_map,  h*0.5))
    v3 = bm.verts.new(( w*0.5, y_map,  h*0.5))
    face = bm.faces.new([v0, v1, v2, v3])
    for loop in face.loops:
        if loop.vert == v0: loop[uv_layer].uv = (1.0, 0.0)
        elif loop.vert == v1: loop[uv_layer].uv = (0.0, 0.0)
        elif loop.vert == v2: loop[uv_layer].uv = (0.0, 1.0)
        elif loop.vert == v3: loop[uv_layer].uv = (1.0, 1.0)

    mesh = bpy.data.meshes.new("MapMesh")
    bm.to_mesh(mesh)
    bm.free()
    map_obj = bpy.data.objects.new("TopoMap", mesh)
    bpy.context.collection.objects.link(map_obj)
    map_obj.data.materials.append(mat_map)

    # 4 Brass pins at corners
    for px in [-0.42, 0.42]:
        for pz in [-0.29, 0.29]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.010, location=(px, -0.008, pz))
            pin = bpy.context.active_object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            pin.data.materials.append(mat_pin)

    export_glb(os.path.join(out_dir, "prop_topomap.glb"), "Prop_TopoMap")

def build_plaster_cast(out_dir):
    reset_scene()
    mat_plaster = create_pbr_material("Mat_PlasterCast", (0.86, 0.84, 0.78, 1.0), roughness=0.88)
    mat_tag = create_pbr_material("Mat_ManilaTag", (0.75, 0.68, 0.52, 1.0), roughness=0.85)

    # Heavy rectangular plaster slab lying flat: base at Z = 0, height 0.045m, width 0.32m, length 0.58m
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.0225))
    slab = bpy.context.active_object
    slab.scale = (0.32, 0.58, 0.045)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    slab.data.materials.append(mat_plaster)

    # Sculpted 18.5" Footprint Imprint (depressed into top face at Z = 0.045)
    # Heel depression
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.075, location=(0, -0.16, 0.040))
    heel = bpy.context.active_object
    heel.scale = (1.0, 1.3, 0.35)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    heel.data.materials.append(mat_plaster)

    # Midfoot / Ball depression
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.09, location=(0.01, 0.05, 0.038))
    ball = bpy.context.active_object
    ball.scale = (1.1, 1.4, 0.35)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ball.data.materials.append(mat_plaster)

    # 5 Splayed Toes
    toe_offsets = [(-0.08, 0.20, 0.028), (-0.035, 0.22, 0.026), (0.01, 0.23, 0.025), (0.05, 0.22, 0.024), (0.085, 0.19, 0.022)]
    for tx, ty, r in toe_offsets:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=r, location=(tx, ty, 0.042))
        toe = bpy.context.active_object
        toe.scale = (1.0, 1.2, 0.4)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        toe.data.materials.append(mat_plaster)

    # Manila evidence label tag wired to side
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.14, -0.22, 0.046))
    tag = bpy.context.active_object
    tag.scale = (0.08, 0.14, 0.002)
    tag.rotation_euler = (0, 0, 0.2)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    tag.data.materials.append(mat_tag)

    export_glb(os.path.join(out_dir, "prop_plaster_cast.glb"), "Prop_PlasterCast")

def build_evidence_jar(out_dir):
    reset_scene()
    mat_glass = create_pbr_material("Mat_JarGlass", (0.92, 0.95, 0.93, 0.4), roughness=0.10, transmission=0.85)
    mat_lid = create_pbr_material("Mat_ZincLid", (0.50, 0.52, 0.54, 1.0), roughness=0.45, metallic=0.8)
    mat_hair = create_pbr_material("Mat_CryptidHair", (0.10, 0.07, 0.05, 1.0), roughness=0.85)

    # Glass specimen jar upright along Z: base at Z = 0, height 0.20m, radius 0.065m
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.18, location=(0, 0, 0.09))
    body = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    body.data.materials.append(mat_glass)

    # Zinc screw band & lid at top
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.068, depth=0.025, location=(0, 0, 0.19))
    lid = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    lid.data.materials.append(mat_lid)

    # Clump of coarse cryptid fur hair inside jar
    for hx, hy, hz in [(-0.015, 0.01, 0.06), (0.01, -0.01, 0.09), (0.0, 0.02, 0.12)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.035, location=(hx, hy, hz))
        clump = bpy.context.active_object
        clump.scale = (0.7, 0.8, 1.2)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        clump.data.materials.append(mat_hair)

    export_glb(os.path.join(out_dir, "prop_evidence_jar.glb"), "Prop_EvidenceJar")

def build_rifle_casings(out_dir):
    reset_scene()
    mat_brass = create_pbr_material("Mat_CasingBrass", (0.80, 0.65, 0.25, 1.0), roughness=0.32, metallic=0.92)

    # 3 spent .30-06 cartridges scattered on floorboards (base at Z = 0)
    casings_data = [
        (-0.08, -0.04, 0.35),
        ( 0.04,  0.02, -0.65),
        ( 0.10, -0.06, 1.10)
    ]
    for cx, cy, rot_z in casings_data:
        # Cartridge body
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.010, depth=0.063, location=(cx, cy, 0.010))
        casing = bpy.context.active_object
        casing.rotation_euler = (1.5708, 0, rot_z) # lying flat
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        casing.data.materials.append(mat_brass)

        # Extractor rim & rim groove
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=0.008, location=(cx, cy, 0.010))
        rim = bpy.context.active_object
        rim.rotation_euler = (1.5708, 0, rot_z)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        rim.data.materials.append(mat_brass)

    export_glb(os.path.join(out_dir, "prop_rifle_casings.glb"), "Prop_RifleCasings")

if __name__ == "__main__":
    out_dir = "/home/m3tal/apps/the-black-pines/assets/models"
    tex_dir = "/home/m3tal/apps/the-black-pines/assets/textures"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_dir, exist_ok=True)

    print("Building Photorealistic PBR Assets in Blender LTS...")
    build_ranger_desk_and_chair(out_dir)
    build_potbelly_woodstove(out_dir)
    build_cot_and_bedding(out_dir)
    build_utility_shelving(out_dir)
    build_shortwave_radio(out_dir)
    build_evacuation_notice(out_dir, tex_dir)
    build_field_journal(out_dir, tex_dir)
    build_topomap(out_dir, tex_dir)
    build_plaster_cast(out_dir)
    build_evidence_jar(out_dir)
    build_rifle_casings(out_dir)
    print("All assets successfully built and exported!")
