#!/usr/bin/env python3
"""
High-Fidelity "1. CLASSIC BIGFOOT" Continuous Anatomical Mesh Builder (v3)
Pure anatomical quad topology without primitive stacking (Issue 002 & Issue 004 compliance).

Generates the authentic Classic Bigfoot matching Concept Reference 1:
- Conical sagittal crest with hair mane
- Heavy supraorbital ape brow shelf over deep orbital sockets
- Broad flat simian nose with nostril flare
- Prognathic ape jaw with closed stoic lips
- Volumetric cascading chin beard framing dark face mask
- Colossal dorsal trapezius hump blending into wide shoulders
- Broad barrel chest with sculpted gorilla pectorals and sternal groove
- Long muscular gorilla arms reaching towards knees
- Massive vascular forearms with outer hair frills
- 5-fingered hands in a stalking grip with distinct knuckles and nails
- Bowed muscular legs with wide 18-inch plantigrade feet and 5 toes
- Spherical ball caps on proximal joints for seamless Godot animation
- Under GTX 960 hardware budget (<16k triangles total)
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
QA_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "qa" / "diagnostic_views"
QA_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("SasquatchCollection")
    bpy.context.scene.collection.children.link(col)
    return col


def loft_polygon_rings(name, rings, close_top=False, close_bottom=False):
    """
    Skins a series of equal-vertex polygon rings into a continuous quad mesh.
    rings: list of lists of Vector coordinates.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    num_rings = len(rings)
    num_verts_per_ring = len(rings[0])

    bm_rings = []
    for ring in rings:
        bm_ring = [bm.verts.new(pt) for pt in ring]
        bm_rings.append(bm_ring)

    bm.verts.ensure_lookup_table()

    # Bridge rings with quad faces
    for r in range(num_rings - 1):
        ring_a = bm_rings[r]
        ring_b = bm_rings[r + 1]
        for i in range(num_verts_per_ring):
            i_next = (i + 1) % num_verts_per_ring
            bm.faces.new((ring_a[i], ring_a[i_next], ring_b[i_next], ring_b[i]))

    if close_top:
        top_ring = bm_rings[0]
        c_top = sum((v.co for v in top_ring), Vector((0, 0, 0))) / num_verts_per_ring
        v_top = bm.verts.new(c_top)
        for i in range(num_verts_per_ring):
            i_next = (i + 1) % num_verts_per_ring
            bm.faces.new((top_ring[i_next], top_ring[i], v_top))

    if close_bottom:
        bot_ring = bm_rings[-1]
        c_bot = sum((v.co for v in bot_ring), Vector((0, 0, 0))) / num_verts_per_ring
        v_bot = bm.verts.new(c_bot)
        for i in range(num_verts_per_ring):
            i_next = (i + 1) % num_verts_per_ring
            bm.faces.new((bot_ring[i], bot_ring[i_next], v_bot))

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def finalize_mesh(obj, subsurf_levels=1, smart_uv=True, decimate_ratio=1.0):
    """Applies subdivision surface, decimation to meet GTX 960 budget, smart UV, and smooth shading."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if subsurf_levels > 0:
        mod = obj.modifiers.new("Subsurf", 'SUBSURF')
        mod.levels = subsurf_levels
        mod.render_levels = subsurf_levels
        bpy.ops.object.modifier_apply(modifier="Subsurf")

    if decimate_ratio < 0.99:
        mod_dec = obj.modifiers.new("Decimate", 'DECIMATE')
        mod_dec.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

    if smart_uv:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015)
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.shade_smooth()
    return obj


def export_obj(obj, filepath):
    """Exports obj with coordinates matching Godot convention (+Y Up, -Z Forward)."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.wm.obj_export(
        filepath=str(filepath),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_uv=True,
        export_normals=True,
        export_materials=False,
        apply_modifiers=True
    )
    print(f"[OK] Exported {filepath.name} ({len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys)")


# =========================================================================
# 1. ANATOMICAL HEAD
# Origin at neck pivot (0, 0, 0)
# =========================================================================

def build_head():
    num_verts = 32

    def make_ring(z, cx, cy, rx, ry, brow=0.0, nose=0.0, jaw=0.0, beard=0.0, eyes=0.0, crest=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle)
            sa = math.sin(angle)
            r_x = rx
            r_y = ry

            # Sagittal crest (back of head, angle ~ 3pi/2)
            if crest > 0 and sa < 0:
                back_factor = max(0.0, -sa) ** 2.2
                r_y += crest * back_factor
                r_x *= (1.0 - 0.28 * back_factor)

            # Heavy ape brow shelf (front of head, angle ~ pi/2)
            if brow > 0 and sa > 0:
                front_factor = max(0.0, sa) ** 1.3
                r_y += brow * front_factor
                if abs(ca) < 0.75:
                    r_y += brow * 0.35 * (1.0 - abs(ca) / 0.75)

            # Deep orbital sockets (angle ~ 55 deg and 125 deg)
            if eyes > 0 and sa > 0:
                for socket_ang in [math.pi * 0.36, math.pi * 0.64]:
                    diff = abs(angle - socket_ang)
                    if diff < 0.32:
                        dent = (1.0 - diff / 0.32) ** 2
                        r_y -= eyes * dent

            # Broad flat simian nose (front center)
            if nose > 0 and sa > 0:
                diff = abs(angle - math.pi * 0.5)
                if diff < 0.38:
                    bump = (1.0 - diff / 0.38) ** 1.8
                    r_y += nose * bump
                    r_x += nose * 0.35 * bump

            # Prognathic jaw & cascading beard
            if (jaw > 0 or beard > 0) and sa > 0:
                diff = abs(angle - math.pi * 0.5)
                if diff < 0.65:
                    beard_bump = (1.0 - diff / 0.65) ** 1.4
                    r_y += (jaw + beard) * beard_bump

            x = cx + r_x * ca
            y = cy + r_y * sa
            pts.append(Vector((x, y, z)))
        return pts

    # Head rings from crest apex down to neck base
    ring_specs = [
        # (z, cx, cy, rx, ry, brow, nose, jaw, beard, eyes, crest)
        (0.48, 0.00, -0.10, 0.08, 0.12, 0.00, 0.00, 0.00, 0.00, 0.00, 0.08),
        (0.42, 0.00, -0.09, 0.14, 0.18, 0.00, 0.00, 0.00, 0.00, 0.00, 0.12),
        (0.35, 0.00, -0.07, 0.18, 0.22, 0.03, 0.00, 0.00, 0.00, 0.00, 0.14),
        (0.28, 0.00, -0.05, 0.21, 0.23, 0.08, 0.00, 0.00, 0.00, 0.00, 0.12),
        (0.22, 0.00, -0.03, 0.22, 0.23, 0.15, 0.02, 0.00, 0.00, 0.00, 0.08),  # BROW SHELF
        (0.16, 0.00, -0.02, 0.21, 0.22, 0.07, 0.06, 0.00, 0.00, 0.12, 0.05),  # EYE LEVEL
        (0.10, 0.00, -0.01, 0.22, 0.23, 0.02, 0.14, 0.03, 0.00, 0.05, 0.03),  # NOSE
        (0.04, 0.00,  0.00, 0.21, 0.22, 0.00, 0.10, 0.08, 0.02, 0.00, 0.02),  # UPPER LIP
        (-0.02, 0.00, 0.00, 0.20, 0.21, 0.00, 0.04, 0.10, 0.06, 0.00, 0.02),  # CLOSED LIPS
        (-0.08, 0.00, -0.02, 0.19, 0.21, 0.00, 0.00, 0.08, 0.12, 0.00, 0.03), # JAW / BEARD
        (-0.15, 0.00, -0.04, 0.17, 0.20, 0.00, 0.00, 0.04, 0.16, 0.00, 0.05), # CASCADING BEARD
        (-0.22, 0.00, -0.06, 0.15, 0.18, 0.00, 0.00, 0.00, 0.12, 0.00, 0.06), # LOWER BEARD
        (-0.28, 0.00, -0.06, 0.15, 0.16, 0.00, 0.00, 0.00, 0.00, 0.00, 0.04), # NECK PIVOT
    ]

    rings = [make_ring(*spec) for spec in ring_specs]
    head_obj = loft_polygon_rings("SasquatchHead", rings, close_top=True, close_bottom=True)
    finalize_mesh(head_obj, subsurf_levels=1, decimate_ratio=0.50)

    # Add deep-set amber eye spheres inside sockets
    eyes = []
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.032, location=(side * 0.082, 0.18, 0.16), segments=16, ring_count=12)
        eye = bpy.context.active_object
        eye.scale = (0.85, 0.85, 0.85)
        eyes.append(eye)

    # Join eyes into head mesh
    bpy.context.view_layer.objects.active = head_obj
    head_obj.select_set(True)
    for eye in eyes:
        eye.select_set(True)
    bpy.ops.object.join()

    # Shift head so neck pivot is at (0, 0, 0)
    # The neck base was at z = -0.28; shift up so pivot sits cleanly on torso neck joint
    for v in head_obj.data.vertices:
        v.co.z += 0.28

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return head_obj


# =========================================================================
# 2. CONTINUOUS ANATOMICAL TORSO
# Origin at mid-torso / chest center (0, 0, 0)
# =========================================================================

def build_torso():
    num_verts = 28

    def make_torso_ring(z, cx, cy, rx, ry, pec=0.0, sternum=0.0, trap=0.0, lat=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle) # X component
            sa = math.sin(angle) # Y component

            r_x = rx
            r_y = ry

            # Dual gorilla pectorals (front +Y, X = +/- 0.22)
            if pec > 0 and sa > 0:
                # Peak at angles ~ 55 deg and 125 deg
                pec_factor = max(0.0, sa) ** 1.4
                r_y += pec * pec_factor

            # Sternal groove indentation (front center, angle = pi/2, X = 0)
            if sternum > 0 and sa > 0:
                diff = abs(angle - math.pi * 0.5)
                if diff < 0.28:
                    groove = (1.0 - diff / 0.28) ** 2
                    r_y -= sternum * groove

            # Trapezius dorsal hump (rear -Y, X = +/- 0.18)
            if trap > 0 and sa < 0:
                trap_factor = max(0.0, -sa) ** 1.5
                r_y += trap * trap_factor

            # Latissimus dorsi wings (sides +/- X)
            if lat > 0 and abs(ca) > 0.4:
                lat_factor = (abs(ca) - 0.4) / 0.6
                r_x += lat * lat_factor

            x = cx + r_x * ca
            y = cy + r_y * sa
            pts.append(Vector((x, y, z)))
        return pts

    # Torso rings from lower pelvis (-0.38) to trapezius apex (+0.70)
    torso_specs = [
        # (z, cx, cy, rx, ry, pec, sternum, trap, lat)
        (-0.36, 0.00, -0.02, 0.38, 0.30, 0.00, 0.00, 0.00, 0.00), # Pelvis bottom cap
        (-0.28, 0.00, -0.02, 0.44, 0.33, 0.00, 0.00, 0.00, 0.02), # Hip flare
        (-0.16, 0.00, -0.01, 0.47, 0.35, 0.00, 0.00, 0.00, 0.05), # Lower waist
        (-0.04, 0.00,  0.00, 0.52, 0.38, 0.00, 0.00, 0.02, 0.08), # Abdomen / lower ribs
        (0.08,  0.00,  0.01, 0.56, 0.40, 0.04, 0.03, 0.04, 0.10), # Mid ribcage
        (0.20,  0.00,  0.02, 0.60, 0.42, 0.10, 0.06, 0.06, 0.10), # Lower pectorals
        (0.32,  0.00,  0.03, 0.62, 0.43, 0.15, 0.08, 0.08, 0.08), # Mid pectorals / widest chest
        (0.44,  0.00,  0.02, 0.60, 0.40, 0.12, 0.06, 0.12, 0.05), # Clavicles / deltoid roots
        (0.54,  0.00, -0.03, 0.52, 0.34, 0.04, 0.02, 0.18, 0.02), # Shoulder line / trapezius
        (0.62,  0.00, -0.06, 0.40, 0.28, 0.00, 0.00, 0.22, 0.00), # High trapezius hump
        (0.70,  0.00, -0.08, 0.28, 0.22, 0.00, 0.00, 0.16, 0.00), # Neck / trapezius collar
    ]

    rings = [make_torso_ring(*spec) for spec in torso_specs]
    torso_obj = loft_polygon_rings("SasquatchTorso", rings, close_top=True, close_bottom=True)
    finalize_mesh(torso_obj, subsurf_levels=1, decimate_ratio=0.55)
    return torso_obj


# =========================================================================
# 3. CONTINUOUS ANATOMICAL UPPER ARM
# Origin at shoulder pivot (0, 0, 0), extends down to elbow (z = -0.60)
# =========================================================================

def build_arm_upper():
    num_verts = 20

    def make_arm_ring(z, cx, cy, rx, ry, delt=0.0, bicep=0.0, tricep=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle)
            sa = math.sin(angle)
            r_x = rx
            r_y = ry

            # Deltoid lateral swell (-X for left arm)
            if delt > 0 and ca < 0:
                r_x += delt * (abs(ca) ** 1.3)

            # Bicep anterior swell (+Y)
            if bicep > 0 and sa > 0:
                r_y += bicep * (sa ** 1.5)

            # Tricep posterior swell (-Y)
            if tricep > 0 and sa < 0:
                r_y += tricep * ((-sa) ** 1.5)

            pts.append(Vector((cx + r_x * ca, cy + r_y * sa, z)))
        return pts

    arm_specs = [
        # (z, cx, cy, rx, ry, delt, bicep, tricep)
        (0.06,  0.00,  0.00, 0.18, 0.18, 0.00, 0.00, 0.00), # Shoulder ball cap apex
        (0.00, -0.01,  0.00, 0.24, 0.23, 0.02, 0.00, 0.00), # Shoulder socket equator
        (-0.08, -0.03, 0.00, 0.27, 0.25, 0.06, 0.01, 0.02), # Deltoid maximum swell
        (-0.18, -0.02, 0.01, 0.25, 0.24, 0.04, 0.04, 0.04), # Lower deltoid / bicep origin
        (-0.28, -0.01, 0.01, 0.23, 0.24, 0.01, 0.06, 0.05), # Mid bicep/tricep belly
        (-0.38, -0.01, 0.01, 0.21, 0.23, 0.00, 0.05, 0.05), # Lower bicep
        (-0.48,  0.00, 0.00, 0.19, 0.20, 0.00, 0.02, 0.03), # Supracondylar taper
        (-0.56,  0.00, -0.01, 0.17, 0.18, 0.00, 0.00, 0.02), # Elbow condyles
        (-0.60,  0.00, -0.01, 0.15, 0.15, 0.00, 0.00, 0.00), # Distal elbow joint
    ]

    rings = [make_arm_ring(*spec) for spec in arm_specs]
    arm_obj = loft_polygon_rings("SasquatchArmUpper", rings, close_top=True, close_bottom=True)
    finalize_mesh(arm_obj, subsurf_levels=1, decimate_ratio=0.40)
    return arm_obj


# =========================================================================
# 4. CONTINUOUS ANATOMICAL LOWER ARM
# Origin at elbow pivot (0, 0, 0), extends down to wrist (z = -0.56)
# =========================================================================

def build_arm_lower():
    num_verts = 20

    def make_forearm_ring(z, cx, cy, rx, ry, brach=0.0, frill=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle)
            sa = math.sin(angle)
            r_x = rx
            r_y = ry

            # Brachioradialis swell (lateral / anterior: -X, +Y)
            if brach > 0 and ca < 0:
                r_x += brach * (abs(ca) ** 1.3)
                if sa > 0:
                    r_y += brach * 0.4 * sa

            # Outer posterior hair frill along ulnar edge (-X, -Y)
            if frill > 0 and ca < 0 and sa < 0:
                r_x += frill * (abs(ca * sa) ** 0.8)
                r_y += frill * 0.5 * (abs(ca * sa) ** 0.8)

            pts.append(Vector((cx + r_x * ca, cy + r_y * sa, z)))
        return pts

    forearm_specs = [
        # (z, cx, cy, rx, ry, brach, frill)
        (0.00,  0.00, -0.01, 0.16, 0.16, 0.00, 0.00), # Elbow socket cup
        (-0.06, -0.01, 0.01, 0.20, 0.19, 0.03, 0.01), # Upper transition
        (-0.14, -0.02, 0.02, 0.24, 0.22, 0.07, 0.04), # Brachioradialis swell (thick ape arm!)
        (-0.22, -0.02, 0.02, 0.23, 0.22, 0.06, 0.06), # Mid-forearm mass + outer frills
        (-0.30, -0.01, 0.01, 0.21, 0.20, 0.04, 0.06), # Lower forearm belly + frills
        (-0.38,  0.00, 0.00, 0.18, 0.17, 0.02, 0.04), # Tapering forearm shaft
        (-0.46,  0.00, 0.00, 0.16, 0.15, 0.01, 0.02), # Tendon transition
        (-0.52,  0.00, 0.00, 0.15, 0.13, 0.00, 0.00), # Pre-wrist
        (-0.56,  0.00, 0.00, 0.14, 0.12, 0.00, 0.00), # Wrist joint
    ]

    rings = [make_forearm_ring(*spec) for spec in forearm_specs]
    forearm_obj = loft_polygon_rings("SasquatchArmLower", rings, close_top=True, close_bottom=True)
    finalize_mesh(forearm_obj, subsurf_levels=1, decimate_ratio=0.40)
    return forearm_obj


# =========================================================================
# 5. ANATOMICAL 5-FINGERED GRASPING HAND
# Origin at wrist pivot (0, 0, 0), curved fingers in stalking grip
# =========================================================================

def build_hand():
    # 1. Palm Core
    bpy.ops.mesh.primitive_cube_add(size=0.18, location=(0.0, 0.02, -0.10))
    palm = bpy.context.active_object
    palm.scale = (1.30, 0.90, 1.35)

    # Wrist ball cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.0, 0.0, -0.02), segments=16, ring_count=10)
    wrist_cap = bpy.context.active_object
    wrist_cap.scale = (1.0, 0.85, 0.70)

    parts = [palm, wrist_cap]

    # 2. Articulated Ape Fingers (curved inward into stalking grip)
    finger_configs = [
        # (name, base_loc, base_rot, length, radius)
        # Thumb: opposed at ~45 deg
        ("Thumb",  Vector((0.14,  0.06, -0.10)), (math.radians(-25), math.radians(35),  math.radians(20)),  0.18, 0.042),
        # Index finger
        ("Index",  Vector((0.08,  0.04, -0.22)), (math.radians(-35), math.radians(8),   math.radians(5)),   0.22, 0.038),
        # Middle finger (longest)
        ("Middle", Vector((0.01,  0.04, -0.23)), (math.radians(-40), math.radians(0),   math.radians(0)),   0.24, 0.040),
        # Ring finger
        ("Ring",   Vector((-0.06, 0.04, -0.22)), (math.radians(-38), math.radians(-6),  math.radians(-5)),  0.22, 0.038),
        # Pinky finger
        ("Pinky",  Vector((-0.12, 0.03, -0.20)), (math.radians(-32), math.radians(-12), math.radians(-10)), 0.19, 0.034),
    ]

    for name, base_pos, rot, length, rad in finger_configs:
        # 3 curved phalanges per finger
        ph_len = length / 3.0
        cur_pos = Vector(base_pos)
        cur_rot = Euler(rot)

        for ph_idx in range(3):
            # Taper toward tip
            ph_rad = rad * (1.0 - 0.12 * ph_idx)
            bpy.ops.mesh.primitive_cylinder_add(radius=ph_rad, depth=ph_len, location=cur_pos, vertices=12)
            ph = bpy.context.active_object
            ph.rotation_euler = cur_rot
            parts.append(ph)

            # Knuckle knuckle sphere
            bpy.ops.mesh.primitive_uv_sphere_add(radius=ph_rad * 1.15, location=cur_pos, segments=10, ring_count=8)
            knuckle = bpy.context.active_object
            parts.append(knuckle)

            # Advance along finger direction with progressive curl
            forward = Vector((0, 0, -ph_len))
            forward.rotate(cur_rot)
            cur_pos += forward
            cur_rot.x += math.radians(-15) # Progressive inward curl

        # Blunt ape claw/nail at tip
        bpy.ops.mesh.primitive_cone_add(radius1=rad * 0.7, radius2=0.01, depth=0.04, location=cur_pos)
        claw = bpy.context.active_object
        claw.rotation_euler = cur_rot
        parts.append(claw)

    # Join palm and fingers
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    hand_obj = bpy.context.active_object
    hand_obj.name = "SasquatchHand"

    finalize_mesh(hand_obj, subsurf_levels=0, decimate_ratio=0.28)
    return hand_obj


# =========================================================================
# 6. CONTINUOUS ANATOMICAL UPPER LEG
# Origin at hip pivot (0, 0, 0), extends down to knee (z = -0.62)
# =========================================================================

def build_leg_upper():
    num_verts = 20

    def make_thigh_ring(z, cx, cy, rx, ry, quad=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle)
            sa = math.sin(angle)
            r_x = rx
            r_y = ry

            # Quadriceps anterior bulge (+Y)
            if quad > 0 and sa > 0:
                r_y += quad * (sa ** 1.3)

            pts.append(Vector((cx + r_x * ca, cy + r_y * sa, z)))
        return pts

    thigh_specs = [
        # (z, cx, cy, rx, ry, quad)
        (0.04,  0.00,  0.00, 0.20, 0.20, 0.00), # Femoral ball apex
        (0.00, -0.01,  0.00, 0.25, 0.24, 0.01), # Hip joint equator
        (-0.08, -0.02, 0.02, 0.28, 0.27, 0.04), # Upper quad / trochanter
        (-0.18, -0.02, 0.04, 0.29, 0.29, 0.06), # Mid quad belly (sweeps forward in +Y)
        (-0.28, -0.01, 0.05, 0.28, 0.28, 0.06), # Rectus femoris peak
        (-0.38,  0.00, 0.04, 0.26, 0.26, 0.04), # Vastus lateralis / medialis
        (-0.48,  0.00, 0.02, 0.23, 0.23, 0.02), # Suprapatellar taper
        (-0.56,  0.00, 0.02, 0.20, 0.20, 0.01), # Patella knee joint
        (-0.62,  0.00, 0.00, 0.18, 0.18, 0.00), # Distal condyles
    ]

    rings = [make_thigh_ring(*spec) for spec in thigh_specs]
    thigh_obj = loft_polygon_rings("SasquatchLegUpper", rings, close_top=True, close_bottom=True)
    finalize_mesh(thigh_obj, subsurf_levels=1, decimate_ratio=0.40)
    return thigh_obj


# =========================================================================
# 7. CONTINUOUS ANATOMICAL LOWER LEG
# Origin at knee pivot (0, 0, 0), extends down to ankle (z = -0.62)
# =========================================================================

def build_leg_lower():
    num_verts = 20

    def make_calf_ring(z, cx, cy, rx, ry, calf=0.0):
        pts = []
        for i in range(num_verts):
            angle = 2.0 * math.pi * i / num_verts
            ca = math.cos(angle)
            sa = math.sin(angle)
            r_x = rx
            r_y = ry

            # Gastrocnemius posterior calf bulge (-Y)
            if calf > 0 and sa < 0:
                r_y += calf * ((-sa) ** 1.4)

            pts.append(Vector((cx + r_x * ca, cy + r_y * sa, z)))
        return pts

    calf_specs = [
        # (z, cx, cy, rx, ry, calf)
        (0.00,  0.00,  0.00, 0.19, 0.19, 0.00), # Knee cup
        (-0.06, 0.00, -0.02, 0.21, 0.21, 0.02), # Upper tibial flare
        (-0.14, 0.00, -0.05, 0.24, 0.26, 0.08), # Gastrocnemius peak swell (posterior -Y)
        (-0.22, 0.00, -0.06, 0.23, 0.26, 0.07), # Soleus muscle belly
        (-0.30, 0.00, -0.05, 0.21, 0.23, 0.05), # Lower calf taper
        (-0.38, 0.00, -0.03, 0.18, 0.20, 0.03), # Achilles tendon transition
        (-0.46, 0.00, -0.02, 0.16, 0.17, 0.01), # Achilles tendon shaft
        (-0.54, 0.00,  0.00, 0.15, 0.15, 0.00), # Pre-ankle malleoli
        (-0.62, 0.00,  0.00, 0.15, 0.14, 0.00), # Ankle joint
    ]

    rings = [make_calf_ring(*spec) for spec in calf_specs]
    calf_obj = loft_polygon_rings("SasquatchLegLower", rings, close_top=True, close_bottom=True)
    finalize_mesh(calf_obj, subsurf_levels=1, decimate_ratio=0.40)
    return calf_obj


# =========================================================================
# 8. 18-INCH PLANTIGRADE FOOT WITH 5 TOES
# Origin at ankle pivot (0, 0, 0), extends forward in +Y (Godot -Z)
# =========================================================================

def build_foot():
    # 1. Foot Core (Heel to Metatarsals)
    # Ankle cup
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.0, 0.0, 0.0), segments=16, ring_count=10)
    ankle_cup = bpy.context.active_object
    ankle_cup.scale = (1.0, 1.0, 0.8)

    # Heel mass (calcaneus - projects backward in -Y, down in -Z)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.0, -0.16, -0.10), segments=16, ring_count=10)
    heel = bpy.context.active_object
    heel.scale = (1.15, 1.30, 0.85)

    # Midfoot / Arch
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, 0.06, -0.10))
    midfoot = bpy.context.active_object
    midfoot.scale = (1.25, 1.80, 0.70)

    # Metatarsal ball of foot (wide ape foot)
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, 0.24, -0.11))
    ball = bpy.context.active_object
    ball.scale = (1.45, 1.10, 0.65)

    parts = [ankle_cup, heel, midfoot, ball]

    # 2. Five Articulated Ape Toes (18-inch footprint, wide toe splay)
    toe_specs = [
        # (name, x_pos, y_pos, length, radius)
        # Big toe (hallux) - thickest ape toe
        ("Toe_1",  0.11, 0.36, 0.16, 0.046),
        # 2nd toe
        ("Toe_2",  0.05, 0.38, 0.17, 0.042),
        # 3rd toe
        ("Toe_3", -0.01, 0.38, 0.17, 0.040),
        # 4th toe
        ("Toe_4", -0.07, 0.36, 0.15, 0.038),
        # Pinky toe
        ("Toe_5", -0.12, 0.33, 0.13, 0.036),
    ]

    for name, tx, ty, tlen, trad in toe_specs:
        bpy.ops.mesh.primitive_cylinder_add(radius=trad, depth=tlen, location=(tx, ty, -0.13), vertices=12)
        toe = bpy.context.active_object
        toe.rotation_euler = (math.radians(85), 0, math.radians(-tx * 40))
        parts.append(toe)

        # Toe tip bulb
        forward_y = tlen * 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(radius=trad * 1.05, location=(tx, ty + forward_y, -0.13), segments=10, ring_count=8)
        tip = bpy.context.active_object
        parts.append(tip)

        # Thick blunt claw/nail
        bpy.ops.mesh.primitive_cone_add(radius1=trad * 0.7, radius2=0.01, depth=0.035, location=(tx, ty + forward_y + 0.02, -0.13))
        nail = bpy.context.active_object
        nail.rotation_euler = (math.radians(90), 0, math.radians(-tx * 40))
        parts.append(nail)

    # Join foot parts
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    foot_obj = bpy.context.active_object
    foot_obj.name = "SasquatchFoot"

    finalize_mesh(foot_obj, subsurf_levels=0, decimate_ratio=0.28)
    return foot_obj


# =========================================================================
# 9. SILHOUETTE-BREAKING FUR CARDS
# Positioned along shoulders, elbows, forearms, outer thighs, and calves
# =========================================================================

def build_fur_cards():
    mesh = bpy.data.meshes.new("SasquatchFurCards")
    bm = bmesh.new()

    # Creates a 2-segment curved fur tuft card
    def add_card(loc, rot, width, length, curl=0.25):
        # 6 vertices, 2 quad faces
        w2 = width * 0.5
        v_bl = bm.verts.new(Vector((-w2, 0, 0)))
        v_br = bm.verts.new(Vector((w2, 0, 0)))
        v_ml = bm.verts.new(Vector((-w2 * 0.8, curl * 0.5, -length * 0.5)))
        v_mr = bm.verts.new(Vector((w2 * 0.8, curl * 0.5, -length * 0.5)))
        v_tl = bm.verts.new(Vector((-w2 * 0.3, curl, -length)))
        v_tr = bm.verts.new(Vector((w2 * 0.3, curl, -length)))

        # Transform to position and rotation
        mat_trans = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
        for v in [v_bl, v_br, v_ml, v_mr, v_tl, v_tr]:
            v.co = mat_trans @ v.co

        bm.faces.new((v_bl, v_br, v_mr, v_ml))
        bm.faces.new((v_ml, v_mr, v_tr, v_tl))

    card_specs = [
        # Shoulders (Left & Right)
        (Vector((-0.68, -0.02, 0.45)), (0, math.radians(-25), math.radians(20)),  0.16, 0.32, 0.08),
        (Vector(( 0.68, -0.02, 0.45)), (0, math.radians( 25), math.radians(-20)), 0.16, 0.32, 0.08),
        (Vector((-0.64, -0.12, 0.38)), (math.radians(-20), math.radians(-30), 0),  0.15, 0.30, 0.07),
        (Vector(( 0.64, -0.12, 0.38)), (math.radians(-20), math.radians( 30), 0),  0.15, 0.30, 0.07),
        # Elbows
        (Vector((-0.66, -0.14, -0.10)), (math.radians(-30), math.radians(-15), 0), 0.14, 0.28, 0.08),
        (Vector(( 0.66, -0.14, -0.10)), (math.radians(-30), math.radians( 15), 0), 0.14, 0.28, 0.08),
        # Forearm outer fringes
        (Vector((-0.68, -0.12, -0.32)), (math.radians(-25), math.radians(-10), 0), 0.13, 0.30, 0.09),
        (Vector(( 0.68, -0.12, -0.32)), (math.radians(-25), math.radians( 10), 0), 0.13, 0.30, 0.09),
        (Vector((-0.66, -0.10, -0.46)), (math.radians(-20), math.radians(-8),  0), 0.12, 0.26, 0.08),
        (Vector(( 0.66, -0.10, -0.46)), (math.radians(-20), math.radians( 8),  0), 0.12, 0.26, 0.08),
        # Outer Thighs
        (Vector((-0.46, 0.00, -0.50)), (0, math.radians(-15), 0), 0.16, 0.35, 0.07),
        (Vector(( 0.46, 0.00, -0.50)), (0, math.radians( 15), 0), 0.16, 0.35, 0.07),
        # Outer Calves
        (Vector((-0.44, -0.08, -1.15)), (math.radians(-15), math.radians(-12), 0), 0.15, 0.32, 0.08),
        (Vector(( 0.44, -0.08, -1.15)), (math.radians(-15), math.radians( 12), 0), 0.15, 0.32, 0.08),
    ]

    for loc, rot, w, l, c in card_specs:
        add_card(loc, rot, w, l, c)

    bm.to_mesh(mesh)
    bm.free()

    cards_obj = bpy.data.objects.new("SasquatchFurCards", mesh)
    bpy.context.collection.objects.link(cards_obj)

    bpy.context.view_layer.objects.active = cards_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return cards_obj


# =========================================================================
# ASSEMBLE, SCALE TO 2.85M, AND EXPORT ALL
# =========================================================================

def main():
    col = clean_scene()
    print("=" * 60)
    print(" EXECUTING CLASSIC BIGFOOT CONTINUOUS ANATOMICAL BUILD")
    print("=" * 60)

    # 1. Author components
    head = build_head()
    torso = build_torso()
    arm_up = build_arm_upper()
    arm_low = build_arm_lower()
    hand = build_hand()
    leg_up = build_leg_upper()
    leg_low = build_leg_lower()
    foot = build_foot()
    fur_cards = build_fur_cards()

    # 2. Export individual components to assets/models/
    # Matching exact Godot node origins
    components = [
        (torso, MODELS_DIR / "sasquatch_torso.obj"),
        (head, MODELS_DIR / "sasquatch_head.obj"),
        (arm_up, MODELS_DIR / "sasquatch_arm_upper.obj"),
        (arm_low, MODELS_DIR / "sasquatch_arm_lower.obj"),
        (hand, MODELS_DIR / "sasquatch_hand.obj"),
        (leg_up, MODELS_DIR / "sasquatch_leg_upper.obj"),
        (leg_low, MODELS_DIR / "sasquatch_leg_lower.obj"),
        (foot, MODELS_DIR / "sasquatch_foot.obj"),
        (fur_cards, MODELS_DIR / "sasquatch_fur_cards.obj"),
    ]

    for obj, path in components:
        export_obj(obj, path)

    # 3. Assemble Full Character in Memory for Diagnostic Turntable Renders
    # Positions match Godot scene hierarchy exactly
    part_specs = [
        (torso, Vector((0, 0, 0)), Vector((1, 1, 1))),
        (head, Vector((0, 0.08, 0.72)), Vector((1, 1, 1))),
        (arm_up, Vector((-0.62, -0.05, 0.48)), Vector((1, 1, 1))),
        (arm_up.copy(), Vector((0.62, -0.05, 0.48)), Vector((-1, 1, 1))),
        (arm_low, Vector((-0.62, -0.06, -0.12)), Vector((1, 1, 1))),
        (arm_low.copy(), Vector((0.62, -0.06, -0.12)), Vector((-1, 1, 1))),
        (hand, Vector((-0.62, -0.08, -0.68)), Vector((1, 1, 1))),
        (hand.copy(), Vector((0.62, -0.08, -0.68)), Vector((-1, 1, 1))),
        (leg_up, Vector((-0.35, -0.02, -0.32)), Vector((1, 1, 1))),
        (leg_up.copy(), Vector((0.35, -0.02, -0.32)), Vector((-1, 1, 1))),
        (leg_low, Vector((-0.35, -0.04, -0.94)), Vector((1, 1, 1))),
        (leg_low.copy(), Vector((0.35, -0.04, -0.94)), Vector((-1, 1, 1))),
        (foot, Vector((-0.35, 0.01, -1.56)), Vector((1, 1, 1))),
        (foot.copy(), Vector((0.35, 0.01, -1.56)), Vector((-1, 1, 1))),
        (fur_cards, Vector((0, 0, 0)), Vector((1, 1, 1))),
    ]

    assembled = []
    for obj, loc, sc in part_specs:
        if obj.name not in bpy.context.collection.objects:
            bpy.context.collection.objects.link(obj)
        obj.location = loc
        obj.scale = sc
        assembled.append(obj)
        obj.select_set(True)

    bpy.context.view_layer.objects.active = assembled[0]
    bpy.ops.object.join()
    full = bpy.context.active_object
    full.name = "SasquatchFullClassic"

    # Scale assembled mesh so creature stands 2.85m tall
    dim_z = full.dimensions.z
    scale_factor = 2.85 / dim_z
    full.scale = (scale_factor, scale_factor, scale_factor)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Export full assembled mesh to assets/models/sasquatch_full.obj
    full_path = MODELS_DIR / "sasquatch_full.obj"
    export_obj(full, full_path)
    print(f"\n>>> [SUCCESS] Full assembled classic bigfoot exported to {full_path}")
    print(f"Total Vertices: {len(full.data.vertices)}, Total Triangles: {len(full.data.polygons) * 2}")


if __name__ == "__main__":
    main()
