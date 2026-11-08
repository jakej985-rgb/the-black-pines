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

    def add_quad(self, p1, p2, p3, p4, uv=None, normal=None):
        v1 = self.add_v(*p1)
        v2 = self.add_v(*p2)
        v3 = self.add_v(*p3)
        v4 = self.add_v(*p4)
        if normal is None:
            ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
            bx, by, bz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
            nx = ay*bz - az*by
            ny = az*bx - ax*bz
            nz = ax*by - ay*bx
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl > 0.0001:
                nx, ny, nz = nx/nl, ny/nl, nz/nl
            else:
                nx, ny, nz = 0.0, 1.0, 0.0
            n_idx = self.add_vn(nx, ny, nz)
            n_list = [n_idx]*4
        else:
            n_idx = self.add_vn(*normal)
            n_list = [n_idx]*4
        if uv is None:
            vt_list = [self.add_vt(0, 0), self.add_vt(1, 0), self.add_vt(1, 1), self.add_vt(0, 1)]
        else:
            vt_list = [self.add_vt(*u) for u in uv]
        self.add_face([v1, v2, v3, v4], n_list, vt_list)

    def add_tri(self, p1, p2, p3, uv=None, normal=None):
        v1 = self.add_v(*p1)
        v2 = self.add_v(*p2)
        v3 = self.add_v(*p3)
        if normal is None:
            ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
            bx, by, bz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
            nx = ay*bz - az*by
            ny = az*bx - ax*bz
            nz = ax*by - ay*bx
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl > 0.0001:
                nx, ny, nz = nx/nl, ny/nl, nz/nl
            else:
                nx, ny, nz = 0.0, 1.0, 0.0
            n_idx = self.add_vn(nx, ny, nz)
            n_list = [n_idx]*3
        else:
            n_idx = self.add_vn(*normal)
            n_list = [n_idx]*3
        if uv is None:
            vt_list = [self.add_vt(0, 0), self.add_vt(1, 0), self.add_vt(0.5, 1)]
        else:
            vt_list = [self.add_vt(*u) for u in uv]
        self.add_face([v1, v2, v3], n_list, vt_list)

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
    - Modular limb segments for articulated animation rig + complete single-mesh.
    - Anatomical Proportions: 8.5-foot hulking frame, massive trapezius and dorsal hump
      burying the neck into the shoulder girdle (iconic Patterson-Gimlin silhouette).
    - Menacing Facial Sculpt: Heavy supraorbital brow, cavernous sunken eye orbits,
      wrinkled black snout, snarling canines and incisors, peaked sagittal crest.
    - Corded Forearms & Claws: Heavy vascular forearms, broad ape palms, and razor talons.
    - Bowed Muscular Legs & Plantigrade Feet: Bulging calves, broad 5-toed clawed feet.
    - Volumetric Fur Cards: Multi-tiered silhouette breakup cards along spine, mantle, arms.
    """
    os.makedirs("assets/models", exist_ok=True)

    # --------------------------------------------------------------------------
    # 1.1 Torso: Deep chest, hunched spine, colossal traps, lats, and dorsal hump
    # Center relative to Torso node (y = 0 is mid-torso, around y=1.65 in world)
    # --------------------------------------------------------------------------
    torso = ObjMesh("sasquatch_torso")
    torso.usemtl("Fur")
    
    # Thoracic spine and ribcage spine sweep
    torso_spine = [
        ((0.0, -0.48,  0.02), (0.44, 0.40)),  # Pelvis / Lower abdomen
        ((0.0, -0.22,  0.06), (0.52, 0.46)),  # Mid waist
        ((0.0,  0.08,  0.10), (0.66, 0.56)),  # Lower chest & lats
        ((0.0,  0.34,  0.15), (0.72, 0.60)),  # Broad pectoral chest
        ((0.0,  0.56,  0.18), (0.68, 0.56)),  # Shoulder girdle / upper back
        ((0.0,  0.74,  0.12), (0.48, 0.42))   # Cervical base
    ]
    torso.add_tapered_tube(torso_spine, segs=16, u_scale=2.0, v_scale=2.0)

    # Massive Muscular Dorsal Hump (characteristic cryptid silhouette behind neck)
    torso.add_ellipsoid((0.0, 0.54, 0.34), (0.50, 0.32, 0.36), segs_u=14, segs_v=10)
    torso.add_ellipsoid((0.0, 0.32, 0.38), (0.44, 0.28, 0.30), segs_u=12, segs_v=8)
    
    # Pectoral muscle slabs (left and right with defined lower boundary)
    torso.add_ellipsoid((-0.26, 0.28, -0.32), (0.26, 0.20, 0.18), segs_u=12, segs_v=8)
    torso.add_ellipsoid(( 0.26, 0.28, -0.32), (0.26, 0.20, 0.18), segs_u=12, segs_v=8)

    # Abdominal muscle definition under pelt
    for ay in [0.06, -0.12]:
        torso.add_ellipsoid((-0.15, ay, -0.30), (0.14, 0.08, 0.10), segs_u=8, segs_v=6)
        torso.add_ellipsoid(( 0.15, ay, -0.30), (0.14, 0.08, 0.10), segs_u=8, segs_v=6)

    # Colossal Trapezius muscles burying neck into shoulder tips
    torso.add_ellipsoid((-0.36, 0.56, 0.10), (0.26, 0.24, 0.30), segs_u=12, segs_v=8)
    torso.add_ellipsoid(( 0.36, 0.56, 0.10), (0.26, 0.24, 0.30), segs_u=12, segs_v=8)

    # Flared Latissimus Dorsi curves
    torso.add_ellipsoid((-0.46, 0.12, 0.12), (0.22, 0.30, 0.24), segs_u=10, segs_v=6)
    torso.add_ellipsoid(( 0.46, 0.12, 0.12), (0.22, 0.30, 0.24), segs_u=10, segs_v=6)

    torso.save("assets/models/sasquatch_torso.obj")

    # --------------------------------------------------------------------------
    # 1.2 Head: Sagittal crest, heavy brow, recessed orbits, snarling canine fangs
    # --------------------------------------------------------------------------
    head = ObjMesh("sasquatch_head")
    head.usemtl("Fur")

    # Braincase / Cranium with sloping forehead
    head.add_ellipsoid((0.0, 0.05, 0.02), (0.32, 0.30, 0.36), segs_u=16, segs_v=12)
    
    # Peaked Sagittal crest (raised bony blade along top and back of skull)
    crest_pts = [
        ((0.0,  0.18, -0.12), (0.05, 0.09)),
        ((0.0,  0.30,  0.02), (0.06, 0.14)),
        ((0.0,  0.28,  0.18), (0.05, 0.12)),
        ((0.0,  0.14,  0.28), (0.04, 0.08))
    ]
    head.add_tapered_tube(crest_pts, segs=10)

    # Heavy ape-man supraorbital brow ridge projecting forward over eyes
    brow_pts = [
        ((-0.28, 0.07, -0.22), 0.06),
        ((-0.14, 0.11, -0.28), 0.08),
        (( 0.00, 0.12, -0.31), 0.09),
        (( 0.14, 0.11, -0.28), 0.08),
        (( 0.28, 0.07, -0.22), 0.06)
    ]
    head.add_tapered_tube(brow_pts, segs=10)

    # Flared Zygomatic arches (cheekbones)
    head.add_ellipsoid((-0.24, -0.02, -0.20), (0.12, 0.09, 0.14), segs_u=10, segs_v=6)
    head.add_ellipsoid(( 0.24, -0.02, -0.20), (0.12, 0.09, 0.14), segs_u=10, segs_v=6)

    # Pronounced ape muzzle / snout extending forward
    muzzle_pts = [
        ((0.0,  0.02, -0.16), (0.25, 0.21)),
        ((0.0, -0.06, -0.33), (0.21, 0.19)),
        ((0.0, -0.12, -0.43), (0.17, 0.15))
    ]
    head.add_tapered_tube(muzzle_pts, segs=12)

    # Black wrinkled leathery nasal bridge & flared predatory nostrils
    head.add_ellipsoid((-0.07, -0.06, -0.43), (0.05, 0.04, 0.05), segs_u=8, segs_v=6)
    head.add_ellipsoid(( 0.07, -0.06, -0.43), (0.05, 0.04, 0.05), segs_u=8, segs_v=6)
    head.add_box((0.0, -0.03, -0.40), (0.08, 0.06, 0.06), rot_y=0.0)

    # Deep cavernous eye orbits (recessed cavities for eye glow spheres at +/-0.13, 0.04, -0.28)
    head.add_ellipsoid((-0.13, 0.04, -0.28), (0.075, 0.065, 0.07), segs_u=10, segs_v=6)
    head.add_ellipsoid(( 0.13, 0.04, -0.28), (0.075, 0.065, 0.07), segs_u=10, segs_v=6)

    # Lower Jaw / Mandible pulled into an aggressive snarling display
    jaw_pts = [
        ((0.0, -0.14, -0.14), (0.24, 0.14)),
        ((0.0, -0.21, -0.29), (0.20, 0.12)),
        ((0.0, -0.23, -0.39), (0.15, 0.09))
    ]
    head.add_tapered_tube(jaw_pts, segs=12)

    # Flared Ape Ears (tucked flat against sides of skull)
    head.add_ellipsoid((-0.30, 0.02, 0.02), (0.04, 0.12, 0.08), segs_u=8, segs_v=6)
    head.add_ellipsoid(( 0.30, 0.02, 0.02), (0.04, 0.12, 0.08), segs_u=8, segs_v=6)

    # Lethal Predatory Bone Dentition (Snarling Fangs & Incisors)
    head.usemtl("Bone")
    # Upper canines (sabre-curved fangs protruding downward from muzzle)
    head.add_claw((-0.11, -0.09, -0.38), (-0.11, -0.17, -0.40), (-0.10, -0.24, -0.39), base_r=0.024, mid_r=0.016, segs=6)
    head.add_claw(( 0.11, -0.09, -0.38), ( 0.11, -0.17, -0.40), ( 0.10, -0.24, -0.39), base_r=0.024, mid_r=0.016, segs=6)
    # Lower canines (protruding upward from mandible into canine diastema)
    head.add_claw((-0.09, -0.20, -0.36), (-0.09, -0.13, -0.38), (-0.08, -0.08, -0.37), base_r=0.020, mid_r=0.013, segs=6)
    head.add_claw(( 0.09, -0.20, -0.36), ( 0.09, -0.13, -0.38), ( 0.08, -0.08, -0.37), base_r=0.020, mid_r=0.013, segs=6)

    # Sharp serrated incisors & shearing premolars
    for tx in [-0.06, -0.02, 0.02, 0.06]:
        head.add_cylinder((tx, -0.10, -0.40), (tx, -0.14, -0.40), 0.011, 0.008, segs=4)
        head.add_cylinder((tx, -0.20, -0.38), (tx, -0.16, -0.38), 0.010, 0.007, segs=4)

    head.save("assets/models/sasquatch_head.obj", mat_order=["Fur", "Bone"])

    # --------------------------------------------------------------------------
    # 1.3 Upper Arm: Deltoid cap, bulging bicep/tricep (extends from shoulder down)
    # --------------------------------------------------------------------------
    arm_upper = ObjMesh("sasquatch_arm_upper")
    arm_upper.usemtl("Fur")
    # Massive rounded deltoid cap wrapping over the shoulder socket
    arm_upper.add_ellipsoid((0.0, 0.0, 0.0), (0.26, 0.24, 0.24), segs_u=14, segs_v=10)
    # Bicep / Tricep arm cylinder tapering to elbow at y = -0.60
    arm_pts = [
        ((0.0,  0.00, 0.00), 0.23),
        ((0.0, -0.20, 0.01), 0.25),  # Peak of bulging bicep
        ((0.0, -0.42, 0.01), 0.20),
        ((0.0, -0.60, 0.01), 0.17)   # Elbow joint
    ]
    arm_upper.add_tapered_tube(arm_pts, segs=14)
    # Posterior tricep muscle mass
    arm_upper.add_ellipsoid((0.0, -0.22, 0.10), (0.16, 0.20, 0.12), segs_u=10, segs_v=6)
    arm_upper.save("assets/models/sasquatch_arm_upper.obj")

    # --------------------------------------------------------------------------
    # 1.4 Lower Arm / Forearm: Corded brachioradialis, wrist joint (y = 0 to -0.58)
    # --------------------------------------------------------------------------
    arm_lower = ObjMesh("sasquatch_arm_lower")
    arm_lower.usemtl("Fur")
    # Elbow joint ball
    arm_lower.add_ellipsoid((0.0, 0.0, 0.0), (0.18, 0.16, 0.17), segs_u=12, segs_v=8)
    # Powerful brachioradialis & forearm muscular sweep
    forearm_pts = [
        ((0.0,  0.00, 0.00), 0.18),
        ((0.0, -0.18, 0.03), 0.20),  # Muscular belly of forearm
        ((0.0, -0.38, 0.02), 0.16),
        ((0.0, -0.56, 0.00), 0.14)   # Heavy wrist
    ]
    arm_lower.add_tapered_tube(forearm_pts, segs=14)
    # Vascular ridge along forearm
    arm_lower.add_cylinder((0.0, -0.10, -0.12), (0.0, -0.48, -0.08), 0.02, 0.015, segs=6)
    arm_lower.save("assets/models/sasquatch_arm_lower.obj")

    # --------------------------------------------------------------------------
    # 1.5 Hand: Broad ape palm, 5 digits with razor curved predator claw talons
    # --------------------------------------------------------------------------
    hand = ObjMesh("sasquatch_hand")
    hand.usemtl("Fur")
    # Thick leathery ape palm with thenar eminence
    hand.add_box((0.0, -0.10, 0.0), (0.26, 0.19, 0.13), rot_y=0.0)

    # 5 Digits with sharp predatory claw talons
    finger_configs = [
        (-0.12, -0.06,  0.04, 0.35,  -0.13, 0.05),   # Opposable Thumb
        (-0.09, -0.19, -0.02, 0.05,  -0.17, 0.07),   # Index
        (-0.02, -0.21, -0.02, 0.00,  -0.19, 0.08),   # Middle (longest)
        ( 0.04, -0.20, -0.02, -0.05, -0.17, 0.07),   # Ring
        ( 0.10, -0.18, -0.01, -0.10, -0.15, 0.06)    # Pinky
    ]
    for fx, fy, fz, ang_x, f_len, c_len in finger_configs:
        # Finger proximal segment (fur/leather)
        hand.usemtl("Fur")
        p_base = (fx, fy, fz)
        p_knuckle = (fx + math.sin(ang_x)*0.05, fy + f_len, fz + 0.04)
        hand.add_cylinder(p_base, p_knuckle, 0.028, 0.022, segs=8)

        # Curved Keratin Talon Claw Tip
        hand.usemtl("Claw")
        p_tip = (p_knuckle[0] + math.sin(ang_x)*0.04, p_knuckle[1] + c_len * 0.85, p_knuckle[2] + c_len * 1.1)
        hand.add_claw(p_knuckle, (p_knuckle[0], p_knuckle[1] - 0.02, p_knuckle[2] + c_len*0.6), p_tip, base_r=0.020, mid_r=0.012, segs=8)

    hand.save("assets/models/sasquatch_hand.obj", mat_order=["Fur", "Claw"])

    # --------------------------------------------------------------------------
    # 1.6 Upper Leg / Thigh: Bowed muscular quadriceps and knee (y = 0 to -0.62)
    # --------------------------------------------------------------------------
    leg_upper = ObjMesh("sasquatch_leg_upper")
    leg_upper.usemtl("Fur")
    # Hip joint socket
    leg_upper.add_ellipsoid((0.0, 0.0, 0.0), (0.27, 0.24, 0.26), segs_u=12, segs_v=8)
    # Bowed muscular thigh sweep (vastus lateralis & rectus femoris)
    thigh_pts = [
        ((0.0,  0.00, 0.00), 0.26),
        ((0.03, -0.22, 0.02), 0.28),  # Bulging quadricep
        ((0.02, -0.44, 0.01), 0.23),
        ((0.00, -0.62, 0.00), 0.19)   # Heavy knee
    ]
    leg_upper.add_tapered_tube(thigh_pts, segs=14)
    # Posterior hamstring bulge
    leg_upper.add_ellipsoid((0.0, -0.25, 0.10), (0.18, 0.22, 0.14), segs_u=10, segs_v=6)
    leg_upper.save("assets/models/sasquatch_leg_upper.obj")

    # --------------------------------------------------------------------------
    # 1.7 Lower Leg / Shin & Calf: Bulging gastrocnemius, thick shin (y = 0 to -0.55)
    # --------------------------------------------------------------------------
    leg_lower = ObjMesh("sasquatch_leg_lower")
    leg_lower.usemtl("Fur")
    # Knee joint ball
    leg_lower.add_ellipsoid((0.0, 0.0, 0.0), (0.20, 0.17, 0.19), segs_u=12, segs_v=8)
    # Bulging calf and tapering shin
    shin_pts = [
        ((0.0,  0.00, 0.00), 0.19),
        ((0.0, -0.16, 0.05), 0.24),  # Bulging posterior calf belly
        ((0.0, -0.36, 0.03), 0.18),
        ((0.0, -0.52, 0.00), 0.16)   # Heavy ankle joint
    ]
    leg_lower.add_tapered_tube(shin_pts, segs=14)
    leg_lower.save("assets/models/sasquatch_leg_lower.obj")

    # --------------------------------------------------------------------------
    # 1.8 Foot: Broad 5-toed plantigrade cryptid foot with clawed toes and heel pad
    # --------------------------------------------------------------------------
    foot = ObjMesh("sasquatch_foot")
    foot.usemtl("Fur")
    # Broad heel and metatarsal foot pad resting flat on ground
    foot.add_box((0.0, 0.06, 0.02), (0.26, 0.12, 0.42), rot_y=0.0)

    # 5 Splayed plantigrade toes with heavy claw tips
    toe_xs = [-0.10, -0.05, 0.0, 0.05, 0.10]
    toe_lens = [0.15, 0.17, 0.18, 0.16, 0.13]
    for tx, tl in zip(toe_xs, toe_lens):
        foot.usemtl("Fur")
        # Toe base
        p_t_base = (tx, 0.05, -0.18)
        p_t_mid = (tx * 1.1, 0.04, -0.18 - tl * 0.7)
        foot.add_cylinder(p_t_base, p_t_mid, 0.026, 0.020, segs=8)

        # Toe claw tip digging into the earth
        foot.usemtl("Claw")
        p_claw_tip = (tx * 1.15, 0.01, -0.18 - tl - 0.05)
        foot.add_claw(p_t_mid, (p_t_mid[0], 0.03, p_t_mid[2] - 0.02), p_claw_tip, base_r=0.018, mid_r=0.011, segs=8)

    foot.save("assets/models/sasquatch_foot.obj", mat_order=["Fur", "Claw"])

    # --------------------------------------------------------------------------
    # 1.9 Shaggy Fur Silhouette Fringe Cards (shoulders, dorsal hump, forearms)
    # Double-sided textured cards for realistic silhouette breakup
    # --------------------------------------------------------------------------
    fur_cards = ObjMesh("sasquatch_fur_cards")
    fur_cards.usemtl("Fur")
    
    # Expanded volumetric fur tuft positions across entire torso & limbs
    mantle_positions = [
        # Shoulder mantle & trapezius overhang
        ((-0.48, 0.58,  0.15), (-0.78, 0.35,  0.18)),
        (( 0.48, 0.58,  0.15), ( 0.78, 0.35,  0.18)),
        ((-0.42, 0.46,  0.28), (-0.68, 0.25,  0.34)),
        (( 0.42, 0.46,  0.28), ( 0.68, 0.25,  0.34)),
        # Sagittal crest & nape ridge tufts
        (( 0.00, 0.72,  0.32), ( 0.00, 0.45,  0.55)),
        (( 0.00, 0.48,  0.44), ( 0.00, 0.24,  0.60)),
        (( 0.00, 0.25,  0.42), ( 0.00, 0.04,  0.56)),
        # Dorsal spinal crest sides
        ((-0.20, 0.60,  0.38), (-0.32, 0.38,  0.52)),
        (( 0.20, 0.60,  0.38), ( 0.32, 0.38,  0.52)),
        ((-0.18, 0.38,  0.42), (-0.28, 0.18,  0.54)),
        (( 0.18, 0.38,  0.42), ( 0.28, 0.18,  0.54)),
        # Flank & Latissimus fringe
        ((-0.52, 0.15,  0.10), (-0.75, 0.02,  0.14)),
        (( 0.52, 0.15,  0.10), ( 0.75, 0.02,  0.14))
    ]
    for p1, p2 in mantle_positions:
        fur_cards.add_cylinder(p1, p2, 0.16, 0.02, segs=6)

    fur_cards.save("assets/models/sasquatch_fur_cards.obj")

    # --------------------------------------------------------------------------
    # 1.10 Assembled Unified Sasquatch Model (for reference / distant LOD)
    # --------------------------------------------------------------------------
    full = ObjMesh("sasquatch_full")
    full.usemtl("Fur")
    # Full torso
    full.add_tapered_tube([((p[0], p[1] + 1.65, p[2]), r) for p, r in torso_spine], segs=16)
    full.add_ellipsoid((0.0, 2.19, 0.34), (0.50, 0.32, 0.36), segs_u=14, segs_v=10)
    full.add_ellipsoid((-0.26, 1.93, -0.32), (0.26, 0.20, 0.18), segs_u=12, segs_v=8)
    full.add_ellipsoid(( 0.26, 1.93, -0.32), (0.26, 0.20, 0.18), segs_u=12, segs_v=8)
    # Head at y = 2.45
    full.add_ellipsoid((0.0, 2.50, -0.10), (0.32, 0.30, 0.36), segs_u=16, segs_v=12)
    full.add_tapered_tube([((p[0], p[1] + 2.45, p[2] - 0.12), r) for p, r in crest_pts], segs=10)
    full.add_tapered_tube([((p[0], p[1] + 2.45, p[2] - 0.12), r) for p, r in muzzle_pts], segs=12)
    # Limbs
    for side in [-1.0, 1.0]:
        # Arm: Shoulder -> Elbow -> Wrist
        p_sh = (side * 0.70, 2.05, 0.05)
        p_elb = (side * 0.84, 1.45, 0.08)
        p_wr = (side * 0.88, 0.88, 0.10)
        p_hnd = (side * 0.90, 0.68, 0.12)
        full.add_ellipsoid(p_sh, (0.26, 0.24, 0.24), segs_u=12, segs_v=8)
        full.add_cylinder(p_sh, p_elb, 0.24, 0.18, segs=12)
        full.add_cylinder(p_elb, p_wr, 0.18, 0.14, segs=12)
        full.add_box(p_hnd, (0.24, 0.18, 0.12), rot_y=0.0)

        # Leg: Hip -> Knee -> Ankle -> Foot
        p_hip = (side * 0.36, 1.25, 0.02)
        p_knee = (side * 0.38, 0.65, 0.04)
        p_ank = (side * 0.38, 0.14, 0.00)
        p_ft = (side * 0.38, 0.05, -0.10)
        full.add_ellipsoid(p_hip, (0.27, 0.24, 0.26), segs_u=12, segs_v=8)
        full.add_cylinder(p_hip, p_knee, 0.26, 0.19, segs=12)
        full.add_cylinder(p_knee, p_ank, 0.19, 0.16, segs=12)
        full.add_box(p_ft, (0.26, 0.12, 0.42), rot_y=0.0)

    full.save("assets/models/sasquatch_full.obj")


# ==============================================================================
# 2. PROPS & LANDMARKS OVERHAUL (Issue #7 & Issue #4)
# ==============================================================================

def generate_cabin():
    """
    Overhauled Ranger Station Cabin with high-fidelity architecture:
    - Foundation: Continuous rough-hewn fieldstone masonry perimeter skirting
    - Walls: 16 courses of interlocking saddle-notched cedar logs with rough overhangs
    - Gables: Board-and-batten siding and horizontal logs filling gable triangles
    - Windows: 3D timber casings, 4-pane cross mullions, boarded weathered planks, glass
    - Door: Recessed vertical plank door with diagonal Z-brace, iron strap hinges and latch
    - Roof: Thick dimensional 0.75m overhanging eaves, fascia barge boards, exposed
      rafter tails, 3D stepped cedar shake shingle courses, and interlocking ridge cap
    - Porch: Sloping timber awning roof over deck, 4 heavy 8x8 posts with 45° knee
      brackets, X-brace balustrades, plank flooring with timber rim joists, and 3-tread steps
    - Storytelling Props: USFS carved station sign, stacked split firewood cord under eave,
      cast-iron stovepipe with flashing collar, guy wires, and wall lantern sconce
    """
    mesh = ObjMesh("cabin")
    cabin_w = 6.4
    cabin_d = 5.2
    wall_h = 3.2
    half_w = cabin_w * 0.5
    half_d = cabin_d * 0.5
    roof_peak_h = wall_h + 1.65
    roof_overhang = 0.75

    # =========================================================================
    # 1. FIELDSTONE MASONRY FOUNDATION & PIERS (usemtl Stone)
    # =========================================================================
    mesh.usemtl("Stone")
    f_thick = 0.42
    f_h = 0.55
    f_y = 0.05

    # Continuous stone perimeter foundation under all walls
    # Front foundation (recessed under sill log)
    mesh.add_box((0.0, f_y, half_d), (cabin_w + 0.3, f_h, f_thick), rot_y=0.0)
    # Back foundation
    mesh.add_box((0.0, f_y, -half_d), (cabin_w + 0.3, f_h, f_thick), rot_y=0.0)
    # Left foundation
    mesh.add_box((-half_w, f_y, 0.0), (f_thick, f_h, cabin_d + 0.3), rot_y=0.0)
    # Right foundation
    mesh.add_box(( half_w, f_y, 0.0), (f_thick, f_h, cabin_d + 0.3), rot_y=0.0)

    # Foundation piers supporting the front porch corners and steps
    for px in [-half_w, -half_w * 0.35, half_w * 0.35, half_w]:
        mesh.add_box((px, f_y, half_d + 2.0), (0.45, f_h, 0.45), rot_y=0.05)

    # Irregular protruding masonry boulders around perimeter
    stone_bumps = [
        (-half_w - 0.15, 0.12, -1.2, 0.28, 0.22, 0.25),
        (-half_w - 0.12, 0.08,  1.4, 0.32, 0.20, 0.26),
        ( half_w + 0.14, 0.10, -0.8, 0.30, 0.24, 0.28),
        ( half_w + 0.12, 0.09,  1.1, 0.26, 0.22, 0.24),
        (-1.8, 0.08, -half_d - 0.12, 0.34, 0.20, 0.26),
        ( 1.6, 0.10, -half_d - 0.14, 0.30, 0.24, 0.28)
    ]
    for bx, by, bz, sx, sy, sz in stone_bumps:
        mesh.add_box((bx, by, bz), (sx, sy, sz), rot_y=0.15)

    # =========================================================================
    # 2. INTERLOCKING CEDAR LOG WALLS & TIMBER FRAMING (usemtl Wood)
    # =========================================================================
    mesh.usemtl("Wood")
    num_logs = 16
    log_h_step = wall_h / num_logs
    log_r = log_h_step * 0.58
    overhang = 0.42

    for i in range(num_logs):
        y = log_r + i * log_h_step

        # Front & Back walls (running along X axis)
        if i % 2 == 0:
            # Back wall full continuous log
            mesh.add_cylinder((-half_w - overhang, y, -half_d), (half_w + overhang, y, -half_d), log_r, log_r, segs=10)
            # Front wall with door opening in center (-0.75m to 0.75m)
            if i >= 11:
                # Header logs over the door
                mesh.add_cylinder((-half_w - overhang, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=10)
            else:
                mesh.add_cylinder((-half_w - overhang, y, half_d), (-0.75, y, half_d), log_r, log_r, segs=8)
                mesh.add_cylinder((0.75, y, half_d), (half_w + overhang, y, half_d), log_r, log_r, segs=8)

        # Left & Right walls (running along Z axis)
        else:
            # Window openings left and right (logs 5 to 10)
            if 5 <= i <= 10:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, -0.65), log_r, log_r, segs=8)
                mesh.add_cylinder((-half_w, y, 0.65), (-half_w, y, half_d + overhang), log_r, log_r, segs=8)

                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, -0.65), log_r, log_r, segs=8)
                mesh.add_cylinder((half_w, y, 0.65), (half_w, y, half_d + overhang), log_r, log_r, segs=8)
            else:
                mesh.add_cylinder((-half_w, y, -half_d - overhang), (-half_w, y, half_d + overhang), log_r, log_r, segs=10)
                mesh.add_cylinder((half_w, y, -half_d - overhang), (half_w, y, half_d + overhang), log_r, log_r, segs=10)

    # 2.1 Dimensional Gable Wall Ends (Board & Batten + Siding filling the peak)
    for gz, g_norm in [(half_d, (0, 0, 1)), (-half_d, (0, 0, -1))]:
        num_gable_planks = 10
        for gi in range(num_gable_planks):
            gy = wall_h + gi * (roof_peak_h - wall_h) / num_gable_planks
            gh = (roof_peak_h - wall_h) / num_gable_planks
            gw = half_w * (1.0 - float(gi) / num_gable_planks)
            mesh.add_box((0.0, gy + gh * 0.5, gz), (gw * 2.0, gh * 0.95, 0.08), rot_y=0.0)

    # 2.2 Heavy Timber Door Frame & Inward-Swung Plank Door
    # Casing header and side jambs
    mesh.add_box((-0.78, 1.15, half_d + 0.04), (0.12, 2.30, 0.12), rot_y=0.0)
    mesh.add_box(( 0.78, 1.15, half_d + 0.04), (0.12, 2.30, 0.12), rot_y=0.0)
    mesh.add_box(( 0.00, 2.30, half_d + 0.04), (1.68, 0.14, 0.12), rot_y=0.0)
    # Threshold sill timber
    mesh.add_box(( 0.00, f_h + 0.02, half_d + 0.02), (1.56, 0.08, 0.16), rot_y=0.0)
    
    # Door swung completely open 90 degrees flat along the interior wall
    door_angle = math.pi * 0.5  # 90 degrees open
    door_w = 1.35
    door_cx = -0.74
    door_cz = (half_d - 0.06) - (door_w * 0.5)
    mesh.add_box((door_cx, 1.15, door_cz), (0.06, 2.20, door_w), rot_y=0.0)
    # Diagonal Z-brace battens on open door
    mesh.add_box((door_cx + 0.04, 1.85, door_cz), (0.04, 0.12, door_w * 0.9), rot_y=0.0)
    mesh.add_box((door_cx + 0.04, 0.45, door_cz), (0.04, 0.12, door_w * 0.9), rot_y=0.0)



    # 2.3 3D Window Frames, 4-Pane Mullions & Barricade Planks
    for wx in [-half_w, half_w]:
        w_dir = 1.0 if wx > 0 else -1.0
        # Casing header, sill, and side jambs
        mesh.add_box((wx + w_dir * 0.04, 1.25, 0.0), (0.10, 0.08, 1.45), rot_y=0.0) # Sill
        mesh.add_box((wx + w_dir * 0.04, 2.25, 0.0), (0.10, 0.08, 1.45), rot_y=0.0) # Header
        mesh.add_box((wx + w_dir * 0.04, 1.75, -0.68), (0.10, 1.05, 0.08), rot_y=0.0) # Jamb
        mesh.add_box((wx + w_dir * 0.04, 1.75,  0.68), (0.10, 1.05, 0.08), rot_y=0.0) # Jamb
        # 4-pane cross-mullion grid
        mesh.add_box((wx + w_dir * 0.01, 1.75, 0.0), (0.04, 0.04, 1.28), rot_y=0.0) # Horizontal
        mesh.add_box((wx + w_dir * 0.01, 1.75, 0.0), (0.04, 0.92, 0.04), rot_y=0.0) # Vertical
        # Weathered protective barricade planks nailed at angles
        mesh.add_box((wx + w_dir * 0.08, 1.95, 0.0), (0.04, 0.18, 1.40), rot_y=0.04 * w_dir)
        mesh.add_box((wx + w_dir * 0.08, 1.55, 0.0), (0.04, 0.18, 1.40), rot_y=-0.05 * w_dir)

    # 2.4 Front Porch Deck, Framing, Posts, Railings, and Steps
    porch_d = 2.0
    porch_h = 0.38
    porch_z_front = half_d + porch_d

    # Rim joists and underside timber framing
    mesh.add_box((0.0, porch_h * 0.5, porch_z_front), (cabin_w + 0.4, porch_h, 0.12), rot_y=0.0)
    mesh.add_box((-half_w - 0.2, porch_h * 0.5, half_d + porch_d * 0.5), (0.12, porch_h, porch_d), rot_y=0.0)
    mesh.add_box(( half_w + 0.2, porch_h * 0.5, half_d + porch_d * 0.5), (0.12, porch_h, porch_d), rot_y=0.0)

    # 18 individual floor planks running across the deck
    num_deck_planks = 18
    plank_d = porch_d / num_deck_planks
    for di in range(num_deck_planks):
        pz = half_d + (di + 0.5) * plank_d
        mesh.add_box((0.0, porch_h - 0.02, pz), (cabin_w + 0.38, 0.04, plank_d * 0.92), rot_y=0.0)

    # Heavy 8x8 Square Timber Posts (4 posts)
    post_size = 0.18
    posts_x = [-half_w, -1.25, 1.25, half_w]
    for px in posts_x:
        # Vertical post extending from foundation up to porch roof header at Y = 2.65
        mesh.add_box((px, 1.35, porch_z_front), (post_size, 2.60, post_size), rot_y=0.0)
        # 45-degree diagonal knee braces (timber gallows brackets)
        brace_dir = 1.0 if px < 0 else -1.0
        if abs(px) > 1.5:
            # Outer corner post brackets
            mesh.add_cylinder((px, 2.10, porch_z_front), (px + brace_dir * 0.55, 2.60, porch_z_front), 0.05, 0.05, segs=6)
            mesh.add_cylinder((px, 2.10, porch_z_front), (px, 2.60, porch_z_front - 0.55), 0.05, 0.05, segs=6)

    # Top Porch Header Beams
    mesh.add_box((0.0, 2.65, porch_z_front), (cabin_w + 0.4, 0.20, 0.18), rot_y=0.0)
    # Side beams back to cabin wall
    mesh.add_box((-half_w, 2.65, half_d + porch_d * 0.5), (0.18, 0.20, porch_d), rot_y=0.0)
    mesh.add_box(( half_w, 2.65, half_d + porch_d * 0.5), (0.18, 0.20, porch_d), rot_y=0.0)

    # Rustic X-Brace Porch Balustrade Railings
    rail_top_y = porch_h + 0.72
    rail_bot_y = porch_h + 0.12
    # Left side railing
    mesh.add_box((-half_w, rail_top_y, half_d + porch_d * 0.5), (0.10, 0.08, porch_d), rot_y=0.0)
    mesh.add_box((-half_w, rail_bot_y, half_d + porch_d * 0.5), (0.10, 0.08, porch_d), rot_y=0.0)
    mesh.add_cylinder((-half_w, rail_bot_y, half_d + 0.1), (-half_w, rail_top_y, porch_z_front - 0.1), 0.04, 0.04, segs=6)
    mesh.add_cylinder((-half_w, rail_top_y, half_d + 0.1), (-half_w, rail_bot_y, porch_z_front - 0.1), 0.04, 0.04, segs=6)

    # Right side railing
    mesh.add_box(( half_w, rail_top_y, half_d + porch_d * 0.5), (0.10, 0.08, porch_d), rot_y=0.0)
    mesh.add_box(( half_w, rail_bot_y, half_d + porch_d * 0.5), (0.10, 0.08, porch_d), rot_y=0.0)
    mesh.add_cylinder(( half_w, rail_bot_y, half_d + 0.1), ( half_w, rail_top_y, porch_z_front - 0.1), 0.04, 0.04, segs=6)
    mesh.add_cylinder(( half_w, rail_top_y, half_d + 0.1), ( half_w, rail_bot_y, porch_z_front - 0.1), 0.04, 0.04, segs=6)

    # Front Railing Left of entry (-3.2 to -1.25)
    r_mid_l = (-half_w + (-1.25 - (-half_w)) * 0.5)
    r_len_l = abs(-1.25 - (-half_w))
    mesh.add_box((r_mid_l, rail_top_y, porch_z_front), (r_len_l, 0.08, 0.10), rot_y=0.0)
    mesh.add_box((r_mid_l, rail_bot_y, porch_z_front), (r_len_l, 0.08, 0.10), rot_y=0.0)
    mesh.add_cylinder((-half_w + 0.1, rail_bot_y, porch_z_front), (-1.25 - 0.1, rail_top_y, porch_z_front), 0.04, 0.04, segs=6)
    mesh.add_cylinder((-half_w + 0.1, rail_top_y, porch_z_front), (-1.25 - 0.1, rail_bot_y, porch_z_front), 0.04, 0.04, segs=6)

    # Front Railing Right of entry (1.25 to 3.2)
    r_mid_r = (1.25 + (half_w - 1.25) * 0.5)
    r_len_r = abs(half_w - 1.25)
    mesh.add_box((r_mid_r, rail_top_y, porch_z_front), (r_len_r, 0.08, 0.10), rot_y=0.0)
    mesh.add_box((r_mid_r, rail_bot_y, porch_z_front), (r_len_r, 0.08, 0.10), rot_y=0.0)
    mesh.add_cylinder((1.25 + 0.1, rail_bot_y, porch_z_front), (half_w - 0.1, rail_top_y, porch_z_front), 0.04, 0.04, segs=6)
    mesh.add_cylinder((1.25 + 0.1, rail_top_y, porch_z_front), (half_w - 0.1, rail_bot_y, porch_z_front), 0.04, 0.04, segs=6)

    # Sturdy 3-Tread Wooden Steps (centered at doorway)
    step_w = 2.1
    mesh.add_box((0.0, porch_h * 0.75, porch_z_front + 0.25), (step_w, 0.12, 0.45), rot_y=0.0)
    mesh.add_box((0.0, porch_h * 0.50, porch_z_front + 0.58), (step_w, 0.12, 0.45), rot_y=0.0)
    mesh.add_box((0.0, porch_h * 0.25, porch_z_front + 0.90), (step_w, 0.12, 0.45), rot_y=0.0)
    # Side timber stringers
    mesh.add_cylinder((-step_w * 0.5, porch_h, porch_z_front), (-step_w * 0.5, 0.05, porch_z_front + 1.1), 0.08, 0.08, segs=6)
    mesh.add_cylinder(( step_w * 0.5, porch_h, porch_z_front), ( step_w * 0.5, 0.05, porch_z_front + 1.1), 0.08, 0.08, segs=6)

    # 2.5 Exposed Roof Rafter Tails (8 per side) & Ridge Beam
    mesh.add_cylinder((0.0, roof_peak_h + 0.05, -half_d - roof_overhang - 0.25),
                      (0.0, roof_peak_h + 0.05,  half_d + roof_overhang + 0.25), 0.14, 0.14, segs=10)

    for side_x in [-1.0, 1.0]:
        eave_x = side_x * (half_w + roof_overhang)
        for ri in range(8):
            rz = -half_d - 0.2 + ri * (cabin_d + 0.4) / 7.0
            # Square rafter tail projecting out under eave
            mesh.add_box((eave_x - side_x * 0.15, wall_h - 0.08, rz), (0.35, 0.10, 0.10), rot_y=0.0)

    # 2.6 Carved USFS Ranger Station Sign (mounted above porch header)
    mesh.add_box((0.0, 2.95, porch_z_front + 0.08), (1.95, 0.42, 0.06), rot_y=0.0)
    # Sign mounting brackets
    mesh.add_cylinder((-0.75, 2.75, porch_z_front + 0.02), (-0.75, 2.95, porch_z_front + 0.08), 0.02, 0.02, segs=4)
    mesh.add_cylinder(( 0.75, 2.75, porch_z_front + 0.02), ( 0.75, 2.95, porch_z_front + 0.08), 0.02, 0.02, segs=4)

    # 2.7 Split Firewood Cord Stacked Under Side Eave
    for f_layer in range(4):
        fy = 0.12 + f_layer * 0.22
        for f_col in range(6):
            fz = -1.6 + f_col * 0.24
            mesh.add_cylinder((-half_w - 0.15, fy, fz), (-half_w - 0.55, fy, fz), 0.08, 0.08, segs=6)

    # 2.8 Walk-in Cabin Interior Timber Architecture & Furnishings
    # Interior Pine Floorboards (at f_h + 0.02 so it sits above stone foundation)
    mesh.add_box((0.0, f_h + 0.02, 0.0), (cabin_w - 0.45, 0.06, cabin_d - 0.45), rot_y=0.0)

    # Overhead Heavy Timber Ceiling Rafters spanning cabin width
    for rz in [-1.8, -0.9, 0.0, 0.9, 1.8]:
        mesh.add_box((0.0, wall_h - 0.08, rz), (cabin_w - 0.25, 0.16, 0.14), rot_y=0.0)

    # Ranger's Heavy Timber Work Desk (left wall)
    desk_x = -1.95
    desk_z = -0.75
    desk_top_y = f_h + 0.76
    mesh.add_box((desk_x, desk_top_y, desk_z), (1.65, 0.06, 0.95), rot_y=0.0)
    for lx in [desk_x - 0.72, desk_x + 0.72]:
        for lz in [desk_z - 0.38, desk_z + 0.38]:
            mesh.add_box((lx, f_h + 0.40, lz), (0.09, 0.74, 0.09), rot_y=0.0)
    # Desk drawer pedestal
    mesh.add_box((desk_x + 0.52, f_h + 0.40, desk_z), (0.42, 0.68, 0.85), rot_y=0.0)
    # Timber chair behind desk
    mesh.add_box((desk_x, f_h + 0.45, desk_z + 0.68), (0.46, 0.05, 0.46), rot_y=0.08)
    for cx in [desk_x - 0.18, desk_x + 0.18]:
        for cz in [desk_z + 0.50, desk_z + 0.86]:
            mesh.add_box((cx, f_h + 0.24, cz), (0.05, 0.44, 0.05), rot_y=0.08)
    mesh.add_box((desk_x, f_h + 0.78, desk_z + 0.88), (0.46, 0.64, 0.05), rot_y=0.08)

    # Field Cot (back right corner)
    cot_x = 1.95
    cot_z = 0.95
    mesh.add_box((cot_x, f_h + 0.36, cot_z), (0.95, 0.12, 2.15), rot_y=0.0)
    for clx in [cot_x - 0.42, cot_x + 0.42]:
        for clz in [cot_z - 0.95, cot_z + 0.95]:
            mesh.add_box((clx, f_h + 0.18, clz), (0.07, 0.36, 0.07), rot_y=0.0)

    # Wall Shelving Unit (rear wall)
    shelf_x = 0.0
    shelf_z = -half_d + 0.28
    for sy in [f_h + 1.1, f_h + 1.6, f_h + 2.1]:
        mesh.add_box((shelf_x, sy, shelf_z), (2.2, 0.05, 0.36), rot_y=0.0)
    mesh.add_box((shelf_x - 1.05, f_h + 1.6, shelf_z), (0.06, 1.1, 0.36), rot_y=0.0)
    mesh.add_box((shelf_x + 1.05, f_h + 1.6, shelf_z), (0.06, 1.1, 0.36), rot_y=0.0)

    # =========================================================================
    # 3. DIMENSIONAL CEDAR SHAKE SHINGLE ROOF & AWNING (usemtl Roof)
    # =========================================================================
    mesh.usemtl("Roof")

    r_w = half_w + roof_overhang
    r_d = half_d + roof_overhang
    roof_thick = 0.12

    # 3.1 Main Roof Slopes (Left and Right) with Thick Eaves and Fascia
    # Left slope (top deck and bottom soffit)
    mesh.add_quad(
        (-r_w, wall_h - 0.08,  r_d),
        (-r_w, wall_h - 0.08, -r_d),
        ( 0.0, roof_peak_h + 0.02, -r_d),
        ( 0.0, roof_peak_h + 0.02,  r_d)
    )
    # Left underside soffit
    mesh.add_quad(
        ( 0.0, roof_peak_h + 0.02 - roof_thick,  r_d),
        ( 0.0, roof_peak_h + 0.02 - roof_thick, -r_d),
        (-r_w, wall_h - 0.08 - roof_thick, -r_d),
        (-r_w, wall_h - 0.08 - roof_thick,  r_d)
    )
    # Left eave fascia board
    mesh.add_quad(
        (-r_w, wall_h - 0.08, -r_d),
        (-r_w, wall_h - 0.08,  r_d),
        (-r_w, wall_h - 0.08 - roof_thick,  r_d),
        (-r_w, wall_h - 0.08 - roof_thick, -r_d)
    )

    # Right slope (top deck and bottom soffit)
    mesh.add_quad(
        ( 0.0, roof_peak_h + 0.02,  r_d),
        ( 0.0, roof_peak_h + 0.02, -r_d),
        ( r_w, wall_h - 0.08, -r_d),
        ( r_w, wall_h - 0.08,  r_d)
    )
    # Right underside soffit
    mesh.add_quad(
        ( r_w, wall_h - 0.08 - roof_thick,  r_d),
        ( r_w, wall_h - 0.08 - roof_thick, -r_d),
        ( 0.0, roof_peak_h + 0.02 - roof_thick, -r_d),
        ( 0.0, roof_peak_h + 0.02 - roof_thick,  r_d)
    )
    # Right eave fascia board
    mesh.add_quad(
        ( r_w, wall_h - 0.08,  r_d),
        ( r_w, wall_h - 0.08, -r_d),
        ( r_w, wall_h - 0.08 - roof_thick, -r_d),
        ( r_w, wall_h - 0.08 - roof_thick,  r_d)
    )

    # Gable Barge Boards / Fascia Trim (Front and Back)
    for fz in [r_d, -r_d]:
        mesh.add_quad(
            (-r_w, wall_h - 0.08, fz),
            ( 0.0, roof_peak_h + 0.02, fz),
            ( 0.0, roof_peak_h + 0.02 - roof_thick, fz),
            (-r_w, wall_h - 0.08 - roof_thick, fz)
        )
        mesh.add_quad(
            ( 0.0, roof_peak_h + 0.02, fz),
            ( r_w, wall_h - 0.08, fz),
            ( r_w, wall_h - 0.08 - roof_thick, fz),
            ( 0.0, roof_peak_h + 0.02 - roof_thick, fz)
        )

    # Dimensional Stepped Cedar Shingle Courses (6 relief courses per slope)
    for c_idx in range(6):
        frac1 = float(c_idx) / 6.0
        frac2 = float(c_idx + 1) / 6.0
        # Left slope stepped courses
        x1 = -r_w + frac1 * r_w
        x2 = -r_w + frac2 * r_w
        y1 = (wall_h - 0.08) + frac1 * (roof_peak_h - wall_h + 0.1) + 0.02
        y2 = (wall_h - 0.08) + frac2 * (roof_peak_h - wall_h + 0.1) + 0.02
        mesh.add_box(((x1 + x2) * 0.5, (y1 + y2) * 0.5, 0.0), (abs(x2 - x1), 0.04, r_d * 2.02), rot_y=0.0)

        # Right slope stepped courses
        rx1 = r_w - frac1 * r_w
        rx2 = r_w - frac2 * r_w
        mesh.add_box(((rx1 + rx2) * 0.5, (y1 + y2) * 0.5, 0.0), (abs(rx2 - rx1), 0.04, r_d * 2.02), rot_y=0.0)

    # 3.2 Timber Porch Roof Awning (Shed Roof extending over porch deck)
    porch_roof_z_front = porch_z_front + 0.25
    mesh.add_quad(
        (-r_w * 0.95, 3.25, half_d - 0.1),
        ( r_w * 0.95, 3.25, half_d - 0.1),
        ( r_w * 0.95, 2.65, porch_roof_z_front),
        (-r_w * 0.95, 2.65, porch_roof_z_front)
    )
    # Porch awning fascia front edge
    mesh.add_quad(
        (-r_w * 0.95, 2.65, porch_roof_z_front),
        ( r_w * 0.95, 2.65, porch_roof_z_front),
        ( r_w * 0.95, 2.55, porch_roof_z_front),
        (-r_w * 0.95, 2.55, porch_roof_z_front)
    )

    # =========================================================================
    # 4. CAST-IRON CHIMNEY, HARDWARE & LANTERN SCONCE (usemtl Metal)
    # =========================================================================
    mesh.usemtl("Metal")

    # 4.1 Cast-Iron Woodstove Stovepipe Chimney
    chim_x = -1.8
    chim_z = -0.6
    chim_base_y = roof_peak_h - 0.4
    chim_top_y = roof_peak_h + 1.25

    # Flashing collar plate at roof penetration
    mesh.add_box((chim_x, chim_base_y + 0.08, chim_z), (0.42, 0.08, 0.42), rot_y=0.0)
    # Stovepipe flanged cylinder
    mesh.add_cylinder((chim_x, chim_base_y, chim_z), (chim_x, chim_top_y, chim_z), 0.13, 0.13, segs=12)
    # Clamp ring flange
    mesh.add_cylinder((chim_x, chim_base_y + 0.8, chim_z), (chim_x, chim_base_y + 0.86, chim_z), 0.15, 0.15, segs=10)
    # Chimney rain cap & spark arrestor hood
    mesh.add_cylinder((chim_x, chim_top_y, chim_z), (chim_x, chim_top_y + 0.14, chim_z), 0.24, 0.06, segs=10)
    # Chimney support struts to cap
    mesh.add_cylinder((chim_x - 0.10, chim_top_y - 0.05, chim_z), (chim_x - 0.10, chim_top_y + 0.05, chim_z), 0.015, 0.015, segs=4)
    mesh.add_cylinder((chim_x + 0.10, chim_top_y - 0.05, chim_z), (chim_x + 0.10, chim_top_y + 0.05, chim_z), 0.015, 0.015, segs=4)

    # 3 Steel Guy Wires anchoring chimney to roof deck
    gw_top = (chim_x, chim_top_y - 0.15, chim_z)
    mesh.add_cylinder(gw_top, (chim_x - 1.1, chim_base_y - 0.2, chim_z - 0.8), 0.008, 0.008, segs=4)
    mesh.add_cylinder(gw_top, (chim_x - 0.9, chim_base_y - 0.2, chim_z + 0.8), 0.008, 0.008, segs=4)
    mesh.add_cylinder(gw_top, (chim_x + 0.8, chim_base_y - 0.1, chim_z), 0.008, 0.008, segs=4)

    # 4.2 Forged Iron Door Strap Hinges and Heavy Latch
    mesh.add_box((-0.55, 1.85, half_d + 0.03), (0.48, 0.08, 0.02), rot_y=0.0)
    mesh.add_box((-0.55, 0.45, half_d + 0.03), (0.48, 0.08, 0.02), rot_y=0.0)
    # Hinge pin barrels
    mesh.add_cylinder((-0.74, 1.78, half_d + 0.04), (-0.74, 1.92, half_d + 0.04), 0.025, 0.025, segs=6)
    mesh.add_cylinder((-0.74, 0.38, half_d + 0.04), (-0.74, 0.52, half_d + 0.04), 0.025, 0.025, segs=6)
    # Latch bar and strike plate
    mesh.add_box((0.48, 1.15, half_d + 0.04), (0.12, 0.22, 0.04), rot_y=0.0)
    mesh.add_cylinder((0.48, 1.08, half_d + 0.05), (0.48, 1.02, half_d + 0.05), 0.02, 0.02, segs=4)

    # 4.3 Wall Lantern Housing & Arm Sconce (enclosing PorchLight at (0, 3.0, 3.4))
    mesh.add_cylinder((0.0, 2.75, half_d + 0.05), (0.0, 2.95, half_d + 0.38), 0.03, 0.03, segs=6)
    mesh.add_box((0.0, 3.0, half_d + 0.38), (0.24, 0.34, 0.24), rot_y=0.0)

    # 4.4 Walk-In Interior Metal Fixtures & Storytelling Props
    # Vintage Shortwave Radio Receiver on ranger desk (desk_x = -1.95, desk_top_y = f_h + 0.76, desk_z = -0.75)
    desk_x = -1.95
    desk_z = -0.75
    desk_top_y = f_h + 0.76
    # Metal radio chassis
    mesh.add_box((desk_x - 0.38, desk_top_y + 0.18, desk_z - 0.05), (0.54, 0.30, 0.34), rot_y=0.05)
    # Frequency dial & tuner knobs on faceplate
    mesh.add_box((desk_x - 0.38, desk_top_y + 0.18, desk_z + 0.13), (0.45, 0.20, 0.03), rot_y=0.05)
    # Telescopic whip antenna
    mesh.add_cylinder((desk_x - 0.58, desk_top_y + 0.32, desk_z - 0.15), (desk_x - 0.58, desk_top_y + 1.15, desk_z - 0.15), 0.012, 0.005, segs=6)
    # Microphone handset on cradle
    mesh.add_box((desk_x - 0.02, desk_top_y + 0.08, desk_z + 0.15), (0.10, 0.12, 0.10), rot_y=0.2)

    # Cast-Iron Potbelly Woodstove (front-right cabin corner)
    stove_x = 1.95
    stove_z = -1.1
    # Heavy hearth base plate
    mesh.add_box((stove_x, f_h + 0.04, stove_z), (0.90, 0.04, 0.90), rot_y=0.0)
    # Cylindrical belly
    mesh.add_cylinder((stove_x, f_h + 0.16, stove_z), (stove_x, f_h + 0.92, stove_z), 0.34, 0.38, segs=12)
    # Cast-iron fire door with draft vents
    mesh.add_box((stove_x - 0.28, f_h + 0.55, stove_z), (0.05, 0.32, 0.28), rot_y=0.0)
    # 4 curved stove feet
    for sfx in [-0.28, 0.28]:
        for sfz in [-0.28, 0.28]:
            mesh.add_cylinder((stove_x + sfx, f_h + 0.04, stove_z + sfz), (stove_x + sfx * 0.7, f_h + 0.16, stove_z + sfz * 0.7), 0.04, 0.05, segs=6)
    # Interior stovepipe connecting upward through ceiling
    mesh.add_cylinder((stove_x, f_h + 0.92, stove_z), (stove_x, wall_h - 0.05, stove_z), 0.11, 0.11, segs=10)

    # Center hanging rafter lantern fixture (at (0, 2.2, 0))
    mesh.add_cylinder((0.0, wall_h - 0.08, 0.0), (0.0, 2.35, 0.0), 0.012, 0.012, segs=4)
    mesh.add_box((0.0, 2.22, 0.0), (0.22, 0.28, 0.22), rot_y=0.0)

    # Canned food rations and emergency kerosene cans on shelving
    shelf_z = -half_d + 0.28
    for cx in [-0.6, -0.3, 0.0, 0.3, 0.6]:
        mesh.add_cylinder((cx, f_h + 1.13, shelf_z), (cx, f_h + 1.35, shelf_z), 0.065, 0.065, segs=8)
    mesh.add_box((0.7, f_h + 1.76, shelf_z), (0.24, 0.30, 0.22), rot_y=0.0)

    # 4.5 Wool Blanket on Field Cot (usemtl Stone for rough fabric texture)
    mesh.usemtl("Stone")
    cot_x = 1.95
    cot_z = 0.95
    mesh.add_box((cot_x, f_h + 0.50, cot_z - 0.55), (0.78, 0.20, 0.85), rot_y=0.0)


    # =========================================================================
    # 5. WINDOW GLASS PANES (usemtl Glass)
    # =========================================================================
    mesh.usemtl("Glass")
    for wx in [-half_w, half_w]:
        mesh.add_box((wx, 1.75, 0.0), (0.02, 0.94, 1.30), rot_y=0.0)

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
    Overhauled Anatomical Mutilated Cervid Carcass (700lb Bull Elk):
    - Full anatomical animal body mass collapsed on its flank
    - Dark brown shaggy elk pelt/hide draped over haunches, neck, and shoulders
    - Torn hide flaps peeled back with jagged ripped margins
    - Shredded dark red muscle walls, sinew, and intercostal muscle
    - Catastrophic skeletal trauma: 16-segment dislocated spine, pried-apart
      thoracic ribcage with shattered compound fractures and exposed bone marrow
    - Massive 6-point branching antlers with velvet peels, skull, and mandible
    - Spilled viscera: looping tubular intestines and torn thoracic organs
    - Cloven hooves, compound fractured foreleg, and sprawling hindquarters
    """
    mesh = ObjMesh("elk_carcass")

    # =========================================================================
    # 1. ELK PELT & ANATOMICAL BODY MASS (usemtl Pelt)
    # =========================================================================
    mesh.usemtl("Pelt")

    # 1.1 Massive Collapsed Torso & Haunches
    # Heavy rear haunch (pelvis & rump)
    mesh.add_ellipsoid((0.75, 0.28, 0.05), (0.50, 0.32, 0.40), segs_u=14, segs_v=10, rot_y=-0.1)
    # Flank / abdomen belly mass (lower portion resting on ground)
    mesh.add_ellipsoid((0.10, 0.22, 0.02), (0.54, 0.26, 0.42), segs_u=14, segs_v=10, rot_y=0.05)
    # Heavy front shoulder girdle & withers
    mesh.add_ellipsoid((-0.55, 0.32, 0.08), (0.50, 0.34, 0.38), segs_u=14, segs_v=10, rot_y=0.15)

    # 1.2 Muscular Cervid Neck & Mane
    # Thick neck tube sweeping forward and twisting slightly toward the ground
    neck_pts = [
        ((-0.55, 0.32, 0.08), (0.28, 0.24)),
        ((-0.80, 0.28, 0.12), (0.26, 0.22)),
        ((-1.05, 0.24, 0.16), (0.23, 0.20)),
        ((-1.32, 0.18, 0.20), (0.20, 0.16))   # Base of skull
    ]
    mesh.add_tapered_tube(neck_pts, segs=12, u_scale=2.0, v_scale=2.0)

    # Shaggy dorsal neck mane fur ridges
    for mx, my, mz in [(-0.65, 0.44, 0.08), (-0.85, 0.40, 0.12), (-1.05, 0.35, 0.15)]:
        mesh.add_ellipsoid((mx, my, mz), (0.14, 0.09, 0.12), segs_u=8, segs_v=6)

    # 1.3 Elk Head (Furred Skull Cap, Snout, Muzzle, Ears)
    # Cranium (furred braincase)
    mesh.add_ellipsoid((-1.36, 0.22, 0.20), (0.20, 0.15, 0.17), segs_u=12, segs_v=8, rot_y=0.2)
    # Long cervid muzzle & bridge
    muzzle_pts = [
        ((-1.36, 0.20, 0.20), 0.14),
        ((-1.55, 0.16, 0.22), 0.11),
        ((-1.75, 0.12, 0.24), 0.075)  # Black leathery nose pad
    ]
    mesh.add_tapered_tube(muzzle_pts, segs=10)
    # Black nose pad
    mesh.add_ellipsoid((-1.76, 0.12, 0.24), (0.05, 0.04, 0.06), segs_u=8, segs_v=6)

    # Pinned back cervid ears (lying flat against the furred neck)
    # Left ear
    ear_l = [((-1.28, 0.30, 0.12), 0.06), ((-1.18, 0.32, 0.08), 0.04), ((-1.08, 0.33, 0.05), 0.015)]
    mesh.add_tapered_tube(ear_l, segs=6)
    # Right ear
    ear_r = [((-1.32, 0.28, 0.28), 0.06), ((-1.22, 0.29, 0.32), 0.04), ((-1.12, 0.30, 0.35), 0.015)]
    mesh.add_tapered_tube(ear_r, segs=6)

    # 1.4 Limbs & Cloven Hooves
    # Left Hind Leg: Sprawled backward askew
    mesh.add_cylinder((0.85, 0.24, 0.20), (1.25, 0.20, 0.38), 0.16, 0.11, segs=8)  # Thigh
    mesh.add_cylinder((1.25, 0.20, 0.38), (1.60, 0.10, 0.52), 0.11, 0.07, segs=8)  # Cannon bone / hock
    # Cloven dark hoof
    mesh.add_box((1.68, 0.05, 0.56), (0.13, 0.08, 0.09), rot_y=-0.35)

    # Left Foreleg: Compound fracture - torn upper limb and dangling broken shaft
    mesh.add_cylinder((-0.55, 0.28, -0.18), (-0.85, 0.22, -0.42), 0.14, 0.09, segs=8) # Upper arm
    mesh.add_cylinder((-0.88, 0.16, -0.48), (-1.18, 0.08, -0.68), 0.08, 0.05, segs=6) # Broken dangling forearm
    mesh.add_box((-1.24, 0.04, -0.74), (0.12, 0.07, 0.08), rot_y=0.45) # Hoof

    # 1.5 Torn Hide Flaps & Shredded Skin Borders (folded back to expose raw muscle)
    hide_flaps = [
        # (p1, p2, p3, p4) peeled back skin tags
        ((-0.45, 0.36, -0.05), (-0.35, 0.38, -0.15), (-0.25, 0.22, -0.22), (-0.35, 0.20, -0.10)),
        ((-0.20, 0.38, -0.08), (-0.05, 0.40, -0.18), ( 0.05, 0.24, -0.25), (-0.10, 0.22, -0.12)),
        (( 0.10, 0.36, -0.05), ( 0.25, 0.38, -0.15), ( 0.35, 0.20, -0.22), ( 0.20, 0.18, -0.10)),
        (( 0.40, 0.34, -0.02), ( 0.55, 0.35, -0.12), ( 0.62, 0.18, -0.18), ( 0.48, 0.16, -0.06)),
        # Flaps on abdominal/haunch side
        ((-0.30, 0.35, 0.18), (-0.20, 0.36, 0.32), (-0.15, 0.18, 0.38), (-0.25, 0.16, 0.24)),
        (( 0.05, 0.33, 0.16), ( 0.18, 0.34, 0.30), ( 0.25, 0.16, 0.36), ( 0.12, 0.15, 0.22))
    ]
    for p1, p2, p3, p4 in hide_flaps:
        mesh.add_quad(p1, p2, p3, p4)

    # =========================================================================
    # 2. RAW FLESH, STRIATED MUSCLE & SINEW (usemtl Flesh)
    # =========================================================================
    mesh.usemtl("Flesh")

    # 2.1 Internal Raw Muscle Lining of Torn Cavity
    # Deep red intercostal and abdominal muscle walls
    mesh.add_ellipsoid((-0.05, 0.18, -0.02), (0.62, 0.18, 0.32), segs_u=12, segs_v=8)
    mesh.add_ellipsoid((-0.45, 0.24, -0.05), (0.35, 0.16, 0.25), segs_u=10, segs_v=6)
    mesh.add_ellipsoid(( 0.42, 0.22,  0.00), (0.38, 0.18, 0.28), segs_u=10, segs_v=6)

    # Torn visceral thoracic organ masses (collapsed lung tissue & dark liver lobe)
    mesh.add_ellipsoid((-0.25, 0.16, -0.04), (0.24, 0.12, 0.18), segs_u=10, segs_v=6)
    mesh.add_ellipsoid(( 0.15, 0.14, -0.06), (0.22, 0.11, 0.16), segs_u=10, segs_v=6)

    # 2.2 Shredded Muscle Tendons & Hanging Sinew Strands
    sinew_strands = [
        ((-0.42, 0.32, -0.18), (-0.46, 0.10, -0.28), 0.022, 0.006),
        ((-0.22, 0.36, -0.22), (-0.20, 0.08, -0.35), 0.020, 0.005),
        (( 0.02, 0.34, -0.24), ( 0.06, 0.06, -0.38), 0.024, 0.007),
        (( 0.24, 0.30, -0.20), ( 0.30, 0.08, -0.32), 0.018, 0.005),
        ((-0.72, 0.26, -0.32), (-0.82, 0.06, -0.42), 0.025, 0.008),
        (( 0.65, 0.26,  0.15), ( 0.85, 0.05,  0.28), 0.022, 0.007)
    ]
    for sp1, sp2, sr1, sr2 in sinew_strands:
        mesh.add_cylinder(sp1, sp2, sr1, sr2, segs=6)

    # =========================================================================
    # 3. SKELETON, PRIED RIBCAGE & ANTLERS (usemtl Bone)
    # =========================================================================
    mesh.usemtl("Bone")

    # 3.1 16-Segment Curved Spine with Catastrophic Traumatic Dislocation
    spine_x = [-1.25, -1.10, -0.95, -0.80, -0.65, -0.50, -0.35, -0.20, -0.05, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    spine_pts = []
    for idx, sx in enumerate(spine_x):
        # Traumatic dislocation at index 7-9 (snapped backward)
        disloc_y = 0.08 if 6 <= idx <= 9 else 0.0
        disloc_z = -0.08 if 6 <= idx <= 9 else 0.0
        sy = 0.22 + 0.14 * math.sin(float(idx) / len(spine_x) * math.pi) + disloc_y
        sz = 0.04 * math.cos(float(idx) / len(spine_x) * math.pi) + disloc_z
        spine_pts.append((sx, sy, sz))

    for i in range(len(spine_pts)-1):
        mesh.add_cylinder(spine_pts[i], spine_pts[i+1], 0.055, 0.055, segs=8)
        # Spinous dorsal processes
        top_p = (spine_pts[i][0], spine_pts[i][1] + 0.12, spine_pts[i][2])
        mesh.add_cylinder(spine_pts[i], top_p, 0.024, 0.010, segs=6)

    # 3.2 Shattered Thoracic Ribcage (10 anatomical rib pairs)
    for idx in range(3, 13):
        rx = spine_pts[idx][0]
        ry = spine_pts[idx][1]
        rib_w = 0.38 + 0.16 * math.sin((idx - 3) / 10.0 * math.pi)
        
        # Lower right ribs (resting curved in the gore pool)
        r_mid = (rx, ry - 0.08, rib_w * 0.65)
        r_tip = (rx, 0.03, rib_w * 0.95)
        mesh.add_cylinder((rx, ry, 0.0), r_mid, 0.022, 0.018, segs=6)
        mesh.add_cylinder(r_mid, r_tip, 0.018, 0.012, segs=6)

        # Upper left ribs: Pried apart, shattered outward by cryptid claws
        if idx in [5, 6, 7, 8]:
            # Jagged compound breaks pointing upward with exposed marrow hollows
            l_mid = (rx + 0.04, ry + 0.22, -rib_w * 0.70)
            l_tip = (rx + 0.08, ry + 0.45, -rib_w * 1.05)
            mesh.add_cylinder((rx, ry, 0.0), l_mid, 0.024, 0.018, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.018, 0.008, segs=6)
            # Splintered bone shards
            mesh.add_cylinder(l_tip, (l_tip[0] + 0.04, l_tip[1] + 0.08, l_tip[2] - 0.03), 0.007, 0.002, segs=4)
        else:
            l_mid = (rx, ry + 0.10, -rib_w * 0.60)
            l_tip = (rx, 0.05, -rib_w * 0.90)
            mesh.add_cylinder((rx, ry, 0.0), l_mid, 0.020, 0.016, segs=6)
            mesh.add_cylinder(l_mid, l_tip, 0.016, 0.010, segs=6)

    # 3.3 Compound Fracture Leg Bone Protrusions
    # Exposed shattered radius/ulna sticking out of left foreleg
    mesh.add_cylinder((-0.82, 0.20, -0.40), (-0.98, 0.16, -0.52), 0.028, 0.014, segs=6)
    # Shattered pelvis crest bone plate
    mesh.add_box((0.92, 0.30, -0.08), (0.22, 0.14, 0.06), rot_y=0.25)

    # 3.4 Skull Zygomatic Plate & Mandible with Molar Dentition
    # Mandible lying askew in the gore
    mesh.add_cylinder((-1.36, 0.12, 0.26), (-1.72, 0.06, 0.30), 0.055, 0.025, segs=6)
    # Molars along mandible
    for mx in [-1.45, -1.52, -1.59, -1.66]:
        mesh.add_box((mx, 0.11, 0.28), (0.025, 0.025, 0.020), rot_y=0.1)

    # 3.5 Magnificent 6-Point Branching Antlers with Velvet Strips
    def add_antler(side=1.0):
        # Base burr / coronet at pedicle
        p_base = (-1.38, 0.30, 0.20 + side * 0.12)
        p1 = (-1.42, 0.52, 0.20 + side * 0.34)
        p2 = (-1.35, 0.80, 0.20 + side * 0.54)
        p3 = (-1.16, 1.04, 0.20 + side * 0.60)
        p4 = (-0.88, 1.15, 0.20 + side * 0.52)
        mesh.add_cylinder(p_base, p1, 0.052, 0.042, segs=8)
        mesh.add_cylinder(p1, p2, 0.042, 0.032, segs=8)
        mesh.add_cylinder(p2, p3, 0.032, 0.024, segs=6)
        mesh.add_cylinder(p3, p4, 0.024, 0.012, segs=6)

        # Brow tine (eyeguard) pointing forward over the eyes
        mesh.add_cylinder(p1, (-1.70, 0.50, 0.20 + side * 0.26), 0.030, 0.010, segs=6)
        # Bay / Bez tine pointing forward-up
        mesh.add_cylinder(p2, (-1.55, 0.78, 0.20 + side * 0.46), 0.026, 0.009, segs=6)
        # Royal tine branching upward at mid-beam
        mesh.add_cylinder(p3, (-1.12, 1.28, 0.20 + side * 0.58), 0.024, 0.008, segs=6)
        # Crown / terminal fork tine
        mesh.add_cylinder(p4, (-0.72, 1.22, 0.20 + side * 0.44), 0.016, 0.006, segs=6)

    add_antler(1.0)
    add_antler(-1.0)

    # =========================================================================
    # 4. SPILLED VISCERA, INTESTINES & COAGULATED GORE (usemtl Gore)
    # =========================================================================
    mesh.usemtl("Gore")

    # 4.1 Spilled Intestinal Loops (convoluted winding tubular coils spilling onto ground)
    gut_points = [
        ( 0.05, 0.16, -0.05),
        ( 0.12, 0.12, -0.15),
        ( 0.22, 0.08, -0.22),
        ( 0.15, 0.05, -0.32),
        ( 0.02, 0.04, -0.26),
        (-0.08, 0.04, -0.34),
        (-0.02, 0.05, -0.42),
        ( 0.12, 0.05, -0.44),
        ( 0.26, 0.06, -0.38),
        ( 0.38, 0.05, -0.45),
        ( 0.46, 0.04, -0.35),
        ( 0.35, 0.04, -0.25),
        ( 0.28, 0.06, -0.16),
        ( 0.36, 0.05, -0.08),
        ( 0.48, 0.04, -0.14)
    ]
    gut_pts_radii = [(p, 0.034) for p in gut_points]
    mesh.add_tapered_tube(gut_pts_radii, segs=8, u_scale=1.0, v_scale=4.0)

    # Second winding intestine loop
    gut_points2 = [
        ( 0.20, 0.14,  0.08),
        ( 0.32, 0.10,  0.18),
        ( 0.45, 0.06,  0.24),
        ( 0.52, 0.04,  0.16),
        ( 0.42, 0.04,  0.08),
        ( 0.50, 0.04,  0.02),
        ( 0.60, 0.03,  0.08)
    ]
    gut_pts_radii2 = [(p, 0.030) for p in gut_points2]
    mesh.add_tapered_tube(gut_pts_radii2, segs=8, u_scale=1.0, v_scale=2.0)

    # 4.2 Thick Coagulated Clot Mound Inside Cavity Floor
    mesh.add_ellipsoid((-0.08, 0.08, -0.05), (0.45, 0.06, 0.28), segs_u=10, segs_v=6)

    # 4.3 Bloody Velvet Strips Peeling from Antlers
    mesh.add_cylinder((-1.35, 0.80, 0.54), (-1.38, 0.62, 0.56), 0.015, 0.005, segs=4)
    mesh.add_cylinder((-1.16, 1.04, 0.60), (-1.18, 0.86, 0.62), 0.012, 0.004, segs=4)
    mesh.add_cylinder((-1.35, 0.80, -0.14), (-1.38, 0.62, -0.16), 0.015, 0.005, segs=4)

    mesh.save("assets/models/elk_carcass.obj", mat_order=["Pelt", "Flesh", "Bone", "Gore"])


def generate_carcass_gore_pool():
    """
    Multi-tiered organic coagulated gore splatter pool decal:
    - Tier 1: Thick coagulated central gore mound (raised viscous clots)
    - Tier 2: Wide irregular spreading blood pool with lobed fingers
    - Tier 3: Radiating satellite arterial spray droplets & directional drag streaks
    """
    mesh = ObjMesh("carcass_gore_pool")
    mesh.usemtl("Gore")

    # 1. Tier 1: Thick Coagulated Central Gore Mound (Y = 0.012m)
    c1 = (0.05, 0.012, -0.10)
    c1_idx = mesh.add_v(c1[0], c1[1], c1[2])
    c1_vn = mesh.add_vn(0, 1, 0)
    c1_vt = mesh.add_vt(0.5, 0.5)

    n_mound = 24
    mound_radii = [
        1.1, 0.9, 1.3, 1.5, 1.2, 0.8, 1.4, 1.6,
        1.3, 1.0, 1.5, 1.7, 1.4, 0.9, 1.3, 1.6,
        1.2, 0.9, 1.4, 1.5, 1.1, 0.8, 1.2, 1.4
    ]
    mound_v = []
    mound_vn = []
    mound_vt = []
    for i in range(n_mound):
        angle = 2.0 * math.pi * i / n_mound
        r = mound_radii[i] * 0.75
        px = c1[0] + math.cos(angle) * r * 1.35
        pz = c1[2] + math.sin(angle) * r * 0.85
        mound_v.append(mesh.add_v(px, 0.008, pz))
        mound_vn.append(mesh.add_vn(0, 1, 0))
        mound_vt.append(mesh.add_vt(0.5 + px * 0.25, 0.5 + pz * 0.25))

    for i in range(n_mound):
        nxt = (i + 1) % n_mound
        mesh.add_face([c1_idx, mound_v[i], mound_v[nxt]],
                      [c1_vn, mound_vn[i], mound_vn[nxt]],
                      [c1_vt, mound_vt[i], mound_vt[nxt]])

    # 2. Tier 2: Sprawling Viscous Base Pool (Y = 0.004m, 36 lobes)
    c2 = (0.0, 0.004, 0.0)
    c2_idx = mesh.add_v(c2[0], c2[1], c2[2])
    c2_vn = mesh.add_vn(0, 1, 0)
    c2_vt = mesh.add_vt(0.5, 0.5)

    n_pts = 36
    radii_base = [
        1.6, 2.1, 1.4, 1.0, 1.8, 2.5, 2.0, 1.3,
        0.9, 1.7, 2.3, 1.5, 1.1, 2.0, 2.8, 2.2,
        1.5, 1.0, 1.8, 2.4, 1.9, 1.3, 0.9, 1.5,
        2.0, 2.7, 1.8, 1.2, 1.6, 2.2, 1.6, 1.1,
        1.7, 2.3, 1.5, 1.2
    ]
    outer_v = []
    outer_vn = []
    outer_vt = []
    for i in range(n_pts):
        angle = 2.0 * math.pi * i / n_pts
        r = radii_base[i] * 0.95
        px = math.cos(angle) * r * 1.50
        pz = math.sin(angle) * r * 0.95
        outer_v.append(mesh.add_v(px, 0.004, pz))
        outer_vn.append(mesh.add_vn(0, 1, 0))
        outer_vt.append(mesh.add_vt(0.5 + px * 0.18, 0.5 + pz * 0.18))

    for i in range(n_pts):
        nxt = (i + 1) % n_pts
        mesh.add_face([c2_idx, outer_v[i], outer_v[nxt]],
                      [c2_vn, outer_vn[i], outer_vn[nxt]],
                      [c2_vt, outer_vt[i], outer_vt[nxt]])

    # 3. Tier 3: Directional Drag Streaks (where carcass was thrashed/dragged)
    drag_streaks = [
        ((-0.8, -0.6), (-2.2, -1.2), 0.35),
        (( 0.6, -0.5), ( 2.4, -0.9), 0.40),
        ((-0.2,  0.8), (-0.6,  2.2), 0.32)
    ]
    for (sx, sz), (ex, ez), width in drag_streaks:
        dx, dz = ex - sx, ez - sz
        dl = math.sqrt(dx*dx + dz*dz)
        if dl > 0.001:
            px, pz = -dz / dl * width * 0.5, dx / dl * width * 0.5
            mesh.add_quad(
                (sx + px, 0.005, sz + pz),
                (ex + px * 0.6, 0.005, ez + pz * 0.6),
                (ex - px * 0.6, 0.005, ez - pz * 0.6),
                (sx - px, 0.005, sz - pz)
            )

    # 4. Radiating Arterial Spray Droplets & Satellite Splatters (14 droplets)
    splatters = [
        (-2.4, -1.2, 0.35),
        (-1.8,  1.4, 0.42),
        ( 2.5, -1.1, 0.38),
        ( 2.1,  1.3, 0.44),
        (-1.1, -1.8, 0.30),
        ( 0.8,  1.9, 0.32),
        (-3.1, -0.4, 0.25),
        ( 3.0,  0.2, 0.28),
        (-1.5, -2.2, 0.22),
        ( 1.4, -1.7, 0.26),
        ( 1.9, -2.0, 0.20),
        (-2.6,  0.8, 0.24),
        ( 0.2, -2.4, 0.22),
        ( 2.7,  1.8, 0.26)
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
                          [c2_vn, c2_vn, c2_vn],
                          [c2_vt, c2_vt, c2_vt])

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


def generate_document_and_evidence_props():
    """
    Generates high-realism 3D props for Phase 2 investigation storytelling:
    - prop_evacuation_notice.obj: Plywood clipboard with iron spring clip and USFS order.
    - prop_field_journal.obj: Open leather-bound journal with warden's log and sketches.
    - prop_topomap.obj: Framed district survey quadrangle map.
    - prop_plaster_footprint.obj: Plaster forensic cast showing 18.5" cryptid track.
    - prop_evidence_jar.obj: Glass specimen jar containing coarse cryptid hair clump.
    - prop_rifle_casings.obj: Ejected brass .30-06 cartridges.
    """
    os.makedirs("assets/models", exist_ok=True)

    # 1. USFS Evacuation Notice Clipboard
    cb = ObjMesh("prop_evacuation_notice")
    cb.usemtl("Wood")
    # Plywood backing board (width 0.48, height 0.68, thickness 0.02)
    cb.add_box((0.0, 0.0, 0.0), (0.48, 0.68, 0.02), rot_y=0.0)
    # Beveled edges
    cb.add_box((0.0, 0.34, 0.0), (0.46, 0.015, 0.018), rot_y=0.0)
    cb.add_box((0.0, -0.34, 0.0), (0.46, 0.015, 0.018), rot_y=0.0)

    cb.usemtl("Metal")
    # Iron spring clip at top
    cb.add_box((0.0, 0.28, 0.025), (0.22, 0.065, 0.03), rot_y=0.0)
    # Clip lever wire & rivet
    cb.add_cylinder((-0.08, 0.31, 0.035), (0.08, 0.31, 0.035), 0.008, 0.008, segs=6)
    cb.add_cylinder((0.0, 0.32, 0.015), (0.0, 0.35, 0.015), 0.012, 0.012, segs=6)

    cb.usemtl("Paper")
    # Paper sheet quad mapped to USFS texture
    pw, ph = 0.40, 0.58
    pz = 0.012
    v1 = cb.add_v(-pw * 0.5, -ph * 0.5, pz)
    v2 = cb.add_v( pw * 0.5, -ph * 0.5, pz)
    v3 = cb.add_v( pw * 0.5,  ph * 0.5, pz)
    v4 = cb.add_v(-pw * 0.5,  ph * 0.5, pz)
    vn = cb.add_vn(0.0, 0.0, 1.0)
    vt1 = cb.add_vt(0.0, 0.0)
    vt2 = cb.add_vt(1.0, 0.0)
    vt3 = cb.add_vt(1.0, 1.0)
    vt4 = cb.add_vt(0.0, 1.0)
    cb.add_face([v1, v2, v3, v4], [vn, vn, vn, vn], [vt1, vt2, vt3, vt4])
    cb.save("assets/models/prop_evacuation_notice.obj", mat_order=["Wood", "Metal", "Paper"])

    # 2. Open Field Journal
    fj = ObjMesh("prop_field_journal")
    fj.usemtl("Wood")
    # Leather cover backboard
    fj.add_box((0.0, 0.01, 0.0), (0.52, 0.025, 0.38), rot_y=0.0)
    # Center spine ridge
    fj.add_cylinder((0.0, 0.01, -0.19), (0.0, 0.01, 0.19), 0.02, 0.02, segs=6)

    fj.usemtl("Paper")
    # Left and right pages open
    jw, jh = 0.48, 0.34
    jy = 0.024
    jv1 = fj.add_v(-jw * 0.5, jy,  jh * 0.5)
    jv2 = fj.add_v( jw * 0.5, jy,  jh * 0.5)
    jv3 = fj.add_v( jw * 0.5, jy, -jh * 0.5)
    jv4 = fj.add_v(-jw * 0.5, jy, -jh * 0.5)
    jvn = fj.add_vn(0.0, 1.0, 0.0)
    jvt1 = fj.add_vt(0.0, 0.0)
    jvt2 = fj.add_vt(1.0, 0.0)
    jvt3 = fj.add_vt(1.0, 1.0)
    jvt4 = fj.add_vt(0.0, 1.0)
    fj.add_face([jv1, jv2, jv3, jv4], [jvn, jvn, jvn, jvn], [jvt1, jvt2, jvt3, jvt4])
    fj.save("assets/models/prop_field_journal.obj", mat_order=["Wood", "Paper"])

    # 3. Framed District Topographic Map
    tm = ObjMesh("prop_topomap")
    tm.usemtl("Wood")
    # Timber frame
    tm.add_box((0.0, 0.0, 0.0), (1.36, 1.02, 0.04), rot_y=0.0)

    tm.usemtl("Paper")
    mw, mh = 1.24, 0.90
    mz = 0.022
    mv1 = tm.add_v(-mw * 0.5, -mh * 0.5, mz)
    mv2 = tm.add_v( mw * 0.5, -mh * 0.5, mz)
    mv3 = tm.add_v( mw * 0.5,  mh * 0.5, mz)
    mv4 = tm.add_v(-mw * 0.5,  mh * 0.5, mz)
    mvn = tm.add_vn(0.0, 0.0, 1.0)
    mvt1 = tm.add_vt(0.0, 0.0)
    mvt2 = tm.add_vt(1.0, 0.0)
    mvt3 = tm.add_vt(1.0, 1.0)
    mvt4 = tm.add_vt(0.0, 1.0)
    tm.add_face([mv1, mv2, mv3, mv4], [mvn, mvn, mvn, mvn], [mvt1, mvt2, mvt3, mvt4])
    tm.save("assets/models/prop_topomap.obj", mat_order=["Wood", "Paper"])


    # 4. Forensic Plaster Footprint Cast
    pf = ObjMesh("prop_plaster_footprint")
    pf.usemtl("Stone")
    # Heavy rectangular plaster slab
    pf.add_box((0.0, 0.04, 0.0), (0.58, 0.08, 0.34), rot_y=0.0)
    # Excavated depression of 18.5" hominid footprint
    # Sole hollow
    pf.add_ellipsoid((0.0, 0.065, -0.02), (0.13, 0.025, 0.22), segs_u=12, segs_v=8)
    pf.add_ellipsoid((0.0, 0.065,  0.09), (0.11, 0.022, 0.09), segs_u=10, segs_v=6)
    # 5 deep toe impressions
    for ti in range(5):
        tx = -0.09 + ti * 0.045
        tz = -0.11 - abs(ti - 2) * 0.008
        pf.add_ellipsoid((tx, 0.072, tz), (0.018, 0.016, 0.025), segs_u=8, segs_v=6)
    pf.save("assets/models/prop_plaster_footprint.obj", mat_order=["Stone"])

    # 5. Cryptid Hair Specimen Jar
    ej = ObjMesh("prop_evidence_jar")
    ej.usemtl("Glass")
    # Cylindrical glass jar
    ej.add_cylinder((0.0, 0.01, 0.0), (0.0, 0.20, 0.0), 0.075, 0.075, segs=12)

    ej.usemtl("Metal")
    # Threaded tin screw-on lid
    ej.add_cylinder((0.0, 0.19, 0.0), (0.0, 0.225, 0.0), 0.08, 0.08, segs=12)

    ej.usemtl("Fur")
    # Coarse dark clump of hair strands suspended inside
    ej.add_ellipsoid((0.0, 0.09, 0.0), (0.045, 0.06, 0.045), segs_u=10, segs_v=8)
    ej.save("assets/models/prop_evidence_jar.obj", mat_order=["Glass", "Metal", "Fur"])

    # 6. Spent Rifle Casings (.30-06)
    rc = ObjMesh("prop_rifle_casings")
    rc.usemtl("Metal")
    casings = [
        (( 0.00, 0.015,  0.00), ( 0.08, 0.015,  0.03)),
        ((-0.06, 0.015,  0.05), (-0.02, 0.015,  0.13)),
        (( 0.05, 0.015, -0.06), ( 0.12, 0.015, -0.02))
    ]
    for p1, p2 in casings:
        rc.add_cylinder(p1, p2, 0.014, 0.014, segs=8)
        # Extractor groove
        rc.add_cylinder(p1, (p1[0]*0.9+p2[0]*0.1, p1[1], p1[2]*0.9+p2[2]*0.1), 0.012, 0.012, segs=8)
    rc.save("assets/models/prop_rifle_casings.obj", mat_order=["Metal"])
    print("Investigation and storytelling evidence props generated successfully.")


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
    generate_document_and_evidence_props()
    print("All models generated successfully!")

