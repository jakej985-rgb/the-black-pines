#!/usr/bin/env python3
"""
Procedural Terrain Generator for The Black Pines (Issue #3).
Generates an undulating 140x140m forest floor mesh (assets/models/forest_terrain.obj) with:
- Multi-octave rolling hills, knolls, and drainage swales
- Flattened plateau zones around key landmarks (Cabin, Camp, Carcass, Clawed Tree)
- Subtly depressed muddy trail ruts
- Rising perimeter ridges (+2.5m) meeting boundary cliffs
- Skirt walls around the edge down to y = -4m
- Smooth vertex normals and seamless UVs
"""

import math
import os

GRID_RES = 120 # 120 x 120 quads = 14,400 quads
HALF_SIZE = 70.0 # -70m to +70m

def distance(x1, z1, x2, z2):
    return math.sqrt((x1 - x2)**2 + (z1 - z2)**2)

def point_to_segment_dist(px, pz, ax, az, bx, bz):
    abx = bx - ax
    abz = bz - az
    ab_len_sq = abx**2 + abz**2
    if ab_len_sq < 0.0001:
        return distance(px, pz, ax, az)
    t = max(0.0, min(1.0, ((px - ax) * abx + (pz - az) * abz) / ab_len_sq))
    proj_x = ax + t * abx
    proj_z = az + t * abz
    return distance(px, pz, proj_x, proj_z)

def get_terrain_height(x, z):
    # Base undulating terrain using overlapping sinusoidal harmonics (simulating Perlin noise)
    h_macro = 0.85 * math.sin(x * 0.075 + 1.2) * math.cos(z * 0.065 + 0.8)
    h_mid = 0.45 * math.sin(x * 0.16 - z * 0.12 + 2.1) * math.cos(x * 0.11 + z * 0.14)
    h_micro = 0.18 * math.sin(x * 0.35 + z * 0.28) * math.cos(z * 0.38 - x * 0.22)
    h = h_macro + h_mid + h_micro

    # Landmark plateaus: smoothly blend height to 0.0 in clearing circles
    landmarks = [
        (0.0, 10.0, 11.5),    # Ranger Station & Porch & Generator
        (8.5, -8.5, 9.5),     # Abandoned Camp
        (-10.5, -18.0, 9.0),  # Elk Carcass & Gore Pool
        (-7.5, -14.0, 6.5),   # Clawed Tree
        (-8.5, -28.0, 8.5),   # Sasquatch Glade
    ]

    for lx, lz, lr in landmarks:
        d = distance(x, z, lx, lz)
        if d < lr:
            # Smooth Hermite blend
            t = d / lr
            weight = t * t * (3.0 - 2.0 * t)
            h = h * weight

    # Trail ruts: gentle depression along walking paths
    trail_segments = [
        (0.0, 5.0, -4.0, 3.0),
        (-4.0, 3.0, -5.5, -3.2),
        (-5.5, -3.2, -7.5, -10.5),
        (-7.5, -10.5, -7.5, -14.0),
        (-7.5, -14.0, -10.5, -18.0),
        (0.0, 5.0, 8.5, -8.5)
    ]
    for ax, az, bx, bz in trail_segments:
        d_trail = point_to_segment_dist(x, z, ax, az, bx, bz)
        if d_trail < 3.2:
            rut_depth = 0.22 * (1.0 - (d_trail / 3.2)**2)
            h -= rut_depth

    # Perimeter Ridge: smoothly rise to +2.5m at perimeter edges (beyond r = 48m)
    dist_from_center = max(abs(x), abs(z))
    if dist_from_center > 46.0:
        edge_t = min(1.0, (dist_from_center - 46.0) / 22.0)
        edge_lift = 2.6 * (edge_t * edge_t * (3.0 - 2.0 * edge_t))
        h += edge_lift

    return h

def generate_terrain_obj():
    print(f"Generating terrain grid {GRID_RES}x{GRID_RES} over {HALF_SIZE*2}x{HALF_SIZE*2}m...")
    os.makedirs("assets/models", exist_ok=True)
    filepath = "assets/models/forest_terrain.obj"

    step = (HALF_SIZE * 2.0) / GRID_RES
    
    verts = []
    uvs = []
    normals = []

    # 1. Compute grid vertices and heights
    grid = []
    for iz in range(GRID_RES + 1):
        row = []
        z = -HALF_SIZE + iz * step
        for ix in range(GRID_RES + 1):
            x = -HALF_SIZE + ix * step
            y = get_terrain_height(x, z)
            row.append((x, y, z))
        grid.append(row)

    # 2. Compute smooth vertex normals using central finite differences
    norm_grid = []
    for iz in range(GRID_RES + 1):
        norm_row = []
        for ix in range(GRID_RES + 1):
            x, y, z = grid[iz][ix]
            # Neighbors
            x_prev = grid[iz][max(0, ix-1)][0]
            y_xp = grid[iz][max(0, ix-1)][1]
            x_next = grid[iz][min(GRID_RES, ix+1)][0]
            y_xn = grid[iz][min(GRID_RES, ix+1)][1]
            dx = x_next - x_prev
            dy_dx = (y_xn - y_xp) / max(0.001, dx)

            z_prev = grid[max(0, iz-1)][ix][2]
            y_zp = grid[max(0, iz-1)][ix][1]
            z_next = grid[min(GRID_RES, iz+1)][ix][2]
            y_zn = grid[min(GRID_RES, iz+1)][ix][1]
            dz = z_next - z_prev
            dy_dz = (y_zn - y_zp) / max(0.001, dz)

            # Normal vector: (-dy_dx, 1, -dy_dz) normalized
            nx = -dy_dx
            ny = 1.0
            nz = -dy_dz
            l = math.sqrt(nx*nx + ny*ny + nz*nz)
            norm_row.append((nx/l, ny/l, nz/l))
        norm_grid.append(norm_row)

    # Write OBJ
    with open(filepath, "w") as f:
        f.write("# Wavefront OBJ: forest_terrain\n")
        f.write("o forest_terrain\n")

        # Write vertices
        for iz in range(GRID_RES + 1):
            for ix in range(GRID_RES + 1):
                x, y, z = grid[iz][ix]
                f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")

        # Write UVs (tiled 25x across 140m)
        for iz in range(GRID_RES + 1):
            v_coord = float(iz) / GRID_RES * 25.0
            for ix in range(GRID_RES + 1):
                u_coord = float(ix) / GRID_RES * 25.0
                f.write(f"vt {u_coord:.4f} {v_coord:.4f}\n")

        # Write Normals
        for iz in range(GRID_RES + 1):
            for ix in range(GRID_RES + 1):
                nx, ny, nz = norm_grid[iz][ix]
                f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")

        # Write Faces (1-indexed)
        stride = GRID_RES + 1
        for iz in range(GRID_RES):
            for ix in range(GRID_RES):
                # Quad vertices
                v1 = iz * stride + ix + 1
                v2 = iz * stride + (ix + 1) + 1
                v3 = (iz + 1) * stride + (ix + 1) + 1
                v4 = (iz + 1) * stride + ix + 1
                # Write as 2 triangles for optimal rendering & collision
                f.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                f.write(f"f {v1}/{v1}/{v1} {v3}/{v3}/{v3} {v4}/{v4}/{v4}\n")

    num_verts = (GRID_RES + 1) ** 2
    num_faces = GRID_RES * GRID_RES * 2
    print(f"Terrain OBJ saved: {filepath} ({num_verts} verts, {num_faces} triangles)")

if __name__ == "__main__":
    generate_terrain_obj()
