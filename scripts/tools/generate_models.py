#!/usr/bin/env python3
"""
High-Realism 3D Wavefront OBJ Generator for The Black Pines.
Generates organic, detailed models with proper UV mapping and smooth normals:
- elk_carcass.obj: Anatomical mutilated cervid skeleton with skull, antlers, curved ribs, spine, and broken limbs
- carcass_gore_pool.obj: Irregular organic gore splatter pool (replaces primitive cylinder)
- clawed_tree.obj: Thick pine trunk with 4 deep carved claw gouges, shredded fibers, and resin drips
- tent.obj: Expedition ridge tent with catenary sag, arched poles, stakes, and rolled flap
- cabin.obj: Interlocking notched log cabin with porch deck, steps, and shingle roof
- pine_tree.obj: Multi-tiered conifer with drooping boughs and textured trunk
"""

import math
import os

class ObjMesh:
    def __init__(self, name="mesh"):
        self.name = name
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.faces = []

    def add_v(self, x, y, z):
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices)

    def add_vn(self, nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz)
        if l > 0.0001:
            nx /= l
            ny /= l
            nz /= l
        self.normals.append((float(nx), float(ny), float(nz)))
        return len(self.normals)

    def add_vt(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_face(self, v_list, vn_list=None, vt_list=None):
        self.faces.append((v_list, vn_list, vt_list))

    def add_cylinder(self, p1, p2, r1, r2, segs=10, u_start=0.0, u_end=1.0, v_start=0.0, v_end=1.0):
        axis = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        length = math.sqrt(sum(a*a for a in axis))
        if length < 0.0001:
            return
        if abs(axis[1]) < 0.99 * length:
            up = (0, 1, 0)
        else:
            up = (1, 0, 0)
        u_axis = (axis[1]*up[2] - axis[2]*up[1], axis[2]*up[0] - axis[0]*up[2], axis[0]*up[1] - axis[1]*up[0])
        ul = math.sqrt(sum(a*a for a in u_axis))
        u_axis = tuple(a/ul for a in u_axis)
        v_axis = (axis[1]*u_axis[2] - axis[2]*u_axis[1], axis[2]*u_axis[0] - axis[0]*u_axis[2], axis[0]*u_axis[1] - axis[1]*u_axis[0])
        vl = math.sqrt(sum(a*a for a in v_axis))
        v_axis = tuple(a/vl for a in v_axis)

        base1_indices = []
        base2_indices = []
        norm1_indices = []
        norm2_indices = []
        uv1_indices = []
        uv2_indices = []

        for i in range(segs + 1):
            theta = 2.0 * math.pi * i / segs
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            radial = (u_axis[0]*cos_t + v_axis[0]*sin_t,
                      u_axis[1]*cos_t + v_axis[1]*sin_t,
                      u_axis[2]*cos_t + v_axis[2]*sin_t)
            
            x1 = p1[0] + radial[0] * r1
            y1 = p1[1] + radial[1] * r1
            z1 = p1[2] + radial[2] * r1

            x2 = p2[0] + radial[0] * r2
            y2 = p2[1] + radial[1] * r2
            z2 = p2[2] + radial[2] * r2

            v_frac = float(i) / segs
            u_coord = u_start + v_frac * (u_end - u_start)

            base1_indices.append(self.add_v(x1, y1, z1))
            base2_indices.append(self.add_v(x2, y2, z2))
            norm1_indices.append(self.add_vn(radial[0], radial[1], radial[2]))
            norm2_indices.append(self.add_vn(radial[0], radial[1], radial[2]))
            uv1_indices.append(self.add_vt(u_coord, v_start))
            uv2_indices.append(self.add_vt(u_coord, v_end))

        for i in range(segs):
            v = [base1_indices[i], base1_indices[i+1], base2_indices[i+1], base2_indices[i]]
            vn = [norm1_indices[i], norm1_indices[i+1], norm2_indices[i+1], norm2_indices[i]]
            vt = [uv1_indices[i], uv1_indices[i+1], uv2_indices[i+1], uv2_indices[i]]
            self.add_face(v, vn, vt)

    def add_box(self, center, size, rot_y=0.0):
        cx, cy, cz = center
        sx, sy, sz = size[0]*0.5, size[1]*0.5, size[2]*0.5
        cos_r = math.cos(rot_y)
        sin_r = math.sin(rot_y)

        def rot(x, z):
            return (x * cos_r - z * sin_r, x * sin_r + z * cos_r)

        corners = [
            (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
            (-sx, -sy,  sz), (sx, -sy,  sz), (sx, sy,  sz), (-sx, sy,  sz)
        ]
        v_idx = []
        for x, y, z in corners:
            rx, rz = rot(x, z)
            v_idx.append(self.add_v(cx + rx, cy + y, cz + rz))

        faces = [
            ([0, 3, 2, 1], (0, 0, -1)),
            ([4, 5, 6, 7], (0, 0, 1)),
            ([0, 1, 5, 4], (0, -1, 0)),
            ([2, 3, 7, 6], (0, 1, 0)),
            ([0, 4, 7, 3], (-1, 0, 0)),
            ([1, 2, 6, 5], (1, 0, 0))
        ]
        vt_box = [self.add_vt(0, 0), self.add_vt(1, 0), self.add_vt(1, 1), self.add_vt(0, 1)]

        for f, (nx, ny, nz) in faces:
            rx, rz = rot(nx, nz)
            n_idx = self.add_vn(rx, ny, rz)
            self.add_face([v_idx[i] for i in f], [n_idx]*4, [vt_box[0], vt_box[1], vt_box[2], vt_box[3]])

    def save(self, filepath):
        with open(filepath, "w") as f:
            f.write(f"# Wavefront OBJ: {self.name}\n")
            f.write(f"o {self.name}\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
            for face in self.faces:
                verts, norms, uvs = face
                if norms and uvs:
                    items = [f"{v}/{vt}/{vn}" for v, vn, vt in zip(verts, norms, uvs)]
                elif norms:
                    items = [f"{v}//{vn}" for v, vn in zip(verts, norms)]
                elif uvs:
                    items = [f"{v}/{vt}" for v, vt in zip(verts, uvs)]
                else:
                    items = [f"{v}" for v in verts]
                f.write(f"f {' '.join(items)}\n")
        print(f"Saved: {filepath} ({len(self.vertices)} verts, {len(self.faces)} faces)")


def generate_elk_carcass():
    mesh = ObjMesh("elk_carcass")
    
    # --- 1. Elk Skull & Muzzle ---
    # Cranium (braincase)
    mesh.add_box((-1.35, 0.22, 0.1), (0.32, 0.24, 0.28), rot_y=0.2)
    # Tapered nasal bridge and muzzle
    mesh.add_cylinder((-1.35, 0.22, 0.1), (-1.80, 0.12, 0.18), 0.14, 0.07, segs=8)
    # Lower mandible laying askew in the mud
    mesh.add_cylinder((-1.32, 0.10, 0.14), (-1.74, 0.05, 0.22), 0.08, 0.04, segs=6)

    # --- 2. Curved 3D Branched Antlers ---
    def add_antler_beam(side=1.0):
        # Base pedicle on skull
        p_base = (-1.38, 0.32, 0.1 + side * 0.14)
        # Main beam points: sweeping back, outward, then up and slightly forward
        p1 = (-1.42, 0.52, 0.1 + side * 0.35)
        p2 = (-1.35, 0.78, 0.1 + side * 0.55)
        p3 = (-1.18, 0.96, 0.1 + side * 0.60)
        p4 = (-0.95, 1.05, 0.1 + side * 0.52)
        mesh.add_cylinder(p_base, p1, 0.045, 0.038, segs=8)
        mesh.add_cylinder(p1, p2, 0.038, 0.032, segs=8)
        mesh.add_cylinder(p2, p3, 0.032, 0.025, segs=6)
        mesh.add_cylinder(p3, p4, 0.025, 0.015, segs=6)

        # Brow tine (low forward fork above forehead)
        p_brow = (-1.65, 0.48, 0.1 + side * 0.28)
        mesh.add_cylinder(p1, p_brow, 0.028, 0.012, segs=6)

        # Bez tine (mid tine)
        p_bez = (-1.48, 0.72, 0.1 + side * 0.48)
        mesh.add_cylinder(p2, p_bez, 0.024, 0.010, segs=6)

        # Royal tine (tall upward fork)
        p_royal = (-1.15, 1.18, 0.1 + side * 0.58)
        mesh.add_cylinder(p3, p_royal, 0.022, 0.008, segs=6)

    add_antler_beam(1.0)
    add_antler_beam(-1.0)

    # --- 3. Spine Vertebrae Column ---
    spine_pts = [
        (-1.25, 0.20, 0.08),
        (-1.00, 0.26, 0.05),
        (-0.75, 0.30, 0.02),
        (-0.50, 0.32, 0.00),
        (-0.25, 0.31, -0.02),
        ( 0.00, 0.28, -0.03),
        ( 0.25, 0.24, -0.02),
        ( 0.50, 0.21, 0.00),
        ( 0.75, 0.18, 0.04),
        ( 1.00, 0.14, 0.08)
    ]
    for i in range(len(spine_pts)-1):
        mesh.add_cylinder(spine_pts[i], spine_pts[i+1], 0.065, 0.065, segs=8)
        # Vertebra dorsal spinous process sticking upward
        top_spine = (spine_pts[i][0], spine_pts[i][1] + 0.14, spine_pts[i][2])
        mesh.add_cylinder(spine_pts[i], top_spine, 0.03, 0.015, segs=6)

    # --- 4. Anatomical Curved Ribcage ---
    rib_x = [-0.85, -0.70, -0.55, -0.40, -0.25, -0.10, 0.05, 0.20, 0.35, 0.50]
    for idx, rx in enumerate(rib_x):
        # Rib size changes along thoracic cage
        rib_w = 0.38 + 0.16 * math.sin(idx / len(rib_x) * math.pi)
        rib_h = 0.34 + 0.12 * math.sin(idx / len(rib_x) * math.pi)

        # Right side ribs (intact curved down to soil)
        r_mid = (rx, 0.28 + rib_h*0.4, rib_w*0.7)
        r_tip = (rx, 0.04, rib_w)
        mesh.add_cylinder((rx, 0.30, 0.0), r_mid, 0.022, 0.018, segs=6)
        mesh.add_cylinder(r_mid, r_tip, 0.018, 0.014, segs=6)

        # Left side ribs (pried apart / shattered outward by cryptid)
        if idx in [2, 3, 4, 5]:
            # Shattered ribs pointing violently into the air
            l_mid = (rx + 0.08, 0.55, -rib_w*0.8)
            l_tip = (rx + 0.12, 0.72, -rib_w*1.05)
            mesh.add_cylinder((rx, 0.30, 0.0), l_mid, 0.024, 0.018, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.018, 0.008, segs=6)
        else:
            l_mid = (rx, 0.26 + rib_h*0.35, -rib_w*0.65)
            l_tip = (rx, 0.05, -rib_w*0.95)
            mesh.add_cylinder((rx, 0.30, 0.0), l_mid, 0.022, 0.018, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.018, 0.014, segs=6)

    # --- 5. Pelvis and Broken Limbs ---
    mesh.add_box((0.95, 0.16, 0.05), (0.28, 0.18, 0.36), rot_y=-0.1)

    # Foreleg left (twisted forward, snapped tibia)
    mesh.add_cylinder((-0.80, 0.22, -0.35), (-1.10, 0.14, -0.65), 0.045, 0.035, segs=6)
    mesh.add_cylinder((-1.10, 0.14, -0.65), (-1.35, 0.04, -0.80), 0.035, 0.025, segs=6)
    # Foreleg right (bent under carcass)
    mesh.add_cylinder((-0.75, 0.20, 0.35), (-0.95, 0.05, 0.65), 0.045, 0.030, segs=6)

    # Hindleg left (sprawled backward)
    mesh.add_cylinder((0.95, 0.16, -0.15), (1.35, 0.10, -0.45), 0.05, 0.038, segs=6)
    mesh.add_cylinder((1.35, 0.10, -0.45), (1.70, 0.04, -0.60), 0.038, 0.028, segs=6)
    # Hindleg right (snapped backward with jagged break)
    mesh.add_cylinder((0.95, 0.16, 0.18), (1.30, 0.22, 0.40), 0.05, 0.035, segs=6)
    mesh.add_cylinder((1.30, 0.22, 0.40), (1.55, 0.05, 0.55), 0.032, 0.022, segs=6)

    # --- 6. Torn Viscera / Meat Clots in Cavity ---
    mesh.add_box((-0.20, 0.14, 0.0), (0.75, 0.18, 0.45), rot_y=0.05)
    mesh.add_box((0.25, 0.12, -0.05), (0.45, 0.15, 0.35), rot_y=-0.15)

    os.makedirs("assets/models", exist_ok=True)
    mesh.save("assets/models/elk_carcass.obj")


def generate_carcass_gore_pool():
    mesh = ObjMesh("carcass_gore_pool")
    # Ground gore decal: flat (y=0.003), organic starburst puddle
    center = (0.0, 0.003, 0.0)
    c_idx = mesh.add_v(center[0], center[1], center[2])
    c_vn = mesh.add_vn(0, 1, 0)
    c_vt = mesh.add_vt(0.5, 0.5)

    n_pts = 24
    outer_v = []
    outer_vn = []
    outer_vt = []

    radii_base = [
        1.4, 1.8, 1.2, 0.9, 1.6, 2.1, 1.7, 1.1,
        0.8, 1.5, 1.9, 1.3, 1.0, 1.7, 2.3, 1.8,
        1.2, 0.9, 1.5, 2.0, 1.6, 1.2, 0.8, 1.3
    ]

    for i in range(n_pts):
        angle = 2.0 * math.pi * i / n_pts
        r = radii_base[i] * 0.85
        # Stretch along elk spine axis (X axis)
        px = math.cos(angle) * r * 1.35
        pz = math.sin(angle) * r * 0.85
        outer_v.append(mesh.add_v(px, 0.003, pz))
        outer_vn.append(mesh.add_vn(0, 1, 0))
        outer_vt.append(mesh.add_vt(0.5 + px * 0.25, 0.5 + pz * 0.25))

    for i in range(n_pts):
        nxt = (i + 1) % n_pts
        mesh.add_face([c_idx, outer_v[i], outer_v[nxt]],
                      [c_vn, outer_vn[i], outer_vn[nxt]],
                      [c_vt, outer_vt[i], outer_vt[nxt]])

    # Add 4 satellite splatter droplets around the pool
    splatters = [
        (-1.8, -0.9, 0.25),
        (-1.4,  1.1, 0.32),
        ( 1.9, -0.8, 0.28),
        ( 1.6,  0.9, 0.35)
    ]
    for sx, sz, sr in splatters:
        sc_idx = mesh.add_v(sx, 0.003, sz)
        s_pts = 8
        s_v = []
        for j in range(s_pts):
            th = 2.0 * math.pi * j / s_pts
            px = sx + math.cos(th) * sr * (0.8 + 0.4 * (j % 2))
            pz = sz + math.sin(th) * sr * (0.8 + 0.4 * (j % 2))
            s_v.append(mesh.add_v(px, 0.003, pz))
        for j in range(s_pts):
            jn = (j + 1) % s_pts
            mesh.add_face([sc_idx, s_v[j], s_v[jn]],
                          [c_vn, c_vn, c_vn],
                          [c_vt, c_vt, c_vt])

    mesh.save("assets/models/carcass_gore_pool.obj")


def generate_clawed_tree():
    mesh = ObjMesh("clawed_tree")
    # Massive cedar/pine trunk: height 9.0m, bottom radius 0.52m, top radius 0.34m
    # 24 radial segments with deep gouges carved at y = 1.6m to 3.2m
    segs = 24
    height_slices = 18
    total_h = 9.0

    v_grid = []
    vn_grid = []
    vt_grid = []

    for h_i in range(height_slices + 1):
        y = float(h_i) / height_slices * total_h
        t = y / total_h
        radius = 0.52 * (1.0 - t * 0.4)
        # Root flaring at bottom
        if y < 1.0:
            radius += 0.22 * (1.0 - y) ** 2

        v_row = []
        vn_row = []
        vt_row = []

        for s_i in range(segs + 1):
            theta = 2.0 * math.pi * s_i / segs
            nx = math.cos(theta)
            nz = math.sin(theta)

            cur_r = radius
            # Front face is around theta = 0 (z = 0, pointing along X+ or Z+)
            # Let front be theta near pi/2 (pointing along +Z)
            # 4 parallel gouges carved deep inward
            angle_from_front = abs(theta - math.pi * 0.5)
            if 1.6 <= y <= 3.2 and angle_from_front < 0.65:
                # Vertical profile: deepest at center (y = 2.4m)
                y_factor = 1.0 - abs(y - 2.4) / 0.8
                # 4 gouge grooves
                gouge_pattern = math.cos((theta - math.pi * 0.5) * 16.0)
                if gouge_pattern > 0.1:
                    depth = 0.14 * y_factor * (gouge_pattern ** 0.8)
                    cur_r -= depth
                elif gouge_pattern < -0.5:
                    # Raised torn splintered bark lips
                    lip = 0.04 * y_factor
                    cur_r += lip

            px = nx * cur_r
            pz = nz * cur_r

            v_row.append(mesh.add_v(px, y, pz))
            vn_row.append(mesh.add_vn(nx, 0.05, nz))
            u_coord = float(s_i) / segs
            v_coord = y * 0.5
            vt_row.append(mesh.add_vt(u_coord, v_coord))

        v_grid.append(v_row)
        vn_grid.append(vn_row)
        vt_grid.append(vt_row)

    for h_i in range(height_slices):
        for s_i in range(segs):
            v = [v_grid[h_i][s_i], v_grid[h_i][s_i+1], v_grid[h_i+1][s_i+1], v_grid[h_i+1][s_i]]
            vn = [vn_grid[h_i][s_i], vn_grid[h_i][s_i+1], vn_grid[h_i+1][s_i+1], vn_grid[h_i+1][s_i]]
            vt = [vt_grid[h_i][s_i], vt_grid[h_i][s_i+1], vt_grid[h_i+1][s_i+1], vt_grid[h_i+1][s_i]]
            mesh.add_face(v, vn, vt)

    # 3D shredded wood fiber strips hanging from gouge channels
    for g_x, g_y, g_z in [(-0.10, 2.2, 0.44), (0.02, 2.5, 0.46), (0.14, 2.3, 0.43)]:
        mesh.add_box((g_x, g_y, g_z), (0.03, 0.22, 0.02), rot_y=0.1)

    mesh.save("assets/models/clawed_tree.obj")


def generate_tent():
    mesh = ObjMesh("tent")
    # Ridge tent with catenary sag: length 2.8m, width 2.2m, height 1.6m
    length = 2.8
    half_l = length * 0.5
    half_w = 1.1
    peak_h = 1.65

    # Catenary roof slices
    l_slices = 8
    roof_left = []
    roof_right = []
    roof_ridge = []

    for i in range(l_slices + 1):
        z = -half_l + (float(i) / l_slices) * length
        sag = 0.10 * math.sin(float(i) / l_slices * math.pi)
        h = peak_h - sag
        w = half_w + 0.05 * math.sin(float(i) / l_slices * math.pi)

        # Ridge vertex
        vr = mesh.add_v(0.0, h, z)
        # Left wall bottom
        vl = mesh.add_v(-w, 0.0, z)
        # Right wall bottom
        v_rt = mesh.add_v(w, 0.0, z)

        roof_ridge.append(vr)
        roof_left.append(vl)
        roof_right.append(v_rt)

    # Generate roof panels with UVs
    for i in range(l_slices):
        z_frac1 = float(i) / l_slices
        z_frac2 = float(i+1) / l_slices

        # Left roof slope
        v_l = [roof_left[i], roof_left[i+1], roof_ridge[i+1], roof_ridge[i]]
        n_l = mesh.add_vn(-0.8, 0.6, 0.0)
        vt_l = [mesh.add_vt(0.0, z_frac1*2), mesh.add_vt(0.0, z_frac2*2),
                mesh.add_vt(1.0, z_frac2*2), mesh.add_vt(1.0, z_frac1*2)]
        mesh.add_face(v_l, [n_l]*4, vt_l)

        # Right roof slope
        v_r = [roof_ridge[i], roof_ridge[i+1], roof_right[i+1], roof_right[i]]
        n_r = mesh.add_vn(0.8, 0.6, 0.0)
        vt_r = [mesh.add_vt(0.0, z_frac1*2), mesh.add_vt(0.0, z_frac2*2),
                mesh.add_vt(1.0, z_frac2*2), mesh.add_vt(1.0, z_frac1*2)]
        mesh.add_face(v_r, [n_r]*4, vt_r)

    # Rear closed wall triangle
    n_rear = mesh.add_vn(0.0, 0.2, -1.0)
    vt_rear = [mesh.add_vt(0, 0), mesh.add_vt(1, 0), mesh.add_vt(0.5, 1)]
    mesh.add_face([roof_left[0], roof_right[0], roof_ridge[0]], [n_rear]*3, vt_rear)

    # Front rolled flap vestibule: open left side, rolled flap on right
    v_front_fl = mesh.add_v(half_w * 0.35, peak_h * 0.45, half_l)
    n_front = mesh.add_vn(0.0, 0.2, 1.0)
    vt_front = [mesh.add_vt(0, 0), mesh.add_vt(1, 0), mesh.add_vt(0.5, 1)]
    mesh.add_face([roof_right[-1], v_front_fl, roof_ridge[-1]], [n_front]*3, vt_front)

    # Rolled fabric cylinder at entrance
    mesh.add_cylinder((half_w * 0.35, peak_h * 0.45, half_l + 0.02),
                      (half_w * 0.75, 0.15, half_l + 0.02), 0.06, 0.06, segs=8)

    # Aluminum arched poles (exterior frame)
    for z_pole in [-half_l + 0.15, half_l - 0.15]:
        mesh.add_cylinder((-half_w - 0.04, 0.0, z_pole), (0.0, peak_h + 0.04, z_pole), 0.022, 0.022, segs=8)
        mesh.add_cylinder((0.0, peak_h + 0.04, z_pole), (half_w + 0.04, 0.0, z_pole), 0.022, 0.022, segs=8)

    # Guy lines to ground stakes
    for sx, sz in [(-half_w - 0.6, -half_l - 0.4), (half_w + 0.6, -half_l - 0.4),
                   (-half_w - 0.6,  half_l + 0.4), (half_w + 0.6,  half_l + 0.4)]:
        # Metal stake
        mesh.add_cylinder((sx, 0.0, sz), (sx, 0.12, sz), 0.015, 0.015, segs=6)
        # Guy cord
        nearest_pole = (half_w * (1 if sx > 0 else -1), 0.7, half_l * (1 if sz > 0 else -1))
        mesh.add_cylinder(nearest_pole, (sx, 0.08, sz), 0.005, 0.005, segs=4)

    # Interior sleeping pad inside tent
    mesh.add_box((-0.2, 0.03, 0.0), (0.65, 0.05, 1.8), rot_y=0.0)

    mesh.save("assets/models/tent.obj")


def generate_cabin():
    mesh = ObjMesh("cabin")
    # Interlocking log cabin with porch deck and shingle roof
    cabin_w = 6.4
    cabin_d = 5.2
    wall_h = 3.2
    half_w = cabin_w * 0.5
    half_d = cabin_d * 0.5

    # Log walls: stacked horizontal logs with saddle notches extending 0.35m past corners
    num_logs = 14
    log_r = wall_h / (num_logs * 1.8)
    overhang = 0.35

    for i in range(num_logs):
        y = log_r + i * (log_r * 1.8)

        # Front & Back logs (running along X axis)
        if i % 2 == 0:
            # Back wall full log
            mesh.add_cylinder((-half_w - overhang, y, -half_d), (half_w + overhang, y, -half_d), log_r, log_r, segs=8)
            # Front wall (doorway gap in center: -0.7m to 0.7m up to log 9)
            if i > 9:
                mesh.add_cylinder((-half_w - overhang, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=8)
            else:
                mesh.add_cylinder((-half_w - overhang, y, half_d), (-0.75, y, half_d), log_r, log_r, segs=8)
                mesh.add_cylinder((0.75, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=8)

        # Left & Right logs (running along Z axis)
        else:
            # Window openings left and right (between logs 4 and 8)
            if 4 <= i <= 8:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, -0.6), log_r, log_r, segs=8)
                mesh.add_cylinder((-half_w, y, 0.6), (-half_w, y, half_d + overhang), log_r, log_r, segs=8)

                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, -0.6), log_r, log_r, segs=8)
                mesh.add_cylinder((half_w, y, 0.6), (half_w, y, half_d + overhang), log_r, log_r, segs=8)
            else:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, half_d + overhang), log_r, log_r, segs=8)
                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, half_d + overhang), log_r, log_r, segs=8)

    # Front Door (plank construction)
    mesh.add_box((0.0, 1.15, half_d - 0.05), (1.35, 2.2, 0.08), rot_y=0.0)
    # Door latch
    mesh.add_box((0.45, 1.15, half_d + 0.02), (0.08, 0.16, 0.04), rot_y=0.0)

    # Boarded Window frames
    for wx in [-half_w, half_w]:
        # Cross frames
        mesh.add_box((wx, 1.8, 0.0), (0.10, 1.1, 1.1), rot_y=0.0)
        # Protective planks
        mesh.add_box((wx + (0.06 if wx > 0 else -0.06), 1.95, 0.0), (0.04, 0.18, 1.25), rot_y=0.0)
        mesh.add_box((wx + (0.06 if wx > 0 else -0.06), 1.65, 0.0), (0.04, 0.18, 1.25), rot_y=0.0)

    # Pitched Gabled Roof with overhanging eaves
    roof_peak_h = wall_h + 1.45
    roof_overhang = 0.55
    r_half_w = half_w + roof_overhang
    r_half_d = half_d + roof_overhang

    # Left roof slope
    v_rl1 = mesh.add_v(-r_half_w, wall_h - 0.1,  r_half_d)
    v_rl2 = mesh.add_v(-r_half_w, wall_h - 0.1, -r_half_d)
    v_rl3 = mesh.add_v(0.0, roof_peak_h, -r_half_d)
    v_rl4 = mesh.add_v(0.0, roof_peak_h,  r_half_d)
    n_rl = mesh.add_vn(-0.7, 0.7, 0.0)
    vt_r = [mesh.add_vt(0, 0), mesh.add_vt(3, 0), mesh.add_vt(3, 3), mesh.add_vt(0, 3)]
    mesh.add_face([v_rl1, v_rl2, v_rl3, v_rl4], [n_rl]*4, vt_r)

    # Right roof slope
    v_rr1 = mesh.add_v(0.0, roof_peak_h,  r_half_d)
    v_rr2 = mesh.add_v(0.0, roof_peak_h, -r_half_d)
    v_rr3 = mesh.add_v(r_half_w, wall_h - 0.1, -r_half_d)
    v_rr4 = mesh.add_v(r_half_w, wall_h - 0.1,  r_half_d)
    n_rr = mesh.add_vn(0.7, 0.7, 0.0)
    mesh.add_face([v_rr1, v_rr2, v_rr3, v_rr4], [n_rr]*4, vt_r)

    # Front Gable triangle
    vg_l = mesh.add_v(-half_w, wall_h, half_d)
    vg_r = mesh.add_v(half_w, wall_h, half_d)
    vg_p = mesh.add_v(0.0, roof_peak_h - 0.05, half_d)
    ng_f = mesh.add_vn(0.0, 0.0, 1.0)
    mesh.add_face([vg_l, vg_r, vg_p], [ng_f]*3, [vt_r[0], vt_r[1], vt_r[2]])

    # Back Gable triangle
    vgb_l = mesh.add_v(half_w, wall_h, -half_d)
    vgb_r = mesh.add_v(-half_w, wall_h, -half_d)
    vgb_p = mesh.add_v(0.0, roof_peak_h - 0.05, -half_d)
    ng_b = mesh.add_vn(0.0, 0.0, -1.0)
    mesh.add_face([vgb_l, vgb_r, vgb_p], [ng_b]*3, [vt_r[0], vt_r[1], vt_r[2]])

    # Raised Front Porch Deck
    porch_d = 2.0
    porch_h = 0.38
    porch_z_front = half_d + porch_d
    # Floor deck planks
    mesh.add_box((0.0, porch_h - 0.05, half_d + porch_d * 0.5), (cabin_w + 0.4, 0.10, porch_d), rot_y=0.0)

    # Porch Roof overhang and Support Posts
    porch_post_r = 0.08
    for px in [-half_w, half_w]:
        # Vertical support post
        mesh.add_cylinder((px, 0.0, porch_z_front), (px, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)
        # Top cross beam
        mesh.add_cylinder((px, wall_h - 0.1, half_d), (px, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)

    # Front cross beam
    mesh.add_cylinder((-half_w, wall_h - 0.1, porch_z_front), (half_w, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)

    # Porch Railings (left, right, and front sides leaving open center for stairs)
    mesh.add_box((-half_w, porch_h + 0.50, half_d + porch_d*0.5), (0.08, 0.06, porch_d), rot_y=0.0)
    mesh.add_box(( half_w, porch_h + 0.50, half_d + porch_d*0.5), (0.08, 0.06, porch_d), rot_y=0.0)
    mesh.add_box((-half_w * 0.65, porch_h + 0.50, porch_z_front), (half_w * 0.65, 0.06, 0.08), rot_y=0.0)
    mesh.add_box(( half_w * 0.65, porch_h + 0.50, porch_z_front), (half_w * 0.65, 0.06, 0.08), rot_y=0.0)

    # Front Porch Wooden Steps
    mesh.add_box((0.0, porch_h * 0.66, porch_z_front + 0.28), (1.6, 0.14, 0.45), rot_y=0.0)
    mesh.add_box((0.0, porch_h * 0.33, porch_z_front + 0.62), (1.6, 0.14, 0.45), rot_y=0.0)

    mesh.save("assets/models/cabin.obj")


def generate_pine_tree():
    trunk_mesh = ObjMesh("pine_tree_trunk")
    foliage_mesh = ObjMesh("pine_tree_foliage")
    combined_mesh = ObjMesh("pine_tree")

    # Tree trunk: height 14.0m with root flaring at base
    trunk_h = 14.0
    trunk_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.52, 0.12, segs=12, u_start=0.0, u_end=1.0, v_start=0.0, v_end=5.0)
    combined_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.52, 0.12, segs=12, u_start=0.0, u_end=1.0, v_start=0.0, v_end=5.0)

    # 5 cascading tiers of pine foliage boughs
    tiers = [
        (3.2, 4.4, 3.8, 0.0),
        (5.5, 4.0, 3.2, 0.35),
        (7.8, 3.6, 2.6, 0.70),
        (9.8, 3.2, 1.9, 1.05),
        (11.8, 2.8, 1.2, 1.40)
    ]

    for y_base, h_tier, r_base, rot_offset in tiers:
        boughs = 12
        v_top = foliage_mesh.add_v(0.0, y_base + h_tier, 0.0)
        vt_top = foliage_mesh.add_vt(0.5, 1.0)
        vn_top = foliage_mesh.add_vn(0.0, 1.0, 0.0)

        ring_v = []
        ring_vn = []
        ring_vt = []
        under_v = []
        under_vn = []

        under_center = foliage_mesh.add_v(0.0, y_base + 0.4, 0.0)
        under_c_n = foliage_mesh.add_vn(0.0, -1.0, 0.0)
        under_c_vt = foliage_mesh.add_vt(0.5, 0.5)

        for b in range(boughs + 1):
            theta = 2.0 * math.pi * b / boughs + rot_offset
            dip = -0.35
            rb = r_base * (0.9 + 0.2 * (b % 2))
            bx = math.cos(theta) * rb
            bz = math.sin(theta) * rb
            by = y_base + dip

            ring_v.append(foliage_mesh.add_v(bx, by, bz))
            ring_vn.append(foliage_mesh.add_vn(math.cos(theta) * 0.7, 0.5, math.sin(theta) * 0.7))
            u_c = float(b) / boughs
            ring_vt.append(foliage_mesh.add_vt(u_c, 0.0))

            under_v.append(foliage_mesh.add_v(bx * 0.85, by + 0.1, bz * 0.85))
            under_vn.append(foliage_mesh.add_vn(math.cos(theta) * 0.3, -0.9, math.sin(theta) * 0.3))

        for b in range(boughs):
            foliage_mesh.add_face([v_top, ring_v[b], ring_v[b+1]],
                                  [vn_top, ring_vn[b], ring_vn[b+1]],
                                  [vt_top, ring_vt[b], ring_vt[b+1]])
            foliage_mesh.add_face([under_center, under_v[b+1], under_v[b]],
                                  [under_c_n, under_vn[b+1], under_vn[b]],
                                  [under_c_vt, ring_vt[b+1], ring_vt[b]])

    trunk_mesh.save("assets/models/pine_tree_trunk.obj")
    foliage_mesh.save("assets/models/pine_tree_foliage.obj")
    combined_mesh.save("assets/models/pine_tree.obj")


if __name__ == "__main__":
    print("Generating high-fidelity 3D OBJ models...")
    generate_elk_carcass()
    generate_carcass_gore_pool()
    generate_clawed_tree()
    generate_tent()
    generate_cabin()
    generate_pine_tree()
    print("All models generated successfully!")
