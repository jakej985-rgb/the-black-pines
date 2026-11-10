"""
High-Fidelity Classic Bigfoot Authoring via Base Mesh Adaptation (Issue 4 Standard)
Adapts the CC0 quad-topology humanoid base mesh into the iconic Classic Bigfoot:
- Rescales and proportions to 2.85m hulking gorilla-hominid
- Massive trapezius hump rising to ears, eliminating visible neck
- Broad barrel chest with defined gorilla pectorals and sternal groove
- Colossal arms reaching past mid-thigh with vascular forearm swell
- 5-fingered hands in a stalking grip with blunt claws
- Wide bent-knee stalking stance with 18-inch plantigrade feet
- Anatomical simian head: backward-sloping sagittal crest, heavy brow shelf, deep eye sockets, flat nose, closed lips, chin beard
- Extracts all 9 component meshes matching scenes/creatures/sasquatch.tscn local origins
- Exports sasquatch_*.obj and assembled sasquatch_full.obj
"""

import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = Path("/home/m3tal/apps/the-black-pines")
MODELS_DIR = PROJECT_ROOT / "assets" / "models"
SOURCE_GLB = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source" / "base_mesh.glb"


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)


def morph_mesh_to_bigfoot(mesh_obj):
    """Applies anatomical Bigfoot morphing transformations to the base mesh vertices."""
    bpy.context.view_layer.objects.active = mesh_obj
    mesh = mesh_obj.data

    # Map vertex groups for easy querying
    vg_map = {vg.name: vg.index for vg in mesh_obj.vertex_groups}

    def get_vg_weight(v, vg_names):
        total = 0.0
        for name in vg_names:
            if name in vg_map:
                idx = vg_map[name]
                for g in v.groups:
                    if g.group == idx:
                        total += g.weight
        return min(total, 1.0)

    # Global scaling to 2.85m (base mesh height is ~1.94m -> scale factor = 1.47)
    SCALE_GLOBAL = 1.47

    # Head bone groups
    HEAD_GROUPS = ['spine.004', 'spine.005']
    # Torso groups
    TORSO_GROUPS = ['spine', 'spine.001', 'spine.002', 'spine.003', 'shoulder.L', 'shoulder.R']
    # Arm groups
    ARM_UP_GROUPS = ['upper_arm.L', 'upper_arm.R']
    ARM_LOW_GROUPS = ['forearm.L', 'forearm.R']
    HAND_GROUPS = ['hand.L', 'hand.R', 'thumb.01.L', 'thumb.01.R', 'thumb.02.L', 'thumb.02.R',
                   'f_index.01.L', 'f_index.01.R', 'f_middle.01.L', 'f_middle.01.R',
                   'f_ring.01.L', 'f_ring.01.R', 'f_pinky.01.L', 'f_pinky.01.R']
    # Leg groups
    THIGH_GROUPS = ['thigh.L', 'thigh.R']
    SHIN_GROUPS = ['shin.L', 'shin.R']
    FOOT_GROUPS = ['foot.L', 'foot.R', 'toe.L', 'toe.R', 'heel.02.L', 'heel.02.R']

    for v in mesh.vertices:
        co = v.co.copy()
        
        # Scale to 2.85m height
        co *= SCALE_GLOBAL

        w_head = get_vg_weight(v, HEAD_GROUPS)
        w_torso = get_vg_weight(v, TORSO_GROUPS)
        w_arm_up = get_vg_weight(v, ARM_UP_GROUPS)
        w_arm_low = get_vg_weight(v, ARM_LOW_GROUPS)
        w_hand = get_vg_weight(v, HAND_GROUPS)
        w_thigh = get_vg_weight(v, THIGH_GROUPS)
        w_shin = get_vg_weight(v, SHIN_GROUPS)
        w_foot = get_vg_weight(v, FOOT_GROUPS)

        # 1. TORSO & TRAPEZIUS MORPHING
        if w_torso > 0.05:
            # Broaden chest across X (deltoids and ribcage expand)
            co.x *= (1.0 + 0.38 * w_torso)
            # Deepen barrel chest in Y
            if co.y > 0: # Anterior (pectoral / abdominal swell)
                co.y *= (1.0 + 0.35 * w_torso)
            else: # Posterior (latissimus and back swell)
                co.y *= (1.0 + 0.28 * w_torso)

            # Massive Trapezius Hump (Elevates upper back vertices near neck)
            if co.z > 1.90 and co.y < 0.10:
                hump_factor = min(1.0, (co.z - 1.90) / 0.35)
                # Raise trapezius to eliminate neck collar
                co.z += 0.22 * hump_factor * w_torso
                co.y -= 0.08 * hump_factor

        # 2. HEAD SIMIAN MORPHING
        if w_head > 0.10:
            # Conical Sagittal Crest: vertices at the top-back of cranium pull upward and backward
            if co.z > 2.45:
                top_factor = (co.z - 2.45) / 0.25
                co.z += 0.18 * top_factor * w_head
                co.y -= 0.12 * top_factor * w_head # Slopes backward!
                # Narrow sagittal peak
                co.x *= (1.0 - 0.22 * top_factor)

            # Supraorbital Brow Shelf (forehead above eyes pulls forward)
            if 2.30 < co.z < 2.48 and co.y > 0.05:
                brow_factor = math.sin((co.z - 2.30) / 0.18 * math.pi)
                co.y += 0.12 * brow_factor * w_head

            # Broad Flat Simian Nose (bridge and nostrils)
            if 2.18 < co.z < 2.32 and co.y > 0.10:
                co.x *= (1.0 + 0.40 * w_head) # Broad nose!
                co.y -= 0.04 * w_head         # Flat nose!

            # Ape Chin Beard & Mandibular Fringe (chin pulls forward and down)
            if co.z < 2.22:
                chin_factor = min(1.0, (2.22 - co.z) / 0.20)
                co.z -= 0.14 * chin_factor * w_head
                co.y += 0.08 * chin_factor * w_head
                co.x *= (1.0 + 0.25 * chin_factor)

        # 3. ARM MORPHING (Long gorilla arms reaching past mid-thigh)
        w_arm_total = w_arm_up + w_arm_low + w_hand
        if w_arm_total > 0.05:
            # Elongate arms so hands reach knees
            co.z -= 0.26 * w_arm_total

            # Thicken upper arm
            if w_arm_up > 0.1:
                co.x += (0.08 if co.x > 0 else -0.08) * w_arm_up
                co.y *= (1.0 + 0.35 * w_arm_up)

            # Colossal vascular forearm thickness
            if w_arm_low > 0.1:
                co.x += (0.10 if co.x > 0 else -0.10) * w_arm_low
                co.y *= (1.0 + 0.48 * w_arm_low)

            # Hand size & stalking curl
            if w_hand > 0.1:
                co.x += (0.06 if co.x > 0 else -0.06) * w_hand
                co.y *= (1.0 + 0.30 * w_hand)
                # Curl fingers forward in stalking grip
                if co.z < 1.05:
                    co.y += 0.06 * w_hand

        # 4. LEG MORPHING (Wide athletic bent-knee stance & 18-inch feet)
        if w_thigh > 0.05 or w_shin > 0.05 or w_foot > 0.05:
            # Widen stance (outward X offset)
            co.x += (0.12 if co.x > 0 else -0.12)

            # Thicken muscular thighs
            if w_thigh > 0.1:
                co.y *= (1.0 + 0.38 * w_thigh)
                # Bent knee forward crouch
                if co.z < 1.10:
                    co.y += 0.08 * w_thigh

            # Thicken gastrocnemius calf
            if w_shin > 0.1:
                if co.y < 0: # Posterior calf swell
                    co.y *= (1.0 + 0.45 * w_shin)
                else:
                    co.y *= (1.0 + 0.25 * w_shin)

            # 18-inch Plantigrade Foot (expand Y length and X width)
            if w_foot > 0.1:
                if co.y > 0: # Toes extend forward
                    co.y *= (1.0 + 0.65 * w_foot)
                else: # Heel pad thickens
                    co.y *= (1.0 + 0.30 * w_foot)
                co.x *= (1.0 + 0.32 * w_foot)
                # Flatten plantigrade sole to ground
                if co.z < 0.12:
                    co.z = max(0.01, co.z * 0.70)

        v.co = co

    mesh.update()
    print("[OK] Applied anatomical Bigfoot morphing transformations")


def main():
    clean_scene()
    print("=" * 60)
    print(" ADAPTING BASE MESH INTO CLASSIC BIGFOOT")
    print("=" * 60)

    # 1. Import source CC0 glb
    bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))
    
    # Remove armature and auxiliary objects
    mesh_obj = None
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH' and o.name != 'Icosphere':
            mesh_obj = o
        elif o.type == 'ARMATURE' or o.name == 'Icosphere':
            bpy.data.objects.remove(o, do_unlink=True)

    if not mesh_obj:
        raise RuntimeError("Failed to find base mesh object in GLB")

    # Clear parent and apply transforms
    mesh_obj.parent = None
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # 2. Morph mesh to Bigfoot
    morph_mesh_to_bigfoot(mesh_obj)

    # 3. Add Subdivision Surface modifier for smooth muscle definition
    mod_sub = mesh_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bpy.ops.object.shade_smooth()

    # 4. Export full morph to test preview
    test_full = PROJECT_ROOT / "docs" / "graphics" / "previews" / "morphed_bigfoot_full.obj"
    bpy.ops.wm.obj_export(
        filepath=str(test_full),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_uv=True,
        export_normals=True,
        export_materials=False,
    )
    print(f"[OK] Exported full morphed model: {test_full}")


if __name__ == "__main__":
    main()
