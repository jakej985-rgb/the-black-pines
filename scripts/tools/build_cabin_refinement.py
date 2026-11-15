#!/usr/bin/env python3
"""Review-only staged prop builder for The Black Pines ranger station.

Usage:
  blender --background --python scripts/tools/build_cabin_refinement.py -- \
    --stage interior --project-root /path/to/the-black-pines
  blender --background --python scripts/tools/build_cabin_refinement.py -- \
    --stage exterior --project-root /path/to/the-black-pines

All outputs are isolated under working/cabin_refinement/<pass>/.
No production asset or scene path is written.
"""
import bpy, math, json, argparse, sys, random
from pathlib import Path
from mathutils import Vector

def parse_args():
    raw = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", required=True)
    p.add_argument("--stage", choices=["interior", "exterior", "all"], default="all")
    return p.parse_args(raw)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=.75, metal=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = color
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    return m

def box(name, loc, scale, material, bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Edge_softening", "BEVEL")
        mod.width, mod.segments = bevel, 2
        mod.profile = .5
        mod2 = o.modifiers.new("Weighted_corner_normals", "WEIGHTED_NORMAL")
    return o

def cyl(name, loc, radius, depth, material, vertices=16, bevel=.004):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Edge_softening","BEVEL"); mod.width=bevel; mod.segments=2
        o.modifiers.new("Weighted_corner_normals","WEIGHTED_NORMAL")
    return o

def rod(name, a, b, radius, material, vertices=10):
    a,b=Vector(a),Vector(b); d=b-a
    o=cyl(name,(a+b)*.5,radius,d.length,material,vertices)
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    return o

def export_asset(objects, out, asset_name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",use_selection=True,
                              export_apply=True,export_yup=True,export_materials="EXPORT")
    deps=bpy.context.evaluated_depsgraph_get(); tris=0
    for o in objects:
        if o.type!="MESH": continue
        ev=o.evaluated_get(deps); me=ev.to_mesh()
        me.calc_loop_triangles(); tris+=len(me.loop_triangles)
        ev.to_mesh_clear()
    return {"asset":asset_name,"path":str(out),"objects":len(objects),"triangles":tris}

def layout_for_review(groups, spacing=1.8):
    # Spread exported groups along X so the saved review scene doesn't overlap.
    start=-spacing*(len(groups)-1)/2
    for i,(_,objects) in enumerate(groups):
        for o in objects: o.location.x+=start+i*spacing

def create_review_camera():
    bpy.ops.object.camera_add(location=(3.6,-4.6,3.0))
    cam=bpy.context.object; cam.name="ReviewCamera"
    target=Vector((0,0,.55)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=48; bpy.context.scene.camera=cam
    bpy.ops.object.light_add(type="AREA",location=(1.5,-3.0,4.0))
    key=bpy.context.object; key.data.energy=650; key.data.shape="DISK"; key.data.size=4
    key.rotation_euler=(Vector((0,0,.5))-Vector(key.location)).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.light_add(type="AREA",location=(-3,1,2.5))
    fill=bpy.context.object; fill.data.energy=250; fill.data.size=3
    fill.rotation_euler=(Vector((0,0,.5))-Vector(fill.location)).to_track_quat("-Z","Y").to_euler()
    s=bpy.context.scene; s.render.engine="BLENDER_EEVEE_NEXT"
    s.render.resolution_x=1000; s.render.resolution_y=750; s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    s.render.filepath="//preview.png"

def build_table(m):
    o=[]
    o.append(box("Tabletop_weathered_pine",(0,0,.76),(1.55,.82,.075),m["wood"],.025))
    for x in (-.66,.66):
        for y in (-.31,.31):
            o.append(box("Table_leg",(x,y,.37),(.085,.085,.72),m["wood"],.012))
    o.append(box("Apron_long_front",(0,-.34,.64),(1.34,.055,.16),m["darkwood"],.01))
    o.append(box("Apron_long_back",(0,.34,.64),(1.34,.055,.16),m["darkwood"],.01))
    o.append(box("Apron_end_left",(-.66,0,.64),(.055,.62,.16),m["darkwood"],.01))
    o.append(box("Apron_end_right",(.66,0,.64),(.055,.62,.16),m["darkwood"],.01))
    # Drawer fronts, knobs, and lower stretcher
    for x in (-.38,.38):
        o.append(box("Drawer_front",(x,-.375,.65),(.34,.025,.105),m["wood"],.008))
        o.append(cyl("Drawer_pull",(x,-.397,.65),.012,.025,m["iron"],12,.002))
    o.append(box("Lower_stretcher",(0,0,.19),(1.12,.055,.07),m["darkwood"],.008))
    return o

def build_chair(m, offset=0):
    o=[]; x=offset
    o.append(box("Chair_seat",(x,0,.46),(.44,.44,.055),m["wood"],.018))
    for dx in (-.18,.18):
        for y in (-.18,.18):
            o.append(box("Chair_leg",(x+dx,y,.225),(.045,.045,.43),m["darkwood"],.008))
    for dx in (-.18,.18):
        o.append(box("Back_post",(x+dx,.19,.78),(.045,.045,.66),m["darkwood"],.008))
    for z in (.62,.78,.94):
        o.append(box("Back_slat",(x,.19,z),(.36,.035,.07),m["wood"],.01))
    for y in (-.18,.18):
        o.append(box("Side_stretcher",(x,y,.22),(.36,.035,.06),m["darkwood"],.006))
    return o

def build_filing_cabinet(m):
    o=[box("Cabinet_body",(0,0,.78),(.82,.62,1.55),m["green"],.025)]
    for z in (.28,.66,1.04,1.42):
        o.append(box("Drawer_face",(0,-.318,z),(.75,.025,.32),m["metal"],.008))
        o.append(box("Label_holder",(0,-.337,z+.08),(.18,.008,.045),m["iron"],.003))
        o.append(rod("Drawer_pull",(-.08,-.35,z-.03),(.08,-.35,z-.03),.009,m["iron"]))
    o.append(box("Toe_kick",(0,0,.06),(.74,.52,.12),m["darkwood"],.01))
    return o

def build_stove_tools(m):
    o=[]
    # Tool stand, shovel, poker, brush and small ash bucket
    o.append(box("Tool_stand_base",(0,0,.035),(.30,.22,.07),m["iron"],.015))
    o.append(rod("Tool_stand_upright",(0,0,.07),(0,0,.72),.018,m["iron"]))
    for i,ang in enumerate((-.32,0,.32)):
        x=math.sin(ang)*.11
        o.append(rod("Hanging_tool_handle_%d"%i,(x,-.02,.12),(x,-.02,.67),.012,m["darkwood"]))
        o.append(rod("Hanging_tool_head_%d"%i,(x-.045,-.02,.12),(x+.045,-.02,.12),.018,m["iron"]))
    o.append(cyl("Ash_bucket_body",(0,.38,.17),.17,.32,m["iron"],16,.01))
    o.append(cyl("Ash_bucket_rim",(0,.38,.34),.18,.025,m["metal"],20,.004))
    o.append(rod("Bucket_handle",(-.17,.38,.30),(0,.38,.53),.012,m["iron"]))
    o.append(rod("Bucket_handle_right",(0,.38,.53),(.17,.38,.30),.012,m["iron"]))
    return o

def build_boot_pair(m):
    o=[]
    for x in (-.15,.15):
        o.append(box("Boot_sole",(x,0,.035),(.13,.30,.055),m["rubber"],.02))
        o.append(box("Boot_upper",(x,-.025,.15),(.14,.20,.22),m["leather"],.045))
        o.append(box("Boot_shaft",(x,.065,.27),(.13,.12,.28),m["leather"],.025))
        for z in (.22,.29,.36):
            o.append(box("Boot_lace_band",(x,-.13,z),(.12,.012,.012),m["darkwood"],.003))
    return o

def build_mugs_and_kettle(m):
    o=[]
    for x in (-.18,.18):
        o.append(cyl("Enamel_mug",(x,0,.055),.055,.11,m["enamel"],20,.004))
        # side loop handle
        o.append(rod("Mug_handle_a",(x+.045,0,.075),(x+.105,0,.075),.009,m["iron"]))
        o.append(rod("Mug_handle_b",(x+.105,0,.075),(x+.105,0,.025),.009,m["iron"]))
    o.append(cyl("Kettle_body",(0,.32,.13),.15,.24,m["metal"],24,.012))
    o.append(cyl("Kettle_lid",(0,.32,.26),.13,.025,m["iron"],24,.004))
    o.append(rod("Kettle_spout",(0,.18,.18),(0,.06,.25),.035,m["metal"]))
    return o

def build_firewood_basket(m):
    o=[]
    o.append(cyl("Basket_base",(0,0,.04),.25,.07,m["darkwood"],20,.008))
    for i in range(12):
        a=2*math.pi*i/12
        x,y=math.cos(a)*.22,math.sin(a)*.22
        o.append(rod("Basket_upright_%02d"%i,(x,y,.06),(x,y,.48),.012,m["wood"]))
    for z in (.15,.30,.45):
        for i in range(12):
            a=2*math.pi*i/12; b=2*math.pi*(i+1)/12
            o.append(rod("Basket_weave_%02d"%i,(math.cos(a)*.22,math.sin(a)*.22,z),
                (math.cos(b)*.22,math.sin(b)*.22,z),.009,m["darkwood"]))
    return o

def build_interior(root, passdir, mats):
    reports=[]
    groups=[
        ("furniture_dining_work_table",build_table(mats)),
        ("furniture_ranger_chair",build_chair(mats,-.28)+build_chair(mats,.28)),
        ("furniture_filing_cabinet",build_filing_cabinet(mats)),
        ("prop_stove_tools_and_ash_bucket",build_stove_tools(mats)),
        ("prop_ranger_boot_pair",build_boot_pair(mats)),
        ("prop_enamel_mugs_and_kettle",build_mugs_and_kettle(mats)),
        ("prop_firewood_basket",build_firewood_basket(mats)),
    ]
    for name,objects in groups:
        p=passdir/"exports"/(name+".glb")
        reports.append(export_asset(objects,p,name))
    layout_for_review(groups)
    return reports

def build_split_block(m):
    o=[cyl("Splitting_block",(0,0,.30),.34,.60,m["bark"],12,.025)]
    for i in range(5):
        a=i*math.tau/5
        o.append(rod("Endgrain_split",(math.cos(a)*.03,math.sin(a)*.03,.605),
            (math.cos(a)*.29,math.sin(a)*.29,.605),.003,m["darkwood"],6))
    return o

def build_axe(m):
    o=[box("Axe_handle",(0,0,.48),(.045,.055,.82),m["darkwood"],.012),
       box("Axe_head",(0,0,.88),(.32,.075,.13),m["iron"],.018),
       box("Axe_bit",(0,0,.88),(.06,.09,.17),m["metal"],.012)]
    return o

def build_utility_crate(m):
    o=[box("Crate_base",(0,0,.06),(.62,.48,.12),m["wood"],.012)]
    for x in (-.28,.28):
        for y in (-.21,.21):
            o.append(box("Crate_corner_post",(x,y,.29),(.045,.045,.46),m["darkwood"],.006))
    for z in (.16,.30,.44):
        for y in (-.21,.21):
            o.append(box("Crate_long_slats",(0,y,z),(.56,.035,.09),m["wood"],.006))
        for x in (-.28,.28):
            o.append(box("Crate_end_slats",(x,0,z),(.035,.40,.09),m["wood"],.006))
    return o

def build_exterior(root, passdir, mats):
    groups=[
        ("prop_wood_splitting_block",build_split_block(mats)),
        ("prop_ranger_axe",build_axe(mats)),
        ("prop_weathered_utility_crate",build_utility_crate(mats)),
    ]
    reports=[]
    for name,objects in groups:
        reports.append(export_asset(objects,passdir/"exports"/(name+".glb"),name))
    layout_for_review(groups)
    return reports

def main():
    a=parse_args(); root=Path(a.project_root).resolve()
    if not root.exists(): raise SystemExit("Project root does not exist: "+str(root))
    stages=["interior","exterior"] if a.stage=="all" else [a.stage]
    for stage in stages:
        reset()
        passdir=root/"working/cabin_refinement"/("pass02_interior" if stage=="interior" else "pass03_exterior")
        passdir.mkdir(parents=True,exist_ok=True)
        mats={
          "wood":mat("M_weathered_pine",(0.27,.18,.105,1),.82),
          "darkwood":mat("M_dark_worn_wood",(.12,.075,.045,1),.88),
          "green":mat("M_forest_service_green",(.12,.20,.13,1),.72),
          "metal":mat("M_dull_galvanized_metal",(.34,.37,.36,1),.58,.72),
          "iron":mat("M_blackened_iron",(.075,.082,.08,1),.66,.78),
          "leather":mat("M_worn_leather",(.18,.105,.055,1),.9),
          "rubber":mat("M_boot_rubber",(.025,.027,.026,1),.94),
          "enamel":mat("M_chipped_enamel",(.58,.61,.54,1),.34,.18),
          "bark":mat("M_split_log_bark",(.20,.13,.075,1),.92),
        }
        reports=build_interior(root,passdir,mats) if stage=="interior" else build_exterior(root,passdir,mats)
        create_review_camera()
        # Save the assembled review scene; no production source is opened or overwritten.
        bpy.ops.wm.save_as_mainfile(filepath=str(passdir/"review.blend"))
        (passdir/"qa.json").write_text(json.dumps({
            "stage":stage,"status":"GENERATED_REVIEW_ONLY",
            "production_assets_modified":False,
            "assets":reports,
            "checks_required":["inspect scale and pivots","inspect UVs and material response",
              "check intersections and ground contact","capture in-game lighting",
              "verify player clearance","human visual approval required"]
        },indent=2))
        print("[CABIN REFINEMENT]",stage,"review outputs:",passdir)

if __name__=="__main__": main()
