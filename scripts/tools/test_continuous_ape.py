"""
Test script for Continuous Anatomical Quad Lofting for the Classic Bigfoot:
Replaces stacked primitive spheres with smooth, continuous anatomical lofting:
- Arm: Single continuous lofted quad tube with deltoid, bicep, tricep, forearm brachioradialis swell, and wrist
- Leg: Single continuous lofted quad tube with hip, quad sweep, patella knee, gastrocnemius calf, Achilles, and ankle
- Torso: Continuous lofted barrel chest with pectorals, sternal groove, latissimus wings, and trapezius slope
- Head: Continuous quad simian head with sagittal slope, ape brow, deep eye sockets, flat nose, and beard
- Hand: Anatomical palm with 5 articulated fingers
- Foot: 18-inch plantigrade foot with 5 distinct toes
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
QA_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "qa" / "diagnostic_views"


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)


def loft_rings(name, rings, close_top=False, close_bottom=False):
    """
    Creates a smooth quad-mesh tube by skinning a sequence of vertex rings.
    rings: list of lists of 3D points (Vector), each ring must have the same number of vertices.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    num_rings = len(rings)
    num_verts_per_ring = len(rings[0])

    bm_rings = []
    for r_idx, ring in enumerate(rings):
        bm_ring = [bm.verts.new(pt) for pt in ring]
        bm_rings.append(bm_ring)

    bm.verts.ensure_lookup_table()

    # Bridge rings with quad faces
    for r in range(num_rings - 1):
        ring_a = bm_rings[r]
        ring_b = bm_rings[r + 1]
        for i in range(num_verts_per_ring):
            i_next = (i + 1) % num_verts_per_ring
            # Quad face (v0, v1, v2, v3)
            bm.faces.new((ring_a[i], ring_a[i_next], ring_b[i_next], ring_b[i]))

    if close_top:
        # Cap top ring with a center vertex or fan
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


def create_ellipse_ring(center, radius_x, radius_y, num_verts=16, rot_z=0.0):
    pts = []
    for i in range(num_verts):
        angle = 2.0 * math.pi * i / num_verts + rot_z
        x = center.x + radius_x * math.cos(angle)
        y = center.y + radius_y * math.sin(angle)
        z = center.z
        pts.append(Vector((x, y, z)))
    return pts


# =========================================================================
# 1. CONTINUOUS APE UPPER ARM
# Single smooth limb from shoulder cap to elbow joint
# =========================================================================

def build_ape_arm_upper():
    # 10 cross-sections along Z from 0.0 down to -0.60
    # Center lines have a slight organic curve
    ring_defs = [
        # (z, center_x, center_y, rx, ry)
        (0.04, 0.00, 0.00, 0.16, 0.16),   # Shoulder ball apex
        (0.00, 0.01, -0.01, 0.22, 0.22),  # Shoulder socket equator
        (-0.08, 0.03, -0.01, 0.25, 0.24), # Deltoid maximum swell
        (-0.16, 0.02, 0.00, 0.23, 0.22),  # Lower deltoid / bicep origin
        (-0.26, 0.00, 0.01, 0.21, 0.23),  # Mid bicep/tricep (bicep pulls forward in +Y)
        (-0.36, -0.01, 0.01, 0.20, 0.22), # Lower bicep belly
        (-0.46, -0.01, 0.00, 0.18, 0.19), # Supracondylar taper
        (-0.54, 0.00, -0.02, 0.17, 0.18), # Elbow condyles (olecranon pulls back in -Y)
        (-0.60, 0.00, -0.01, 0.15, 0.15), # Distal elbow joint
    ]

    rings = []
    for z, cx, cy, rx, ry in ring_defs:
        rings.append(create_ellipse_ring(Vector((cx, cy, z)), rx, ry, num_verts=16))

    arm_obj = loft_rings("SasquatchArmUpper", rings, close_top=True, close_bottom=True)

    # Apply subdivision + smooth
    mod_sub = arm_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return arm_obj


# =========================================================================
# 2. CONTINUOUS APE LOWER ARM
# Single smooth limb from elbow to wrist with brachioradialis swell
# =========================================================================

def build_ape_arm_lower():
    # 10 cross-sections along Z from 0.0 down to -0.56
    ring_defs = [
        (0.00, 0.00, -0.01, 0.16, 0.16),   # Elbow socket cup
        (-0.06, 0.01, 0.01, 0.19, 0.18),   # Upper forearm transition
        (-0.14, 0.02, 0.03, 0.23, 0.22),   # Brachioradialis maximum swell (ape thick forearm!)
        (-0.22, 0.02, 0.02, 0.22, 0.21),   # Mid-forearm mass
        (-0.30, 0.01, 0.01, 0.20, 0.19),   # Lower forearm belly
        (-0.38, 0.00, 0.00, 0.18, 0.17),   # Tapering forearm shaft
        (-0.46, 0.00, 0.00, 0.16, 0.15),   # Lower pronator/extensor tendon
        (-0.52, 0.00, 0.00, 0.15, 0.13),   # Pre-wrist
        (-0.56, 0.00, 0.00, 0.14, 0.12),   # Wrist joint
    ]

    rings = []
    for z, cx, cy, rx, ry in ring_defs:
        rings.append(create_ellipse_ring(Vector((cx, cy, z)), rx, ry, num_verts=16))

    forearm_obj = loft_rings("SasquatchArmLower", rings, close_top=True, close_bottom=True)

    # Add posterior hair fringe along outer edge
    bpy.ops.object.mode_set(mode='OBJECT')
    mod_sub = forearm_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.context.view_layer.objects.active = forearm_obj
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return forearm_obj


# =========================================================================
# 3. CONTINUOUS APE UPPER LEG
# Single smooth limb from femoral hip to knee with forward quad curve
# =========================================================================

def build_ape_leg_upper():
    # 10 cross-sections along Z from 0.0 down to -0.62
    ring_defs = [
        (0.02, 0.00, 0.00, 0.18, 0.18),    # Femoral ball apex
        (0.00, -0.01, 0.00, 0.23, 0.22),   # Hip joint equator
        (-0.08, -0.02, 0.02, 0.26, 0.25),  # Greater trochanter / upper quad
        (-0.18, -0.02, 0.04, 0.26, 0.27),  # Mid quad belly (sweeps forward in +Y)
        (-0.28, -0.01, 0.05, 0.25, 0.26),  # Rectus femoris maximum thickness
        (-0.38, 0.00, 0.04, 0.23, 0.24),   # Vastus lateralis / medialis
        (-0.48, 0.00, 0.02, 0.21, 0.21),   # Suprapatellar taper
        (-0.56, 0.00, 0.02, 0.19, 0.19),   # Patellar knee joint
        (-0.62, 0.00, 0.00, 0.17, 0.17),   # Distal femoral condyles
    ]

    rings = []
    for z, cx, cy, rx, ry in ring_defs:
        rings.append(create_ellipse_ring(Vector((cx, cy, z)), rx, ry, num_verts=16))

    thigh_obj = loft_rings("SasquatchLegUpper", rings, close_top=True, close_bottom=True)

    mod_sub = thigh_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.context.view_layer.objects.active = thigh_obj
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return thigh_obj


# =========================================================================
# 4. CONTINUOUS APE LOWER LEG
# Single smooth limb from knee to ankle with posterior calf curve
# =========================================================================

def build_ape_leg_lower():
    # 10 cross-sections along Z from 0.0 down to -0.62
    ring_defs = [
        (0.00, 0.00, 0.00, 0.18, 0.18),    # Knee cup
        (-0.06, 0.00, -0.02, 0.20, 0.20),  # Upper tibial flare
        (-0.14, 0.00, -0.05, 0.22, 0.24),  # Gastrocnemius maximum swell (posterior in -Y)
        (-0.22, 0.00, -0.06, 0.21, 0.24),  # Soleus muscle belly
        (-0.30, 0.00, -0.05, 0.19, 0.21),  # Lower calf taper
        (-0.38, 0.00, -0.03, 0.17, 0.18),  # Transition to Achilles tendon
        (-0.46, 0.00, -0.02, 0.15, 0.15),  # Achilles tendon column
        (-0.54, 0.00, 0.00, 0.14, 0.13),   # Pre-ankle malleoli
        (-0.62, 0.00, 0.00, 0.14, 0.13),   # Ankle joint
    ]

    rings = []
    for z, cx, cy, rx, ry in ring_defs:
        rings.append(create_ellipse_ring(Vector((cx, cy, z)), rx, ry, num_verts=16))

    calf_obj = loft_rings("SasquatchLegLower", rings, close_top=True, close_bottom=True)

    mod_sub = calf_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.context.view_layer.objects.active = calf_obj
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return calf_obj


# =========================================================================
# 5. CONTINUOUS APE TORSO
# Single continuous torso lofted from pelvis to neck with pectorals & trapezius
# =========================================================================

def build_ape_torso():
    # 12 cross-sections along Z from pelvis (-0.38) to upper neck/trapezius (+0.68)
    ring_defs = [
        # (z, cx, cy, rx, ry)
        (-0.36, 0.00, -0.02, 0.38, 0.32),  # Lower pelvis base (curved, no flat cutoff!)
        (-0.28, 0.00, -0.02, 0.44, 0.35),  # Hip flare / iliac crests
        (-0.18, 0.00, -0.01, 0.46, 0.36),  # Lower waist / gluteal transition
        (-0.06, 0.00, 0.00, 0.50, 0.38),   # Abdomen / lower ribs
        (0.06, 0.00, 0.01, 0.54, 0.40),    # Mid ribcage / serratus anterior
        (0.18, 0.00, 0.02, 0.58, 0.42),    # Thorax / widest barrel chest
        (0.30, 0.00, 0.04, 0.60, 0.42),    # Pectoral plates (full chest swell in +Y)
        (0.42, 0.00, 0.02, 0.58, 0.38),    # Clavicles & deltoid roots
        (0.52, 0.00, -0.04, 0.50, 0.32),   # Shoulder line / lower trapezius
        (0.60, 0.00, -0.08, 0.38, 0.25),   # Trapezius hump (concentrated in -Y)
        (0.68, 0.00, -0.06, 0.26, 0.18),   # Neck base collar
    ]

    rings = []
    for z, cx, cy, rx, ry in ring_defs:
        rings.append(create_ellipse_ring(Vector((cx, cy, z)), rx, ry, num_verts=20))

    torso_obj = loft_rings("SasquatchTorso", rings, close_top=True, close_bottom=True)

    # Sculpt pectoral sternal groove & deltoid sockets
    bpy.context.view_layer.objects.active = torso_obj
    mod_sub = torso_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    # Add sternal groove indentation with boolean cutter
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.45, location=(0.0, 0.44, 0.30))
    groove = bpy.context.active_object
    groove.rotation_euler = (math.radians(-12), 0, 0)
    groove.scale = (0.5, 1.2, 1.0)
    mod_bool = torso_obj.modifiers.new("SternalGroove", 'BOOLEAN')
    mod_bool.operation = 'DIFFERENCE'
    mod_bool.object = groove
    bpy.context.view_layer.objects.active = torso_obj
    bpy.ops.object.modifier_apply(modifier="SternalGroove")
    bpy.data.objects.remove(groove, do_unlink=True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return torso_obj


# =========================================================================
# ASSEMBLE ALL AND RENDER DIAGNOSTICS
# =========================================================================

def main():
    clean_scene()
    print("=" * 60)
    print(" TESTING CONTINUOUS APE ANATOMY LOFTING")
    print("=" * 60)

    # Build continuous limbs & torso
    arm_up = build_ape_arm_upper()
    arm_low = build_ape_arm_lower()
    leg_up = build_ape_leg_upper()
    leg_low = build_ape_leg_lower()
    torso = build_ape_torso()

    # Re-import existing refined head, hand, foot
    bpy.ops.wm.obj_import(filepath=str(MODELS_DIR / "sasquatch_head.obj"))
    head = bpy.context.selected_objects[0]
    head.rotation_euler = (0, 0, 0)

    bpy.ops.wm.obj_import(filepath=str(MODELS_DIR / "sasquatch_hand.obj"))
    hand = bpy.context.selected_objects[0]
    hand.rotation_euler = (0, 0, 0)

    bpy.ops.wm.obj_import(filepath=str(MODELS_DIR / "sasquatch_foot.obj"))
    foot = bpy.context.selected_objects[0]
    foot.rotation_euler = (0, 0, 0)

    # Position in full assembled pose
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
    full.name = "SasquatchFullContinuous"

    # Export assembled full mesh to test preview
    test_full_path = PROJECT_ROOT / "docs" / "graphics" / "previews" / "test_continuous_full.obj"
    bpy.ops.wm.obj_export(
        filepath=str(test_full_path),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_uv=True,
        export_normals=True,
        export_materials=False,
    )
    print(f"[OK] Exported test full model: {test_full_path}")


if __name__ == "__main__":
    main()
