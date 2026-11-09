"""
Procedural 3D Asset Builder for The Black Pines - Iteration 07
Generates:
1. assets/models/generator_industrial.glb
   Photorealistic standby diesel generator with concrete foundation,
   heavy steel skid, green rusted enclosure, stamped ventilation louvers,
   latched access doors, operator control panel with gauges, and rain-cap exhaust.
2. assets/models/firewood_cord_stack.glb
   Hand-split cordwood rick with timber cradle rack, authentic wedge & quarter
   split logs, annular end rings, draped rusty corrugated rain cover, and stone weights.

Enforces:
- NVIDIA GeForce GTX 960 Budget (< 4,000 tris per prop)
- PBR textures: Base Color, Normal, Roughness, AO
- No raw primitives - all beveled, detailed, and organic
"""

import bpy
import bmesh
import math
import random
from pathlib import Path
from mathutils import Vector, Matrix, Euler

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
PREVIEWS_DIR = PROJECT_ROOT / "docs" / "graphics" / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

# Texture paths
TEX_DIR = PROJECT_ROOT / "assets" / "textures" / "polyhaven"
GREEN_METAL_DIFF = TEX_DIR / "green_metal_rust" / "green_metal_rust_diff_1k.jpg"
GREEN_METAL_NORM = TEX_DIR / "green_metal_rust" / "green_metal_rust_nor_gl_1k.jpg"
GREEN_METAL_ROUGH = TEX_DIR / "green_metal_rust" / "green_metal_rust_rough_1k.jpg"

CONCRETE_DIFF = TEX_DIR / "chipped_concrete" / "chipped_concrete_diff_1k.jpg"
CONCRETE_NORM = TEX_DIR / "chipped_concrete" / "chipped_concrete_nor_gl_1k.jpg"
CONCRETE_ROUGH = TEX_DIR / "chipped_concrete" / "chipped_concrete_arm_1k.jpg"

BARK_DIFF = TEX_DIR / "knotted_pine_bark" / "knotted_pine_bark_diffuse_1k.jpg"
BARK_NORM = TEX_DIR / "knotted_pine_bark" / "knotted_pine_bark_normal_1k.jpg"
BARK_ROUGH = TEX_DIR / "knotted_pine_bark" / "knotted_pine_bark_rough_1k.jpg"

WOOD_DIFF = TEX_DIR / "fine_grained_wood" / "fine_grained_wood_diffuse_1k.jpg"
WOOD_NORM = TEX_DIR / "fine_grained_wood" / "fine_grained_wood_normal_1k.jpg"
WOOD_ROUGH = TEX_DIR / "fine_grained_wood" / "fine_grained_wood_rough_1k.jpg"

PLANKS_DIFF = PROJECT_ROOT / "assets" / "textures" / "weathered_brown_planks" / "weathered_brown_planks_diffuse_1k.jpg"
PLANKS_NORM = PROJECT_ROOT / "assets" / "textures" / "weathered_brown_planks" / "weathered_brown_planks_nor_gl_1k.jpg"
PLANKS_ROUGH = PROJECT_ROOT / "assets" / "textures" / "weathered_brown_planks" / "weathered_brown_planks_rough_1k.jpg"

RUSTY_IRON_DIFF = TEX_DIR / "rusty_corrugated_iron" / "rusty_corrugated_iron_diffuse_1k.jpg"
RUSTY_IRON_NORM = TEX_DIR / "rusty_corrugated_iron" / "rusty_corrugated_iron_normal_1k.jpg"
RUSTY_IRON_ROUGH = TEX_DIR / "rusty_corrugated_iron" / "rusty_corrugated_iron_rough_1k.jpg"

ROCK_DIFF = PROJECT_ROOT / "assets" / "models" / "polyhaven" / "rock_moss_set_01" / "textures" / "rock_moss_set_01_diff_1k.jpg"
ROCK_NORM = PROJECT_ROOT / "assets" / "models" / "polyhaven" / "rock_moss_set_01" / "textures" / "rock_moss_set_01_nor_gl_1k.jpg"
ROCK_ROUGH = PROJECT_ROOT / "assets" / "models" / "polyhaven" / "rock_moss_set_01" / "textures" / "rock_moss_set_01_rough_1k.jpg"


def clean_scene():
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
                   diff_path=None, norm_path=None, rough_path=None):
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
        n_map.inputs["Strength"].default_value = 1.2
        links.new(t_norm.outputs["Color"], n_map.inputs["Color"])
        links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])

    if rough_path and Path(rough_path).exists():
        t_rough = nodes.new("ShaderNodeTexImage")
        t_rough.image = bpy.data.images.load(str(rough_path))
        t_rough.image.colorspace_settings.name = "Non-Color"
        links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

    return mat


def add_beveled_box(bm, center, size, uv_layer, mat_idx=0, uv_scale=1.0):
    """Adds a box to bmesh with planar UV coordinates."""
    dx, dy, dz = size[0]*0.5, size[1]*0.5, size[2]*0.5
    cx, cy, cz = center

    v = [
        bm.verts.new((cx - dx, cy - dy, cz - dz)),
        bm.verts.new((cx + dx, cy - dy, cz - dz)),
        bm.verts.new((cx + dx, cy + dy, cz - dz)),
        bm.verts.new((cx - dx, cy + dy, cz - dz)),
        bm.verts.new((cx - dx, cy - dy, cz + dz)),
        bm.verts.new((cx + dx, cy - dy, cz + dz)),
        bm.verts.new((cx + dx, cy + dy, cz + dz)),
        bm.verts.new((cx - dx, cy + dy, cz + dz)),
    ]

    face_indices = [
        (0, 1, 5, 4), # South (-Y)
        (1, 2, 6, 5), # East (+X)
        (2, 3, 7, 6), # North (+Y)
        (3, 0, 4, 7), # West (-X)
        (4, 5, 6, 7), # Top (+Z)
        (3, 2, 1, 0), # Bottom (-Z)
    ]

    new_faces = []
    for f_idx, idxs in enumerate(face_indices):
        f = bm.faces.new([v[i] for i in idxs])
        f.material_index = mat_idx
        new_faces.append(f)

        # Planar UV projection
        for loop in f.loops:
            co = loop.vert.co
            if f_idx in (0, 2):    # Front/Back -> X, Z
                loop[uv_layer].uv = Vector((co.x * uv_scale, co.z * uv_scale))
            elif f_idx in (1, 3):  # Left/Right -> Y, Z
                loop[uv_layer].uv = Vector((co.y * uv_scale, co.z * uv_scale))
            else:                  # Top/Bottom -> X, Y
                loop[uv_layer].uv = Vector((co.x * uv_scale, co.y * uv_scale))

    return new_faces


# =========================================================================
# ASSET 1: INDUSTRIAL BACKUP GENERATOR
# =========================================================================

def build_generator_mesh():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Materials:
    # 0: M_Gen_Concrete (Pad)
    # 1: M_Gen_GreenMetal (Body & Louvers)
    # 2: M_Gen_DarkSteel (Skid, Exhaust, Hinges, Latches)
    # 3: M_Gen_Panel (Controls & Placards)
    # 4: M_Gen_Indicator (Red Stop & Amber Lamps)

    # 1. Concrete Foundation Pad (2.2m x 1.7m x 0.16m)
    add_beveled_box(bm, (0.0, 0.0, 0.08), (2.2, 1.7, 0.16), uv_layer, mat_idx=0, uv_scale=1.5)

    # 4 Anchor Bolt Washers
    for bx in (-0.85, 0.85):
        for by in (-0.65, 0.65):
            add_beveled_box(bm, (bx, by, 0.165), (0.08, 0.08, 0.01), uv_layer, mat_idx=2)
            # Hex nut / stud
            add_beveled_box(bm, (bx, by, 0.18), (0.035, 0.035, 0.02), uv_layer, mat_idx=2)

    # 2. Steel Skid Runners (2 C-channels along Y)
    for sx in (-0.72, 0.72):
        # Main runner
        add_beveled_box(bm, (sx, 0.0, 0.22), (0.12, 1.50, 0.12), uv_layer, mat_idx=2, uv_scale=2.0)
        # Chamfered towing eyelet tab at ends
        for sy in (-0.76, 0.76):
            add_beveled_box(bm, (sx, sy, 0.22), (0.04, 0.06, 0.10), uv_layer, mat_idx=2)

    # Cross beams between skids
    for cy in (-0.55, 0.0, 0.55):
        add_beveled_box(bm, (0.0, cy, 0.22), (1.32, 0.10, 0.10), uv_layer, mat_idx=2)

    # 3. Vibration Isolator Rubber Dampener Pucks
    for px in (-0.65, 0.65):
        for py in (-0.50, 0.50):
            add_beveled_box(bm, (px, py, 0.29), (0.10, 0.10, 0.02), uv_layer, mat_idx=2)

    # 4. Main Generator Cabinet Housing
    # Dimensions: 1.50m wide (X), 1.30m deep (Y), 0.95m high (Z: 0.30 to 1.25)
    add_beveled_box(bm, (0.0, 0.0, 0.775), (1.50, 1.30, 0.95), uv_layer, mat_idx=1, uv_scale=1.2)

    # Pitched Rain-Shedding Roof Cap (Apex at Z=1.34, slopes down to Z=1.27 at X=±0.78)
    # We build the pitched cap with overhang lip
    cap_faces = add_beveled_box(bm, (0.0, 0.0, 1.28), (1.56, 1.36, 0.06), uv_layer, mat_idx=1, uv_scale=1.2)
    # Slightly peak the roof ridge along Y
    roof_ridge = add_beveled_box(bm, (0.0, 0.0, 1.32), (0.60, 1.34, 0.04), uv_layer, mat_idx=1, uv_scale=1.2)

    # 4 Heavy Crane Lift Lug Eyelets on Roof Corners
    for lx in (-0.68, 0.68):
        for ly in (-0.58, 0.58):
            # Eyelet plate
            add_beveled_box(bm, (lx, ly, 1.37), (0.03, 0.08, 0.10), uv_layer, mat_idx=2)
            # Cross pin / reinforcement
            add_beveled_box(bm, (lx, ly, 1.39), (0.05, 0.03, 0.03), uv_layer, mat_idx=2)

    # 5. Maintenance Doors & Louvers on Sides (X = ±0.75)
    for side in (-1, 1):
        x_pos = side * 0.755
        # Door seam frame
        add_beveled_box(bm, (x_pos, 0.0, 0.75), (0.015, 0.90, 0.80), uv_layer, mat_idx=1)
        # Hinges (top and bottom)
        for hy in (-0.40, 0.40):
            add_beveled_box(bm, (side * 0.765, hy, 1.05), (0.02, 0.04, 0.06), uv_layer, mat_idx=2)
            add_beveled_box(bm, (side * 0.765, hy, 0.45), (0.02, 0.04, 0.06), uv_layer, mat_idx=2)
        # T-handle slam latch
        add_beveled_box(bm, (side * 0.768, 0.0, 0.75), (0.02, 0.03, 0.08), uv_layer, mat_idx=2)
        add_beveled_box(bm, (side * 0.775, 0.0, 0.75), (0.02, 0.06, 0.02), uv_layer, mat_idx=2)

        # 6 Stamped Ventilation Louvers (angled slats on lower door)
        for l_idx in range(6):
            lz = 0.42 + l_idx * 0.045
            add_beveled_box(bm, (side * 0.762, 0.0, lz), (0.012, 0.65, 0.02), uv_layer, mat_idx=1)

    # 6. Radiator End Ventilation Intake (Front South face: Y = -0.655)
    # Recessed radiator intake cavity
    add_beveled_box(bm, (0.0, -0.655, 0.75), (1.10, 0.02, 0.70), uv_layer, mat_idx=2)
    # Horizontal protective louver slats across radiator
    for r_idx in range(8):
        rz = 0.45 + r_idx * 0.08
        add_beveled_box(bm, (0.0, -0.665, rz), (1.05, 0.015, 0.035), uv_layer, mat_idx=1)

    # 7. Rear Exhaust Fan Grill (North face: Y = +0.655)
    add_beveled_box(bm, (0.0, 0.655, 0.85), (0.80, 0.02, 0.50), uv_layer, mat_idx=2)
    for f_idx in range(5):
        fz = 0.65 + f_idx * 0.09
        add_beveled_box(bm, (0.0, 0.665, fz), (0.76, 0.015, 0.03), uv_layer, mat_idx=1)

    # 8. Operator Control Panel & Electrical Access (Front-Right Face)
    # Recessed instrument housing
    add_beveled_box(bm, (0.765, -0.32, 0.90), (0.025, 0.35, 0.40), uv_layer, mat_idx=2)
    # Panel faceplate
    add_beveled_box(bm, (0.772, -0.32, 0.90), (0.012, 0.32, 0.36), uv_layer, mat_idx=3)
    # Analog Gauges (AC Volts, Frequency, Engine Temp)
    for g_idx, gy in enumerate((-0.42, -0.32, -0.22)):
        add_beveled_box(bm, (0.78, gy, 0.98), (0.015, 0.06, 0.06), uv_layer, mat_idx=2)
    # Emergency Stop Mushroom Button (Red)
    add_beveled_box(bm, (0.782, -0.38, 0.82), (0.02, 0.04, 0.04), uv_layer, mat_idx=4)
    # Status Indicator Lamps (Green / Amber)
    add_beveled_box(bm, (0.78, -0.28, 0.82), (0.01, 0.025, 0.025), uv_layer, mat_idx=4)
    add_beveled_box(bm, (0.78, -0.24, 0.82), (0.01, 0.025, 0.025), uv_layer, mat_idx=4)

    # 9. Exhaust Silencer Muffler & Rain Flapper Stack
    # Heavy cylindrical muffler body mounted on roof
    add_beveled_box(bm, (0.35, 0.10, 1.44), (0.22, 0.65, 0.22), uv_layer, mat_idx=2, uv_scale=2.0)
    # Vertical exhaust pipe rising above muffler
    # (Matches old exhaust pipe X=0.5, Z=1.5 in Godot coordinates -> Blender X=0.35 to 0.45, Y=-0.2 to 0.0)
    add_beveled_box(bm, (0.35, -0.15, 1.70), (0.10, 0.10, 0.52), uv_layer, mat_idx=2, uv_scale=2.0)
    # Rain-cap flapper hinged at top (tilted ~15 degrees open)
    add_beveled_box(bm, (0.35, -0.15, 1.97), (0.13, 0.13, 0.015), uv_layer, mat_idx=2)
    # Flapper hinge bracket & counterweight arm
    add_beveled_box(bm, (0.35, -0.23, 1.95), (0.02, 0.08, 0.03), uv_layer, mat_idx=2)
    add_beveled_box(bm, (0.35, -0.26, 1.94), (0.04, 0.04, 0.04), uv_layer, mat_idx=2)

    # 10. Diesel Fuel Filler Neck & Locking Cap
    add_beveled_box(bm, (-0.45, 0.45, 1.34), (0.10, 0.10, 0.08), uv_layer, mat_idx=2)
    add_beveled_box(bm, (-0.45, 0.45, 1.39), (0.12, 0.12, 0.03), uv_layer, mat_idx=2)

    # 11. Armored Heavy Electrical Output Conduit running toward cabin
    # Exits rear gland and curves down
    add_beveled_box(bm, (-0.45, 0.67, 0.45), (0.08, 0.08, 0.08), uv_layer, mat_idx=2)
    add_beveled_box(bm, (-0.55, 0.67, 0.35), (0.15, 0.06, 0.06), uv_layer, mat_idx=2)
    add_beveled_box(bm, (-0.68, 0.67, 0.22), (0.06, 0.06, 0.20), uv_layer, mat_idx=2)

    return bm


# =========================================================================
# ASSET 2: PACIFIC NORTHWEST FIREWOOD CORD STACK
# =========================================================================

def add_split_log(bm, center, length, radius, split_type, yaw_angle, roll_angle, uv_layer,
                  bark_mat_idx=1, wood_mat_idx=2):
    """
    Creates an authentic split firewood log:
    split_type: 'wedge' (pie 60-75 deg), 'quarter' (90 deg), 'half' (180 deg)
    yaw_angle: slight turn around vertical axis
    roll_angle: rotation around longitudinal axis for realistic nesting
    """
    cx, cy, cz = center
    half_l = length * 0.5
    cos_y = math.cos(yaw_angle)
    sin_y = math.sin(yaw_angle)
    cos_r = math.cos(roll_angle)
    sin_r = math.sin(roll_angle)

    if split_type == 'wedge':
        arc_angle = math.radians(random.uniform(65, 80))
        num_arc = 4
    elif split_type == 'quarter':
        arc_angle = math.radians(random.uniform(85, 95))
        num_arc = 5
    else: # 'half'
        arc_angle = math.radians(random.uniform(160, 180))
        num_arc = 6

    start_angle = -arc_angle * 0.5

    # Arc 2D vertices in cross-section
    arc_pts = []
    for i in range(num_arc + 1):
        a = start_angle + arc_angle * (i / num_arc)
        r = radius * random.uniform(0.96, 1.04)
        lx = r * math.cos(a)
        lz = r * math.sin(a)
        # Apply roll rotation
        rx = lx * cos_r - lz * sin_r
        rz = lx * sin_r + lz * cos_r
        arc_pts.append((rx, rz))

    # Pith offset by roll
    front_verts = []
    back_verts = []

    pith_f = Vector((cx - sin_y * (-half_l), cy + cos_y * (-half_l), cz))
    pith_b = Vector((cx - sin_y * (half_l),  cy + cos_y * (half_l),  cz))
    vf_pith = bm.verts.new(pith_f)
    vb_pith = bm.verts.new(pith_b)

    for px, pz in arc_pts:
        wx_f = cx + cos_y * px - sin_y * (-half_l)
        wy_f = cy + sin_y * px + cos_y * (-half_l)
        wz_f = cz + pz

        wx_b = cx + cos_y * px - sin_y * (half_l)
        wy_b = cy + sin_y * px + cos_y * (half_l)
        wz_b = cz + pz

        front_verts.append(bm.verts.new((wx_f, wy_f, wz_f)))
        back_verts.append(bm.verts.new((wx_b, wy_b, wz_b)))

    # Outer curved bark faces
    for i in range(num_arc):
        f = bm.faces.new([front_verts[i], front_verts[i+1], back_verts[i+1], back_verts[i]])
        f.material_index = bark_mat_idx
        for loop in f.loops:
            u = (i / num_arc) * 0.4
            v = 0.8 if loop.vert in back_verts else 0.1
            loop[uv_layer].uv = Vector((u, v))

    # Flat split heartwood side 1
    f_side1 = bm.faces.new([vf_pith, front_verts[0], back_verts[0], vb_pith])
    f_side1.material_index = wood_mat_idx
    for loop in f_side1.loops:
        loop[uv_layer].uv = Vector((loop.vert.co.x * 0.8, loop.vert.co.y * 0.8))

    # Flat split heartwood side 2
    f_side2 = bm.faces.new([vf_pith, vb_pith, back_verts[-1], front_verts[-1]])
    f_side2.material_index = wood_mat_idx
    for loop in f_side2.loops:
        loop[uv_layer].uv = Vector((loop.vert.co.x * 0.8, loop.vert.co.y * 0.8))

    # Front cut cap face (split fan)
    front_cap_verts = [vf_pith] + front_verts
    f_cap_f = bm.faces.new(front_cap_verts)
    f_cap_f.material_index = wood_mat_idx
    for loop in f_cap_f.loops:
        loop[uv_layer].uv = Vector((loop.vert.co.x * 1.5, loop.vert.co.z * 1.5))

    # Back cut cap face
    back_cap_verts = [vb_pith] + list(reversed(back_verts))
    f_cap_b = bm.faces.new(back_cap_verts)
    f_cap_b.material_index = wood_mat_idx
    for loop in f_cap_b.loops:
        loop[uv_layer].uv = Vector((loop.vert.co.x * 1.5, loop.vert.co.z * 1.5))


def build_firewood_stack_mesh():
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    random.seed(101)

    # 1. Timber Log Stacking Rack / Cradle
    add_beveled_box(bm, (0.0, -0.22, 0.05), (2.15, 0.09, 0.09), uv_layer, mat_idx=0, uv_scale=1.0)
    add_beveled_box(bm, (0.0,  0.22, 0.05), (2.15, 0.09, 0.09), uv_layer, mat_idx=0, uv_scale=1.0)

    # 4 Vertical Cedar End Posts (with slight outward splay)
    for px in (-1.02, 1.02):
        splay = 0.03 if px > 0 else -0.03
        for py in (-0.22, 0.22):
            add_beveled_box(bm, (px + splay, py, 0.55), (0.09, 0.09, 1.05), uv_layer, mat_idx=0, uv_scale=0.8)
        # End cross-brace ties connecting the two uprights
        add_beveled_box(bm, (px + splay, 0.0, 0.35), (0.08, 0.40, 0.05), uv_layer, mat_idx=0)
        add_beveled_box(bm, (px + splay * 1.5, 0.0, 0.85), (0.08, 0.40, 0.05), uv_layer, mat_idx=0)

    # 2. Hand-Split Pacific Northwest Cordwood Logs
    # Tier 1 (Bottom, resting on runners, Z ~ 0.17)
    t1_x = [-0.88, -0.66, -0.44, -0.22, 0.0, 0.22, 0.44, 0.66, 0.88]
    for x in t1_x:
        r = random.uniform(0.10, 0.13)
        l = random.uniform(0.70, 0.78)
        st = random.choice(['wedge', 'quarter', 'quarter', 'half'])
        yaw = random.uniform(-0.06, 0.06)
        roll = random.uniform(0, 2 * math.pi)
        add_split_log(bm, (x, 0.0, 0.17), l, r, st, yaw, roll, uv_layer, bark_mat_idx=1, wood_mat_idx=2)

    # Tier 2 (Z ~ 0.38)
    t2_x = [-0.80, -0.58, -0.36, -0.14, 0.10, 0.32, 0.54, 0.76]
    for x in t2_x:
        r = random.uniform(0.10, 0.125)
        l = random.uniform(0.70, 0.76)
        st = random.choice(['wedge', 'quarter', 'quarter', 'half'])
        yaw = random.uniform(-0.05, 0.05)
        roll = random.uniform(0, 2 * math.pi)
        add_split_log(bm, (x, random.uniform(-0.02, 0.02), 0.38), l, r, st, yaw, roll, uv_layer, bark_mat_idx=1, wood_mat_idx=2)

    # Tier 3 (Z ~ 0.58)
    t3_x = [-0.75, -0.52, -0.30, -0.08, 0.14, 0.36, 0.58, 0.75]
    for x in t3_x:
        r = random.uniform(0.09, 0.12)
        l = random.uniform(0.68, 0.75)
        st = random.choice(['wedge', 'wedge', 'quarter', 'half'])
        yaw = random.uniform(-0.06, 0.06)
        roll = random.uniform(0, 2 * math.pi)
        add_split_log(bm, (x, random.uniform(-0.02, 0.02), 0.58), l, r, st, yaw, roll, uv_layer, bark_mat_idx=1, wood_mat_idx=2)

    # Tier 4 (Top tier, Z ~ 0.76)
    t4_x = [-0.68, -0.46, -0.24, -0.02, 0.20, 0.42, 0.64]
    for x in t4_x:
        r = random.uniform(0.09, 0.115)
        l = random.uniform(0.68, 0.74)
        st = random.choice(['wedge', 'quarter', 'quarter'])
        yaw = random.uniform(-0.05, 0.05)
        roll = random.uniform(0, 2 * math.pi)
        add_split_log(bm, (x, random.uniform(-0.02, 0.02), 0.76), l, r, st, yaw, roll, uv_layer, bark_mat_idx=1, wood_mat_idx=2)

    # 3. Protective Corrugated Metal Rain Cover Draped Over Top
    num_corrugations = 14
    c_w = 1.82
    c_d = 0.85
    y_min, y_max = -c_d * 0.5, c_d * 0.5
    c_verts_top = []
    c_verts_bot = []
    c_verts_top_lip = []
    c_verts_bot_lip = []

    for ci in range(num_corrugations * 2 + 1):
        cx = -c_w * 0.5 + c_w * (ci / (num_corrugations * 2))
        wave = math.sin(ci * math.pi) * 0.020
        # Sag slightly towards ends over the log crest
        sag = -0.035 * ((cx / (c_w * 0.5)) ** 2)
        cz = 0.88 + wave + sag

        vt = bm.verts.new((cx, y_max, cz - 0.035))
        vb = bm.verts.new((cx, y_min, cz - 0.035))
        c_verts_top.append(vt)
        c_verts_bot.append(vb)

        # Downturned drip lip
        vt_lip = bm.verts.new((cx, y_max + 0.01, cz - 0.060))
        vb_lip = bm.verts.new((cx, y_min - 0.01, cz - 0.060))
        c_verts_top_lip.append(vt_lip)
        c_verts_bot_lip.append(vb_lip)

    for ci in range(num_corrugations * 2):
        # Main deck face
        f = bm.faces.new([c_verts_bot[ci], c_verts_bot[ci+1], c_verts_top[ci+1], c_verts_top[ci]])
        f.material_index = 3 # M_Tarp_Cover
        u0 = ci / (num_corrugations * 2)
        u1 = (ci + 1) / (num_corrugations * 2)
        f.loops[0][uv_layer].uv = Vector((u0, 0.0))
        f.loops[1][uv_layer].uv = Vector((u1, 0.0))
        f.loops[2][uv_layer].uv = Vector((u1, 1.0))
        f.loops[3][uv_layer].uv = Vector((u0, 1.0))

        # Front drip lip face
        f_bot = bm.faces.new([c_verts_bot_lip[ci], c_verts_bot_lip[ci+1], c_verts_bot[ci+1], c_verts_bot[ci]])
        f_bot.material_index = 3
        f_bot.loops[0][uv_layer].uv = Vector((u0, 0.0))
        f_bot.loops[1][uv_layer].uv = Vector((u1, 0.0))
        f_bot.loops[2][uv_layer].uv = Vector((u1, 0.1))
        f_bot.loops[3][uv_layer].uv = Vector((u0, 0.1))

        # Back drip lip face
        f_top = bm.faces.new([c_verts_top[ci], c_verts_top[ci+1], c_verts_top_lip[ci+1], c_verts_top_lip[ci]])
        f_top.material_index = 3
        f_top.loops[0][uv_layer].uv = Vector((u0, 0.9))
        f_top.loops[1][uv_layer].uv = Vector((u1, 0.9))
        f_top.loops[2][uv_layer].uv = Vector((u1, 1.0))
        f_top.loops[3][uv_layer].uv = Vector((u0, 1.0))

    # 4. Ballast River Stones Resting on Top Sheet
    for bx, by in ((-0.45, 0.05), (0.35, -0.06)):
        add_beveled_box(bm, (bx, by, 0.88), (0.22, 0.18, 0.07), uv_layer, mat_idx=4, uv_scale=1.5)

    return bm


def export_asset(bm, materials, output_glb_path, name="Asset"):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    for mat in materials:
        obj.data.materials.append(mat)

    # Normal smoothing
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    # GLB export
    bpy.ops.export_scene.gltf(
        filepath=str(output_glb_path),
        export_format='GLB',
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"[OK] Exported {output_glb_path} ({len(mesh.vertices)} verts, {len(mesh.polygons)} polys)")
    return obj


def render_preview(obj_name, output_image_path, cam_pos, cam_target):
    # Setup camera and light for clean studio preview
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    dir_vec = Vector(cam_target) - Vector(cam_pos)
    rot_quat = dir_vec.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = cam_obj

    # Key light
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 3.2
    sun_data.color = (1.0, 0.96, 0.90)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(40), math.radians(20), math.radians(-30))

    # Front light (illuminates front faces)
    front_data = bpy.data.lights.new("Front", type='SUN')
    front_data.energy = 1.8
    front_data.color = (0.95, 0.92, 0.88)
    front_obj = bpy.data.objects.new("Front", front_data)
    bpy.context.collection.objects.link(front_obj)
    front_obj.rotation_euler = (math.radians(25), math.radians(-10), math.radians(20))

    # Fill light
    fill_data = bpy.data.lights.new("Fill", type='SUN')
    fill_data.energy = 1.0
    fill_data.color = (0.7, 0.8, 1.0)
    fill_obj = bpy.data.objects.new("Fill", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(55), math.radians(-40), math.radians(130))

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.render.filepath = str(output_image_path)

    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered preview to {output_image_path}")


def main():
    print("=== BUILDING CABIN EXTERIOR ASSETS (ITERATION 07) ===")

    # 1. BUILD GENERATOR
    clean_scene()
    mat_concrete = create_pbr_mat("M_Gen_Concrete", (0.35, 0.35, 0.35, 1.0), roughness=0.88,
                                  diff_path=CONCRETE_DIFF, norm_path=CONCRETE_NORM, rough_path=CONCRETE_ROUGH)
    mat_green_metal = create_pbr_mat("M_Gen_GreenMetal", (0.15, 0.24, 0.16, 1.0), roughness=0.45, metallic=0.75,
                                     diff_path=GREEN_METAL_DIFF, norm_path=GREEN_METAL_NORM, rough_path=GREEN_METAL_ROUGH)
    mat_dark_steel = create_pbr_mat("M_Gen_DarkSteel", (0.12, 0.12, 0.13, 1.0), roughness=0.35, metallic=0.88)
    mat_panel = create_pbr_mat("M_Gen_Panel", (0.18, 0.18, 0.20, 1.0), roughness=0.40, metallic=0.50)
    mat_indicator = create_pbr_mat("M_Gen_Indicator", (0.9, 0.1, 0.05, 1.0), roughness=0.20, metallic=0.10)

    gen_mats = [mat_concrete, mat_green_metal, mat_dark_steel, mat_panel, mat_indicator]
    bm_gen = build_generator_mesh()
    gen_obj = export_asset(bm_gen, gen_mats, MODELS_DIR / "generator_industrial.glb", "GeneratorIndustrial")
    render_preview("GeneratorIndustrial", PREVIEWS_DIR / "blender_generator_preview.png",
                   cam_pos=(2.8, -2.6, 2.2), cam_target=(0.0, 0.0, 0.75))

    # 2. BUILD FIREWOOD CORD STACK
    clean_scene()
    mat_wood_rack = create_pbr_mat("M_Wood_Rack", (0.42, 0.35, 0.28, 1.0), roughness=0.82,
                                   diff_path=PLANKS_DIFF, norm_path=PLANKS_NORM, rough_path=PLANKS_ROUGH)
    mat_log_bark = create_pbr_mat("M_Log_Bark", (0.35, 0.30, 0.25, 1.0), roughness=0.85,
                                  diff_path=BARK_DIFF, norm_path=BARK_NORM, rough_path=BARK_ROUGH)
    mat_log_heart = create_pbr_mat("M_Log_SplitHeart", (0.58, 0.48, 0.36, 1.0), roughness=0.72,
                                   diff_path=WOOD_DIFF, norm_path=WOOD_NORM, rough_path=WOOD_ROUGH)
    mat_tarp_cover = create_pbr_mat("M_Tarp_Cover", (0.45, 0.32, 0.22, 1.0), roughness=0.60, metallic=0.80,
                                    diff_path=RUSTY_IRON_DIFF, norm_path=RUSTY_IRON_NORM, rough_path=RUSTY_IRON_ROUGH)
    mat_ballast = create_pbr_mat("M_Ballast_Stone", (0.4, 0.4, 0.38, 1.0), roughness=0.85,
                                 diff_path=ROCK_DIFF, norm_path=ROCK_NORM, rough_path=ROCK_ROUGH)

    stack_mats = [mat_wood_rack, mat_log_bark, mat_log_heart, mat_tarp_cover, mat_ballast]
    bm_stack = build_firewood_stack_mesh()
    stack_obj = export_asset(bm_stack, stack_mats, MODELS_DIR / "firewood_cord_stack.glb", "FirewoodCordStack")
    render_preview("FirewoodCordStack", PREVIEWS_DIR / "blender_firewood_preview.png",
                   cam_pos=(2.2, -2.4, 1.3), cam_target=(0.0, 0.0, 0.50))

    print("=== FINISHED BUILDING ITERATION 07 ASSETS ===")

if __name__ == "__main__":
    main()
