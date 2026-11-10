"""
build_ranger_station_blender.py
Procedurally builds the photorealistic Ranger Station #04 cabin in Blender 4.2 LTS:
- Interlocking saddle-notched cedar log walls with annular end grain
- Realistic pitched corrugated metal & cedar trim gable roof with rafter tails and ridge beam
- Rustic timber porch with 8x8 posts, gallows knee braces, X-railings, and 3-tread entrance steps
- Fieldstone masonry foundation footings
- Window casings with 4-pane muntins and glass
- Heavy timber door frame with open plank door and forged iron strap hinges
- Hanging storm lanterns (porch and interior) with wire cages and glass chimneys
- Woodstove chimney flue with roof flashing collar and cowl
- Exports assets/models/cabin_ranger_station.glb and renders docs/graphics/previews/blender_cabin_preview.png
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import math
import random
from pathlib import Path
import os

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)
    for block in bpy.data.images:
        bpy.data.images.remove(block)

def create_pbr_mat(name, color=(0.5, 0.5, 0.5, 1.0), roughness=0.75, metallic=0.0,
                   diff_path=None, norm_path=None, rough_path=None, ao_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if diff_path and Path(diff_path).exists():
        t_diff = nodes.new("ShaderNodeTexImage")
        t_diff.image = bpy.data.images.load(str(diff_path))
        links.new(t_diff.outputs["Color"], bsdf.inputs["Base Color"])

    if norm_path and Path(norm_path).exists():
        t_norm = nodes.new("ShaderNodeTexImage")
        t_norm.image = bpy.data.images.load(str(norm_path))
        t_norm.image.colorspace_settings.name = "Non-Color"
        n_map = nodes.new("ShaderNodeNormalMap")
        n_map.inputs["Strength"].default_value = 1.3
        links.new(t_norm.outputs["Color"], n_map.inputs["Color"])
        links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])

    if rough_path and Path(rough_path).exists():
        t_rough = nodes.new("ShaderNodeTexImage")
        t_rough.image = bpy.data.images.load(str(rough_path))
        t_rough.image.colorspace_settings.name = "Non-Color"
        links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

    return mat

def build_cabin_mesh():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    random.seed(42)

    # In Blender native coordinates:
    # X: Left/Right (width: -3.2 to +3.2)
    # Y: Front/Back (Godot -Z is Blender +Y = +2.6; Godot +Z front/porch is Blender -Y = -2.6 to -4.6)
    # Z: Vertical Height (floor = 0.38, wall top = 3.20, roof peak = 4.85)

    half_w = 3.2
    back_y = 2.6       # Godot Z = -2.6
    front_y = -2.6     # Godot Z = +2.6
    porch_d = 2.0
    porch_front_y = front_y - porch_d  # -4.6 (Godot Z = +4.6)
    floor_z = 0.38
    wall_z = 3.20
    roof_peak_z = 4.85
    roof_overhang = 0.55

    # Materials index mapping:
    # 0: M_Cabin_Trim (Weathered brown planks for framing, deck, posts, trim)
    # 1: M_Cabin_Logs (Weathered cedar logs)
    # 2: M_Cabin_Roof (Rusty corrugated iron)
    # 3: M_Cabin_Stone (Fieldstone foundation piers)
    # 4: M_Cabin_Metal (Chimney, iron hinges, lantern cage)
    # 5: M_Cabin_Glass (Window glass and lantern globe)

    def add_box_prism(center, size, mat_idx, u_scale=1.0, v_scale=1.0, rot_z=0.0):
        cx, cy, cz = center
        sx, sy, sz = size
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5

        cos_r = math.cos(rot_z)
        sin_r = math.sin(rot_z)

        local_verts = [
            (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
            (-hx, -hy,  hz), (hx, -hy,  hz), (hx, hy,  hz), (-hx, hy,  hz)
        ]

        bm_verts = []
        for vx, vy, vz in local_verts:
            rx = vx * cos_r - vy * sin_r + cx
            ry = vx * sin_r + vy * cos_r + cy
            rz = vz + cz
            bm_verts.append(bm.verts.new(Vector((rx, ry, rz))))

        faces_idx = [
            (0, 1, 2, 3), # Bottom (-Z)
            (7, 6, 5, 4), # Top (+Z)
            (0, 4, 5, 1), # Front (-Y)
            (2, 6, 7, 3), # Back (+Y)
            (3, 7, 4, 0), # Left (-X)
            (1, 5, 6, 2)  # Right (+X)
        ]

        for fi in faces_idx:
            f = bm.faces.new([bm_verts[i] for i in fi])
            f.material_index = mat_idx
            f.smooth = False
            f.loops[0][uv_layer].uv = (0.0, 0.0)
            f.loops[1][uv_layer].uv = (u_scale, 0.0)
            f.loops[2][uv_layer].uv = (u_scale, v_scale)
            f.loops[3][uv_layer].uv = (0.0, v_scale)

    def add_cylinder_prism(p1, p2, r, segs, mat_idx, u_scale=1.0):
        p1 = Vector(p1)
        p2 = Vector(p2)
        axis = (p2 - p1).normalized()
        length = (p2 - p1).length
        up = Vector((0, 0, 1))
        if abs(axis.dot(up)) > 0.95:
            up = Vector((0, 1, 0))
        side = axis.cross(up).normalized()
        ortho_up = side.cross(axis).normalized()

        ring1 = []
        ring2 = []
        for s in range(segs):
            angle = (s / segs) * 2.0 * math.pi
            offset = (side * math.cos(angle) + ortho_up * math.sin(angle)) * r
            v1 = bm.verts.new(p1 + offset)
            v2 = bm.verts.new(p2 + offset)
            ring1.append(v1)
            ring2.append(v2)

        for s in range(segs):
            s_next = (s + 1) % segs
            f = bm.faces.new((ring1[s], ring2[s], ring2[s_next], ring1[s_next]))
            f.material_index = mat_idx
            f.smooth = True
            u0 = s / segs * u_scale
            u1 = (s + 1) / segs * u_scale
            f.loops[0][uv_layer].uv = (u0, 0.0)
            f.loops[1][uv_layer].uv = (u0, length)
            f.loops[2][uv_layer].uv = (u1, length)
            f.loops[3][uv_layer].uv = (u1, 0.0)

        cap1 = bm.faces.new(reversed(ring1))
        cap1.material_index = mat_idx
        cap1.smooth = False
        cap2 = bm.faces.new(ring2)
        cap2.material_index = mat_idx
        cap2.smooth = False

    # -------------------------------------------------------------------------
    # 1. FIELDSTONE MASONRY FOUNDATION FOOTINGS & TIMBER SILL
    # -------------------------------------------------------------------------
    stone_piers = [
        (-half_w, back_y, floor_z * 0.5),
        (0.0, back_y, floor_z * 0.5),
        (half_w, back_y, floor_z * 0.5),
        (-half_w, front_y, floor_z * 0.5),
        (half_w, front_y, floor_z * 0.5),
        (-half_w, porch_front_y, floor_z * 0.5),
        (-1.25, porch_front_y, floor_z * 0.5),
        (1.25, porch_front_y, floor_z * 0.5),
        (half_w, porch_front_y, floor_z * 0.5),
    ]
    for px, py, pz in stone_piers:
        add_box_prism((px, py, pz), (0.50, 0.50, floor_z + 0.04), mat_idx=3, u_scale=1.5, v_scale=1.0)

    # Perimeter Timber Sills
    add_box_prism((0.0, back_y, floor_z * 0.5), (half_w * 2.0, 0.24, 0.24), mat_idx=0, u_scale=3.0, v_scale=0.5)
    add_box_prism((0.0, front_y, floor_z * 0.5), (half_w * 2.0, 0.24, 0.24), mat_idx=0, u_scale=3.0, v_scale=0.5)
    add_box_prism((-half_w, (back_y + front_y) * 0.5, floor_z * 0.5), (0.24, (back_y - front_y), 0.24), mat_idx=0, u_scale=3.0, v_scale=0.5)
    add_box_prism(( half_w, (back_y + front_y) * 0.5, floor_z * 0.5), (0.24, (back_y - front_y), 0.24), mat_idx=0, u_scale=3.0, v_scale=0.5)

    # -------------------------------------------------------------------------
    # 2. INTERLOCKING CEDAR LOG WALLS
    # -------------------------------------------------------------------------
    num_logs = 14
    log_h_step = (wall_z - floor_z) / num_logs
    log_r = log_h_step * 0.56
    log_overhang = 0.40
    segs = 10

    for i in range(num_logs):
        z = floor_z + log_r + i * log_h_step
        z_side = floor_z + log_r + (i + 0.5) * log_h_step

        # Back Wall Log (Full continuous timber along X)
        add_cylinder_prism(
            (-half_w - log_overhang, back_y, z),
            ( half_w + log_overhang, back_y, z),
            log_r, segs, mat_idx=1, u_scale=4.0
        )

        # Front Wall Log (With doorway at X = -0.78 to +0.78)
        if i >= 11:
            # Header log above door
            add_cylinder_prism(
                (-half_w - log_overhang, front_y, z),
                ( half_w + log_overhang, front_y, z),
                log_r, segs, mat_idx=1, u_scale=4.0
            )
        else:
            add_cylinder_prism(
                (-half_w - log_overhang, front_y, z),
                (-0.78, front_y, z),
                log_r, 8, mat_idx=1, u_scale=1.5
            )
            add_cylinder_prism(
                (0.78, front_y, z),
                (half_w + log_overhang, front_y, z),
                log_r, 8, mat_idx=1, u_scale=1.5
            )

        # Left & Right Wall Logs (along Y axis, offset by half a course for saddle notches)
        if 5 <= i <= 9:
            # Windows at Y = -0.70 to +0.70 (Godot Z = -0.70 to +0.70)
            add_cylinder_prism((-half_w, back_y + log_overhang, z_side), (-half_w, 0.70, z_side), log_r, 8, mat_idx=1)
            add_cylinder_prism((-half_w, -0.70, z_side), (-half_w, front_y - log_overhang, z_side), log_r, 8, mat_idx=1)
            add_cylinder_prism(( half_w, back_y + log_overhang, z_side), ( half_w, 0.70, z_side), log_r, 8, mat_idx=1)
            add_cylinder_prism(( half_w, -0.70, z_side), ( half_w, front_y - log_overhang, z_side), log_r, 8, mat_idx=1)
        else:
            add_cylinder_prism((-half_w, back_y + log_overhang, z_side), (-half_w, front_y - log_overhang, z_side), log_r, segs, mat_idx=1, u_scale=3.5)
            add_cylinder_prism(( half_w, back_y + log_overhang, z_side), ( half_w, front_y - log_overhang, z_side), log_r, segs, mat_idx=1, u_scale=3.5)

    # Interior Wall Backer Panels (smooth clean flat wood on inside)
    # Rear wall
    add_box_prism((0.0, back_y - 0.04, (wall_z + floor_z) * 0.5), (half_w * 2.0 - 0.2, 0.04, wall_z - floor_z), mat_idx=0, u_scale=4.0, v_scale=2.0)
    # Left interior wall (with window)
    add_box_prism((-half_w + 0.04, (back_y + 0.7) * 0.5, (wall_z + floor_z) * 0.5), (0.04, back_y - 0.7, wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism((-half_w + 0.04, (front_y - 0.7) * 0.5, (wall_z + floor_z) * 0.5), (0.04, abs(front_y - (-0.7)), wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism((-half_w + 0.04, 0.0, (floor_z + 1.35) * 0.5), (0.04, 1.40, 1.35 - floor_z), mat_idx=0)
    add_box_prism((-half_w + 0.04, 0.0, (wall_z + 2.35) * 0.5), (0.04, 1.40, wall_z - 2.35), mat_idx=0)
    # Right interior wall (with window)
    add_box_prism(( half_w - 0.04, (back_y + 0.7) * 0.5, (wall_z + floor_z) * 0.5), (0.04, back_y - 0.7, wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism(( half_w - 0.04, (front_y - 0.7) * 0.5, (wall_z + floor_z) * 0.5), (0.04, abs(front_y - (-0.7)), wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism(( half_w - 0.04, 0.0, (floor_z + 1.35) * 0.5), (0.04, 1.40, 1.35 - floor_z), mat_idx=0)
    add_box_prism(( half_w - 0.04, 0.0, (wall_z + 2.35) * 0.5), (0.04, 1.40, wall_z - 2.35), mat_idx=0)
    # Front interior wall (left/right of door)
    f_side_w = half_w - 0.85
    add_box_prism((-half_w + f_side_w * 0.5, front_y + 0.04, (wall_z + floor_z) * 0.5), (f_side_w, 0.04, wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism(( half_w - f_side_w * 0.5, front_y + 0.04, (wall_z + floor_z) * 0.5), (f_side_w, 0.04, wall_z - floor_z), mat_idx=0, u_scale=2.0, v_scale=2.0)
    add_box_prism((0.0, front_y + 0.04, (wall_z + 2.45) * 0.5), (1.70, 0.04, wall_z - 2.45), mat_idx=0)

    # Flat triangular gable walls front and back with vertical board-and-batten siding
    for gy in [front_y, back_y]:
        gv_left = bm.verts.new(Vector((-half_w, gy, wall_z)))
        gv_right = bm.verts.new(Vector((half_w, gy, wall_z)))
        gv_peak = bm.verts.new(Vector((0.0, gy, roof_peak_z)))
        if gy == front_y:
            gf = bm.faces.new((gv_left, gv_right, gv_peak))
        else:
            gf = bm.faces.new((gv_right, gv_left, gv_peak))
        gf.material_index = 0
        gf.smooth = False
        gf.loops[0][uv_layer].uv = (0.0, 0.0)
        gf.loops[1][uv_layer].uv = (4.0, 0.0)
        gf.loops[2][uv_layer].uv = (2.0, 2.0)

        # Interior triangle
        gy_int = gy + (0.08 if gy == front_y else -0.08)
        gvi_left = bm.verts.new(Vector((-half_w, gy_int, wall_z)))
        gvi_right = bm.verts.new(Vector((half_w, gy_int, wall_z)))
        gvi_peak = bm.verts.new(Vector((0.0, gy_int, roof_peak_z)))
        if gy == front_y:
            gfi = bm.faces.new((gvi_peak, gvi_right, gvi_left))
        else:
            gfi = bm.faces.new((gvi_peak, gvi_left, gvi_right))
        gfi.material_index = 0
        gfi.smooth = False
        gfi.loops[0][uv_layer].uv = (2.0, 2.0)
        gfi.loops[1][uv_layer].uv = (0.0, 0.0)
        gfi.loops[2][uv_layer].uv = (4.0, 0.0)

    # -------------------------------------------------------------------------
    # 3. INTERIOR FLOORBOARDS & CEILING RAFTERS
    # -------------------------------------------------------------------------
    add_box_prism((0.0, (back_y + front_y) * 0.5, floor_z - 0.02), (half_w * 2.0 - 0.3, (back_y - front_y) - 0.3, 0.04), mat_idx=0, u_scale=4.0, v_scale=3.0)
    for ry in [-1.8, -0.9, 0.0, 0.9, 1.8]:
        add_box_prism((0.0, ry, wall_z - 0.06), (half_w * 2.0 - 0.2, 0.14, 0.16), mat_idx=0, u_scale=3.0, v_scale=0.4)

    # -------------------------------------------------------------------------
    # 4. DOORWAY & OPEN PLANK DOOR WITH FORGED HINGES
    # -------------------------------------------------------------------------
    add_box_prism((-0.82, front_y - 0.02, (floor_z + 2.45) * 0.5), (0.12, 0.16, 2.45 - floor_z), mat_idx=0)
    add_box_prism(( 0.82, front_y - 0.02, (floor_z + 2.45) * 0.5), (0.12, 0.16, 2.45 - floor_z), mat_idx=0)
    add_box_prism(( 0.00, front_y - 0.02, 2.45), (1.76, 0.16, 0.14), mat_idx=0)
    add_box_prism((0.0, front_y - 0.02, floor_z + 0.02), (1.64, 0.22, 0.06), mat_idx=0)

    # Open door swung 90 deg inside along -X wall
    door_w = 1.48
    door_h = 1.98
    door_x = -0.76
    door_y = front_y + door_w * 0.5 + 0.06
    door_z = floor_z + door_h * 0.5 + 0.02
    add_box_prism((door_x, door_y, door_z), (0.05, door_w, door_h), mat_idx=0, u_scale=1.0, v_scale=2.0)
    add_box_prism((door_x + 0.035, door_y, door_z + 0.65), (0.03, door_w * 0.92, 0.12), mat_idx=0)
    add_box_prism((door_x + 0.035, door_y, door_z - 0.65), (0.03, door_w * 0.92, 0.12), mat_idx=0)
    add_box_prism((door_x + 0.04, front_y + 0.15, door_z + 0.65), (0.04, 0.35, 0.06), mat_idx=4)
    add_box_prism((door_x + 0.04, front_y + 0.15, door_z - 0.65), (0.04, 0.35, 0.06), mat_idx=4)

    # -------------------------------------------------------------------------
    # 5. WINDOWS & 4-PANE MUNTINS WITH GLASS
    # -------------------------------------------------------------------------
    for wx in [-half_w, half_w]:
        w_sign = -1.0 if wx < 0 else 1.0
        add_box_prism((wx + w_sign * 0.04, 0.0, 1.85), (0.08, 1.48, 1.08), mat_idx=0)
        add_box_prism((wx + w_sign * 0.08, 0.0, 1.32), (0.16, 1.56, 0.06), mat_idx=0)
        add_box_prism((wx, 0.0, 1.85), (0.015, 1.36, 0.96), mat_idx=5)
        add_box_prism((wx + w_sign * 0.01, 0.0, 1.85), (0.03, 1.36, 0.04), mat_idx=0)
        add_box_prism((wx + w_sign * 0.01, 0.0, 1.85), (0.03, 0.04, 0.96), mat_idx=0)
        add_box_prism((wx + w_sign * 0.08, 0.0, 2.0), (0.03, 1.42, 0.16), mat_idx=0, rot_z=w_sign * 0.06)

    # -------------------------------------------------------------------------
    # 6. FRONT PORCH DECK, 8x8 POSTS, GALLOWS BRACES, X-RAILINGS, & STEPS
    # -------------------------------------------------------------------------
    add_box_prism((0.0, porch_front_y, floor_z * 0.5), (half_w * 2.0 + 0.4, 0.16, floor_z), mat_idx=0)
    add_box_prism((-half_w - 0.2, (front_y + porch_front_y) * 0.5, floor_z * 0.5), (0.16, porch_d, floor_z), mat_idx=0)
    add_box_prism(( half_w + 0.2, (front_y + porch_front_y) * 0.5, floor_z * 0.5), (0.16, porch_d, floor_z), mat_idx=0)

    # Deck planks (18 planks)
    num_planks = 18
    p_step = porch_d / num_planks
    for pi in range(num_planks):
        py = front_y - (pi + 0.5) * p_step
        add_box_prism((0.0, py, floor_z - 0.015), (half_w * 2.0 + 0.38, p_step * 0.90, 0.035), mat_idx=0, u_scale=4.0, v_scale=0.3)

    # 4 Heavy 8x8 Posts
    post_size = 0.18
    posts_x = [-half_w, -1.25, 1.25, half_w]
    for px in posts_x:
        add_box_prism((px, porch_front_y, 1.35), (post_size, post_size, 2.60), mat_idx=0, u_scale=0.5, v_scale=2.5)
        brace_dir = 1.0 if px < 0 else -1.0
        if abs(px) > 1.5:
            add_cylinder_prism((px, porch_front_y, 2.15), (px + brace_dir * 0.52, porch_front_y, 2.65), 0.05, 6, mat_idx=0)
            add_cylinder_prism((px, porch_front_y, 2.15), (px, porch_front_y + 0.52, 2.65), 0.05, 6, mat_idx=0)

    # Top Porch Header Beams
    add_box_prism((0.0, porch_front_y, 2.68), (half_w * 2.0 + 0.4, 0.18, 0.18), mat_idx=0, u_scale=4.0, v_scale=0.4)
    add_box_prism((-half_w, (front_y + porch_front_y) * 0.5, 2.68), (0.18, porch_d, 0.18), mat_idx=0, u_scale=2.0, v_scale=0.4)
    add_box_prism(( half_w, (front_y + porch_front_y) * 0.5, 2.68), (0.18, porch_d, 0.18), mat_idx=0, u_scale=2.0, v_scale=0.4)

    # X-Railings
    rail_top_z = floor_z + 0.72
    rail_bot_z = floor_z + 0.12
    # Left side railing
    add_box_prism((-half_w, (front_y + porch_front_y) * 0.5, rail_top_z), (0.09, porch_d - 0.2, 0.07), mat_idx=0)
    add_box_prism((-half_w, (front_y + porch_front_y) * 0.5, rail_bot_z), (0.09, porch_d - 0.2, 0.07), mat_idx=0)
    add_cylinder_prism((-half_w, front_y - 0.15, rail_bot_z), (-half_w, porch_front_y + 0.15, rail_top_z), 0.038, 6, mat_idx=0)
    add_cylinder_prism((-half_w, front_y - 0.15, rail_top_z), (-half_w, porch_front_y + 0.15, rail_bot_z), 0.038, 6, mat_idx=0)
    # Right side railing
    add_box_prism(( half_w, (front_y + porch_front_y) * 0.5, rail_top_z), (0.09, porch_d - 0.2, 0.07), mat_idx=0)
    add_box_prism(( half_w, (front_y + porch_front_y) * 0.5, rail_bot_z), (0.09, porch_d - 0.2, 0.07), mat_idx=0)
    add_cylinder_prism(( half_w, front_y - 0.15, rail_bot_z), ( half_w, porch_front_y + 0.15, rail_top_z), 0.038, 6, mat_idx=0)
    add_cylinder_prism(( half_w, front_y - 0.15, rail_top_z), ( half_w, porch_front_y + 0.15, rail_bot_z), 0.038, 6, mat_idx=0)

    # Front railings left & right of steps
    r_len_l = abs(-1.25 - (-half_w))
    r_mid_l = -half_w + r_len_l * 0.5
    add_box_prism((r_mid_l, porch_front_y, rail_top_z), (r_len_l - 0.18, 0.09, 0.07), mat_idx=0)
    add_box_prism((r_mid_l, porch_front_y, rail_bot_z), (r_len_l - 0.18, 0.09, 0.07), mat_idx=0)
    add_cylinder_prism((-half_w + 0.15, porch_front_y, rail_bot_z), (-1.25 - 0.15, porch_front_y, rail_top_z), 0.038, 6, mat_idx=0)
    add_cylinder_prism((-half_w + 0.15, porch_front_y, rail_top_z), (-1.25 - 0.15, porch_front_y, rail_bot_z), 0.038, 6, mat_idx=0)

    r_len_r = abs(half_w - 1.25)
    r_mid_r = 1.25 + r_len_r * 0.5
    add_box_prism((r_mid_r, porch_front_y, rail_top_z), (r_len_r - 0.18, 0.09, 0.07), mat_idx=0)
    add_box_prism((r_mid_r, porch_front_y, rail_bot_z), (r_len_r - 0.18, 0.09, 0.07), mat_idx=0)
    add_cylinder_prism((1.25 + 0.15, porch_front_y, rail_bot_z), (half_w - 0.15, porch_front_y, rail_top_z), 0.038, 6, mat_idx=0)
    add_cylinder_prism((1.25 + 0.15, porch_front_y, rail_top_z), (half_w - 0.15, porch_front_y, rail_bot_z), 0.038, 6, mat_idx=0)

    # 3-Tread Steps
    step_w = 2.10
    step_depth = 0.30
    step_h = floor_z / 3.0
    for si in range(3):
        sz = floor_z - (si + 0.5) * step_h
        sy = porch_front_y - (si + 0.5) * step_depth
        add_box_prism((0.0, sy, sz), (step_w, step_depth * 0.98, step_h * 0.95), mat_idx=0, u_scale=2.0, v_scale=0.3)
    add_box_prism((-step_w * 0.5 - 0.05, porch_front_y - 0.45, floor_z * 0.5), (0.08, 0.95, floor_z), mat_idx=0)
    add_box_prism(( step_w * 0.5 + 0.05, porch_front_y - 0.45, floor_z * 0.5), (0.08, 0.95, floor_z), mat_idx=0)

    # -------------------------------------------------------------------------
    # 7. CARVED USFS RANGER STATION SIGN
    # -------------------------------------------------------------------------
    add_box_prism((0.0, porch_front_y - 0.12, 2.96), (2.15, 0.06, 0.44), mat_idx=0, u_scale=2.0, v_scale=0.5)
    add_box_prism((-0.85, porch_front_y - 0.08, 2.80), (0.04, 0.04, 0.42), mat_idx=4)
    add_box_prism(( 0.85, porch_front_y - 0.08, 2.80), (0.04, 0.04, 0.42), mat_idx=4)

    # -------------------------------------------------------------------------
    # 8. REALISTIC PITCHED CORRUGATED METAL GABLE ROOF
    # -------------------------------------------------------------------------
    r_w = half_w + roof_overhang
    r_y_back = back_y + roof_overhang + 0.15
    r_y_front = front_y - roof_overhang - 0.15
    eave_z = wall_z - 0.08
    roof_thick = 0.10

    # Exposed Rafter Tails (8 per side) & Ridge Beam
    add_cylinder_prism((0.0, r_y_front - 0.20, roof_peak_z + 0.06), (0.0, r_y_back + 0.20, roof_peak_z + 0.06), 0.14, 10, mat_idx=0, u_scale=4.0)
    for side_x in [-1.0, 1.0]:
        eave_x = side_x * r_w
        for ri in range(9):
            ry = r_y_front + ri * (r_y_back - r_y_front) / 8.0
            add_box_prism((eave_x - side_x * 0.16, ry, eave_z - 0.05), (0.36, 0.10, 0.10), mat_idx=0)

    # Left slope (-X)
    v_l_top1 = bm.verts.new(Vector((-r_w, r_y_front, eave_z)))
    v_l_top2 = bm.verts.new(Vector((-r_w, r_y_back,  eave_z)))
    v_l_top3 = bm.verts.new(Vector(( 0.0, r_y_back,  roof_peak_z + 0.03)))
    v_l_top4 = bm.verts.new(Vector(( 0.0, r_y_front, roof_peak_z + 0.03)))
    f_l_top = bm.faces.new((v_l_top1, v_l_top2, v_l_top3, v_l_top4))
    f_l_top.material_index = 2
    f_l_top.smooth = False
    f_l_top.loops[0][uv_layer].uv = (0.0, 0.0)
    f_l_top.loops[1][uv_layer].uv = (0.0, 5.0)
    f_l_top.loops[2][uv_layer].uv = (4.0, 5.0)
    f_l_top.loops[3][uv_layer].uv = (4.0, 0.0)

    v_l_bot1 = bm.verts.new(Vector((-r_w, r_y_front, eave_z - roof_thick)))
    v_l_bot2 = bm.verts.new(Vector((-r_w, r_y_back,  eave_z - roof_thick)))
    v_l_bot3 = bm.verts.new(Vector(( 0.0, r_y_back,  roof_peak_z + 0.03 - roof_thick)))
    v_l_bot4 = bm.verts.new(Vector(( 0.0, r_y_front, roof_peak_z + 0.03 - roof_thick)))
    f_l_bot = bm.faces.new((v_l_bot4, v_l_bot3, v_l_bot2, v_l_bot1))
    f_l_bot.material_index = 0
    f_l_bot.smooth = False

    f_l_fascia = bm.faces.new((v_l_top2, v_l_top1, v_l_bot1, v_l_bot2))
    f_l_fascia.material_index = 0

    # Right slope (+X)
    v_r_top1 = bm.verts.new(Vector(( 0.0, r_y_front, roof_peak_z + 0.03)))
    v_r_top2 = bm.verts.new(Vector(( 0.0, r_y_back,  roof_peak_z + 0.03)))
    v_r_top3 = bm.verts.new(Vector(( r_w, r_y_back,  eave_z)))
    v_r_top4 = bm.verts.new(Vector(( r_w, r_y_front, eave_z)))
    f_r_top = bm.faces.new((v_r_top1, v_r_top2, v_r_top3, v_r_top4))
    f_r_top.material_index = 2
    f_r_top.smooth = False
    f_r_top.loops[0][uv_layer].uv = (0.0, 0.0)
    f_r_top.loops[1][uv_layer].uv = (0.0, 5.0)
    f_r_top.loops[2][uv_layer].uv = (4.0, 5.0)
    f_r_top.loops[3][uv_layer].uv = (4.0, 0.0)

    v_r_bot1 = bm.verts.new(Vector(( 0.0, r_y_front, roof_peak_z + 0.03 - roof_thick)))
    v_r_bot2 = bm.verts.new(Vector(( 0.0, r_y_back,  roof_peak_z + 0.03 - roof_thick)))
    v_r_bot3 = bm.verts.new(Vector(( r_w, r_y_back,  eave_z - roof_thick)))
    v_r_bot4 = bm.verts.new(Vector(( r_w, r_y_front, eave_z - roof_thick)))
    f_r_bot = bm.faces.new((v_r_bot4, v_r_bot3, v_r_bot2, v_r_bot1))
    f_r_bot.material_index = 0
    f_r_bot.smooth = False

    f_r_fascia = bm.faces.new((v_r_top4, v_r_top3, v_r_bot3, v_r_bot4))
    f_r_fascia.material_index = 0

    # Gable bargeboards front and back
    for gy, vz_top_l, vz_top_r, vz_bot_l, vz_bot_r in [
        (r_y_front, v_l_top1, v_r_top1, v_l_bot1, v_r_bot1),
        (r_y_back,  v_l_top2, v_r_top2, v_l_bot2, v_r_bot2)
    ]:
        v_ridge_top = v_l_top4 if gy == r_y_front else v_l_top3
        v_ridge_bot = v_l_bot4 if gy == r_y_front else v_l_bot3
        if gy == r_y_front:
            bm.faces.new((vz_top_l, v_ridge_top, v_ridge_bot, vz_bot_l)).material_index = 0
            bm.faces.new((v_ridge_top, vz_top_r, vz_bot_r, v_ridge_bot)).material_index = 0
        else:
            bm.faces.new((v_ridge_top, vz_top_l, vz_bot_l, v_ridge_bot)).material_index = 0
            bm.faces.new((vz_top_r, v_ridge_top, v_ridge_bot, vz_bot_r)).material_index = 0

    # Ridge Cap Roll (Material 2)
    add_box_prism((0.0, (r_y_front + r_y_back) * 0.5, roof_peak_z + 0.07), (0.35, (r_y_back - r_y_front) + 0.04, 0.05), mat_idx=2, u_scale=1.0, v_scale=4.0)

    # -------------------------------------------------------------------------
    # 9. TIMBER PORCH SHED ROOF AWNING (Realistic Sloped Shed Awning)
    # -------------------------------------------------------------------------
    porch_roof_front_y = porch_front_y - 0.28
    pw_top = half_w * 0.96

    # Top corrugated metal deck (sloping from 3.20 down to 2.70)
    v_p1 = bm.verts.new(Vector((-pw_top, porch_roof_front_y, 2.70)))
    v_p2 = bm.verts.new(Vector(( pw_top, porch_roof_front_y, 2.70)))
    v_p3 = bm.verts.new(Vector(( pw_top, front_y + 0.05, 3.20)))
    v_p4 = bm.verts.new(Vector((-pw_top, front_y + 0.05, 3.20)))
    f_p = bm.faces.new((v_p1, v_p2, v_p3, v_p4))
    f_p.material_index = 2
    f_p.smooth = False
    f_p.loops[0][uv_layer].uv = (0.0, 0.0)
    f_p.loops[1][uv_layer].uv = (3.0, 0.0)
    f_p.loops[2][uv_layer].uv = (3.0, 2.0)
    f_p.loops[3][uv_layer].uv = (0.0, 2.0)

    # Underside wood soffit
    v_pb1 = bm.verts.new(Vector((-pw_top, porch_roof_front_y, 2.64)))
    v_pb2 = bm.verts.new(Vector(( pw_top, porch_roof_front_y, 2.64)))
    v_pb3 = bm.verts.new(Vector(( pw_top, front_y + 0.05, 3.14)))
    v_pb4 = bm.verts.new(Vector((-pw_top, front_y + 0.05, 3.14)))
    f_pb = bm.faces.new((v_pb4, v_pb3, v_pb2, v_pb1))
    f_pb.material_index = 0
    f_pb.smooth = False

    # Fascia front edge
    f_pf = bm.faces.new((v_p1, v_pb1, v_pb2, v_p2))
    f_pf.material_index = 0

    # -------------------------------------------------------------------------
    # 10. WOODSTOVE CHIMNEY FLUE & ROOF FLASHING
    # -------------------------------------------------------------------------
    # Stove in Godot is at X = 1.95, Z = -1.10. In Blender: X = 1.95, Y = 1.10
    chim_x = 1.95
    chim_y = 1.10
    add_cylinder_prism((chim_x, chim_y, 2.20), (chim_x, chim_y, 5.35), 0.12, 10, mat_idx=4)
    add_cylinder_prism((chim_x, chim_y, 3.80), (chim_x, chim_y, 3.95), 0.22, 10, mat_idx=4)
    add_cylinder_prism((chim_x, chim_y, 5.35), (chim_x, chim_y, 5.48), 0.24, 10, mat_idx=4)
    add_cylinder_prism((chim_x, chim_y, 5.48), (chim_x, chim_y, 5.56), 0.10, 8, mat_idx=4)

    # -------------------------------------------------------------------------
    # 11. PERIOD STORM LANTERNS (Porch & Interior)
    # -------------------------------------------------------------------------
    lantern_positions = [
        (0.0, -3.40, 2.45), # Porch lantern (Godot Z = +3.40, hung cleanly below porch beam)
        (0.0,  0.00, 2.38)  # Interior ceiling lantern (Godot Z = 0)
    ]
    for lx, ly, lz in lantern_positions:
        add_cylinder_prism((lx, ly, lz + 0.35), (lx, ly, lz + 0.15), 0.012, 6, mat_idx=4)
        add_cylinder_prism((lx, ly, lz + 0.10), (lx, ly, lz + 0.15), 0.10, 8, mat_idx=4)
        add_cylinder_prism((lx, ly, lz + 0.15), (lx, ly, lz + 0.18), 0.06, 8, mat_idx=4)
        add_cylinder_prism((lx, ly, lz - 0.06), (lx, ly, lz + 0.10), 0.08, 8, mat_idx=5)
        add_cylinder_prism((lx, ly, lz - 0.14), (lx, ly, lz - 0.06), 0.11, 8, mat_idx=4)
        for ca in [0, math.pi*0.5, math.pi, math.pi*1.5]:
            wx = lx + math.cos(ca) * 0.09
            wy = ly + math.sin(ca) * 0.09
            add_cylinder_prism((wx, wy, lz - 0.08), (wx, wy, lz + 0.11), 0.006, 4, mat_idx=4)

    # Finalize mesh
    mesh = bpy.data.meshes.new("CabinRangerStationMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("CabinRangerStation", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def setup_materials(obj):
    # Material 0: Weathered brown planks
    p_diff = PROJECT_ROOT / "assets/textures/weathered_brown_planks/weathered_brown_planks_diffuse_1k.jpg"
    p_norm = PROJECT_ROOT / "assets/textures/weathered_brown_planks/weathered_brown_planks_nor_gl_1k.jpg"
    p_rough = PROJECT_ROOT / "assets/textures/weathered_brown_planks/weathered_brown_planks_rough_1k.jpg"
    p_ao = PROJECT_ROOT / "assets/textures/weathered_brown_planks/weathered_brown_planks_ao_1k.jpg"
    m_trim = create_pbr_mat("M_Cabin_Trim", (0.35, 0.28, 0.22, 1.0), roughness=0.82, diff_path=p_diff, norm_path=p_norm, rough_path=p_rough, ao_path=p_ao)

    # Material 1: Cedar log walls (deep weathered timber pine bark)
    l_diff = PROJECT_ROOT / "assets/textures/knotted_pine_bark/knotted_pine_bark_diffuse_1k.jpg"
    l_norm = PROJECT_ROOT / "assets/textures/knotted_pine_bark/knotted_pine_bark_nor_gl_1k.jpg"
    l_rough = PROJECT_ROOT / "assets/textures/knotted_pine_bark/knotted_pine_bark_rough_1k.jpg"
    l_ao = PROJECT_ROOT / "assets/textures/knotted_pine_bark/knotted_pine_bark_ao_1k.jpg"
    m_logs = create_pbr_mat("M_Cabin_Logs", (0.32, 0.24, 0.18, 1.0), roughness=0.88, diff_path=l_diff, norm_path=l_norm, rough_path=l_rough, ao_path=l_ao)

    # Material 2: Rusty corrugated metal roof
    r_diff = PROJECT_ROOT / "assets/textures/polyhaven/rusty_corrugated_iron/rusty_corrugated_iron_diffuse_1k.jpg"
    r_norm = PROJECT_ROOT / "assets/textures/polyhaven/rusty_corrugated_iron/rusty_corrugated_iron_normal_1k.jpg"
    r_rough = PROJECT_ROOT / "assets/textures/polyhaven/rusty_corrugated_iron/rusty_corrugated_iron_rough_1k.jpg"
    r_ao = PROJECT_ROOT / "assets/textures/polyhaven/rusty_corrugated_iron/rusty_corrugated_iron_ao_1k.jpg"
    m_roof = create_pbr_mat("M_Cabin_Roof", (0.42, 0.38, 0.34, 1.0), roughness=0.75, metallic=0.70, diff_path=r_diff, norm_path=r_norm, rough_path=r_rough, ao_path=r_ao)

    # Material 3: Fieldstone masonry
    s_diff = PROJECT_ROOT / "assets/models/polyhaven/rock_moss_set_01/textures/rock_moss_set_01_diff_1k.jpg"
    s_norm = PROJECT_ROOT / "assets/models/polyhaven/rock_moss_set_01/textures/rock_moss_set_01_nor_gl_1k.jpg"
    m_stone = create_pbr_mat("M_Cabin_Stone", (0.35, 0.32, 0.28, 1.0), roughness=0.92, diff_path=s_diff, norm_path=s_norm)

    # Material 4: Weathered dark forged metal
    m_metal = create_pbr_mat("M_Cabin_Metal", (0.16, 0.16, 0.17, 1.0), roughness=0.55, metallic=0.88)

    # Material 5: Window glass & lantern globe
    m_glass = create_pbr_mat("M_Cabin_Glass", (0.85, 0.92, 0.90, 0.4), roughness=0.18, metallic=0.05)

    obj.data.materials.append(m_trim)   # 0
    obj.data.materials.append(m_logs)   # 1
    obj.data.materials.append(m_roof)   # 2
    obj.data.materials.append(m_stone)  # 3
    obj.data.materials.append(m_metal)  # 4
    obj.data.materials.append(m_glass)  # 5

def render_preview(obj, out_path):
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Camera looking at front porch from front-right (+X, -Y, +Z)
    cam_obj.location = Vector((7.5, -9.5, 4.2))
    target = Vector((0.0, -2.6, 2.2))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    # Sun / moonlight
    light_data = bpy.data.lights.new("Moonlight", type='SUN')
    light_data.energy = 2.5
    light_data.color = (0.75, 0.85, 1.0)
    light_obj = bpy.data.objects.new("Moonlight", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-40))

    # Fill light
    fill_data = bpy.data.lights.new("Fill", type='SUN')
    fill_data.energy = 0.8
    fill_data.color = (0.9, 0.8, 0.7)
    fill_obj = bpy.data.objects.new("Fill", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(30), math.radians(-45), math.radians(120))

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = str(out_path)

    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview to {out_path}")

def main():
    print("=== BUILDING PHOTOREALISTIC RANGER STATION IN BLENDER LTS ===")
    reset_scene()
    cabin_obj = build_cabin_mesh()
    setup_materials(cabin_obj)

    tri_count = len(cabin_obj.data.polygons)
    vert_count = len(cabin_obj.data.vertices)
    print(f"Cabin stats: {vert_count} vertices, {tri_count} polygons")

    # Render preview
    preview_dir = PROJECT_ROOT / "docs/graphics/previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_path = preview_dir / "blender_cabin_preview.png"
    render_preview(cabin_obj, preview_path)

    # Select and export GLB
    bpy.ops.object.select_all(action='DESELECT')
    cabin_obj.select_set(True)
    bpy.context.view_layer.objects.active = cabin_obj

    out_glb = PROJECT_ROOT / "assets/models/cabin_ranger_station.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(out_glb),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported Ranger Station GLB to {out_glb}")
    print("=== RANGER STATION GENERATION COMPLETE ===")

if __name__ == "__main__":
    main()
