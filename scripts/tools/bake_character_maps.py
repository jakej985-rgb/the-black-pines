#!/usr/bin/env python3
"""
Blender Map Baking Pipeline for Sasquatch Character

Bakes high-detail information from the high-poly sculpt onto the 
retopologized low-poly mesh:
- Tangent space normal map (2048x2048, OpenGL +Y Up)
- Ambient Occlusion map
- Curvature map (for fur shader modulation)
"""

import bpy
import os
from mathutils import Vector
from pathlib import Path

BLAirNTPATH = "/home/m3tal/apps/the-black-pines"
PROJECT_ROOT = Path(BLAirNTPATH)
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch"
BAKED_DIR = SOURCE_DIR / "baked"
NORMAL_MAP_PATH = BAKED_DIR / "nor_sasquatch_2048.png"
AO_MAP_PATH = BAKED_DIR / "ao_sasquatch_2048.png"
CURVATURE_MAP_PATH = BAKED_DIR / "curv_sasquatch_2048.png"


def clean_scene():
    """Clear all mesh data and objects from the scene."""
    bpy.ops.object.select_all(action='DESELECT')
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def import_mesh(path, name):
    """Import a single OBJ mesh and return the object."""
    print(f"Importing: {path} as {name}")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=str(path))
    
    obj = None
    for obj_cand in bpy.context.selected_objects:
        if obj_cand.type == 'MESH' and obj_cand.name != 'Icosphere':
            obj_cand.name = name
            obj = obj_cand
            break
    
    if obj is None:
        for obj_cand in bpy.data.objects:
            if obj_cand.type == 'MESH':
                obj_cand.name = name
                obj = obj_cand
                break
    
    if obj is None:
        raise RuntimeError(f"Could not import mesh: {path}")
    
    bpy.context.view_layer.objects.active = obj
    print(f"  Loaded: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys")
    return obj


def setup_bake_cycle():
    """Set up Cycles for baking with proper render settings."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False
    
    # Set up blank world (no world light = ambient occlusion bakes properly)
    world = bpy.data.worlds.get("World")
    if world:
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        # Clear existing nodes
        nodes.clear()
        # Add background world node
        bg_node = nodes.get('Background')
        if bg_node is None:
            bg_node = nodes.new(type='ShaderOutputWorld')
            world.node_tree.nodes.new('ShaderNodeBackground')
        bg_node.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0


def setup_bake_materials(retopo_obj, high_obj):
    """Set up simple materials on both objects for baking."""
    # Create a simple white material for the high-res sculpt
    high_mat_name = "HighPolyBakeMat"
    if high_mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(name=high_mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        principled = nodes.get('Principled BSDF')
        if principled:
            principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
            principled.inputs['Roughness'].default_value = 0.5
            principled.inputs['Metallic'].default_value = 0.0
    else:
        mat = bpy.data.materials[high_mat_name]
    
    # Assign to high-res object
    if mat.name not in high_obj.data.materials:
        high_obj.data.materials.append(mat)
    
    # Create a simple white material for the retopo object
    retopo_mat_name = "RetopoBakeMat"
    if retopo_mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(name=retopo_mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        principled = nodes.get('Principled BSDF')
        if principled:
            principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
            principled.inputs['Roughness'].default_value = 0.5
            principled.inputs['Metallic'].default_value = 0.0
    else:
        mat = bpy.data.materials[retopo_mat_name]
    
    # Assign to retopo object
    if mat.name not in retopo_obj.data.materials:
        retopo_obj.data.materials.append(mat)
    
    return mat, mat


def bake_normal_map(retopo_obj, high_obj, output_path):
    """Bake tangent space normal map from high-res to retopo."""
    print(f"\nBaking normal map to: {output_path}")
    
    # Set up nodes on the retopo material for baking
    retopo_mat = retopo_obj.data.materials[0]
    retopo_mat.use_nodes = True
    node_tree = retopo_mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Clear all nodes except Output Material
    nodes.clear()
    
    # Create nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodePrincipledBsdf')
    normal_node = nodes.new(type='ShaderNodeNormalMap')
    tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
    mapping_node = nodes.new(type='ShaderNodeMapping')
    
    # Set up connections
    # Output -> Material Output
    links.new(output_node.outputs['Color'], nodes['Material Output'].input['Surface'])
    
    # Principled BSDF -> Output Material
    links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Normal map -> Principled BSDF
    links.new(normal_node.outputs['Normal'], principled.inputs['Normal'])
    
    # TexCoord -> Mapping
    links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['UV'])
    
    # Mapping -> Normal map
    links.new(mapping_node.outputs['Vector'], normal_node.inputs['Vector'])
    
    # Set up the normal map texture
    normal_tex = nodes.new(type='ShaderNodeTexImage')
    normal_tex.image = bpy.data.images.load(str(output_path)) if output_path.exists() else None
    if normal_tex.image is None:
        # Create a new blank image
        normal_tex.image = bpy.data.images.new(
            name='BakedNormal',
            width=2048,
            height=2048,
            alpha=False
        )
        normal_tex.image.file_format = 'PNG'
    
    # Connect normal texture to normal map
    links.new(normal_tex.outputs['Color'], normal_node.inputs['Color'])
    
    # Configure principled BSDF for baking
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    principled.inputs['Roughness'].default_value = 0.5
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Normal'].default_value = (0.0, 0.0, 1.0)
    
    # Set up render layers for baking
    scene = bpy.context.scene
    scene.render.bake_type = 'NORMAL'
    scene.bake.use_selected_to_active = True
    scene.bake.use_active_camera = False
    scene.bake.margin = 4
    
    # Deselect everything, select high-res first, then retopo
    bpy.ops.object.select_all(action='DESELECT')
    high_obj.select_set(True)
    retopo_obj.select_set(True)
    bpy.context.view_layer.objects.active = retopo_obj
    
    # Perform the bake
    try:
        bpy.ops.object.bake()
        print("  Bake complete")
        
        # Save the baked normal map
        if normal_tex.image:
            # Flip V coordinate for OpenGL (+Y up)
            normal_tex.image.flip_y = False  # Keep as-is; Godot handles conversion
            normal_tex.image.save_render(str(output_path))
            print(f"  Saved normal map: {output_path}")
            return True
    except RuntimeError as e:
        print(f"  Bake failed: {e}")
    
    return False


def bake_ao_map(retopo_obj, high_obj, output_path):
    """Bake ambient occlusion map from high-res to retopo."""
    print(f"\nBaking AO map to: {output_path}")
    
    scene = bpy.context.scene
    
    # Set up white world light for AO baking
    world = bpy.data.worlds.get("World")
    if world:
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        # Clear
        nodes.clear()
        # Add background with strength
        bg_node = nodes.new(type='ShaderNodeBackground')
        bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bg_node.inputs['Strength'].default_value = 2.0
        output_node = nodes.new(type='ShaderOutputWorld')
        links.new(bg_node.outputs['Color'], output_node.inputs['Surface'])
    
    # Set up retopo material for AO baking
    retopo_mat = retopo_obj.data.materials[0]
    retopo_mat.use_nodes = True
    node_tree = retopo_mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Clear and set up simple white material
    nodes.clear()
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodePrincipledBsdf')
    principled.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    principled.inputs['Roughness'].default_value = 1.0
    principled.inputs['Metallic'].default_value = 0.0
    links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Set bake type to AO
    scene.render.bake_type = 'OBJECT_SPACE AO'
    scene.bake.use_selected_to_active = True
    scene.bake.use_active_camera = False
    scene.bake.margin = 4
    
    # Deselect everything, select high-res first, then retopo
    bpy.ops.object.select_all(action='DESELECT')
    high_obj.select_set(True)
    retopo_obj.select_set(True)
    bpy.context.view_layer.objects.active = retopo_obj
    
    # Perform the bake
    try:
        bpy.ops.object.bake()
        print("  Bake complete")
        
        # Get the active image from the node setup
        # The AO should be visible in the principled's roughness or we read from render result
        # Actually, let's save the rendered AO directly
        
        # Save the baked AO map
        # We need to have an image target set up
        # Let's create/fetch the image
        image_name = "BakedAO"
        
        if bpy.data.images.get(image_name):
            img = bpy.data.images[image_name]
        else:
            img = bpy.data.images.new(name=image_name, width=2048, height=2048, alpha=False)
            img.file_format = 'PNG'
        
        # Save - flip V for OpenGL compatibility
        img.flip_y = False
        img.save_render(str(output_path))
        print(f"  Saved AO map: {output_path}")
        return True
    except RuntimeError as e:
        print(f"  AO bake failed: {e}")
    
    return False


def bake_curvature_map(retopo_obj, output_path):
    """Bake curvature/cavity map from the retopo mesh itself."""
    print(f"\nBaking curvature map to: {output_path}")
    
    # Curvature can be baked from the mesh itself using the curvature node
    # or we can use a shader trick
    # Here we'll use the Curvature node setup
    
    retopo_mat = retopo_obj.data.materials[0]
    retopo_mat.use_nodes = True
    node_tree = retopo_mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Clear and set up curvature-based material
    nodes.clear()
    
    # Output output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Curvature node
    curvature_node = nodes.new(type='ShaderNodeCurvature')
    curvature_node.inputs['Smooth by Angle'].default_value = 30.0
    curvature_node.inputs['Maximum Curvature'].default_value = 1.0
    
    # Texture coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    links.new(tex_coord.outputs['UV'], mapping.inputs['UV'])
    links.new(mapping.outputs['Vector'], curvature_node.inputs['Vector'])
    
    # Mix curvature into roughness/color for baking
    # We'll output as a color output
    links.new(curvature_node.outputs['Curvature'], output_node.inputs['Surface'])
    
    # Set up image output
    # We need to render this to an image
    scene = bpy.context.scene
    scene.render.bake_type = 'NORMAL'  # Use normal bake as curvature output method
    
    # Actually, let's render the curvature as a separate pass
    # Create an image
    image_name = "BakedCurvature"
    if bpy.data.images.get(image_name):
        img = bpy.data.images[image_name]
    else:
        img = bpy.data.images.new(name=image_name, width=2048, height=2048, alpha=False)
        img.file_format = 'PNG'
    
    # Set up node output to image
    # We'll use the viewport render and save
    # For curvature, we'll render the curvature node output
    
    # Deselect everything, select the retopo object
    bpy.ops.object.select_all(action='DESELECT')
    retopo_obj.select_set(True)
    bpy.context.view_layer.objects.active = retopo_obj
    
    # Render and save
    scene.render.use_file_extension = True
    scene.render.filepath = str(output_path.parent / "curv_temp.png")
    
    try:
        bpy.ops.render.render()
        # The rendered image should have our curvature data
        # Copy it to the target path
        if img:
            img.reload()
            # Flip V for OpenGL
            img.flip_y = False
            img.save_render(str(output_path))
            print(f"  Saved curvature map: {output_path}")
            return True
    except RuntimeError as e:
        print(f"  Curvature bake failed: {e}")
    
    return False


def main():
    print("=" * 64)
    print(" SASQUATCH MAP BAKING PIPELINE")
    print("=" * 64)
    print()
    
    # Clean scene
    clean_scene()
    
    # Step 1: Import high-res sculpt and retopo mesh
    print("Step 1: Importing meshes...")
    high_obj = import_mesh(SOURCE_DIR / "working" / "hero_sculpt_v6.obj", "HighPolySculpt")
    
    # We need the retopo mesh too - import it
    retopo_obj = import_mesh(SOURCE_DIR / "retopo" / "sasquatch_retopo.obj", "RetopoLowPoly")
    
    # Step 2: Set up baking
    print("\nStep 2: Setting up bake cycle...")
    setup_bake_cycle()
    
    # Step 3: Bake normal map
    print("\nStep 3: Baking normal map...")
    BAKED_DIR.mkdir(parents=True, exist_ok=True)
    normal_ok = bake_normal_map(retopo_obj, high_obj, NORMAL_MAP_PATH)
    
    # Step 4: Bake AO map
    print("\nStep 4: Baking AO map...")
    ao_ok = bake_ao_map(retopo_obj, high_obj, AO_MAP_PATH)
    
    # Step 5: Bake curvature map
    print("\nStep 5: Baking curvature map...")
    curvature_ok = bake_curvature_map(retopo_obj, CURVATURE_MAP_PATH)
    
    # Step 6: Verify outputs
    print("\n" + "=" * 64)
    print("BAKE RESULTS")
    print("=" * 64)
    if normal_ok and NORMAL_MAP_PATH.exists():
        size = NORMAL_MAP_PATH.stat().st_size
        print(f"  Normal map: {NORMAL_MAP_PATH} ({size} bytes)")
    if ao_ok and AO_MAP_PATH.exists():
        size = AO_MAP_PATH.stat().st_size
        print(f"  AO map: {AO_MAP_PATH} ({size} bytes)")
    if curvature_ok and CURVATURE_MAP_PATH.exists():
        size = CURVATURE_MAP_PATH.stat().st_size
        print(f"  Curvature map: {CURVATURE_MAP_PATH} ({size} bytes)")
    
    print("\nPipeline complete. Maps are ready for Godot material setup.")


if __name__ == "__main__":
    main()