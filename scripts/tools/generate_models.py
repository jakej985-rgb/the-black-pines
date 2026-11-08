#!/usr/bin/env python3
"""
High-Realism 3D Wavefront OBJ Generator for The Black Pines.
Generates organic, detailed models with proper UV mapping and smooth normals:
- Sasquatch: Photorealistic cryptid anatomy, modular articulated limb hierarchy,
  dorsal hump, deep-set skull with sagittal crest, snarling fangs, 5-digit clawed hands,
  muscular bowed legs, plantigrade feet, and layered shaggy fur cards.
- elk_carcass.obj: Anatomical mutilated cervid skeleton with skull, branching antlers,
  shattered compound rib fractures, exposed marrow, and clinging visceral sinew.
- carcass_gore_pool.obj: Multi-tiered organic coagulated gore splatter pool.
- clawed_tree.obj: Thick pine trunk with 4 deep carved claw gouges, shredded fibers,
  peeled bark curls, and oozing amber resin drips.
- tent.obj: Expedition ridge tent with catenary sag, arched poles, stakes, guy cords,
  rolled flap, and interior sleeping roll.
- cabin.obj: Interlocking notched log cabin with stone piers, porch deck, railings,
  steps, cedar shake roof, cast-iron stovepipe, and rustic wall lantern.
- camp_cooler.obj, camp_firepit.obj, camp_lantern.obj: Storytelling camp props.
- Pine tree archetypes (Douglas fir, tall pine, snag, sapling).
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
        self.current_material = None

    def usemtl(self, mat_name):
        self.current_material = mat_name

    def add_v(self, x, y, z):
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices)

    def add_vn(self, nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz)
        if l > 0.00001:
            nx /= l
            ny /= l
            nz /= l
        else:
            nx, ny, nz = 0.0, 1.0, 0.0
        self.normals.append((float(nx), float(ny), float(nz)))
        return len(self.normals)

    def add_vt(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_face(self, v_list, vn_list=None, vt_list=None):
        self.faces.append((v_list, vn_list, vt_list, self.current_material))

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

    def add_ellipsoid(self, center, radii, segs_u=12, segs_v=8, rot_y=0.0, u_start=0.0, u_end=1.0, v_start=0.0, v_end=1.0):
        cx, cy, cz = center
        rx, ry, rz = radii
        cos_r = math.cos(rot_y)
        sin_r = math.sin(rot_y)

        rings = []
        for v_i in range(segs_v + 1):
            phi = math.pi * v_i / segs_v - math.pi * 0.5
            cos_p = math.cos(phi)
            sin_p = math.sin(phi)
            ring_v = []
            ring_vn = []
            ring_vt = []
            v_coord = v_start + (float(v_i) / segs_v) * (v_end - v_start)
            for u_i in range(segs_u + 1):
                theta = 2.0 * math.pi * u_i / segs_u
                cos_t = math.cos(theta)
                sin_t = math.sin(theta)

                nx = cos_p * cos_t
                ny = sin_p
                nz = cos_p * sin_t

                px = nx * rx
                py = ny * ry
                pz = nz * rz

                r_px = px * cos_r - pz * sin_r
                r_pz = px * sin_r + pz * cos_r
                r_nx = nx * cos_r - nz * sin_r
                r_nz = nx * sin_r + nz * cos_r

                ring_v.append(self.add_v(cx + r_px, cy + py, cz + r_pz))
                ring_vn.append(self.add_vn(r_nx, ny, r_nz))
                u_coord = u_start + (float(u_i) / segs_u) * (u_end - u_start)
                ring_vt.append(self.add_vt(u_coord, v_coord))
            rings.append((ring_v, ring_vn, ring_vt))

        for v_i in range(segs_v):
            r1_v, r1_vn, r1_vt = rings[v_i]
            r2_v, r2_vn, r2_vt = rings[v_i + 1]
            for u_i in range(segs_u):
                v = [r1_v[u_i], r1_v[u_i+1], r2_v[u_i+1], r2_v[u_i]]
                vn = [r1_vn[u_i], r1_vn[u_i+1], r2_vn[u_i+1], r2_vn[u_i]]
                vt = [r1_vt[u_i], r1_vt[u_i+1], r2_vt[u_i+1], r2_vt[u_i]]
                self.add_face(v, vn, vt)

    def add_tapered_tube(self, pts_radii, segs=10, u_scale=1.0, v_scale=1.0):
        if len(pts_radii) < 2:
            return

        rings = []
        u_prev = None

        for idx, (p, r_tuple) in enumerate(pts_radii):
            if isinstance(r_tuple, (float, int)):
                rx = ry = float(r_tuple)
            else:
                rx, ry = float(r_tuple[0]), float(r_tuple[1])

            if idx == 0:
                p_next = pts_radii[1][0]
                tangent = (p_next[0] - p[0], p_next[1] - p[1], p_next[2] - p[2])
            elif idx == len(pts_radii) - 1:
                p_prev = pts_radii[-2][0]
                tangent = (p[0] - p_prev[0], p[1] - p_prev[1], p[2] - p_prev[2])
            else:
                p_prev = pts_radii[idx-1][0]
                p_next = pts_radii[idx+1][0]
                tangent = (p_next[0] - p_prev[0], p_next[1] - p_prev[1], p_next[2] - p_prev[2])

            tl = math.sqrt(sum(t*t for t in tangent))
            if tl < 0.0001:
                tangent = (0, 1, 0)
            else:
                tangent = tuple(t/tl for t in tangent)

            if u_prev is None:
                if abs(tangent[1]) < 0.95:
                    ref_up = (0, 1, 0)
                else:
                    ref_up = (1, 0, 0)
                u_vec = (tangent[1]*ref_up[2] - tangent[2]*ref_up[1],
                         tangent[2]*ref_up[0] - tangent[0]*ref_up[2],
                         tangent[0]*ref_up[1] - tangent[1]*ref_up[0])
                ul = math.sqrt(sum(a*a for a in u_vec))
                u_vec = tuple(a/ul for a in u_vec)
            else:
                dot = sum(u_prev[i] * tangent[i] for i in range(3))
                u_vec = tuple(u_prev[i] - dot * tangent[i] for i in range(3))
                ul = math.sqrt(sum(a*a for a in u_vec))
                if ul < 0.0001:
                    u_vec = (1, 0, 0)
                else:
                    u_vec = tuple(a/ul for a in u_vec)

            v_vec = (tangent[1]*u_vec[2] - tangent[2]*u_vec[1],
                     tangent[2]*u_vec[0] - tangent[0]*u_vec[2],
                     tangent[0]*u_vec[1] - tangent[1]*u_vec[0])
            vl = math.sqrt(sum(a*a for a in v_vec))
            v_vec = tuple(a/vl for a in v_vec)
            u_prev = u_vec

            ring_v = []
            ring_vn = []
            ring_vt = []
            v_coord = float(idx) / (len(pts_radii) - 1) * v_scale

            for s in range(segs + 1):
                theta = 2.0 * math.pi * s / segs
                cos_t = math.cos(theta)
                sin_t = math.sin(theta)

                nx = u_vec[0] * cos_t + v_vec[0] * sin_t
                ny = u_vec[1] * cos_t + v_vec[1] * sin_t
                nz = u_vec[2] * cos_t + v_vec[2] * sin_t

                px = p[0] + u_vec[0] * cos_t * rx + v_vec[0] * sin_t * ry
                py = p[1] + u_vec[1] * cos_t * rx + v_vec[1] * sin_t * ry
                pz = p[2] + u_vec[2] * cos_t * rx + v_vec[2] * sin_t * ry

                ring_v.append(self.add_v(px, py, pz))
                ring_vn.append(self.add_vn(nx, ny, nz))
                ring_vt.append(self.add_vt(float(s)/segs * u_scale, v_coord))

            rings.append((ring_v, ring_vn, ring_vt))

        for idx in range(len(pts_radii) - 1):
            r1_v, r1_vn, r1_vt = rings[idx]
            r2_v, r2_vn, r2_vt = rings[idx + 1]
            for s in range(segs):
                v = [r1_v[s], r1_v[s+1], r2_v[s+1], r2_v[s]]
                vn = [r1_vn[s], r1_vn[s+1], r2_vn[s+1], r2_vn[s]]
                vt = [r1_vt[s], r1_vt[s+1], r2_vt[s+1], r2_vt[s]]
                self.add_face(v, vn, vt)

    def add_claw(self, base_p, mid_p, tip_p, base_r=0.035, mid_r=0.022, segs=8):
        pts = [(base_p, base_r), (mid_p, mid_r), (tip_p, 0.003)]
        self.add_tapered_tube(pts, segs=segs, u_scale=1.0, v_scale=1.0)

    def save(self, filepath, mat_order=None):
        with open(filepath, "w") as f:
            f.write(f"# Wavefront OBJ: {self.name}\n")
            f.write(f"o {self.name}\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
            
            # Group faces by material to guarantee stable surface indices
            if mat_order:
                faces_by_mat = []
                for m in mat_order:
                    faces_by_mat.extend([face for face in self.faces if face[3] == m])
                faces_by_mat.extend([face for face in self.faces if face[3] not in mat_order])
                faces_to_write = faces_by_mat
            elif any(face[3] is not None for face in self.faces):
                seen_mats = []
                for face in self.faces:
                    if face[3] not in seen_mats:
                        seen_mats.append(face[3])
                faces_to_write = []
                for m in seen_mats:
                    faces_to_write.extend([face for face in self.faces if face[3] == m])
            else:
                faces_to_write = self.faces

            current_mat = None
            for face in faces_to_write:
                verts, norms, uvs, mat = face
                if mat != current_mat:
                    current_mat = mat
                    if current_mat:
                        f.write(f"usemtl {current_mat}\n")
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


# ==============================================================================
# 1. SASQUATCH CRYPTID CREATURE PIPELINE (Issue #6)
# ==============================================================================

def generate_sasquatch_models():
    """
    Generates high-fidelity anatomical models for the Sasquatch cryptid:
    Modular limb segments for articulated animation rig + complete single-mesh.
    """
    os.makedirs("assets/models", exist_ok=True)

    # --------------------------------------------------------------------------
    # 1.1 Torso: Deep chest, hunched spine, muscular traps, lats, and dorsal hump
    # Center relative to Torso node (y = 0 is mid-torso, around y=1.65 in world)
    # --------------------------------------------------------------------------
    torso = ObjMesh("sasquatch_torso")
    torso.usemtl("Fur")
    
    # Thoracic spine and ribcage spine sweep
    torso_spine = [
        ((0.0, -0.45,  0.02), (0.42, 0.38)),  # Pelvis / Lower abdomen
        ((0.0, -0.20,  0.05), (0.50, 0.44)),  # Mid waist
        ((0.0,  0.10,  0.10), (0.64, 0.54)),  # Lower chest & lats
        ((0.0,  0.35,  0.14), (0.68, 0.56)),  # Broad pectoral chest
        ((0.0,  0.55,  0.18), (0.62, 0.52)),  # Shoulder girdle / upper back
        ((0.0,  0.72,  0.10), (0.42, 0.38))   # Cervical base
    ]
    torso.add_tapered_tube(torso_spine, segs=16, u_scale=2.0, v_scale=2.0)

    # Muscular Dorsal Hump (characteristic cryptid silhouette behind neck)
    torso.add_ellipsoid((0.0, 0.52, 0.32), (0.46, 0.28, 0.32), segs_u=12, segs_v=8)
    
    # Pectoral muscle slabs (left and right)
    torso.add_ellipsoid((-0.24, 0.28, -0.32), (0.24, 0.18, 0.16), segs_u=10, segs_v=6)
    torso.add_ellipsoid(( 0.24, 0.28, -0.32), (0.24, 0.18, 0.16), segs_u=10, segs_v=6)

    # Flared Trapezius muscles
    torso.add_ellipsoid((-0.34, 0.54, 0.08), (0.22, 0.20, 0.26), segs_u=10, segs_v=6)
    torso.add_ellipsoid(( 0.34, 0.54, 0.08), (0.22, 0.20, 0.26), segs_u=10, segs_v=6)

    torso.save("assets/models/sasquatch_torso.obj")

    # --------------------------------------------------------------------------
    # 1.2 Head: Sagittal crest, heavy brow, recessed orbits, snarling canine fangs
    # --------------------------------------------------------------------------
    head = ObjMesh("sasquatch_head")
    head.usemtl("Fur")

    # Braincase / Cranium with sloping forehead
    head.add_ellipsoid((0.0, 0.05, 0.02), (0.30, 0.28, 0.34), segs_u=14, segs_v=10)
    
    # Sagittal crest (raised bony ridge along top of skull)
    crest_pts = [
        ((0.0,  0.18, -0.10), (0.04, 0.08)),
        ((0.0,  0.28,  0.02), (0.05, 0.12)),
        ((0.0,  0.26,  0.16), (0.04, 0.10)),
        ((0.0,  0.12,  0.25), (0.03, 0.06))
    ]
    head.add_tapered_tube(crest_pts, segs=8)

    # Heavy ape-man supraorbital brow ridge projecting forward over eyes
    brow_pts = [
        ((-0.26, 0.08, -0.22), 0.05),
        ((-0.13, 0.11, -0.28), 0.07),
        (( 0.00, 0.12, -0.30), 0.08),
        (( 0.13, 0.11, -0.28), 0.07),
        (( 0.26, 0.08, -0.22), 0.05)
    ]
    head.add_tapered_tube(brow_pts, segs=8)

    # Pronounced ape muzzle / snout extending forward
    muzzle_pts = [
        ((0.0,  0.02, -0.15), (0.24, 0.20)),
        ((0.0, -0.06, -0.32), (0.20, 0.18)),
        ((0.0, -0.12, -0.42), (0.16, 0.14))
    ]
    head.add_tapered_tube(muzzle_pts, segs=10)

    # Flared nostrils
    head.add_ellipsoid((-0.07, -0.05, -0.42), (0.045, 0.035, 0.05), segs_u=8, segs_v=6)
    head.add_ellipsoid(( 0.07, -0.05, -0.42), (0.045, 0.035, 0.05), segs_u=8, segs_v=6)

    # Deep recessed eye orbits (cavities for the eye glow spheres at +/-0.12, 0.04, -0.28)
    head.add_ellipsoid((-0.13, 0.04, -0.28), (0.07, 0.06, 0.06), segs_u=8, segs_v=6)
    head.add_ellipsoid(( 0.13, 0.04, -0.28), (0.07, 0.06, 0.06), segs_u=8, segs_v=6)

    # Lower Jaw / Mandible pulled into an aggressive snarl
    jaw_pts = [
        ((0.0, -0.14, -0.12), (0.22, 0.12)),
        ((0.0, -0.20, -0.28), (0.18, 0.10)),
        ((0.0, -0.22, -0.38), (0.14, 0.08))
    ]
    head.add_tapered_tube(jaw_pts, segs=10)

    # Snarling Carnivorous Fangs & Teeth
    head.usemtl("Bone")
    # Upper canines (protruding downward from muzzle)
    head.add_claw((-0.11, -0.10, -0.38), (-0.11, -0.17, -0.39), (-0.10, -0.22, -0.39), base_r=0.022, mid_r=0.015, segs=6)
    head.add_claw(( 0.11, -0.10, -0.38), ( 0.11, -0.17, -0.39), ( 0.10, -0.22, -0.39), base_r=0.022, mid_r=0.015, segs=6)
    # Lower canines (protruding upward from mandible)
    head.add_claw((-0.09, -0.19, -0.36), (-0.09, -0.14, -0.37), (-0.08, -0.10, -0.37), base_r=0.018, mid_r=0.012, segs=6)
    head.add_claw(( 0.09, -0.19, -0.36), ( 0.09, -0.14, -0.37), ( 0.08, -0.10, -0.37), base_r=0.018, mid_r=0.012, segs=6)

    # Incisors / Row of sharp front teeth
    for tx in [-0.06, -0.02, 0.02, 0.06]:
        head.add_cylinder((tx, -0.11, -0.39), (tx, -0.14, -0.39), 0.010, 0.007, segs=4)
        head.add_cylinder((tx, -0.19, -0.37), (tx, -0.16, -0.37), 0.009, 0.006, segs=4)

    head.save("assets/models/sasquatch_head.obj")

    # --------------------------------------------------------------------------
    # 1.3 Upper Arm: Deltoid cap, bicep/tricep body (extends from shoulder down)
    # --------------------------------------------------------------------------
    arm_upper = ObjMesh("sasquatch_arm_upper")
    arm_upper.usemtl("Fur")
    # Rounded deltoid cap
    arm_upper.add_ellipsoid((0.0, 0.0, 0.0), (0.24, 0.22, 0.22), segs_u=12, segs_v=8)
    # Bicep / Tricep arm cylinder tapering to elbow at y = -0.60
    arm_pts = [
        ((0.0,  0.00, 0.00), 0.21),
        ((0.0, -0.20, 0.00), 0.22),  # Peak of bicep
        ((0.0, -0.42, 0.01), 0.18),
        ((0.0, -0.60, 0.01), 0.16)   # Elbow joint
    ]
    arm_upper.add_tapered_tube(arm_pts, segs=12)
    arm_upper.save("assets/models/sasquatch_arm_upper.obj")

    # --------------------------------------------------------------------------
    # 1.4 Lower Arm / Forearm: Corded brachioradialis, wrist joint (y = 0 to -0.58)
    # --------------------------------------------------------------------------
    arm_lower = ObjMesh("sasquatch_arm_lower")
    arm_lower.usemtl("Fur")
    # Elbow joint ball
    arm_lower.add_ellipsoid((0.0, 0.0, 0.0), (0.17, 0.15, 0.16), segs_u=10, segs_v=6)
    # Forearm muscular sweep
    forearm_pts = [
        ((0.0,  0.00, 0.00), 0.17),
        ((0.0, -0.18, 0.02), 0.18),  # Muscular belly of forearm
        ((0.0, -0.38, 0.01), 0.15),
        ((0.0, -0.56, 0.00), 0.13)   # Heavy wrist
    ]
    arm_lower.add_tapered_tube(forearm_pts, segs=12)
    arm_lower.save("assets/models/sasquatch_arm_lower.obj")

    # --------------------------------------------------------------------------
    # 1.5 Hand: Broad ape palm, 5 digits with long curved predator claw talons
    # --------------------------------------------------------------------------
    hand = ObjMesh("sasquatch_hand")
    hand.usemtl("Fur")
    # Thick ape palm
    hand.add_box((0.0, -0.10, 0.0), (0.24, 0.18, 0.12), rot_y=0.0)

    # 5 Digits with sharp predatory claw talons
    # Fingers layout: Thumb at angle, index, middle, ring, pinky
    finger_configs = [
        (-0.11, -0.06,  0.04, 0.35,  -0.12, 0.04),   # Opposable Thumb
        (-0.08, -0.19, -0.02, 0.05,  -0.16, 0.06),   # Index
        (-0.02, -0.20, -0.02, 0.00,  -0.18, 0.06),   # Middle (longest)
        ( 0.04, -0.19, -0.02, -0.05, -0.16, 0.06),   # Ring
        ( 0.09, -0.17, -0.01, -0.10, -0.14, 0.05)    # Pinky
    ]
    for fx, fy, fz, ang_x, f_len, c_len in finger_configs:
        # Finger proximal segment (fur/leather)
        hand.usemtl("Fur")
        p_base = (fx, fy, fz)
        p_mid = (fx + math.sin(ang_x)*0.03, fy + f_len * 0.55, fz + 0.02)
        p_knuckle = (fx + math.sin(ang_x)*0.05, fy + f_len, fz + 0.04)
        hand.add_cylinder(p_base, p_knuckle, 0.026, 0.020, segs=6)

        # Curved Keratin Talon Claw Tip
        hand.usemtl("Claw")
        p_tip = (p_knuckle[0] + math.sin(ang_x)*0.03, p_knuckle[1] + c_len * 0.75, p_knuckle[2] + c_len)
        hand.add_claw(p_knuckle, (p_knuckle[0], p_knuckle[1] - 0.02, p_knuckle[2] + c_len*0.6), p_tip, base_r=0.018, mid_r=0.011, segs=6)

    hand.save("assets/models/sasquatch_hand.obj")

    # --------------------------------------------------------------------------
    # 1.6 Upper Leg / Thigh: Bowed muscular quadriceps and knee (y = 0 to -0.62)
    # --------------------------------------------------------------------------
    leg_upper = ObjMesh("sasquatch_leg_upper")
    leg_upper.usemtl("Fur")
    # Hip joint socket
    leg_upper.add_ellipsoid((0.0, 0.0, 0.0), (0.25, 0.22, 0.24), segs_u=10, segs_v=6)
    # Bowed thigh sweep
    thigh_pts = [
        ((0.0,  0.00, 0.00), 0.24),
        ((0.02, -0.22, 0.02), 0.25),  # Bulging quadricep
        ((0.01, -0.44, 0.01), 0.21),
        ((0.00, -0.62, 0.00), 0.18)   # Heavy knee
    ]
    leg_upper.add_tapered_tube(thigh_pts, segs=12)
    leg_upper.save("assets/models/sasquatch_leg_upper.obj")

    # --------------------------------------------------------------------------
    # 1.7 Lower Leg / Shin & Calf: Bulging gastrocnemius, thick shin (y = 0 to -0.55)
    # --------------------------------------------------------------------------
    leg_lower = ObjMesh("sasquatch_leg_lower")
    leg_lower.usemtl("Fur")
    # Knee joint
    leg_lower.add_ellipsoid((0.0, 0.0, 0.0), (0.19, 0.16, 0.18), segs_u=10, segs_v=6)
    # Bulging calf and tapering shin
    shin_pts = [
        ((0.0,  0.00, 0.00), 0.18),
        ((0.0, -0.16, 0.04), 0.22),  # Heavy calf muscle belly (posterior)
        ((0.0, -0.36, 0.02), 0.17),
        ((0.0, -0.52, 0.00), 0.15)   # Ankle joint
    ]
    leg_lower.add_tapered_tube(shin_pts, segs=12)
    leg_lower.save("assets/models/sasquatch_leg_lower.obj")

    # --------------------------------------------------------------------------
    # 1.8 Foot: Broad 5-toed plantigrade cryptid foot with clawed toes and heel pad
    # --------------------------------------------------------------------------
    foot = ObjMesh("sasquatch_foot")
    foot.usemtl("Fur")
    # Broad heel and midfoot pad resting flat on ground
    foot.add_box((0.0, 0.06, 0.02), (0.24, 0.12, 0.38), rot_y=0.0)

    # 5 Splayed plantigrade toes with heavy claw tips
    toe_xs = [-0.09, -0.05, 0.0, 0.05, 0.09]
    toe_lens = [0.14, 0.16, 0.17, 0.15, 0.12]
    for tx, tl in zip(toe_xs, toe_lens):
        foot.usemtl("Fur")
        # Toe base
        p_t_base = (tx, 0.05, -0.16)
        p_t_mid = (tx * 1.1, 0.04, -0.16 - tl * 0.7)
        foot.add_cylinder(p_t_base, p_t_mid, 0.024, 0.018, segs=6)

        # Toe claw tip digging into the earth
        foot.usemtl("Claw")
        p_claw_tip = (tx * 1.15, 0.01, -0.16 - tl - 0.04)
        foot.add_claw(p_t_mid, (p_t_mid[0], 0.03, p_t_mid[2] - 0.02), p_claw_tip, base_r=0.016, mid_r=0.010, segs=6)

    foot.save("assets/models/sasquatch_foot.obj")

    # --------------------------------------------------------------------------
    # 1.9 Shaggy Fur Silhouette Fringe Cards (shoulders, dorsal hump, forearms)
    # Double-sided textured cards for realistic silhouette breakup
    # --------------------------------------------------------------------------
    fur_cards = ObjMesh("sasquatch_fur_cards")
    fur_cards.usemtl("Fur")
    
    # Shoulder mantle fringe tufts
    mantle_positions = [
        ((-0.45, 0.55,  0.15), (-0.72, 0.35,  0.18)),
        (( 0.45, 0.55,  0.15), ( 0.72, 0.35,  0.18)),
        ((-0.38, 0.45,  0.28), (-0.60, 0.25,  0.32)),
        (( 0.38, 0.45,  0.28), ( 0.60, 0.25,  0.32)),
        (( 0.00, 0.68,  0.35), ( 0.00, 0.42,  0.52)),  # Nape/crest spine fringe
        (( 0.00, 0.45,  0.42), ( 0.00, 0.22,  0.55)),  # Mid-back fringe
        ((-0.18, 0.58,  0.38), (-0.28, 0.36,  0.50)),
        (( 0.18, 0.58,  0.38), ( 0.28, 0.36,  0.50))
    ]
    for p1, p2 in mantle_positions:
        # Generate triangular fur tuft
        fur_cards.add_cylinder(p1, p2, 0.14, 0.02, segs=4)

    fur_cards.save("assets/models/sasquatch_fur_cards.obj")

    # --------------------------------------------------------------------------
    # 1.10 Assembled Unified Sasquatch Model (for reference / distant LOD)
    # --------------------------------------------------------------------------
    full = ObjMesh("sasquatch_full")
    full.usemtl("Fur")
    # Full torso
    full.add_tapered_tube([((p[0], p[1] + 1.65, p[2]), r) for p, r in torso_spine], segs=16)
    full.add_ellipsoid((0.0, 2.17, 0.32), (0.46, 0.28, 0.32), segs_u=12, segs_v=8)
    full.add_ellipsoid((-0.24, 1.93, -0.32), (0.24, 0.18, 0.16), segs_u=10, segs_v=6)
    full.add_ellipsoid(( 0.24, 1.93, -0.32), (0.24, 0.18, 0.16), segs_u=10, segs_v=6)
    # Head at y = 2.45
    full.add_ellipsoid((0.0, 2.50, -0.10), (0.30, 0.28, 0.34), segs_u=14, segs_v=10)
    full.add_tapered_tube([((p[0], p[1] + 2.45, p[2] - 0.12), r) for p, r in crest_pts], segs=8)
    full.add_tapered_tube([((p[0], p[1] + 2.45, p[2] - 0.12), r) for p, r in muzzle_pts], segs=10)
    # Limbs
    for side in [-1.0, 1.0]:
        # Arm: Shoulder -> Elbow -> Wrist
        p_sh = (side * 0.68, 2.05, 0.05)
        p_elb = (side * 0.82, 1.45, 0.08)
        p_wr = (side * 0.86, 0.88, 0.10)
        p_hnd = (side * 0.88, 0.68, 0.12)
        full.add_ellipsoid(p_sh, (0.24, 0.22, 0.22), segs_u=10, segs_v=6)
        full.add_cylinder(p_sh, p_elb, 0.22, 0.16, segs=10)
        full.add_cylinder(p_elb, p_wr, 0.17, 0.13, segs=10)
        full.add_box(p_hnd, (0.22, 0.16, 0.10), rot_y=0.0)

        # Leg: Hip -> Knee -> Ankle -> Foot
        p_hip = (side * 0.36, 1.25, 0.02)
        p_knee = (side * 0.38, 0.65, 0.04)
        p_ank = (side * 0.38, 0.14, 0.00)
        p_ft = (side * 0.38, 0.05, -0.10)
        full.add_ellipsoid(p_hip, (0.25, 0.22, 0.24), segs_u=10, segs_v=6)
        full.add_cylinder(p_hip, p_knee, 0.24, 0.18, segs=10)
        full.add_cylinder(p_knee, p_ank, 0.18, 0.15, segs=10)
        full.add_box(p_ft, (0.24, 0.10, 0.38), rot_y=0.0)

    full.save("assets/models/sasquatch_full.obj")


# ==============================================================================
# 2. PROPS & LANDMARKS OVERHAUL (Issue #7 & Issue #4)
# ==============================================================================

def generate_cabin():
    """
    Upgraded Ranger Station Cabin with multi-material surfaces:
    - Wood: Interlocking notched cedar logs, plank door, porch deck, posts, railing, steps
    - Roof: Weathered cedar shake shingles with overhanging eaves and moss
    - Metal: Cast-iron stovepipe chimney with rain cap, forged door hinges and latch
    - Stone: Fieldstone foundation piers grounding the cabin to the terrain
    - Glass: Boarded windows with interior glass reflections
    """
    mesh = ObjMesh("cabin")
    cabin_w = 6.4
    cabin_d = 5.2
    wall_h = 3.2
    half_w = cabin_w * 0.5
    half_d = cabin_d * 0.5

    # --- 2.1 Fieldstone Foundation Piers (grounding cabin into undulating terrain) ---
    mesh.usemtl("Stone")
    pier_locs = [
        (-half_w, -half_d), (0.0, -half_d), (half_w, -half_d),
        (-half_w,  half_d), (0.0,  half_d), (half_w,  half_d),
        (-half_w,  half_d + 1.8), (half_w,  half_d + 1.8)
    ]
    for px, pz in pier_locs:
        # Masonry stone pier extending -0.4m into soil to prevent floating
        mesh.add_box((px, -0.20, pz), (0.55, 0.45, 0.55), rot_y=0.05)

    # --- 2.2 Interlocking Cedar Log Walls ---
    mesh.usemtl("Wood")
    num_logs = 14
    log_r = wall_h / (num_logs * 1.8)
    overhang = 0.38

    for i in range(num_logs):
        y = log_r + i * (log_r * 1.8)

        # Front & Back walls (running along X axis)
        if i % 2 == 0:
            # Back wall full log
            mesh.add_cylinder((-half_w - overhang, y, -half_d), (half_w + overhang, y, -half_d), log_r, log_r, segs=8)
            # Front wall with door opening in center (-0.75m to 0.75m)
            if i > 9:
                mesh.add_cylinder((-half_w - overhang, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=8)
            else:
                mesh.add_cylinder((-half_w - overhang, y, half_d), (-0.75, y, half_d), log_r, log_r, segs=8)
                mesh.add_cylinder((0.75, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=8)

        # Left & Right walls (running along Z axis)
        else:
            # Window openings left and right (logs 4 to 8)
            if 4 <= i <= 8:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, -0.65), log_r, log_r, segs=8)
                mesh.add_cylinder((-half_w, y, 0.65), (-half_w, y, half_d + overhang), log_r, log_r, segs=8)

                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, -0.65), log_r, log_r, segs=8)
                mesh.add_cylinder((half_w, y, 0.65), (half_w, y, half_d + overhang), log_r, log_r, segs=8)
            else:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, half_d + overhang), log_r, log_r, segs=8)
                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, half_d + overhang), log_r, log_r, segs=8)

    # Front Door (heavy weathered vertical planks)
    mesh.add_box((0.0, 1.15, half_d - 0.05), (1.35, 2.2, 0.08), rot_y=0.0)

    # Forged Iron Door Strap Hinges and Latch
    mesh.usemtl("Metal")
    mesh.add_box((-0.55, 1.85, half_d + 0.02), (0.45, 0.08, 0.02), rot_y=0.0)
    mesh.add_box((-0.55, 0.45, half_d + 0.02), (0.45, 0.08, 0.02), rot_y=0.0)
    mesh.add_box(( 0.48, 1.15, half_d + 0.03), (0.10, 0.18, 0.04), rot_y=0.0)

    # Windows: Boarded wood planks + interior glass pane
    for wx in [-half_w, half_w]:
        mesh.usemtl("Glass")
        mesh.add_box((wx, 1.8, 0.0), (0.02, 1.0, 1.0), rot_y=0.0)
        
        mesh.usemtl("Wood")
        # Sill and casing
        mesh.add_box((wx + (0.06 if wx > 0 else -0.06), 1.25, 0.0), (0.12, 0.08, 1.25), rot_y=0.0)
        # Weathered protective barricade planks
        mesh.add_box((wx + (0.06 if wx > 0 else -0.06), 1.95, 0.0), (0.04, 0.18, 1.25), rot_y=0.0)
        mesh.add_box((wx + (0.06 if wx > 0 else -0.06), 1.65, 0.0), (0.04, 0.18, 1.25), rot_y=0.0)

    # --- 2.3 Pitched Cedar Shake Shingle Roof ---
    roof_peak_h = wall_h + 1.55
    roof_overhang = 0.60
    r_half_w = half_w + roof_overhang
    r_half_d = half_d + roof_overhang

    mesh.usemtl("Roof")
    # Left roof slope
    v_rl1 = mesh.add_v(-r_half_w, wall_h - 0.1,  r_half_d)
    v_rl2 = mesh.add_v(-r_half_w, wall_h - 0.1, -r_half_d)
    v_rl3 = mesh.add_v(0.0, roof_peak_h, -r_half_d)
    v_rl4 = mesh.add_v(0.0, roof_peak_h,  r_half_d)
    n_rl = mesh.add_vn(-0.7, 0.7, 0.0)
    vt_r = [mesh.add_vt(0, 0), mesh.add_vt(4, 0), mesh.add_vt(4, 4), mesh.add_vt(0, 4)]
    mesh.add_face([v_rl1, v_rl2, v_rl3, v_rl4], [n_rl]*4, vt_r)

    # Right roof slope
    v_rr1 = mesh.add_v(0.0, roof_peak_h,  r_half_d)
    v_rr2 = mesh.add_v(0.0, roof_peak_h, -r_half_d)
    v_rr3 = mesh.add_v(r_half_w, wall_h - 0.1, -r_half_d)
    v_rr4 = mesh.add_v(r_half_w, wall_h - 0.1,  r_half_d)
    n_rr = mesh.add_vn(0.7, 0.7, 0.0)
    mesh.add_face([v_rr1, v_rr2, v_rr3, v_rr4], [n_rr]*4, vt_r)

    # Roof ridge cap beam
    mesh.usemtl("Wood")
    mesh.add_cylinder((0.0, roof_peak_h + 0.05, -r_half_d), (0.0, roof_peak_h + 0.05, r_half_d), 0.10, 0.10, segs=8)

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

    # --- 2.4 Cast-Iron Woodstove Stovepipe Chimney ---
    mesh.usemtl("Metal")
    chim_base = (-1.8, roof_peak_h - 0.5, -0.6)
    chim_top = (-1.8, roof_peak_h + 1.1, -0.6)
    mesh.add_cylinder(chim_base, chim_top, 0.12, 0.12, segs=10)
    # Chimney rain cap
    mesh.add_cylinder(chim_top, (chim_top[0], chim_top[1] + 0.12, chim_top[2]), 0.22, 0.08, segs=8)

    # --- 2.5 Raised Front Porch Deck, Railings, and Steps ---
    mesh.usemtl("Wood")
    porch_d = 2.0
    porch_h = 0.38
    porch_z_front = half_d + porch_d
    # Floor deck planks
    mesh.add_box((0.0, porch_h - 0.05, half_d + porch_d * 0.5), (cabin_w + 0.4, 0.10, porch_d), rot_y=0.0)

    # Porch Roof overhang and Support Posts
    porch_post_r = 0.09
    for px in [-half_w, half_w]:
        # Vertical post
        mesh.add_cylinder((px, 0.0, porch_z_front), (px, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)
        # Top header beam
        mesh.add_cylinder((px, wall_h - 0.1, half_d), (px, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)

    mesh.add_cylinder((-half_w, wall_h - 0.1, porch_z_front), (half_w, wall_h - 0.1, porch_z_front), porch_post_r, porch_post_r, segs=8)

    # Porch Railings and balusters
    mesh.add_box((-half_w, porch_h + 0.50, half_d + porch_d*0.5), (0.08, 0.06, porch_d), rot_y=0.0)
    mesh.add_box(( half_w, porch_h + 0.50, half_d + porch_d*0.5), (0.08, 0.06, porch_d), rot_y=0.0)
    mesh.add_box((-half_w * 0.65, porch_h + 0.50, porch_z_front), (half_w * 0.65, 0.06, 0.08), rot_y=0.0)
    mesh.add_box(( half_w * 0.65, porch_h + 0.50, porch_z_front), (half_w * 0.65, 0.06, 0.08), rot_y=0.0)

    # Front Wooden Steps
    mesh.add_box((0.0, porch_h * 0.66, porch_z_front + 0.28), (1.6, 0.14, 0.48), rot_y=0.0)
    mesh.add_box((0.0, porch_h * 0.33, porch_z_front + 0.65), (1.6, 0.14, 0.48), rot_y=0.0)

    # Wall Lantern Housing enclosing PorchLight at (0, 3.0, 3.4)
    mesh.usemtl("Metal")
    mesh.add_cylinder((0.0, 2.7, half_d + 0.05), (0.0, 2.9, half_d + 0.35), 0.03, 0.03, segs=6)
    mesh.add_box((0.0, 3.0, half_d + 0.35), (0.22, 0.32, 0.22), rot_y=0.0)

    mesh.save("assets/models/cabin.obj", mat_order=["Wood", "Roof", "Metal", "Stone", "Glass"])


def generate_tent():
    """
    Overhauled expedition tent with catenary sag, wrinkles, guy ropes,
    aluminum poles, ground pegs, and rolled vestibule entrance.
    """
    mesh = ObjMesh("tent")
    length = 2.8
    half_l = length * 0.5
    half_w = 1.15
    peak_h = 1.68

    mesh.usemtl("Canvas")
    # Catenary roof slices with cloth sag
    l_slices = 10
    roof_left = []
    roof_right = []
    roof_ridge = []

    for i in range(l_slices + 1):
        z = -half_l + (float(i) / l_slices) * length
        sag = 0.12 * math.sin(float(i) / l_slices * math.pi)
        h = peak_h - sag
        w = half_w + 0.06 * math.sin(float(i) / l_slices * math.pi)

        vr = mesh.add_v(0.0, h, z)
        vl = mesh.add_v(-w, 0.0, z)
        v_rt = mesh.add_v(w, 0.0, z)

        roof_ridge.append(vr)
        roof_left.append(vl)
        roof_right.append(v_rt)

    for i in range(l_slices):
        z1 = float(i) / l_slices
        z2 = float(i+1) / l_slices

        # Left slope
        v_l = [roof_left[i], roof_left[i+1], roof_ridge[i+1], roof_ridge[i]]
        n_l = mesh.add_vn(-0.8, 0.6, 0.0)
        vt_l = [mesh.add_vt(0.0, z1*2), mesh.add_vt(0.0, z2*2), mesh.add_vt(1.0, z2*2), mesh.add_vt(1.0, z1*2)]
        mesh.add_face(v_l, [n_l]*4, vt_l)

        # Right slope
        v_r = [roof_ridge[i], roof_ridge[i+1], roof_right[i+1], roof_right[i]]
        n_r = mesh.add_vn(0.8, 0.6, 0.0)
        vt_r = [mesh.add_vt(0.0, z1*2), mesh.add_vt(0.0, z2*2), mesh.add_vt(1.0, z2*2), mesh.add_vt(1.0, z1*2)]
        mesh.add_face(v_r, [n_r]*4, vt_r)

    # Rear closed wall triangle
    n_rear = mesh.add_vn(0.0, 0.2, -1.0)
    vt_rear = [mesh.add_vt(0, 0), mesh.add_vt(1, 0), mesh.add_vt(0.5, 1)]
    mesh.add_face([roof_left[0], roof_right[0], roof_ridge[0]], [n_rear]*3, vt_rear)

    # Front rolled flap vestibule: open left entrance, rolled flap on right
    v_front_fl = mesh.add_v(half_w * 0.35, peak_h * 0.45, half_l)
    n_front = mesh.add_vn(0.0, 0.2, 1.0)
    vt_front = [mesh.add_vt(0, 0), mesh.add_vt(1, 0), mesh.add_vt(0.5, 1)]
    mesh.add_face([roof_right[-1], v_front_fl, roof_ridge[-1]], [n_front]*3, vt_front)

    # Rolled fabric cylinder at entrance
    mesh.add_cylinder((half_w * 0.35, peak_h * 0.45, half_l + 0.02),
                      (half_w * 0.78, 0.12, half_l + 0.02), 0.065, 0.065, segs=8)

    # Interior foam sleeping roll & sleeping bag
    mesh.add_box((-0.2, 0.04, 0.0), (0.70, 0.06, 1.9), rot_y=0.0)
    mesh.add_cylinder((-0.2, 0.08, -0.6), (-0.2, 0.08, 0.5), 0.22, 0.18, segs=8)

    # Aluminum Arched Poles & Guy Lines
    mesh.usemtl("Metal")
    for z_pole in [-half_l + 0.15, half_l - 0.15]:
        mesh.add_cylinder((-half_w - 0.04, 0.0, z_pole), (0.0, peak_h + 0.04, z_pole), 0.022, 0.022, segs=8)
        mesh.add_cylinder((0.0, peak_h + 0.04, z_pole), (half_w + 0.04, 0.0, z_pole), 0.022, 0.022, segs=8)

    # Pegs & Guy cords
    for sx, sz in [(-half_w - 0.7, -half_l - 0.4), (half_w + 0.7, -half_l - 0.4),
                   (-half_w - 0.7,  half_l + 0.4), (half_w + 0.7,  half_l + 0.4)]:
        mesh.add_cylinder((sx, 0.0, sz), (sx, 0.14, sz), 0.015, 0.015, segs=6)
        nearest_pole = (half_w * (1 if sx > 0 else -1), 0.75, half_l * (1 if sz > 0 else -1))
        mesh.add_cylinder(nearest_pole, (sx, 0.10, sz), 0.005, 0.005, segs=4)

    mesh.save("assets/models/tent.obj", mat_order=["Canvas", "Metal"])


def generate_camp_props():
    """
    Generates realistic campsite props:
    - camp_firepit.obj: Irregular river stone ring with ash and split charred firewood logs with embers
    - camp_cooler.obj: Scratched expedition cooler with claw puncture dents
    - camp_lantern.obj: Weathered kerosene lantern
    """
    # 1. Firepit: Organic stones + charred firewood + glowing embers
    pit = ObjMesh("camp_firepit")
    n_stones = 10
    pit_radius = 0.65
    
    # Natural weathered river rocks around perimeter
    pit.usemtl("Stone")
    for i in range(n_stones):
        theta = 2.0 * math.pi * i / n_stones
        r = pit_radius * (0.9 + 0.2 * (i % 3))
        sx = math.cos(theta) * r
        sz = math.sin(theta) * r
        pit.add_ellipsoid((sx, 0.09, sz), (0.16, 0.12, 0.16), segs_u=8, segs_v=6, rot_y=theta)

    # Fine ash & charcoal floor bed
    pit.usemtl("Wood")
    pit.add_cylinder((0.0, 0.005, 0.0), (0.0, 0.04, 0.0), 0.52, 0.52, segs=12)

    # Crossed charred logs
    pit.add_cylinder((-0.35, 0.08, -0.20), (0.35, 0.14, 0.20), 0.07, 0.06, segs=8)
    pit.add_cylinder((-0.20, 0.12, 0.30), (0.20, 0.09, -0.30), 0.065, 0.055, segs=8)
    pit.add_cylinder((-0.05, 0.16, -0.25), (0.05, 0.15, 0.25), 0.06, 0.05, segs=8)

    # Embers core
    pit.usemtl("Embers")
    pit.add_ellipsoid((0.0, 0.06, 0.0), (0.28, 0.05, 0.28), segs_u=8, segs_v=6)
    pit.save("assets/models/camp_firepit.obj", mat_order=["Stone", "Wood", "Embers"])

    # 2. Expedition Cooler: With torn latches and claw puncture holes
    cooler = ObjMesh("camp_cooler")
    cooler.usemtl("Cooler")
    # Base body (overturned askew)
    cooler.add_box((0.0, 0.22, 0.0), (0.72, 0.44, 0.42), rot_y=0.15)
    # Hinged lid
    cooler.add_box((0.02, 0.44, -0.05), (0.74, 0.08, 0.44), rot_y=0.35)
    # Latch hardware
    cooler.usemtl("Metal")
    cooler.add_box((-0.20, 0.38, 0.22), (0.06, 0.10, 0.03), rot_y=0.15)
    cooler.add_box(( 0.20, 0.38, 0.22), (0.06, 0.10, 0.03), rot_y=0.15)
    cooler.save("assets/models/camp_cooler.obj", mat_order=["Cooler", "Metal"])

    # 3. Weathered Kerosene Lantern
    lantern = ObjMesh("camp_lantern")
    lantern.usemtl("Metal")
    # Base reservoir
    lantern.add_cylinder((0.0, 0.0, 0.0), (0.0, 0.08, 0.0), 0.10, 0.09, segs=8)
    # Chimney hood
    lantern.add_cylinder((0.0, 0.26, 0.0), (0.0, 0.34, 0.0), 0.07, 0.05, segs=8)
    # Top carry loop handle
    lantern.add_cylinder((-0.08, 0.32, 0.0), (0.08, 0.42, 0.0), 0.01, 0.01, segs=6)
    # Glass globe
    lantern.usemtl("Glass")
    lantern.add_cylinder((0.0, 0.08, 0.0), (0.0, 0.26, 0.0), 0.08, 0.07, segs=8)
    lantern.save("assets/models/camp_lantern.obj", mat_order=["Metal", "Glass"])


def generate_elk_carcass():
    """
    Overhauled Anatomical Mutilated Cervid Carcass:
    - 16-segment curved spinal column with dorsal processes
    - Cervid skull with branching multi-tine antlers and velvet strips
    - Shattered thoracic ribcage with fractured ribs pried open outward
    - Fractured long bones with hollow marrow cavities
    - Clinging visceral muscle sinew and torn viscera
    """
    mesh = ObjMesh("elk_carcass")
    mesh.usemtl("Bone")
    
    # 1. Cervid Skull & Mandible
    # Cranium (braincase)
    mesh.add_box((-1.35, 0.22, 0.1), (0.32, 0.24, 0.28), rot_y=0.2)
    # Nasal bridge and muzzle
    mesh.add_cylinder((-1.35, 0.22, 0.1), (-1.82, 0.11, 0.18), 0.14, 0.06, segs=8)
    # Lower mandible laying askew in the gore
    mesh.add_cylinder((-1.32, 0.09, 0.14), (-1.76, 0.04, 0.22), 0.08, 0.03, segs=6)

    # 2. Curved 3D Branched Antlers with Velvet Peeling
    def add_antler(side=1.0):
        p_base = (-1.38, 0.32, 0.1 + side * 0.14)
        p1 = (-1.42, 0.54, 0.1 + side * 0.36)
        p2 = (-1.35, 0.82, 0.1 + side * 0.58)
        p3 = (-1.16, 1.02, 0.1 + side * 0.62)
        p4 = (-0.92, 1.12, 0.1 + side * 0.54)
        mesh.add_cylinder(p_base, p1, 0.046, 0.038, segs=8)
        mesh.add_cylinder(p1, p2, 0.038, 0.030, segs=8)
        mesh.add_cylinder(p2, p3, 0.030, 0.022, segs=6)
        mesh.add_cylinder(p3, p4, 0.022, 0.012, segs=6)

        # Brow tine
        mesh.add_cylinder(p1, (-1.68, 0.50, 0.1 + side * 0.30), 0.028, 0.010, segs=6)
        # Bez tine
        mesh.add_cylinder(p2, (-1.52, 0.76, 0.1 + side * 0.50), 0.024, 0.009, segs=6)
        # Royal tine
        mesh.add_cylinder(p3, (-1.12, 1.25, 0.1 + side * 0.60), 0.022, 0.008, segs=6)

    add_antler(1.0)
    add_antler(-1.0)

    # 3. 16-Segment Curved Spine Vertebrae Column with Dorsal Spinous Processes
    spine_x = [-1.25, -1.10, -0.95, -0.80, -0.65, -0.50, -0.35, -0.20, -0.05, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    spine_pts = []
    for idx, sx in enumerate(spine_x):
        sy = 0.18 + 0.14 * math.sin(float(idx) / len(spine_x) * math.pi)
        sz = 0.06 * math.cos(float(idx) / len(spine_x) * math.pi)
        spine_pts.append((sx, sy, sz))

    for i in range(len(spine_pts)-1):
        mesh.add_cylinder(spine_pts[i], spine_pts[i+1], 0.065, 0.065, segs=8)
        # Spinous process
        top_p = (spine_pts[i][0], spine_pts[i][1] + 0.14, spine_pts[i][2])
        mesh.add_cylinder(spine_pts[i], top_p, 0.028, 0.012, segs=6)

    # 4. Shattered Thoracic Ribcage (catastrophic cryptid blunt trauma)
    for idx in range(3, 13):
        rx = spine_pts[idx][0]
        ry = spine_pts[idx][1]
        rib_w = 0.42 + 0.18 * math.sin((idx - 3) / 10.0 * math.pi)
        
        # Right side: Intact curved ribs resting in gore
        r_mid = (rx, ry + 0.14, rib_w * 0.7)
        r_tip = (rx, 0.03, rib_w)
        mesh.add_cylinder((rx, ry, 0.0), r_mid, 0.022, 0.018, segs=6)
        mesh.add_cylinder(r_mid, r_tip, 0.018, 0.012, segs=6)

        # Left side: Pried apart, shattered outward by cryptid claws
        if idx in [5, 6, 7, 8]:
            # Jagged compound breaks pointing upward with jagged tips
            l_mid = (rx + 0.06, ry + 0.32, -rib_w * 0.75)
            l_tip = (rx + 0.10, ry + 0.48, -rib_w * 1.05)
            mesh.add_cylinder((rx, ry, 0.0), l_mid, 0.024, 0.018, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.018, 0.007, segs=6)
        else:
            l_mid = (rx, ry + 0.12, -rib_w * 0.65)
            l_tip = (rx, 0.04, -rib_w * 0.95)
            mesh.add_cylinder((rx, ry, 0.0), l_mid, 0.022, 0.018, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.018, 0.012, segs=6)

    # 5. Pelvis and Fractured Limbs with Exposed Marrow Cavities
    mesh.add_box((0.95, 0.16, 0.05), (0.28, 0.18, 0.36), rot_y=-0.1)

    # Snapped foreleg (compound fracture)
    mesh.add_cylinder((-0.80, 0.22, -0.35), (-1.12, 0.14, -0.68), 0.045, 0.035, segs=6)
    mesh.add_cylinder((-1.12, 0.14, -0.68), (-1.38, 0.04, -0.84), 0.035, 0.022, segs=6)

    # Snapped hindleg with jagged bone marrow opening
    mesh.add_cylinder((0.95, 0.16, 0.18), (1.32, 0.22, 0.42), 0.050, 0.035, segs=6)
    mesh.add_cylinder((1.32, 0.22, 0.42), (1.58, 0.05, 0.58), 0.032, 0.020, segs=6)

    # 6. Clinging Visceral Flesh, Sinew, and Torn Muscle Tissue
    mesh.usemtl("Gore")
    mesh.add_box((-0.20, 0.14, 0.0), (0.82, 0.20, 0.48), rot_y=0.05)
    mesh.add_box(( 0.30, 0.12, -0.05), (0.50, 0.16, 0.38), rot_y=-0.15)
    # Sinew strands hanging from shattered ribs
    for sinew_x, sinew_z in [(-0.35, -0.42), (-0.15, -0.52), (0.10, -0.38)]:
        mesh.add_cylinder((sinew_x, 0.28, sinew_z), (sinew_x + 0.04, 0.08, sinew_z - 0.05), 0.015, 0.005, segs=4)

    mesh.save("assets/models/elk_carcass.obj", mat_order=["Bone", "Gore"])


def generate_carcass_gore_pool():
    """
    Multi-tiered organic coagulated gore splatter pool decal.
    """
    mesh = ObjMesh("carcass_gore_pool")
    mesh.usemtl("Gore")
    center = (0.0, 0.004, 0.0)
    c_idx = mesh.add_v(center[0], center[1], center[2])
    c_vn = mesh.add_vn(0, 1, 0)
    c_vt = mesh.add_vt(0.5, 0.5)

    n_pts = 32
    outer_v = []
    outer_vn = []
    outer_vt = []

    radii_base = [
        1.5, 1.9, 1.3, 0.9, 1.7, 2.3, 1.8, 1.2,
        0.8, 1.6, 2.1, 1.4, 1.0, 1.8, 2.5, 1.9,
        1.3, 0.9, 1.6, 2.2, 1.7, 1.2, 0.8, 1.4,
        1.8, 2.4, 1.6, 1.1, 1.5, 2.0, 1.4, 1.0
    ]

    for i in range(n_pts):
        angle = 2.0 * math.pi * i / n_pts
        r = radii_base[i] * 0.88
        px = math.cos(angle) * r * 1.45
        pz = math.sin(angle) * r * 0.90
        outer_v.append(mesh.add_v(px, 0.004, pz))
        outer_vn.append(mesh.add_vn(0, 1, 0))
        outer_vt.append(mesh.add_vt(0.5 + px * 0.22, 0.5 + pz * 0.22))

    for i in range(n_pts):
        nxt = (i + 1) % n_pts
        mesh.add_face([c_idx, outer_v[i], outer_v[nxt]],
                      [c_vn, outer_vn[i], outer_vn[nxt]],
                      [c_vt, outer_vt[i], outer_vt[nxt]])

    # Radiating arterial spray droplets and satellite splatters
    splatters = [
        (-2.1, -1.0, 0.30),
        (-1.6,  1.2, 0.38),
        ( 2.2, -0.9, 0.32),
        ( 1.8,  1.1, 0.40),
        (-0.8, -1.5, 0.26),
        ( 0.6,  1.6, 0.28)
    ]
    for sx, sz, sr in splatters:
        sc_idx = mesh.add_v(sx, 0.004, sz)
        s_pts = 8
        s_v = []
        for j in range(s_pts):
            th = 2.0 * math.pi * j / s_pts
            px = sx + math.cos(th) * sr * (0.8 + 0.4 * (j % 2))
            pz = sz + math.sin(th) * sr * (0.8 + 0.4 * (j % 2))
            s_v.append(mesh.add_v(px, 0.004, pz))
        for j in range(s_pts):
            jn = (j + 1) % s_pts
            mesh.add_face([sc_idx, s_v[j], s_v[jn]],
                          [c_vn, c_vn, c_vn],
                          [c_vt, c_vt, c_vt])

    mesh.save("assets/models/carcass_gore_pool.obj")


def generate_clawed_tree():
    """
    Overhauled Clawed Pine Trunk:
    - Bark: Old-growth knotted pine bark with root flare
    - Wood: 4 violent deep parallel gouges torn 8-10 feet high with shredded wood fibers
    - Resin: Viscous golden amber pine resin oozing down the claw channels
    """
    mesh = ObjMesh("clawed_tree")
    mesh.usemtl("Bark")
    segs = 24
    height_slices = 20
    total_h = 9.0

    v_grid = []
    vn_grid = []
    vt_grid = []

    for h_i in range(height_slices + 1):
        y = float(h_i) / height_slices * total_h
        t = y / total_h
        radius = 0.54 * (1.0 - t * 0.4)
        if y < 1.0:
            radius += 0.24 * (1.0 - y) ** 2

        v_row = []
        vn_row = []
        vt_row = []

        for s_i in range(segs + 1):
            theta = 2.0 * math.pi * s_i / segs
            nx = math.cos(theta)
            nz = math.sin(theta)
            cur_r = radius

            # 4 parallel gouges carved deep inward around theta = pi/2 (+Z axis)
            angle_from_front = abs(theta - math.pi * 0.5)
            if 1.6 <= y <= 3.4 and angle_from_front < 0.65:
                y_factor = 1.0 - abs(y - 2.5) / 0.9
                gouge_pattern = math.cos((theta - math.pi * 0.5) * 16.0)
                if gouge_pattern > 0.1:
                    depth = 0.16 * y_factor * (gouge_pattern ** 0.8)
                    cur_r -= depth
                elif gouge_pattern < -0.4:
                    lip = 0.05 * y_factor
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
        vt_row_copy = list(vt_row)
        vt_grid.append(vt_row_copy)

    for h_i in range(height_slices):
        for s_i in range(segs):
            v = [v_grid[h_i][s_i], v_grid[h_i][s_i+1], v_grid[h_i+1][s_i+1], v_grid[h_i+1][s_i]]
            vn = [vn_grid[h_i][s_i], vn_grid[h_i][s_i+1], vn_grid[h_i+1][s_i+1], vn_grid[h_i+1][s_i]]
            vt = [vt_grid[h_i][s_i], vt_grid[h_i][s_i+1], vt_grid[h_i+1][s_i+1], vt_grid[h_i+1][s_i]]
            mesh.add_face(v, vn, vt)

    # Splintered wood fibers curling out of claw channels
    mesh.usemtl("Wood")
    splinters = [
        ((-0.14, 2.2, 0.44), (0.04, 0.28, 0.03)),
        ((-0.02, 2.6, 0.48), (0.04, 0.32, 0.03)),
        (( 0.12, 2.4, 0.45), (0.04, 0.26, 0.03)),
        (( 0.22, 2.1, 0.41), (0.03, 0.24, 0.03))
    ]
    for sp_pos, sp_sz in splinters:
        mesh.add_box(sp_pos, sp_sz, rot_y=0.15)

    # Viscous Golden Amber Resin Runs oozing down the claw furrows
    mesh.usemtl("Resin")
    resin_runs = [
        [((-0.10, 2.6, 0.46), 0.024), ((-0.11, 2.1, 0.47), 0.032), ((-0.10, 1.5, 0.49), 0.020), ((-0.09, 1.1, 0.52), 0.008)],
        [(( 0.02, 2.7, 0.49), 0.026), (( 0.03, 2.2, 0.50), 0.035), (( 0.02, 1.6, 0.52), 0.022), (( 0.01, 1.0, 0.55), 0.006)],
        [(( 0.14, 2.5, 0.46), 0.022), (( 0.15, 1.9, 0.48), 0.030), (( 0.14, 1.4, 0.50), 0.016), (( 0.13, 0.9, 0.54), 0.005)]
    ]
    for r_pts in resin_runs:
        mesh.add_tapered_tube(r_pts, segs=8)

    mesh.save("assets/models/clawed_tree.obj", mat_order=["Bark", "Wood", "Resin"])


# ==============================================================================
# 3. EXISTING TREE ARCHETYPES (Preserved from Issue #2)
# ==============================================================================

def generate_pine_tree():
    trunk_mesh = ObjMesh("pine_tree_trunk")
    foliage_mesh = ObjMesh("pine_tree_foliage")
    combined_mesh = ObjMesh("pine_tree")

    trunk_h = 14.0
    trunk_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.52, 0.12, segs=12, u_start=0.0, u_end=1.0, v_start=0.0, v_end=5.0)
    combined_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.52, 0.12, segs=12, u_start=0.0, u_end=1.0, v_start=0.0, v_end=5.0)

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

            under_v.append(foliage_mesh.add_v(bx * 0.8, by + 0.15, bz * 0.8))
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


def generate_douglas_fir():
    trunk_mesh = ObjMesh("tree_douglas_fir_trunk")
    foliage_mesh = ObjMesh("tree_douglas_fir_foliage")

    trunk_h = 16.5
    trunk_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.65, 0.14, segs=14, u_start=0.0, u_end=1.0, v_start=0.0, v_end=6.0)

    tiers = [
        (2.5, 4.8, 4.6, 0.1),
        (4.8, 4.4, 4.0, 0.5),
        (7.2, 4.0, 3.4, 0.9),
        (9.5, 3.6, 2.7, 0.3),
        (11.8, 3.2, 2.0, 0.7),
        (13.8, 2.8, 1.3, 1.2)
    ]

    for y_base, h_tier, r_base, rot_offset in tiers:
        boughs = 14
        v_top = foliage_mesh.add_v(0.0, y_base + h_tier, 0.0)
        vt_top = foliage_mesh.add_vt(0.5, 1.0)
        vn_top = foliage_mesh.add_vn(0.0, 1.0, 0.0)

        ring_v = []
        ring_vn = []
        ring_vt = []
        under_v = []
        under_vn = []

        under_center = foliage_mesh.add_v(0.0, y_base + 0.45, 0.0)
        under_c_n = foliage_mesh.add_vn(0.0, -1.0, 0.0)
        under_c_vt = foliage_mesh.add_vt(0.5, 0.5)

        for b in range(boughs + 1):
            theta = 2.0 * math.pi * b / boughs + rot_offset
            dip = -0.45
            rb = r_base * (0.85 + 0.3 * (b % 3 == 0) + 0.15 * math.sin(b * 1.5))
            bx = math.cos(theta) * rb
            bz = math.sin(theta) * rb
            by = y_base + dip

            ring_v.append(foliage_mesh.add_v(bx, by, bz))
            ring_vn.append(foliage_mesh.add_vn(math.cos(theta) * 0.7, 0.5, math.sin(theta) * 0.7))
            u_c = float(b) / boughs
            ring_vt.append(foliage_mesh.add_vt(u_c, 0.0))

            under_v.append(foliage_mesh.add_v(bx * 0.85, by + 0.15, bz * 0.85))
            under_vn.append(foliage_mesh.add_vn(math.cos(theta) * 0.3, -0.9, math.sin(theta) * 0.3))

        for b in range(boughs):
            foliage_mesh.add_face([v_top, ring_v[b], ring_v[b+1]],
                                  [vn_top, ring_vn[b], ring_vn[b+1]],
                                  [vt_top, ring_vt[b], ring_vt[b+1]])
            foliage_mesh.add_face([under_center, under_v[b+1], under_v[b]],
                                  [under_c_n, under_vn[b+1], under_vn[b]],
                                  [under_c_vt, ring_vt[b+1], ring_vt[b]])

    trunk_mesh.save("assets/models/tree_douglas_fir_trunk.obj")
    foliage_mesh.save("assets/models/tree_douglas_fir_foliage.obj")


def generate_tall_pine():
    trunk_mesh = ObjMesh("tree_pine_tall_trunk")
    foliage_mesh = ObjMesh("tree_pine_tall_foliage")

    trunk_h = 15.0
    trunk_mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.38, 0.12, segs=10, u_start=0.0, u_end=1.0, v_start=0.0, v_end=5.0)

    stubs = [
        ((-0.25, 4.2, 0.1), (-0.75, 4.0, 0.2)),
        ((0.15, 5.5, -0.2), (0.65, 5.3, -0.5)),
        ((-0.1, 6.8, -0.2), (-0.5, 6.6, -0.4)),
        ((0.2, 7.8, 0.1), (0.6, 7.6, 0.3))
    ]
    for p1, p2 in stubs:
        trunk_mesh.add_cylinder(p1, p2, 0.06, 0.02, segs=6)

    tiers = [
        (8.5, 3.2, 2.8, 0.1),
        (10.2, 2.8, 2.3, 0.6),
        (11.8, 2.4, 1.8, 1.1),
        (13.2, 2.0, 1.1, 0.3)
    ]
    for y_base, h_tier, r_base, rot_offset in tiers:
        boughs = 10
        v_top = foliage_mesh.add_v(0.0, y_base + h_tier, 0.0)
        vt_top = foliage_mesh.add_vt(0.5, 1.0)
        vn_top = foliage_mesh.add_vn(0.0, 1.0, 0.0)

        ring_v = []
        ring_vn = []
        ring_vt = []
        for b in range(boughs + 1):
            theta = 2.0 * math.pi * b / boughs + rot_offset
            dip = -0.25
            rb = r_base * (0.9 + 0.2 * (b % 2))
            bx = math.cos(theta) * rb
            bz = math.sin(theta) * rb
            by = y_base + dip
            ring_v.append(foliage_mesh.add_v(bx, by, bz))
            ring_vn.append(foliage_mesh.add_vn(math.cos(theta) * 0.7, 0.5, math.sin(theta) * 0.7))
            ring_vt.append(foliage_mesh.add_vt(float(b) / boughs, 0.0))

        for b in range(boughs):
            foliage_mesh.add_face([v_top, ring_v[b], ring_v[b+1]],
                                  [vn_top, ring_vn[b], ring_vn[b+1]],
                                  [vt_top, ring_vt[b], ring_vt[b+1]])

    trunk_mesh.save("assets/models/tree_pine_tall_trunk.obj")
    foliage_mesh.save("assets/models/tree_pine_tall_foliage.obj")


def generate_dead_snag():
    mesh = ObjMesh("tree_snag_dead")
    trunk_h = 8.5
    mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, trunk_h, 0.0), 0.58, 0.38, segs=12, u_start=0.0, u_end=1.0, v_start=0.0, v_end=3.0)

    splinters = [
        (-0.25, trunk_h, -0.15, 1.2),
        ( 0.20, trunk_h, -0.22, 1.6),
        ( 0.30, trunk_h,  0.18, 0.9),
        (-0.18, trunk_h,  0.25, 1.4),
        ( 0.00, trunk_h,  0.00, 1.8)
    ]
    for sx, sy, sz, sh in splinters:
        p1 = (sx, sy - 0.2, sz)
        p2 = (sx + sx * 0.2, sy + sh, sz + sz * 0.2)
        mesh.add_cylinder(p1, p2, 0.10, 0.015, segs=6)

    dead_limbs = [
        ((0.2, 4.5, 0.2), (1.4, 4.2, 0.6)),
        ((-0.2, 5.8, 0.1), (-1.2, 5.4, 0.3)),
        ((0.1, 6.6, -0.2), (0.8, 6.2, -1.0)),
        ((-0.15, 7.2, -0.1), (-0.9, 7.0, -0.7))
    ]
    for lp1, lp2 in dead_limbs:
        mesh.add_cylinder(lp1, lp2, 0.12, 0.03, segs=6)

    mesh.save("assets/models/tree_snag_dead.obj")


def generate_tree_sapling():
    mesh = ObjMesh("tree_sapling")
    mesh.add_cylinder((0.0, 0.0, 0.0), (0.0, 2.8, 0.0), 0.08, 0.02, segs=6, u_start=0.0, u_end=1.0, v_start=0.0, v_end=1.0)

    tiers = [
        (0.6, 1.1, 0.9, 0.0),
        (1.3, 0.9, 0.7, 0.5),
        (1.9, 0.9, 0.45, 1.0)
    ]
    for y_base, h_tier, r_base, rot_offset in tiers:
        boughs = 8
        v_top = mesh.add_v(0.0, y_base + h_tier, 0.0)
        vt_top = mesh.add_vt(0.5, 1.0)
        vn_top = mesh.add_vn(0.0, 1.0, 0.0)

        ring_v = []
        ring_vn = []
        ring_vt = []
        for b in range(boughs + 1):
            theta = 2.0 * math.pi * b / boughs + rot_offset
            dip = -0.18
            rb = r_base * (0.85 + 0.3 * (b % 2))
            bx = math.cos(theta) * rb
            bz = math.sin(theta) * rb
            by = y_base + dip
            ring_v.append(mesh.add_v(bx, by, bz))
            ring_vn.append(mesh.add_vn(math.cos(theta) * 0.7, 0.5, math.sin(theta) * 0.7))
            ring_vt.append(mesh.add_vt(float(b) / boughs, 0.0))

        for b in range(boughs):
            mesh.add_face([v_top, ring_v[b], ring_v[b+1]],
                          [vn_top, ring_vn[b], ring_vn[b+1]],
                          [vt_top, ring_vt[b], ring_vt[b+1]])

    mesh.save("assets/models/tree_sapling.obj")


if __name__ == "__main__":
    print("Generating photorealistic 3D models for The Black Pines...")
    generate_sasquatch_models()
    generate_cabin()
    generate_tent()
    generate_camp_props()
    generate_elk_carcass()
    generate_carcass_gore_pool()
    generate_clawed_tree()
    generate_pine_tree()
    generate_douglas_fir()
    generate_tall_pine()
    generate_dead_snag()
    generate_tree_sapling()
    print("All models generated successfully!")
