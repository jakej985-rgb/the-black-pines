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

def build_evacuation_notice(out_dir, tex_dir):
    reset_scene()

    tex_path = os.path.join(tex_dir, "prop_doc_evacuation_notice.png")
    mat_plaque = create_pbr_material("Mat_PlaqueWood", (0.22, 0.16, 0.11, 1.0), roughness=0.85)
    mat_paper = create_pbr_material("Mat_EvacPaper", (0.90, 0.88, 0.82, 1.0), roughness=0.90, texture_path=tex_path)
    mat_tack = create_pbr_material("Mat_RustedIron", (0.28, 0.22, 0.20, 1.0), roughness=0.55, metallic=0.75)

    objects = []

    # 1. Weathered Cedar Notice Board Backing (0.52m wide, 0.72m high, 0.035m thick)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    plaque = bpy.context.active_object
    plaque.name = "Plaque"
    plaque.scale = (0.52, 0.035, 0.72)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bevel = plaque.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    plaque.data.materials.append(mat_plaque)
    objects.append(plaque)

    # 2. Curled & Weathered Document Sheet with exact UV mapping
    bm = bmesh.new()
    res_x, res_y = 10, 14
    w, h = 0.42, 0.60
    y_paper = 0.020

    verts_grid = []
    for iy in range(res_y):
        row = []
        frac_y = float(iy) / (res_y - 1)
        v_y = (frac_y - 0.5) * h
        for ix in range(res_x):
            frac_x = float(ix) / (res_x - 1)
            v_x = (frac_x - 0.5) * w
            v_z = y_paper
            # Organic curl at bottom
            if iy < 4:
                v_z += (4 - iy) * 0.003 * (1.0 + abs(v_x) * 3.5)
            # Torn bottom right corner
            if ix >= res_x - 2 and iy <= 1:
                v_x -= 0.02
                v_y += 0.025
            vert = bm.verts.new((v_x, v_z, v_y))
            row.append((vert, frac_x, frac_y))
        verts_grid.append(row)

    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    for iy in range(res_y - 1):
        for ix in range(res_x - 1):
            if ix == res_x - 2 and iy == 0:
                continue # Skip torn corner
            v0, u0, f_y0 = verts_grid[iy][ix]
            v1, u1, f_y1 = verts_grid[iy][ix + 1]
            v2, u2, f_y2 = verts_grid[iy + 1][ix + 1]
            v3, u3, f_y3 = verts_grid[iy + 1][ix]

            face = bm.faces.new([v0, v1, v2, v3])
            for loop in face.loops:
                if loop.vert == v0:
                    loop[uv_layer].uv = (u0, f_y0)
                elif loop.vert == v1:
                    loop[uv_layer].uv = (u1, f_y1)
                elif loop.vert == v2:
                    loop[uv_layer].uv = (u2, f_y2)
                elif loop.vert == v3:
                    loop[uv_layer].uv = (u3, f_y3)

    paper_mesh = bpy.data.meshes.new("EvacPaperMesh")
    bm.to_mesh(paper_mesh)
    bm.free()

    paper_obj = bpy.data.objects.new("EvacPaper", paper_mesh)
    bpy.context.collection.objects.link(paper_obj)
    paper_obj.data.materials.append(mat_paper)

    solid = paper_obj.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.0015
    bpy.context.view_layer.objects.active = paper_obj
    bpy.ops.object.modifier_apply(modifier="Solidify")
    objects.append(paper_obj)

    # 3. 4 Rusted Iron Mounting Tacks
    for (tx, ty, tz) in [(-0.17, 0.025, 0.26), (0.17, 0.025, 0.26), (-0.18, 0.025, 0.0), (0.18, 0.025, 0.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.008, location=(tx, ty, tz))
        tack = bpy.context.active_object
        tack.rotation_euler = (1.5708, 0, 0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        tack.data.materials.append(mat_tack)
        objects.append(tack)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Prop_EvacuationNotice"

    out_path = os.path.join(out_dir, "prop_evacuation_notice.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Textured Evacuation Notice -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_field_journal(out_dir, tex_dir):
    reset_scene()

    tex_path = os.path.join(tex_dir, "prop_doc_field_journal.png")
    mat_leather = create_pbr_material("Mat_JournalLeather", (0.16, 0.10, 0.07, 1.0), roughness=0.78)
    mat_paper = create_pbr_material("Mat_JournalPaper", (0.88, 0.84, 0.74, 1.0), roughness=0.90, texture_path=tex_path)
    mat_ribbon = create_pbr_material("Mat_BookmarkRibbon", (0.50, 0.10, 0.08, 1.0), roughness=0.6)

    objects = []

    # 1. Leather Binder Cover
    for (side, rot_y) in [(-0.16, -0.12), (0.16, 0.12)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side, -0.01, 0))
        c = bpy.context.active_object
        c.scale = (0.28, 0.012, 0.38)
        c.rotation_euler = (0, rot_y, 0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        c.data.materials.append(mat_leather)
        objects.append(c)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.38, location=(0, -0.015, 0))
    spine = bpy.context.active_object
    spine.rotation_euler = (1.5708, 0, 0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    spine.data.materials.append(mat_leather)
    objects.append(spine)

    # 2. Open Pages with UV mapping to show left footprint and right notes
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    # Left page quad
    v0 = bm.verts.new((-0.26, 0.014, -0.17))
    v1 = bm.verts.new((-0.01, 0.008, -0.17))
    v2 = bm.verts.new((-0.01, 0.008,  0.17))
    v3 = bm.verts.new((-0.26, 0.014,  0.17))
    f_left = bm.faces.new([v0, v1, v2, v3])
    for loop in f_left.loops:
        if loop.vert == v0: loop[uv_layer].uv = (0.02, 0.02)
        elif loop.vert == v1: loop[uv_layer].uv = (0.48, 0.02)
        elif loop.vert == v2: loop[uv_layer].uv = (0.48, 0.98)
        elif loop.vert == v3: loop[uv_layer].uv = (0.02, 0.98)

    # Right page quad
    v4 = bm.verts.new((0.01, 0.008, -0.17))
    v5 = bm.verts.new((0.26, 0.014, -0.17))
    v6 = bm.verts.new((0.26, 0.014,  0.17))
    v7 = bm.verts.new((0.01, 0.008,  0.17))
    f_right = bm.faces.new([v4, v5, v6, v7])
    for loop in f_right.loops:
        if loop.vert == v4: loop[uv_layer].uv = (0.52, 0.02)
        elif loop.vert == v5: loop[uv_layer].uv = (0.98, 0.02)
        elif loop.vert == v6: loop[uv_layer].uv = (0.98, 0.98)
        elif loop.vert == v7: loop[uv_layer].uv = (0.52, 0.98)

    p_mesh = bpy.data.meshes.new("JournalPageMesh")
    bm.to_mesh(p_mesh)
    bm.free()

    p_obj = bpy.data.objects.new("JournalPages", p_mesh)
    bpy.context.collection.objects.link(p_obj)
    p_obj.data.materials.append(mat_paper)
    objects.append(p_obj)

    # Bookmark ribbon
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.06, 0.026, 0.04))
    ribbon = bpy.context.active_object
    ribbon.scale = (0.016, 0.003, 0.42)
    ribbon.rotation_euler = (0, 0.18, 0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ribbon.data.materials.append(mat_ribbon)
    objects.append(ribbon)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Prop_FieldJournal"

    out_path = os.path.join(out_dir, "prop_field_journal.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Textured Field Journal -> {out_path} ({len(final_obj.data.vertices)} verts)")

def build_topomap(out_dir, tex_dir):
    reset_scene()

    tex_path = os.path.join(tex_dir, "prop_doc_topomap.png")
    mat_map = create_pbr_material("Mat_TopoPaper", (0.84, 0.82, 0.72, 1.0), roughness=0.92, texture_path=tex_path)
    mat_pin = create_pbr_material("Mat_BrassPin", (0.85, 0.65, 0.20, 1.0), roughness=0.35, metallic=0.9)

    objects = []

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    # Single folded map sheet with UVs mapped across the quad
    verts = [
        bm.verts.new((-0.45, 0.008, -0.32)),
        bm.verts.new(( 0.45, 0.007, -0.32)),
        bm.verts.new(( 0.45, 0.003,  0.32)),
        bm.verts.new((-0.45, 0.004,  0.32))
    ]
    face = bm.faces.new(verts)
    for loop in face.loops:
        if loop.vert == verts[0]: loop[uv_layer].uv = (0.0, 0.0)
        elif loop.vert == verts[1]: loop[uv_layer].uv = (1.0, 0.0)
        elif loop.vert == verts[2]: loop[uv_layer].uv = (1.0, 1.0)
        elif loop.vert == verts[3]: loop[uv_layer].uv = (0.0, 1.0)

    mesh = bpy.data.meshes.new("MapMesh")
    bm.to_mesh(mesh)
    bm.free()

    map_obj = bpy.data.objects.new("TopoMap", mesh)
    bpy.context.collection.objects.link(map_obj)
    map_obj.data.materials.append(mat_map)
    objects.append(map_obj)

    # Brass pins at corners
    for px in [-0.42, 0.42]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.009, location=(px, 0.015, 0.30))
        pin = bpy.context.active_object
        pin.data.materials.append(mat_pin)
        objects.append(pin)

    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    final_obj = bpy.context.active_object
    final_obj.name = "Prop_TopoMap"

    out_path = os.path.join(out_dir, "prop_topomap.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_apply=True)
    print(f"[Blender] Exported Textured Topo Map -> {out_path} ({len(final_obj.data.vertices)} verts)")

if __name__ == "__main__":
    out_dir = "/home/m3tal/apps/the-black-pines/assets/models"
    tex_dir = "/home/m3tal/apps/the-black-pines/assets/textures"
    build_evacuation_notice(out_dir, tex_dir)
    build_field_journal(out_dir, tex_dir)
    build_topomap(out_dir, tex_dir)
