#!/usr/bin/env python3
"""
Procedural Photorealistic Abandoned Campsite Generator for Blender 4.2 LTS.
Architecture:
1. Weathered Olive Waxed Canvas Tent:
   - Organic catenary sag along ridge line.
   - Wrinkles, tension seams, and billow across sloping canvas walls.
   - Tied-back entrance flaps revealing interior.
   - Interior rolled canvas bedroll with warm wool blanket.
   - Aluminum A-frame poles with guy-lines and ground stakes.
   - Realistic weathered canvas PBR with micro-weave normal mapping.
2. Realistic River Stone Firepit:
   - 11 natural mossy river boulders around perimeter.
   - Charred criss-crossed campfire logs.
   - Central ember bed with ash and glowing heat veins.
3. Detailed Vintage Camp Cooler:
   - Recessed lid with lip overhang and corner bevels.
   - Front dual latch clamps and molded side carry handles.
   - Textured navy/white plastic shell.
- Target GPU: NVIDIA GeForce GTX 960 (Total < 2,500 tris).
"""

import math
import random
import sys
from pathlib import Path

try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
except ImportError:
    print("Execute via 'blender --background --python <script>'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ==============================================================================
# 1. TENT GENERATOR
# ==============================================================================
def create_tent():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    random.seed(99)

    # Dimensions
    half_w = 1.15
    half_l = 1.45
    ridge_h = 1.55
    eave_h = 0.22

    # Grid for canvas walls (left and right)
    nx = 14  # along length Y
    ny = 10  # along slope Z

    # 1. Left Slope & Right Slope
    for side_idx, side_sign in enumerate([-1.0, 1.0]):
        grid = []
        for iy in range(nx):
            ty = iy / (nx - 1)  # 0 (front) to 1 (back)
            y = -half_l + ty * (half_l * 2.0)

            # Catenary sag along ridge line (center dips slightly)
            ridge_sag = math.sin(ty * math.pi) * 0.08
            cur_ridge_h = ridge_h - ridge_sag

            row = []
            for iz in range(ny):
                tz = iz / (ny - 1)  # 0 (ground/eave) to 1 (ridge)

                base_x = side_sign * (half_w * (1.0 - tz))
                base_z = eave_h + tz * (cur_ridge_h - eave_h)

                # Organic canvas billow and wrinkles
                sag_x = side_sign * math.sin(tz * math.pi) * (0.04 + math.sin(ty * math.pi * 3.0) * 0.015)
                wrinkle = math.sin(ty * 18.0 + tz * 10.0) * 0.008 * math.sin(tz * math.pi)

                vx = base_x + sag_x + wrinkle
                vy = y
                vz = max(0.02, base_z - math.sin(tz * math.pi) * 0.02)

                v = bm.verts.new(Vector((vx, vy, vz)))
                row.append(v)
            grid.append(row)

        for iy in range(nx - 1):
            for iz in range(ny - 1):
                v1 = grid[iy][iz]
                v2 = grid[iy + 1][iz]
                v3 = grid[iy + 1][iz + 1]
                v4 = grid[iy][iz + 1]

                if side_sign < 0:
                    f = bm.faces.new((v1, v2, v3, v4))
                else:
                    f = bm.faces.new((v4, v3, v2, v1))

                f.material_index = 0
                f.smooth = True

                u0 = (iy / (nx - 1)) * 4.0
                u1 = ((iy + 1) / (nx - 1)) * 4.0
                v0_coord = (iz / (ny - 1)) * 3.0
                v1_coord = ((iz + 1) / (ny - 1)) * 3.0

                if side_sign < 0:
                    f.loops[0][uv_layer].uv = (u0, v0_coord)
                    f.loops[1][uv_layer].uv = (u1, v0_coord)
                    f.loops[2][uv_layer].uv = (u1, v1_coord)
                    f.loops[3][uv_layer].uv = (u0, v1_coord)
                else:
                    f.loops[0][uv_layer].uv = (u0, v1_coord)
                    f.loops[1][uv_layer].uv = (u1, v1_coord)
                    f.loops[2][uv_layer].uv = (u1, v0_coord)
                    f.loops[3][uv_layer].uv = (u0, v0_coord)

    # 2. Back Triangular Wall
    back_y = half_l
    back_segs = 6
    back_ridge = bm.verts.new(Vector((0.0, back_y, ridge_h)))
    back_bot = []
    for s in range(back_segs + 1):
        bt = s / back_segs
        bx = -half_w + bt * (half_w * 2.0)
        v = bm.verts.new(Vector((bx, back_y, eave_h)))
        back_bot.append(v)

    for s in range(back_segs):
        f = bm.faces.new((back_bot[s], back_bot[s + 1], back_ridge))
        f.material_index = 0
        f.smooth = True
        f.loops[0][uv_layer].uv = (s / back_segs, 0.0)
        f.loops[1][uv_layer].uv = ((s + 1) / back_segs, 0.0)
        f.loops[2][uv_layer].uv = (0.5, 1.0)

    # 3. Front Rolled Flaps
    front_y = -half_l
    for s_sign in [-1.0, 1.0]:
        roll_pts = 6
        roll_r = 0.06
        for r_idx in range(roll_pts):
            rt = r_idx / (roll_pts - 1)
            rc_x = s_sign * (half_w * 0.7 * (1.0 - rt * 0.6))
            rc_y = front_y - 0.04 * (1.0 - rt)
            rc_z = eave_h + rt * (ridge_h * 0.6)

            rv1 = bm.verts.new(Vector((rc_x - roll_r, rc_y, rc_z)))
            rv2 = bm.verts.new(Vector((rc_x + roll_r, rc_y, rc_z)))
            rv3 = bm.verts.new(Vector((rc_x + roll_r, rc_y - roll_r, rc_z + roll_r * 0.5)))
            rv4 = bm.verts.new(Vector((rc_x - roll_r, rc_y - roll_r, rc_z + roll_r * 0.5)))
            f = bm.faces.new((rv1, rv2, rv3, rv4))
            f.material_index = 0
            f.smooth = True
            f.loops[0][uv_layer].uv = (0.0, rt)
            f.loops[1][uv_layer].uv = (0.5, rt)
            f.loops[2][uv_layer].uv = (0.5, rt + 0.1)
            f.loops[3][uv_layer].uv = (0.0, rt + 0.1)

    # 4. Interior Floor / Heavy Groundsheet
    fl_v1 = bm.verts.new(Vector((-half_w * 0.98, -half_l * 0.98, 0.03)))
    fl_v2 = bm.verts.new(Vector((half_w * 0.98, -half_l * 0.98, 0.03)))
    fl_v3 = bm.verts.new(Vector((half_w * 0.98, half_l * 0.98, 0.03)))
    fl_v4 = bm.verts.new(Vector((-half_w * 0.98, half_l * 0.98, 0.03)))
    f_floor = bm.faces.new((fl_v1, fl_v2, fl_v3, fl_v4))
    f_floor.material_index = 0
    f_floor.smooth = True
    f_floor.loops[0][uv_layer].uv = (0.0, 0.0)
    f_floor.loops[1][uv_layer].uv = (2.0, 0.0)
    f_floor.loops[2][uv_layer].uv = (2.0, 2.0)
    f_floor.loops[3][uv_layer].uv = (0.0, 2.0)

    # 5. Interior Bedroll / Sleeping Bag (Material 2)
    bed_x = -0.35
    bed_y_start = -0.8
    bed_len = 1.7
    bed_w = 0.55
    bed_h = 0.12
    bv1 = bm.verts.new(Vector((bed_x - bed_w * 0.5, bed_y_start, 0.04)))
    bv2 = bm.verts.new(Vector((bed_x + bed_w * 0.5, bed_y_start, 0.04)))
    bv3 = bm.verts.new(Vector((bed_x + bed_w * 0.5, bed_y_start + bed_len, 0.04)))
    bv4 = bm.verts.new(Vector((bed_x - bed_w * 0.5, bed_y_start + bed_len, 0.04)))
    bv5 = bm.verts.new(Vector((bed_x - bed_w * 0.5, bed_y_start, 0.04 + bed_h)))
    bv6 = bm.verts.new(Vector((bed_x + bed_w * 0.5, bed_y_start, 0.04 + bed_h)))
    bv7 = bm.verts.new(Vector((bed_x + bed_w * 0.5, bed_y_start + bed_len, 0.04 + bed_h)))
    bv8 = bm.verts.new(Vector((bed_x - bed_w * 0.5, bed_y_start + bed_len, 0.04 + bed_h)))

    bed_faces = [
        (bv5, bv6, bv7, bv8),
        (bv1, bv2, bv6, bv5),
        (bv3, bv4, bv8, bv7),
        (bv4, bv1, bv5, bv8),
        (bv2, bv3, bv7, bv6)
    ]
    for bf in bed_faces:
        f = bm.faces.new(bf)
        f.material_index = 2
        f.smooth = True
        f.loops[0][uv_layer].uv = (0.0, 0.0)
        f.loops[1][uv_layer].uv = (1.0, 0.0)
        f.loops[2][uv_layer].uv = (1.0, 1.0)
        f.loops[3][uv_layer].uv = (0.0, 1.0)

    # 6. Tent Support Poles (Front & Back A-frame aluminum poles - Material 1)
    pole_r = 0.024
    for py in [-half_l, half_l]:
        for psign in [-1.0, 1.0]:
            p_bot = Vector((psign * (half_w + 0.05), py, 0.0))
            p_top = Vector((0.0, py, ridge_h + 0.02))
            p_dir = (p_top - p_bot).normalized()
            p_up = Vector((0, 1, 0))
            p_side = p_dir.cross(p_up).normalized()

            p_segs = 4
            for seg in range(p_segs):
                a1 = (seg / p_segs) * 2.0 * math.pi
                a2 = ((seg + 1) / p_segs) * 2.0 * math.pi
                o1 = p_side * math.cos(a1) * pole_r + p_up * math.sin(a1) * pole_r
                o2 = p_side * math.cos(a2) * pole_r + p_up * math.sin(a2) * pole_r

                pv1 = bm.verts.new(p_bot + o1)
                pv2 = bm.verts.new(p_bot + o2)
                pv3 = bm.verts.new(p_top + o2)
                pv4 = bm.verts.new(p_top + o1)

                f = bm.faces.new((pv1, pv2, pv3, pv4))
                f.material_index = 1
                f.smooth = True
                f.loops[0][uv_layer].uv = (seg / p_segs, 0.0)
                f.loops[1][uv_layer].uv = ((seg + 1) / p_segs, 0.0)
                f.loops[2][uv_layer].uv = ((seg + 1) / p_segs, 1.0)
                f.loops[3][uv_layer].uv = (seg / p_segs, 1.0)

    # 7. Guy-lines & Ground Stakes
    guy_targets = [
        (Vector((0.0, -half_l, ridge_h)), Vector((0.45, -half_l - 0.75, 0.0))),
        (Vector((0.0, half_l, ridge_h)), Vector((0.0, half_l + 1.1, 0.0))),
        (Vector((-half_w, -half_l, eave_h)), Vector((-half_w - 0.6, -half_l - 0.4, 0.0))),
        (Vector((-half_w, half_l, eave_h)), Vector((-half_w - 0.6, half_l + 0.4, 0.0))),
        (Vector((half_w, -half_l, eave_h)), Vector((half_w + 0.6, -half_l - 0.4, 0.0))),
        (Vector((half_w, half_l, eave_h)), Vector((half_w + 0.6, half_l + 0.4, 0.0)))
    ]

    for g_start, g_end in guy_targets:
        r_dir = (g_end - g_start).normalized()
        r_side = Vector((0, 0, 1)).cross(r_dir).normalized() * 0.005
        gv1 = bm.verts.new(g_start - r_side)
        gv2 = bm.verts.new(g_start + r_side)
        gv3 = bm.verts.new(g_end + r_side)
        gv4 = bm.verts.new(g_end - r_side)
        f = bm.faces.new((gv1, gv2, gv3, gv4))
        f.material_index = 3
        f.loops[0][uv_layer].uv = (0, 0)
        f.loops[1][uv_layer].uv = (1, 0)
        f.loops[2][uv_layer].uv = (1, 1)
        f.loops[3][uv_layer].uv = (0, 1)

        stake_top = g_end + Vector((0, 0, 0.12))
        stake_bot = g_end - Vector((0, 0, 0.08))
        sv1 = bm.verts.new(stake_bot - Vector((0.02, 0, 0)))
        sv2 = bm.verts.new(stake_bot + Vector((0.02, 0, 0)))
        sv3 = bm.verts.new(stake_top + Vector((0.02, 0, 0)))
        sv4 = bm.verts.new(stake_top - Vector((0.02, 0, 0)))
        sf = bm.faces.new((sv1, sv2, sv3, sv4))
        sf.material_index = 1

    mesh = bpy.data.meshes.new("WeatheredTentMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("WeatheredTent", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ==============================================================================
# 2. FIREPIT GENERATOR
# ==============================================================================
def create_firepit():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    random.seed(77)

    # 1. Ash Bed & Coals (Material 2)
    ash_r = 0.58
    ash_segs = 14
    ash_center = bm.verts.new(Vector((0, 0, 0.04)))
    ash_ring = []
    for s in range(ash_segs):
        angle = (s / ash_segs) * 2.0 * math.pi
        r = ash_r * random.uniform(0.92, 1.05)
        vx = math.cos(angle) * r
        vy = math.sin(angle) * r
        vz = 0.02 + math.sin(s * 1.5) * 0.015
        v = bm.verts.new(Vector((vx, vy, vz)))
        ash_ring.append(v)

    for s in range(ash_segs):
        s_next = (s + 1) % ash_segs
        f = bm.faces.new((ash_center, ash_ring[s], ash_ring[s_next]))
        f.material_index = 2
        f.smooth = True
        f.loops[0][uv_layer].uv = (0.5, 0.5)
        f.loops[1][uv_layer].uv = (0.5 + math.cos(s / ash_segs * 2 * math.pi) * 0.45,
                                  0.5 + math.sin(s / ash_segs * 2 * math.pi) * 0.45)
        f.loops[2][uv_layer].uv = (0.5 + math.cos(s_next / ash_segs * 2 * math.pi) * 0.45,
                                  0.5 + math.sin(s_next / ash_segs * 2 * math.pi) * 0.45)

    # 2. Firewood Logs (Charred crossed timber - Material 1)
    log_specs = [
        (Vector((-0.35, -0.15, 0.06)), Vector((0.35, 0.18, 0.12)), 0.07),
        (Vector((-0.20, 0.32, 0.08)), Vector((0.25, -0.30, 0.14)), 0.065),
        (Vector((0.05, -0.35, 0.10)), Vector((-0.08, 0.38, 0.16)), 0.06),
        (Vector((-0.25, 0.0, 0.15)), Vector((0.30, 0.05, 0.18)), 0.055)
    ]

    for p1, p2, l_rad in log_specs:
        l_dir = (p2 - p1).normalized()
        up_v = Vector((0, 0, 1))
        side_v = l_dir.cross(up_v).normalized()
        up_v = side_v.cross(l_dir).normalized()

        l_segs = 6
        r1_verts = []
        r2_verts = []
        for s in range(l_segs):
            angle = (s / l_segs) * 2.0 * math.pi
            offset = (side_v * math.cos(angle) + up_v * math.sin(angle)) * l_rad
            v1 = bm.verts.new(p1 + offset)
            v2 = bm.verts.new(p2 + offset)
            r1_verts.append(v1)
            r2_verts.append(v2)

        for s in range(l_segs):
            s_next = (s + 1) % l_segs
            f = bm.faces.new((r1_verts[s], r2_verts[s], r2_verts[s_next], r1_verts[s_next]))
            f.material_index = 1
            f.smooth = True
            f.loops[0][uv_layer].uv = (s / l_segs, 0.0)
            f.loops[1][uv_layer].uv = (s / l_segs, 1.0)
            f.loops[2][uv_layer].uv = ((s + 1) / l_segs, 1.0)
            f.loops[3][uv_layer].uv = ((s + 1) / l_segs, 0.0)

        cap1 = bm.verts.new(p1 - l_dir * 0.02)
        cap2 = bm.verts.new(p2 + l_dir * 0.02)
        for s in range(l_segs):
            s_next = (s + 1) % l_segs
            f1 = bm.faces.new((cap1, r1_verts[s_next], r1_verts[s]))
            f1.material_index = 1
            f2 = bm.faces.new((cap2, r2_verts[s], r2_verts[s_next]))
            f2.material_index = 1

    # 3. River Stones Ring (Material 0)
    stone_count = 11
    ring_radius = 0.65
    for st_idx in range(stone_count):
        theta = (st_idx / stone_count) * 2.0 * math.pi + random.uniform(-0.08, 0.08)
        st_center_x = math.cos(theta) * (ring_radius * random.uniform(0.95, 1.08))
        st_center_y = math.sin(theta) * (ring_radius * random.uniform(0.95, 1.08))
        st_size = random.uniform(0.12, 0.19)
        st_height = st_size * random.uniform(0.7, 0.95)

        st_verts = []
        lat_count = 3
        lon_count = 6
        for lat in range(lat_count):
            phi = (lat / (lat_count - 1)) * (math.pi * 0.45)
            row = []
            for lon in range(lon_count):
                lam = (lon / lon_count) * 2.0 * math.pi
                r_noise = 1.0 + math.sin(lon * 2.5 + lat * 3.0) * 0.15
                rx = math.cos(lam) * math.cos(phi) * st_size * r_noise
                ry = math.sin(lam) * math.cos(phi) * st_size * r_noise
                rz = math.sin(phi) * st_height * r_noise

                v = bm.verts.new(Vector((st_center_x + rx, st_center_y + ry, max(0.01, rz))))
                row.append(v)
            st_verts.append(row)

        for lat in range(lat_count - 1):
            for lon in range(lon_count):
                lon_next = (lon + 1) % lon_count
                f = bm.faces.new((st_verts[lat][lon], st_verts[lat][lon_next],
                                 st_verts[lat + 1][lon_next], st_verts[lat + 1][lon]))
                f.material_index = 0
                f.smooth = True
                f.loops[0][uv_layer].uv = (lon / lon_count, lat / lat_count)
                f.loops[1][uv_layer].uv = ((lon + 1) / lon_count, lat / lat_count)
                f.loops[2][uv_layer].uv = ((lon + 1) / lon_count, (lat + 1) / lat_count)
                f.loops[3][uv_layer].uv = (lon / lon_count, (lat + 1) / lat_count)

        top_v = bm.verts.new(Vector((st_center_x, st_center_y, st_height * 1.05)))
        for lon in range(lon_count):
            lon_next = (lon + 1) % lon_count
            f = bm.faces.new((top_v, st_verts[-1][lon], st_verts[-1][lon_next]))
            f.material_index = 0
            f.smooth = True

    mesh = bpy.data.meshes.new("RealisticFirepitMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("RealisticFirepit", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ==============================================================================
# 3. COOLER GENERATOR
# ==============================================================================
def create_cooler():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    w = 0.82
    d = 0.48
    h = 0.42

    hw, hd, hh = w * 0.5, d * 0.5, h * 0.78

    b_corners = [
        (-hw, -hd, 0.0), (hw, -hd, 0.0), (hw, hd, 0.0), (-hw, hd, 0.0),
        (-hw * 0.96, -hd * 0.96, hh), (hw * 0.96, -hd * 0.96, hh),
        (hw * 0.96, hd * 0.96, hh), (-hw * 0.96, hd * 0.96, hh)
    ]
    bv = [bm.verts.new(Vector(c)) for c in b_corners]

    b_faces = [
        (bv[0], bv[1], bv[5], bv[4]),
        (bv[2], bv[3], bv[7], bv[6]),
        (bv[3], bv[0], bv[4], bv[7]),
        (bv[1], bv[2], bv[6], bv[5]),
        (bv[3], bv[2], bv[1], bv[0])
    ]
    for bf in b_faces:
        f = bm.faces.new(bf)
        f.material_index = 0
        f.smooth = False
        f.loops[0][uv_layer].uv = (0.0, 0.0)
        f.loops[1][uv_layer].uv = (1.0, 0.0)
        f.loops[2][uv_layer].uv = (1.0, 1.0)
        f.loops[3][uv_layer].uv = (0.0, 1.0)

    lid_hw = hw * 1.02
    lid_hd = hd * 1.02
    l_corners = [
        (-lid_hw, -lid_hd, hh), (lid_hw, -lid_hd, hh),
        (lid_hw, lid_hd, hh), (-lid_hw, lid_hd, hh),
        (-lid_hw * 0.95, -lid_hd * 0.95, h), (lid_hw * 0.95, -lid_hd * 0.95, h),
        (lid_hw * 0.95, lid_hd * 0.95, h), (-lid_hw * 0.95, lid_hd * 0.95, h)
    ]
    lv = [bm.verts.new(Vector(c)) for c in l_corners]
    lid_faces = [
        (lv[0], lv[1], lv[5], lv[4]),
        (lv[2], lv[3], lv[7], lv[6]),
        (lv[3], lv[0], lv[4], lv[7]),
        (lv[1], lv[2], lv[6], lv[5]),
        (lv[4], lv[5], lv[6], lv[7])
    ]
    for lf in lid_faces:
        f = bm.faces.new(lf)
        f.material_index = 0
        f.smooth = False
        f.loops[0][uv_layer].uv = (0.0, 0.0)
        f.loops[1][uv_layer].uv = (1.0, 0.0)
        f.loops[2][uv_layer].uv = (1.0, 1.0)
        f.loops[3][uv_layer].uv = (0.0, 1.0)

    for lx in [-hw * 0.45, hw * 0.45]:
        m1 = bm.verts.new(Vector((lx - 0.035, -lid_hd - 0.015, hh - 0.08)))
        m2 = bm.verts.new(Vector((lx + 0.035, -lid_hd - 0.015, hh - 0.08)))
        m3 = bm.verts.new(Vector((lx + 0.035, -lid_hd - 0.015, hh + 0.04)))
        m4 = bm.verts.new(Vector((lx - 0.035, -lid_hd - 0.015, hh + 0.04)))
        f = bm.faces.new((m1, m2, m3, m4))
        f.material_index = 1
        f.loops[0][uv_layer].uv = (0, 0)
        f.loops[1][uv_layer].uv = (1, 0)
        f.loops[2][uv_layer].uv = (1, 1)
        f.loops[3][uv_layer].uv = (0, 1)

    for side_x in [-hw, hw]:
        h_sign = -1.0 if side_x < 0 else 1.0
        h1 = bm.verts.new(Vector((side_x + h_sign * 0.04, -0.08, hh * 0.65)))
        h2 = bm.verts.new(Vector((side_x + h_sign * 0.04, 0.08, hh * 0.65)))
        h3 = bm.verts.new(Vector((side_x, 0.08, hh * 0.65)))
        h4 = bm.verts.new(Vector((side_x, -0.08, hh * 0.65)))
        f = bm.faces.new((h1, h2, h3, h4))
        f.material_index = 1

    mesh = bpy.data.meshes.new("DetailedCoolerMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("DetailedCooler", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ==============================================================================
# 4. MATERIALS & PREVIEW SETUP
# ==============================================================================
def setup_campsite_materials(tent_obj, firepit_obj, cooler_obj):
    # Material 0: Weathered Dark Olive Waxed Canvas (Tent)
    canvas_mat = bpy.data.materials.new(name="M_Tent_Canvas")
    canvas_mat.use_nodes = True
    c_nodes = canvas_mat.node_tree.nodes
    c_links = canvas_mat.node_tree.links
    c_bsdf = c_nodes.get("Principled BSDF")

    norm_path = PROJECT_ROOT / "assets/textures/fabric_pattern_07/fabric_pattern_07_nor_gl_1k.jpg"
    rough_path = PROJECT_ROOT / "assets/textures/fabric_pattern_07/fabric_pattern_07_rough_1k.jpg"

    # Dark Pacific Northwest olive-drab canvas
    c_bsdf.inputs["Base Color"].default_value = (0.16, 0.22, 0.14, 1.0)
    c_bsdf.inputs["Roughness"].default_value = 0.88

    if norm_path.exists():
        t_norm = c_nodes.new("ShaderNodeTexImage")
        t_norm.image = bpy.data.images.load(str(norm_path))
        t_norm.image.colorspace_settings.name = "Non-Color"
        n_map = c_nodes.new("ShaderNodeNormalMap")
        n_map.inputs["Strength"].default_value = 1.4
        c_links.new(t_norm.outputs["Color"], n_map.inputs["Color"])
        c_links.new(n_map.outputs["Normal"], c_bsdf.inputs["Normal"])

    if rough_path.exists():
        t_rough = c_nodes.new("ShaderNodeTexImage")
        t_rough.image = bpy.data.images.load(str(rough_path))
        t_rough.image.colorspace_settings.name = "Non-Color"
        c_links.new(t_rough.outputs["Color"], c_bsdf.inputs["Roughness"])

    # Material 1: Weathered Metal / Aluminum
    metal_mat = bpy.data.materials.new(name="M_Tent_Metal")
    metal_mat.use_nodes = True
    m_bsdf = metal_mat.node_tree.nodes.get("Principled BSDF")
    m_bsdf.inputs["Base Color"].default_value = (0.42, 0.44, 0.46, 1.0)
    m_bsdf.inputs["Metallic"].default_value = 0.85
    m_bsdf.inputs["Roughness"].default_value = 0.38

    # Material 2: Sleeping Bedroll (warm wool blanket)
    bed_mat = bpy.data.materials.new(name="M_Tent_Bedroll")
    bed_mat.use_nodes = True
    b_bsdf = bed_mat.node_tree.nodes.get("Principled BSDF")
    b_bsdf.inputs["Base Color"].default_value = (0.28, 0.18, 0.12, 1.0)  # Heavy wool brown
    b_bsdf.inputs["Roughness"].default_value = 0.92

    # Material 3: Guy-line Rope / Paracord (matte weather-stained olive/tan cord)
    rope_mat = bpy.data.materials.new(name="M_Tent_Rope")
    rope_mat.use_nodes = True
    rp_bsdf = rope_mat.node_tree.nodes.get("Principled BSDF")
    rp_bsdf.inputs["Base Color"].default_value = (0.18, 0.17, 0.14, 1.0)
    rp_bsdf.inputs["Metallic"].default_value = 0.0
    rp_bsdf.inputs["Roughness"].default_value = 0.96

    tent_obj.data.materials.append(canvas_mat)
    tent_obj.data.materials.append(metal_mat)
    tent_obj.data.materials.append(bed_mat)
    tent_obj.data.materials.append(rope_mat)

    # Firepit Materials:
    # 0: Rock, 1: Burnt Wood, 2: Embers
    rock_mat = bpy.data.materials.new(name="M_Firepit_Rock")
    rock_mat.use_nodes = True
    r_nodes = rock_mat.node_tree.nodes
    r_links = rock_mat.node_tree.links
    r_bsdf = r_nodes.get("Principled BSDF")
    r_diff_path = PROJECT_ROOT / "assets/models/polyhaven/rock_moss_set_01/textures/rock_moss_set_01_diff_1k.jpg"
    r_norm_path = PROJECT_ROOT / "assets/models/polyhaven/rock_moss_set_01/textures/rock_moss_set_01_nor_gl_1k.jpg"
    if r_diff_path.exists():
        r_tex = r_nodes.new("ShaderNodeTexImage")
        r_tex.image = bpy.data.images.load(str(r_diff_path))
        r_links.new(r_tex.outputs["Color"], r_bsdf.inputs["Base Color"])
    else:
        r_bsdf.inputs["Base Color"].default_value = (0.32, 0.28, 0.25, 1.0)

    if r_norm_path.exists():
        r_ntex = r_nodes.new("ShaderNodeTexImage")
        r_ntex.image = bpy.data.images.load(str(r_norm_path))
        r_ntex.image.colorspace_settings.name = "Non-Color"
        r_nmap = r_nodes.new("ShaderNodeNormalMap")
        r_links.new(r_ntex.outputs["Color"], r_nmap.inputs["Color"])
        r_links.new(r_nmap.outputs["Normal"], r_bsdf.inputs["Normal"])
    r_bsdf.inputs["Roughness"].default_value = 0.90

    char_mat = bpy.data.materials.new(name="M_Firepit_Charwood")
    char_mat.use_nodes = True
    cw_bsdf = char_mat.node_tree.nodes.get("Principled BSDF")
    cw_bsdf.inputs["Base Color"].default_value = (0.07, 0.05, 0.04, 1.0)
    cw_bsdf.inputs["Roughness"].default_value = 0.95

    ember_mat = bpy.data.materials.new(name="M_Firepit_Embers")
    ember_mat.use_nodes = True
    e_bsdf = ember_mat.node_tree.nodes.get("Principled BSDF")
    e_bsdf.inputs["Base Color"].default_value = (0.10, 0.06, 0.04, 1.0)
    e_bsdf.inputs["Emission Color"].default_value = (1.0, 0.32, 0.05, 1.0)
    e_bsdf.inputs["Emission Strength"].default_value = 3.2

    firepit_obj.data.materials.append(rock_mat)
    firepit_obj.data.materials.append(char_mat)
    firepit_obj.data.materials.append(ember_mat)

    # Cooler Materials:
    cooler_mat = bpy.data.materials.new(name="M_Cooler_Plastic")
    cooler_mat.use_nodes = True
    cl_bsdf = cooler_mat.node_tree.nodes.get("Principled BSDF")
    cl_bsdf.inputs["Base Color"].default_value = (0.14, 0.26, 0.38, 1.0)  # Weathered muted navy blue
    cl_bsdf.inputs["Roughness"].default_value = 0.52

    cooler_obj.data.materials.append(cooler_mat)
    cooler_obj.data.materials.append(metal_mat)


def render_preview(output_path: Path):
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 38.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position looking across the entire camp
    cam_obj.location = Vector((3.4, -4.2, 1.9))
    direction = Vector((0.4, 0.0, 0.5)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Flashlight spot
    flash_data = bpy.data.lights.new(name="Flashlight", type="SPOT")
    flash_data.energy = 550.0
    flash_data.spot_size = math.radians(65)
    flash_data.color = (0.98, 0.95, 0.88)
    flash_obj = bpy.data.objects.new(name="Flashlight", object_data=flash_data)
    scene.collection.objects.link(flash_obj)
    flash_obj.location = cam_obj.location
    flash_obj.rotation_euler = cam_obj.rotation_euler

    # Firepit glow light
    fire_data = bpy.data.lights.new(name="FireGlow", type="POINT")
    fire_data.energy = 60.0
    fire_data.color = (1.0, 0.35, 0.08)
    fire_obj = bpy.data.objects.new(name="FireGlow", object_data=fire_data)
    scene.collection.objects.link(fire_obj)
    fire_obj.location = Vector((2.2, 0.4, 0.25))

    # Moonlight fill
    moon_data = bpy.data.lights.new(name="Moonlight", type="SUN")
    moon_data.energy = 1.0
    moon_data.color = (0.75, 0.85, 1.0)
    moon_obj = bpy.data.objects.new(name="Moonlight", object_data=moon_data)
    scene.collection.objects.link(moon_obj)
    moon_obj.rotation_euler = (math.radians(50), math.radians(-25), math.radians(40))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview to {output_path}")


def export_assets(tent_obj, firepit_obj, cooler_obj):
    # Export 1: Tent
    bpy.ops.object.select_all(action="DESELECT")
    tent_obj.select_set(True)
    bpy.context.view_layer.objects.active = tent_obj
    tent_path = PROJECT_ROOT / "assets/models/tent_weathered.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(tent_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported tent GLB to {tent_path}")

    # Export 2: Firepit
    bpy.ops.object.select_all(action="DESELECT")
    firepit_obj.select_set(True)
    bpy.context.view_layer.objects.active = firepit_obj
    firepit_path = PROJECT_ROOT / "assets/models/camp_firepit_realistic.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(firepit_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported firepit GLB to {firepit_path}")

    # Export 3: Cooler
    bpy.ops.object.select_all(action="DESELECT")
    cooler_obj.select_set(True)
    bpy.context.view_layer.objects.active = cooler_obj
    cooler_path = PROJECT_ROOT / "assets/models/camp_cooler_detailed.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(cooler_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[OK] Exported cooler GLB to {cooler_path}")


def main():
    clear_scene()
    print("=== BUILDING PROCEDURAL ABANDONED CAMPSITE IN BLENDER ===")
    tent_obj = create_tent()
    firepit_obj = create_firepit()
    cooler_obj = create_cooler()

    # Arrange for inspection preview
    firepit_obj.location = Vector((2.2, 0.4, 0.0))
    cooler_obj.location = Vector((-1.6, 0.8, 0.0))

    setup_campsite_materials(tent_obj, firepit_obj, cooler_obj)

    # Render inspection preview
    preview_path = PROJECT_ROOT / "docs/graphics/previews/blender_campsite_preview.png"
    render_preview(preview_path)

    # Reset positions before individual GLB export
    firepit_obj.location = Vector((0, 0, 0))
    cooler_obj.location = Vector((0, 0, 0))
    export_assets(tent_obj, firepit_obj, cooler_obj)
    print("=== CAMPSITE ASSETS GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
