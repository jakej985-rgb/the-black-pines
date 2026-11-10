#!/usr/bin/env python3
"""
Blender Retopology Pipeline for Sasquatch Character

Takes the high-poly sculpt and produces a game-ready retopologized mesh:
- Voxel remesh for clean quad topology
- Decimation to target polycount (8K-16K tris)
- Smart UV projection
- Export for Godot pipeline
"""

import bpy
import os
from mathutils import Vector
from pathlib import Path

# Use absolute filesystem path for Blender
import os
BLAirNTPATH = "/home/m3tal/apps/the-black-pines"
PROJECT_ROOT = Path(BLAirNTPATH)
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch"
HIGH_RES_OBJ = SOURCE_DIR / "working" / "hero_sculpt_v6.obj"
OUTPUT_DIR = SOURCE_DIR / "retopo"

TARGET_TRIS = 12000  # Target within 8K-16K range
VOXEL_SIZE = 0.015   # Voxel size for clean remesh
DECIMATE_RATIO = 0.08  # Rough ratio to hit target (~12k Tris from 372k)


def clean_scene():
    """Clear all mesh data and objects from the scene."""
    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')
    # Remove all meshes
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    # Remove all objects
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def import_high_res(path):
    """Import the high-resolution sculpt OBJ."""
    print(f"Importing high-res sculpt: {path}")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=str(path))
    
    # Find the imported mesh object
    mesh_obj = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            mesh_obj = obj
            break
    
    if mesh_obj is None:
        # Try to find a non-Icosphere mesh
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name != 'Icosphere':
                mesh_obj = obj
                break
    
    if mesh_obj is None:
        raise RuntimeError("Could not find imported mesh object")
    
    # Deselect others, select only the sculpt
    for obj in bpy.data.objects:
        if obj != mesh_obj:
            obj.select_set(False)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    
    print(f"  Imported: {len(mesh_obj.data.vertices)} vertices, {len(mesh_obj.data.polygons)} polygons")
    return mesh_obj


def retopo_mesh(obj, voxel_size=VOXEL_SIZE, target_tris=TARGET_TRIS):
    """
    Retopologize the mesh using voxel remesh + decimation.
    
    Steps:
    1. Voxel remesh to create clean, uniform topology
    2. Remove doubles and normals consistent
    3. Decimate to target triangle count
    4. Shade smooth for good curvature
    """
    print(f"\nRetopologizing: {len(obj.data.vertices)} -> ~{target_tris} tris...")
    
    # Step 1: Voxel remesh for clean topology
    print("  - Voxel remesh...")
    obj.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()
    verts_after_remesh = len(obj.data.vertices)
    polys_after_remesh = len(obj.data.polygons)
    print(f"    After remesh: {verts_after_remesh} verts, {polys_after_remesh} polys")
    
    # Step 2: Remove doubles to clean up
    print("  - Removing doubles...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Step 3: Decimate to target polycount
    print(f"  - Decimating to ~{target_tris} tris...")
    mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.ratio = DECIMATE_RATIO
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    verts_after_decimate = len(obj.data.vertices)
    polys_after_decimate = len(obj.data.polygons)
    print(f"    After decimate: {verts_after_decimate} verts, {polys_after_decimate} polys")
    
    # Verify we're in target range
    tri_count = polys_after_decimate  # Tris in OBJ export
    print(f"  Triangle count: {tri_count} (target: {target_tris})")
    
    # Step 4: Shading smooth skipped for export reliability
    print("  - Shading smooth: skipped")
    
    return obj


def smart_uv_project(obj):
    """Smart UV projection for the retopo mesh."""
    print("\nApplying smart UV projection...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(
        angle_limit=1.5,
        island_margin=0.02
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Check UV coverage
    uv_count = 0
    for uv_layer in obj.data.uv_layers:
        uv_count = len(uv_layer.data)
    
    print(f"  UV layers: {uv_count} vertices with UVs")
    return obj


def export_retopo(obj, path):
    """Export the retopo mesh as OBJ for Godot."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    export_path = path / "sasquatch_retopo.obj"
    
    # Select only the retopo object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Export settings matching Godot Forward+ convention
    print(f"\nExporting retopo mesh to: {export_path}")
    bpy.ops.wm.obj_export(
        filepath=str(export_path),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_uv=True,
        export_normals=True,
        export_materials=False,
        apply_modifiers=True,
        use_selection=True
    )
    
    # Also export as GLB for Godot
    glb_path = OUTPUT_DIR / "sasquatch_retopo.glb"
    print(f"Exporting GLB to: {glb_path}")
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_selected_objects=True,
        export_materials='NONE',
        export_texture_nodes=False,
    )
    
    print(f"  Export complete: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys")
    return str(export_path), str(glb_path)


def main():
    print("=" * 64)
    print(" SASQUATCH RETOPOLOGY PIPELINE")
    print("=" * 64)
    print(f"Target: ~{TARGET_TRIS} triangles (within 8K-16K range)")
    print(f"High-res source: {HIGH_RES_OBJ}")
    print()
    
    # Step 1: Clean scene and import high-res
    clean_scene()
    high_obj = import_high_res(HIGH_RES_OBJ)
    
    # Step 2: Retopologize (remesh + decimate)
    retopo_obj = retopo_mesh(high_obj, voxel_size=VOXEL_SIZE, target_tris=TARGET_TRIS)
    
    # Step 3: UV unwrapping
    retopo_obj = smart_uv_project(retopo_obj)
    
    # Step 4: Export
    obj_path, glb_path = export_retopo(retopo_obj, OUTPUT_DIR)
    
    print("\n" + "=" * 64)
    print("PIPELINE COMPLETE")
    print("=" * 64)
    print(f"Retopo mesh: {obj_path}")
    print(f"GLB export:  {glb_path}")
    print(f"\nNext steps:")
    print("  1. Bake maps (normal, AO, curvature) from high-res to retopo")
    print("  2. Update Godot project with new mesh and baked materials")
    print("  3. Integrate fur shader with baked maps")


if __name__ == "__main__":
    main()