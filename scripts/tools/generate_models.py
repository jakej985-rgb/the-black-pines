#!/usr/bin/env python3
"""
Procedural 3D Wavefront OBJ Generator for The Black Pines.
Generates high-fidelity organic models without primitive approximations:
- tent.obj: Detailed expedition tent with arched poles and open flap
- cabin.obj: Log cabin with notched corners, porch deck, steps, and roof
- clawed_tree.obj: Tree trunk with 3 gouged-in claw furrows and splinters
- pine_tree.obj: Multi-tiered organic drooping pine boughs
- elk_carcass.obj: Anatomical skeleton with antlers, skull, ribs, and spine
- rock_outcrop.obj: Tall stratified cliff rock
- rock_craggy.obj: Fractured angular mountain boulder
- rock_flat_slab.obj: Low flat slate stepping slab
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

    def add_cylinder(self, p1, p2, r1, r2, segs=8):
        v1 = p1
        v2 = p2
        axis = (v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2])
        length = math.sqrt(sum(a*a for a in axis))
        if length < 0.0001:
            return
        # Find orthogonal vectors
        if abs(axis[1]) < 0.99 * length:
            up = (0, 1, 0)
        else:
            up = (1, 0, 0)
        u = (axis[1]*up[2] - axis[2]*up[1], axis[2]*up[0] - axis[0]*up[2], axis[0]*up[1] - axis[1]*up[0])
        ul = math.sqrt(sum(a*a for a in u))
        u = tuple(a/ul for a in u)
        w = (axis[1]*u[2] - axis[2]*u[1], axis[2]*u[0] - axis[0]*u[2], axis[0]*u[1] - axis[1]*u[0])
        wl = math.sqrt(sum(a*a for a in w))
        w = tuple(a/wl for a in w)

        ring1 = []
        ring2 = []
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)
            pt1 = (v1[0] + r1*(cos_a*u[0] + sin_a*w[0]),
                   v1[1] + r1*(cos_a*u[1] + sin_a*w[1]),
                   v1[2] + r1*(cos_a*u[2] + sin_a*w[2]))
            pt2 = (v2[0] + r2*(cos_a*u[0] + sin_a*w[0]),
                   v2[1] + r2*(cos_a*u[1] + sin_a*w[1]),
                   v2[2] + r2*(cos_a*u[2] + sin_a*w[2]))
            ring1.append(self.add_v(*pt1))
            ring2.append(self.add_v(*pt2))

        for i in range(segs):
            ni = (i + 1) % segs
            self.add_face([ring1[i], ring2[i], ring2[ni], ring1[ni]])

    def save(self, filepath):
        with open(filepath, 'w') as f:
            f.write(f"# Wavefront OBJ exported by The Black Pines\n")
            f.write(f"o {self.name}\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
            for face in self.faces:
                v_list, vn_list, vt_list = face
                if vn_list and vt_list:
                    tokens = [f"{v}/{vt}/{vn}" for v, vt, vn in zip(v_list, vt_list, vn_list)]
                elif vn_list:
                    tokens = [f"{v}//{vn}" for v, vn in zip(v_list, vn_list)]
                elif vt_list:
                    tokens = [f"{v}/{vt}" for v, vt in zip(v_list, vt_list)]
                else:
                    tokens = [f"{v}" for v in v_list]
                f.write(f"f {' '.join(tokens)}\n")


def build_tent(out_path):
    mesh = ObjMesh("ExpeditionTent")
    # Tunnel/Dome ridge tent with catenary sag and open door flaps
    length = 2.8
    width = 2.2
    height = 1.45
    
    # 5 cross sections along length with sag
    nx = 6
    ny = 8
    grid = []
    for i in range(nx):
        z = -length/2.0 + length * i / (nx - 1)
        row = []
        # sag in middle
        sag = 0.88 if 0 < i < nx-1 else 1.0
        h_eff = height * sag
        w_eff = width * (0.95 if 0 < i < nx-1 else 1.0)
        for j in range(ny):
            t = float(j) / (ny - 1) # 0 to 1 across arch
            ang = math.pi * t
            x = -math.cos(ang) * (w_eff / 2.0)
            y = math.sin(ang) * h_eff
            # Flatten bottom slightly
            if y < 0.05: y = 0.0
            row.append(mesh.add_v(x, y, z))
        grid.append(row)

    for i in range(nx - 1):
        for j in range(ny - 1):
            v1 = grid[i][j]
            v2 = grid[i+1][j]
            v3 = grid[i+1][j+1]
            v4 = grid[i][j+1]
            # Leave front flap open by omitting partial front face
            if i == nx - 2 and (2 <= j <= 5):
                continue
            mesh.add_face([v1, v2, v3, v4])

    # End caps
    # Rear wall
    c_rear = mesh.add_v(0, height*0.4, -length/2.0)
    for j in range(ny - 1):
        mesh.add_face([grid[0][j], grid[0][j+1], c_rear])

    # Front open vestibule door flap (peeled back to side)
    flap_v = mesh.add_v(width*0.55, height*0.4, length*0.45)
    mesh.add_face([grid[-1][4], grid[-1][5], flap_v])

    # Aluminum curved poles along arches
    for arch_z in [-length*0.42, 0.0, length*0.42]:
        p_prev = None
        for k in range(10):
            t = float(k) / 9.0
            ang = math.pi * t
            px = -math.cos(ang) * (width * 0.52)
            py = math.sin(ang) * (height * 1.02)
            pt = (px, max(0.0, py), arch_z)
            if p_prev:
                mesh.add_cylinder(p_prev, pt, 0.02, 0.02, segs=6)
            p_prev = pt

    # Rolled sleeping bag inside
    mesh.add_cylinder((0.3, 0.12, -0.6), (0.3, 0.12, 0.6), 0.2, 0.2, segs=8)
    mesh.save(out_path)


def build_cabin(out_path):
    mesh = ObjMesh("LogRangerStation")
    w = 6.0   # width (X)
    d = 4.8   # depth (Z)
    h_wall = 3.2
    
    # Modeled horizontal log walls with notched corners
    num_logs = 12
    log_r = (h_wall / num_logs) * 0.5
    for i in range(num_logs):
        y = log_r + i * (log_r * 2.0)
        # Front wall logs (with door and window gaps)
        if y > 2.4 or y < 0.4:
            mesh.add_cylinder((-w/2 - 0.35, y, d/2), (w/2 + 0.35, y, d/2), log_r, log_r, segs=8)
        else:
            # logs beside door
            mesh.add_cylinder((-w/2 - 0.35, y, d/2), (-0.7, y, d/2), log_r, log_r, segs=6)
            mesh.add_cylinder((1.2, y, d/2), (w/2 + 0.35, y, d/2), log_r, log_r, segs=6)
        # Back wall logs
        mesh.add_cylinder((-w/2 - 0.35, y, -d/2), (w/2 + 0.35, y, -d/2), log_r, log_r, segs=8)
        # Side wall logs (offset by half height for interlocking look)
        mesh.add_cylinder((-w/2, y + log_r*0.5, -d/2 - 0.35), (-w/2, y + log_r*0.5, d/2 + 0.35), log_r, log_r, segs=8)
        mesh.add_cylinder((w/2, y + log_r*0.5, -d/2 - 0.35), (w/2, y + log_r*0.5, d/2 + 0.35), log_r, log_r, segs=8)

    # Gabled roof with corrugated metal overhanging eaves
    roof_h = 1.6
    overhang_side = 0.5
    overhang_front = 1.8  # Covers porch
    overhang_back = 0.6
    
    # Roof panels
    r_ridge_front = mesh.add_v(0, h_wall + roof_h, d/2 + overhang_front)
    r_ridge_back  = mesh.add_v(0, h_wall + roof_h, -d/2 - overhang_back)
    r_left_front  = mesh.add_v(-w/2 - overhang_side, h_wall - 0.1, d/2 + overhang_front)
    r_left_back   = mesh.add_v(-w/2 - overhang_side, h_wall - 0.1, -d/2 - overhang_back)
    r_right_front = mesh.add_v(w/2 + overhang_side, h_wall - 0.1, d/2 + overhang_front)
    r_right_back  = mesh.add_v(w/2 + overhang_side, h_wall - 0.1, -d/2 - overhang_back)
    
    mesh.add_face([r_left_front, r_ridge_front, r_ridge_back, r_left_back])
    mesh.add_face([r_ridge_front, r_right_front, r_right_back, r_ridge_back])

    # Front timber gable
    g_top = mesh.add_v(0, h_wall + roof_h, d/2)
    g_left = mesh.add_v(-w/2, h_wall, d/2)
    g_right = mesh.add_v(w/2, h_wall, d/2)
    mesh.add_face([g_left, g_top, g_right])

    # Porch Deck & Steps
    pw = 5.6
    pd = 1.6
    p_h = 0.35
    # Porch platform
    p1 = mesh.add_v(-pw/2, p_h, d/2)
    p2 = mesh.add_v(pw/2, p_h, d/2)
    p3 = mesh.add_v(pw/2, p_h, d/2 + pd)
    p4 = mesh.add_v(-pw/2, p_h, d/2 + pd)
    mesh.add_face([p1, p2, p3, p4])
    # Porch step
    s1 = mesh.add_v(-1.2, p_h * 0.5, d/2 + pd)
    s2 = mesh.add_v(1.2, p_h * 0.5, d/2 + pd)
    s3 = mesh.add_v(1.2, p_h * 0.5, d/2 + pd + 0.45)
    s4 = mesh.add_v(-1.2, p_h * 0.5, d/2 + pd + 0.45)
    mesh.add_face([s1, s2, s3, s4])

    # Porch posts supporting roof
    mesh.add_cylinder((-pw/2 + 0.3, p_h, d/2 + pd - 0.2), (-pw/2 + 0.3, h_wall, d/2 + pd - 0.2), 0.12, 0.11, segs=8)
    mesh.add_cylinder((pw/2 - 0.3, p_h, d/2 + pd - 0.2), (pw/2 - 0.3, h_wall, d/2 + pd - 0.2), 0.12, 0.11, segs=8)

    # Front Door frame & boarded window
    d1 = mesh.add_v(-0.6, p_h, d/2 + 0.02)
    d2 = mesh.add_v(0.6, p_h, d/2 + 0.02)
    d3 = mesh.add_v(0.6, p_h + 2.1, d/2 + 0.02)
    d4 = mesh.add_v(-0.6, p_h + 2.1, d/2 + 0.02)
    mesh.add_face([d1, d2, d3, d4])

    mesh.save(out_path)


def build_clawed_tree(out_path):
    mesh = ObjMesh("ClawedTreeTrunk")
    h = 9.0
    r_base = 0.55
    r_top = 0.25
    segs = 20
    rings = 18
    
    # Create trunk grid with 3 deep recessed claw gouges carved inward
    grid = []
    for ring in range(rings):
        y = h * ring / (rings - 1)
        t_y = float(ring) / (rings - 1)
        r = r_base + (r_top - r_base) * t_y
        row = []
        for s in range(segs):
            ang = 2.0 * math.pi * s / segs
            # Claw gouge area: front face between 30 deg and 60 deg, height 2.6 to 4.2m
            r_eff = r
            if 2.4 <= y <= 4.4 and (0.2 * math.pi <= ang <= 0.6 * math.pi):
                # 3 claw furrows
                furrow = math.sin((ang - 0.2 * math.pi) / (0.4 * math.pi) * 3.0 * math.pi)
                if furrow < 0.0:
                    depth = (-furrow) * 0.16 * math.sin((y - 2.4) / 2.0 * math.pi)
                    r_eff -= depth
                else:
                    # shredded splinter ridges on edge
                    ridge = furrow * 0.04 * math.sin((y - 2.4) / 2.0 * math.pi)
                    r_eff += ridge

            px = math.cos(ang) * r_eff
            pz = math.sin(ang) * r_eff
            row.append(mesh.add_v(px, y, pz))
        grid.append(row)

    for r in range(rings - 1):
        for s in range(segs):
            ns = (s + 1) % segs
            mesh.add_face([grid[r][s], grid[r+1][s], grid[r+1][ns], grid[r][ns]])

    # Add jagged splinter flaps on the claw marks
    for s_y in [2.8, 3.3, 3.8]:
        sp1 = mesh.add_v(0.12, s_y, 0.46)
        sp2 = mesh.add_v(0.16, s_y + 0.12, 0.52)
        sp3 = mesh.add_v(0.14, s_y - 0.08, 0.48)
        mesh.add_face([sp1, sp2, sp3])

    mesh.save(out_path)


def build_pine_tree(out_path):
    mesh = ObjMesh("RealisticPineTree")
    h = 10.0
    # Trunk
    mesh.add_cylinder((0, 0, 0), (0, h*0.9, 0), 0.45, 0.14, segs=10)
    
    # 6 tiered asymmetrical drooping boughs
    tiers = [
        (3.8, 3.2, 1.2),
        (5.0, 2.7, 1.1),
        (6.1, 2.2, 1.0),
        (7.2, 1.7, 0.9),
        (8.2, 1.2, 0.8),
        (9.1, 0.7, 0.7),
    ]
    for idx, (tier_y, tier_r, tier_h) in enumerate(tiers):
        segs = 10
        # Peak of cone
        apex = mesh.add_v(0, tier_y + tier_h, 0)
        # Drooping outer perimeter
        outer = []
        inner_bottom = mesh.add_v(0, tier_y + 0.1, 0)
        rot_offset = (idx * 0.35)
        for s in range(segs):
            ang = 2.0 * math.pi * s / segs + rot_offset
            # alternate branch radius for jagged bough silhouette
            r_var = tier_r * (1.15 if s % 2 == 0 else 0.85)
            # Droop downward
            droop_y = tier_y - 0.25 * math.cos(ang * 2.0)
            px = math.cos(ang) * r_var
            pz = math.sin(ang) * r_var
            outer.append(mesh.add_v(px, droop_y, pz))

        # Upper canopy faces
        for s in range(segs):
            ns = (s + 1) % segs
            mesh.add_face([apex, outer[s], outer[ns]])
            # Underside faceted bough (recessed up into apex, NO flat square!)
            mesh.add_face([inner_bottom, outer[ns], outer[s]])

    mesh.save(out_path)


def build_elk_carcass(out_path):
    mesh = ObjMesh("ElkCarcass")
    # Horizontal carcass
    # Spine column
    spine_pts = [
        (-1.2, 0.22, 0.2),
        (-0.8, 0.25, 0.1),
        (-0.4, 0.28, 0.0),
        (0.0, 0.32, -0.05),
        (0.4, 0.28, -0.15),
        (0.8, 0.22, -0.25),
        (1.1, 0.18, -0.35)
    ]
    for i in range(len(spine_pts)-1):
        mesh.add_cylinder(spine_pts[i], spine_pts[i+1], 0.07, 0.06, segs=6)

    # Curved Ribs pried apart
    for idx, pt in enumerate(spine_pts[1:5]):
        x, y, z = pt
        rib_span = 0.55 - idx * 0.04
        # Left rib
        mesh.add_cylinder((x, y, z), (x + 0.1, y + 0.25, z + rib_span), 0.025, 0.018, segs=6)
        mesh.add_cylinder((x + 0.1, y + 0.25, z + rib_span), (x + 0.05, 0.08, z + rib_span * 0.9), 0.018, 0.015, segs=6)
        # Right rib
        mesh.add_cylinder((x, y, z), (x + 0.1, y + 0.25, z - rib_span), 0.025, 0.018, segs=6)
        mesh.add_cylinder((x + 0.1, y + 0.25, z - rib_span), (x + 0.05, 0.08, z - rib_span * 0.9), 0.018, 0.015, segs=6)

    # Skull
    sk_pt = spine_pts[-1]
    snout_pt = (sk_pt[0] + 0.45, 0.12, sk_pt[2] - 0.15)
    mesh.add_cylinder(sk_pt, snout_pt, 0.15, 0.07, segs=8)
    
    # Antlers (left and right sweeping beams)
    # Left beam
    ant_l1 = (sk_pt[0] - 0.05, 0.35, sk_pt[2] + 0.15)
    ant_l2 = (sk_pt[0] - 0.25, 0.65, sk_pt[2] + 0.45)
    ant_l3 = (sk_pt[0] - 0.45, 0.9, sk_pt[2] + 0.65)
    mesh.add_cylinder(sk_pt, ant_l1, 0.04, 0.035, segs=6)
    mesh.add_cylinder(ant_l1, ant_l2, 0.035, 0.028, segs=6)
    mesh.add_cylinder(ant_l2, ant_l3, 0.028, 0.018, segs=6)
    # Left tines
    mesh.add_cylinder(ant_l1, (ant_l1[0] + 0.2, ant_l1[1] + 0.2, ant_l1[2] + 0.1), 0.02, 0.01, segs=5)
    mesh.add_cylinder(ant_l2, (ant_l2[0] + 0.15, ant_l2[1] + 0.25, ant_l2[2] + 0.1), 0.018, 0.008, segs=5)

    # Right beam
    ant_r1 = (sk_pt[0] - 0.05, 0.35, sk_pt[2] - 0.15)
    ant_r2 = (sk_pt[0] - 0.25, 0.65, sk_pt[2] - 0.45)
    ant_r3 = (sk_pt[0] - 0.45, 0.9, sk_pt[2] - 0.65)
    mesh.add_cylinder(sk_pt, ant_r1, 0.04, 0.035, segs=6)
    mesh.add_cylinder(ant_r1, ant_r2, 0.035, 0.028, segs=6)
    mesh.add_cylinder(ant_r2, ant_r3, 0.028, 0.018, segs=6)
    # Right tines
    mesh.add_cylinder(ant_r1, (ant_r1[0] + 0.2, ant_r1[1] + 0.2, ant_r1[2] - 0.1), 0.02, 0.01, segs=5)
    mesh.add_cylinder(ant_r2, (ant_r2[0] + 0.15, ant_r2[1] + 0.25, ant_r2[2] - 0.1), 0.018, 0.008, segs=5)

    # Fractured Limb bones
    mesh.add_cylinder((-1.1, 0.2, 0.25), (-1.5, 0.08, 0.6), 0.05, 0.035, segs=6)
    mesh.add_cylinder((-1.0, 0.18, 0.15), (-1.3, 0.08, -0.4), 0.05, 0.035, segs=6)
    mesh.add_cylinder((0.3, 0.2, -0.2), (0.7, 0.08, -0.65), 0.045, 0.03, segs=6)

    mesh.save(out_path)


def build_rock_outcrop(out_path):
    mesh = ObjMesh("RockCliffOutcrop")
    h = 3.6
    w = 2.8
    d = 1.8
    # Stratified tall rock ledge with fractured cliffs
    v = []
    # 4 vertical layers with stepped overhangs
    for lyr in range(5):
        y = h * lyr / 4.0
        w_l = w * (1.0 - lyr * 0.12)
        d_l = d * (1.0 - lyr * 0.15)
        # 8 boundary points with jagged displacement
        ring = []
        for p in range(8):
            ang = 2.0 * math.pi * p / 8.0
            r_scale = 1.0 + 0.25 * math.sin(p * 2.5 + lyr * 1.8)
            px = math.cos(ang) * (w_l / 2.0) * r_scale
            pz = math.sin(ang) * (d_l / 2.0) * r_scale
            ring.append(mesh.add_v(px, y, pz))
        v.append(ring)

    for lyr in range(4):
        for p in range(8):
            np = (p + 1) % 8
            mesh.add_face([v[lyr][p], v[lyr+1][p], v[lyr+1][np], v[lyr][np]])

    # Top cap
    c_top = mesh.add_v(0, h * 1.02, 0)
    for p in range(8):
        np = (p + 1) % 8
        mesh.add_face([c_top, v[4][p], v[4][np]])

    mesh.save(out_path)


def build_rock_craggy(out_path):
    mesh = ObjMesh("RockCraggyBoulder")
    # Low, wide, cleaved angular boulder
    w = 2.4
    h = 1.2
    d = 1.9
    segs = 10
    v_bot = []
    v_mid = []
    v_top = []
    for s in range(segs):
        ang = 2.0 * math.pi * s / segs
        # angular noise
        r_var = 1.0 + 0.3 * math.sin(s * 3.0)
        bx = math.cos(ang) * (w * 0.5) * r_var
        bz = math.sin(ang) * (d * 0.5) * r_var
        v_bot.append(mesh.add_v(bx, 0.05, bz))
        
        mx = math.cos(ang) * (w * 0.45) * r_var
        mz = math.sin(ang) * (d * 0.45) * r_var
        v_mid.append(mesh.add_v(mx, h * 0.55 + 0.15 * math.cos(s*2.0), mz))

        tx = math.cos(ang) * (w * 0.25) * r_var
        tz = math.sin(ang) * (d * 0.25) * r_var
        v_top.append(mesh.add_v(tx, h * 0.95, tz))

    for s in range(segs):
        ns = (s + 1) % segs
        mesh.add_face([v_bot[s], v_mid[s], v_mid[ns], v_bot[ns]])
        mesh.add_face([v_mid[s], v_top[s], v_top[ns], v_mid[ns]])

    # flat fractured top
    c_top = mesh.add_v(0, h, 0)
    for s in range(segs):
        ns = (s + 1) % segs
        mesh.add_face([c_top, v_top[s], v_top[ns]])

    mesh.save(out_path)


def build_rock_flat_slab(out_path):
    mesh = ObjMesh("RockFlatSlateSlab")
    # Thin, flat, mossy slab embedded low in mud
    w = 2.2
    h = 0.28
    d = 1.6
    segs = 12
    v_b = []
    v_t = []
    for s in range(segs):
        ang = 2.0 * math.pi * s / segs
        r_var = 1.0 + 0.18 * math.sin(s * 2.0)
        px = math.cos(ang) * (w * 0.5) * r_var
        pz = math.sin(ang) * (d * 0.5) * r_var
        v_b.append(mesh.add_v(px, 0.02, pz))
        v_t.append(mesh.add_v(px * 0.92, h, pz * 0.92))

    for s in range(segs):
        ns = (s + 1) % segs
        mesh.add_face([v_b[s], v_t[s], v_t[ns], v_b[ns]])

    c_top = mesh.add_v(0, h + 0.02, 0)
    for s in range(segs):
        ns = (s + 1) % segs
        mesh.add_face([c_top, v_t[s], v_t[ns]])

    mesh.save(out_path)


def main():
    target_dir = os.path.abspath("assets/models")
    os.makedirs(target_dir, exist_ok=True)
    print("Generating custom 3D OBJ meshes...")
    
    build_tent(os.path.join(target_dir, "tent.obj"))
    print(" -> tent.obj generated")

    build_cabin(os.path.join(target_dir, "cabin.obj"))
    print(" -> cabin.obj generated")

    build_clawed_tree(os.path.join(target_dir, "clawed_tree.obj"))
    print(" -> clawed_tree.obj generated")

    build_pine_tree(os.path.join(target_dir, "pine_tree.obj"))
    print(" -> pine_tree.obj generated")

    build_elk_carcass(os.path.join(target_dir, "elk_carcass.obj"))
    print(" -> elk_carcass.obj generated")

    build_rock_outcrop(os.path.join(target_dir, "rock_outcrop.obj"))
    print(" -> rock_outcrop.obj generated")

    build_rock_craggy(os.path.join(target_dir, "rock_craggy.obj"))
    print(" -> rock_craggy.obj generated")

    build_rock_flat_slab(os.path.join(target_dir, "rock_flat_slab.obj"))
    print(" -> rock_flat_slab.obj generated")

    print("All 8 3D models generated successfully!")

if __name__ == "__main__":
    main()
