#!/usr/bin/env python3
"""
Sasquatch Hero Sculpt Builder (Phase 2 / Issue #29 & #6).

REWORKED (iteration 3): the previous version displaced a weight-less,
re-remeshed blockout by hard-coded GLOBAL Z coordinate trig functions. Because
the blockout never actually posed the rig (it only translated verts by weight),
the "forward-leaning bent-knee crouch" never happened, and the global-Z facial
features landed as flat plates over a hollow chest.

This version derives the sculpt directly from the rigged base mesh so anatomy
is driven by the skeleton and a real pose:

  1. Import source/base_mesh.glb (rigged human biped, faces +X, arms along Y)
  2. Scale to hero size, subdivide for shaping resolution
  3. Shape anatomy in REST pose (broad shoulders/trapezius, deep barrel chest,
     long thick arms, large plantigrade feet, ape cranium + face)
  4. POSE the rig into the reference's forward-leaning, bent-knee stalking
     crouch, long arms hanging forward past the thighs
  5. Voxel-remesh to a continuous watertight high-res surface (removes seams
     and hollow shells), smooth, ground to z = 0, shade smooth
  6. Save source/hero_sculpt.blend and export build/hero_sculpt.obj

`--out-blend` / `--out-obj` allow writing to a scratch location while iterating.
"""

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Quaternion

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_GLB = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source" / "base_mesh.glb"
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source"
BUILD_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "build"

# Design space (rest pose): +X is FORWARD (face/chest/toes), +Y is the
# character's left, +Z is up. Everything is authored here, then the whole body
# is posed, then finally rotated so the face points +Y (the render convention).

SCALE = 1.40            # hero scale-up (matches the approved blockout mass)
VOXEL = 0.011           # ~1.1 cm remesh for crisp muscular & facial detail
ROT_Z_DEG = 90.0        # final facing: +X -> +Y for the diagnostic cameras


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-blend", default=str(SOURCE_DIR / "hero_sculpt.blend"))
    ap.add_argument("--out-obj", default=str(BUILD_DIR / "hero_sculpt.obj"))
    ap.add_argument("--voxel", type=float, default=VOXEL)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return ap.parse_args(argv)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)


# ---------------------------------------------------------------------------
# Weight helpers
# ---------------------------------------------------------------------------
G_HEAD = ["spine.004", "spine.005"]
G_TRAP = ["spine.003", "shoulder.L", "shoulder.R"]
G_TORSO = ["spine", "spine.001", "spine.002", "spine.003", "pelvis.L", "pelvis.R"]
G_ARMUP_L = ["upper_arm.L"]
G_ARMUP_R = ["upper_arm.R"]
G_ARMLO_L = ["forearm.L"]
G_ARMLO_R = ["forearm.R"]
G_HAND = ["hand.L", "hand.R", "thumb.01.L", "thumb.02.L", "thumb.03.L",
          "f_index.01.L", "f_index.02.L", "f_index.03.L",
          "f_middle.01.L", "f_middle.02.L", "f_middle.03.L",
          "f_ring.01.L", "f_ring.02.L", "f_ring.03.L",
          "f_pinky.01.L", "f_pinky.02.L", "f_pinky.03.L",
          "thumb.01.R", "thumb.02.R", "thumb.03.R",
          "f_index.01.R", "f_index.02.R", "f_index.03.R",
          "f_middle.01.R", "f_middle.02.R", "f_middle.03.R",
          "f_ring.01.R", "f_ring.02.R", "f_ring.03.R",
          "f_pinky.01.R", "f_pinky.02.R", "f_pinky.03.R"]
G_THIGH_L = ["thigh.L"]
G_THIGH_R = ["thigh.R"]
G_SHIN_L = ["shin.L"]
G_SHIN_R = ["shin.R"]
G_FOOT_L = ["foot.L", "toe.L", "heel.02.L"]
G_FOOT_R = ["foot.R", "toe.R", "heel.02.R"]


def make_weight_fn(vg_map, names):
    idx = [vg_map[n] for n in names if n in vg_map]

    def wf(v):
        total = 0.0
        for g in v.groups:
            if g.group in idx:
                total += g.weight
        return min(total, 1.0)
    return wf


def blend(fns):
    def wf(v):
        return min(1.0, sum(f(v) for f in fns))
    return wf


# ---------------------------------------------------------------------------
# Pose math
# ---------------------------------------------------------------------------
def q_to(cur, desired):
    return cur.normalized().rotation_difference(Vector(desired).normalized())


def tp(p, steps):
    """Apply completed (pivot, quat) steps to an anchor point."""
    for piv, q in steps:
        p = piv + q @ (p - piv)
    return p


def apply_step(verts, wf, pivot, quat):
    for v in verts:
        w = wf(v)
        if w <= 0.0:
            continue
        rel = v.co - pivot
        v.co = v.co + w * ((quat @ rel) - rel)


# ---------------------------------------------------------------------------
# Anatomy (rest pose)
# ---------------------------------------------------------------------------
def shape_anatomy(mesh_obj):
    mesh = mesh_obj.data
    vg_map = {vg.name: vg.index for vg in mesh_obj.vertex_groups}
    verts = mesh.vertices

    w_head = make_weight_fn(vg_map, G_HEAD)
    w_trap = make_weight_fn(vg_map, G_TRAP)
    w_torso = make_weight_fn(vg_map, G_TORSO)
    w_armup = blend([make_weight_fn(vg_map, G_ARMUP_L), make_weight_fn(vg_map, G_ARMUP_R)])
    w_armlo = blend([make_weight_fn(vg_map, G_ARMLO_L), make_weight_fn(vg_map, G_ARMLO_R)])
    w_hand = make_weight_fn(vg_map, G_HAND)
    w_thigh = blend([make_weight_fn(vg_map, G_THIGH_L), make_weight_fn(vg_map, G_THIGH_R)])
    w_shin = blend([make_weight_fn(vg_map, G_SHIN_L), make_weight_fn(vg_map, G_SHIN_R)])
    w_foot = blend([make_weight_fn(vg_map, G_FOOT_L), make_weight_fn(vg_map, G_FOOT_R)])

    for v in verts:
        co = v.co
        x, y, z = co.x, co.y, co.z

        # --- Torso: broad shoulders/trapezius (Y width) + deep barrel chest (X) ---
        wt = w_torso(v)
        wtrap = w_trap(v)
        if wt > 0.02 or wtrap > 0.02:
            co.y *= (1.0 + 0.55 * wt + 0.55 * wtrap)      # widen across shoulders/lats
            co.x *= (1.0 + 0.42 * wt)                     # deepen chest/back
            # anterior barrel belly (removes the hollow shell)
            if x > 0.0:
                co.x += 0.05 * wt
        # Trapezius hump rising into the skull (no neck collar)
        if wtrap > 0.02 and z > 1.05:
            hump = min(1.0, (z - 1.05) / 0.45)
            co.z += 0.14 * hump * wtrap
            co.x -= 0.06 * hump * wtrap                       # hump sits behind (-X)

        # --- Arms: thicken + lengthen forward-hanging muscle ---
        wau = w_armup(v)
        wal = w_armlo(v)
        wh = w_hand(v)
        if wau > 0.02:
            co.y *= (1.0 + 0.45 * wau)
            co.x *= (1.0 + 0.40 * wau)
        if wal > 0.02:
            co.y *= (1.0 + 0.65 * wal)                        # colossal forearm
            co.x *= (1.0 + 0.55 * wal)
        if wh > 0.02:
            co.y *= (1.0 + 0.70 * wh)                         # big ape hands
            co.x *= (1.0 + 0.55 * wh)
            co.z -= 0.10 * wh

        # --- Legs: bowed muscular; wide splayed plantigrade feet ---
        wth = w_thigh(v)
        wsh = w_shin(v)
        wft = w_foot(v)
        if wth > 0.02:
            co.y *= (1.0 + 0.40 * wth)
            co.x *= (1.0 + 0.30 * wth)
        if wsh > 0.02:
            co.y *= (1.0 + 0.35 * wsh)
            co.x *= (1.0 + 0.28 * wsh)
        if wft > 0.02:
            co.y *= (1.0 + 0.55 * wft)
            co.x *= (1.0 + 0.35 * wft)
            co.z *= (1.0 - 0.25 * wft)                        # flatten

        # --- Head: broad ape cranium ---
        whd = w_head(v)
        if whd > 0.02:
            co.y *= (1.0 + 0.40 * whd)

    # --- Cranium & face, relative to the actual head bounds ---
    head_verts = [v for v in verts if w_head(v) > 0.4]
    if head_verts:
        hx = [v.co.x for v in head_verts]
        hy = [v.co.y for v in head_verts]
        hz = [v.co.z for v in head_verts]
        hxmax = max(hx)
        hyc = (min(hy) + max(hy)) * 0.5
        hzmin, hzmax = min(hz), max(hz)
        hr = max(hzmax - hzmin, 1e-4)
        front = hxmax

        for v in head_verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            # Conical sagittal crest sloping backward
            t = min(1.0, max(0.0, (z - (hzmax - 0.20)) / 0.20))
            if t > 0.0 and abs(y - hyc) < 0.14:
                v.co.z += 0.10 * t
                v.co.x -= 0.06 * t
            # Heavy supraorbital brow shelf
            upper = hzmin + 0.62 * hr
            if x > front - 0.10 and upper < z < upper + 0.16:
                v.co.x += 0.045
            # Deep-set orbital sockets
            eye_z = hzmin + 0.72 * hr
            for sy in (0.06, -0.06):
                if abs(y - (hyc + sy)) < 0.05 and abs(z - eye_z) < 0.06:
                    v.co.x -= 0.035
            # Broad simian nose + prognathic muzzle
            if z < hzmin + 0.45 * hr and x > front - 0.12:
                v.co.x += 0.05
                v.co.y *= 1.06

    mesh.update()


# ---------------------------------------------------------------------------
# Pose (forward-leaning bent-knee stalking crouch)
# ---------------------------------------------------------------------------
def pose_rig(mesh_obj, anchors):
    mesh = mesh_obj.data
    vg_map = {vg.name: vg.index for vg in mesh_obj.vertex_groups}
    verts = mesh.vertices

    w_upper = blend([
        make_weight_fn(vg_map, G_TORSO),
        make_weight_fn(vg_map, G_HEAD),
        make_weight_fn(vg_map, G_TRAP),
        make_weight_fn(vg_map, G_ARMUP_L), make_weight_fn(vg_map, G_ARMUP_R),
        make_weight_fn(vg_map, G_ARMLO_L), make_weight_fn(vg_map, G_ARMLO_R),
        make_weight_fn(vg_map, G_HAND),
    ])
    w_head = make_weight_fn(vg_map, G_HEAD)
    w_thigh_l = make_weight_fn(vg_map, G_THIGH_L)
    w_thigh_r = make_weight_fn(vg_map, G_THIGH_R)
    w_shin_l = make_weight_fn(vg_map, G_SHIN_L)
    w_shin_r = make_weight_fn(vg_map, G_SHIN_R)
    w_armup_l = make_weight_fn(vg_map, G_ARMUP_L)
    w_armup_r = make_weight_fn(vg_map, G_ARMUP_R)
    w_armlo_l = make_weight_fn(vg_map, G_ARMLO_L)
    w_armlo_r = make_weight_fn(vg_map, G_ARMLO_R)

    hip_l, hip_r = anchors["hip_L"], anchors["hip_R"]
    knee_l, knee_r = anchors["knee_L"], anchors["knee_R"]
    ankle_l, ankle_r = anchors["ankle_L"], anchors["ankle_R"]
    sh_l, sh_r = anchors["shoulder_L"], anchors["shoulder_R"]
    el_l, el_r = anchors["elbow_L"], anchors["elbow_R"]
    hd_l, hd_r = anchors["hand_L"], anchors["hand_R"]
    root = anchors["spine_root"]
    neck = anchors["neck"]

    q_lean = Quaternion((0.0, 1.0, 0.0), math.radians(32.0))
    q_head = Quaternion((0.0, 1.0, 0.0), math.radians(14.0))

    # --- 1. Thighs: knees forward/down ---
    q_tl = q_to(knee_l - hip_l, Vector((0.55, 0.30, -1.0)))
    q_tr = q_to(knee_r - hip_r, Vector((0.55, -0.30, -1.0)))
    apply_step(verts, w_thigh_l, hip_l, q_tl)
    apply_step(verts, w_thigh_r, hip_r, q_tr)

    # --- 2. Shins: ankles back under the hips (deep bent knee) ---
    knee_l2 = tp(knee_l, [(hip_l, q_tl)])
    knee_r2 = tp(knee_r, [(hip_r, q_tr)])
    q_sl = q_to(tp(ankle_l, [(hip_l, q_tl)]) - knee_l2, Vector((-0.60, 0.06, -1.0)))
    q_sr = q_to(tp(ankle_r, [(hip_r, q_tr)]) - knee_r2, Vector((-0.60, -0.06, -1.0)))
    apply_step(verts, w_shin_l, knee_l2, q_sl)
    apply_step(verts, w_shin_r, knee_r2, q_sr)

    # --- 3. Forward lean of everything above the hips ---
    apply_step(verts, w_upper, root, q_lean)

    # --- 4. Head juts forward out of the shoulder mass ---
    neck2 = tp(neck, [(root, q_lean)])
    apply_step(verts, w_head, neck2, q_head)

    # --- 5. Upper arms swing down & forward ---
    sh_l2 = tp(sh_l, [(root, q_lean)])
    sh_r2 = tp(sh_r, [(root, q_lean)])
    q_aul = q_to(el_l - sh_l, Vector((0.45, 0.28, -1.0)))
    q_aur = q_to(el_r - sh_r, Vector((0.45, -0.28, -1.0)))
    apply_step(verts, w_armup_l, sh_l2, q_aul)
    apply_step(verts, w_armup_r, sh_r2, q_aur)

    # --- 6. Forearms continue down (slight elbow bend) ---
    el_l2 = tp(el_l, [(root, q_lean), (sh_l2, q_aul)])
    el_r2 = tp(el_r, [(root, q_lean), (sh_r2, q_aur)])
    q_all_ = q_to(tp(hd_l, [(root, q_lean), (sh_l2, q_aul)]) - el_l2, Vector((0.35, 0.12, -1.0)))
    q_alr = q_to(tp(hd_r, [(root, q_lean), (sh_r2, q_aur)]) - el_r2, Vector((0.35, -0.12, -1.0)))
    apply_step(verts, w_armlo_l, el_l2, q_all_)
    apply_step(verts, w_armlo_r, el_r2, q_alr)

    mesh.update()


def main():
    args = parse_args()
    clean_scene()
    print("=" * 64)
    print(" AUTHORING HIGH-RESOLUTION CLASSIC BIGFOOT HERO SCULPT (rewrite)")
    print("=" * 64)

    bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))

    mesh_obj = None
    arm_obj = None
    for o in list(bpy.context.scene.objects):
        if o.type == "MESH" and o.name != "Icosphere":
            mesh_obj = o
        elif o.type == "ARMATURE":
            arm_obj = o
    if mesh_obj is None:
        raise RuntimeError(f"No mesh found in {SOURCE_GLB}")

    # Detach from the rig; we pose explicitly rather than via the armature.
    mw = mesh_obj.matrix_world.copy()
    mesh_obj.parent = None
    mesh_obj.matrix_world = mw
    for mod in list(mesh_obj.modifiers):
        mesh_obj.modifiers.remove(mod)
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # Pull joint anchors off the rig before deleting it (scaled to hero size).
    bone = {b.name: b for b in arm_obj.data.bones} if arm_obj else {}

    def anchor(name):
        b = bone.get(name)
        if not b:
            return Vector((0, 0, 0))
        return (arm_obj.matrix_world @ b.head_local.copy()) * SCALE
    anchors = {
        "hip_L": anchor("thigh.L"), "hip_R": anchor("thigh.R"),
        "knee_L": anchor("shin.L"), "knee_R": anchor("shin.R"),
        "ankle_L": anchor("foot.L"), "ankle_R": anchor("foot.R"),
        "shoulder_L": anchor("upper_arm.L"), "shoulder_R": anchor("upper_arm.R"),
        "elbow_L": anchor("forearm.L"), "elbow_R": anchor("forearm.R"),
        "hand_L": anchor("hand.L"), "hand_R": anchor("hand.R"),
        "spine_root": anchor("spine"),
        "neck": anchor("spine.005"),
    }
    if arm_obj:
        bpy.data.objects.remove(arm_obj, do_unlink=True)
    for o in list(bpy.context.scene.objects):
        if o.name == "Icosphere":
            bpy.data.objects.remove(o, do_unlink=True)

    # Scale to hero size.
    for v in mesh_obj.data.vertices:
        v.co *= SCALE

    # Subdivide so the shaping pass has resolution to work with.
    sub = mesh_obj.modifiers.new("PreShapeSubdiv", "SUBSURF")
    sub.levels = 2
    bpy.ops.object.modifier_apply(modifier="PreShapeSubdiv")
    print(f"[OK] base verts after subdiv: {len(mesh_obj.data.vertices)}")

    shape_anatomy(mesh_obj)
    print("[OK] anatomy shaped (rest pose)")

    pose_rig(mesh_obj, anchors)
    print("[OK] posed: forward lean + bent-knee crouch + hanging arms")

    bpy.context.view_layer.update()
    d0 = mesh_obj.dimensions
    print(f">>> posed bounds: X={d0.x:.2f} Y={d0.y:.2f} Z={d0.z:.2f}")

    # Continuous watertight high-res remesh.
    mesh_obj.data.remesh_voxel_size = args.voxel
    bpy.ops.object.voxel_remesh()
    print(f"[OK] voxel remesh -> {len(mesh_obj.data.vertices)} verts")

    # Gentle smoothing to fuse limb junctions / fur volume transitions.
    sm = mesh_obj.modifiers.new("SculptSmooth", "SMOOTH")
    sm.factor = 0.5
    sm.iterations = 6
    bpy.ops.object.modifier_apply(modifier="SculptSmooth")

    sub2 = mesh_obj.modifiers.new("HeroSubsurf", "SUBSURF")
    sub2.levels = 1
    bpy.ops.object.modifier_apply(modifier="HeroSubsurf")

    # Ground to z = 0.
    bpy.context.view_layer.update()
    corners = [mesh_obj.matrix_world @ Vector(c) for c in mesh_obj.bound_box]
    min_z = min(c.z for c in corners)
    mesh_obj.location.z -= min_z
    bpy.ops.object.transform_apply(location=True)

    bpy.ops.object.shade_smooth()

    # Face the +Y render convention.
    mesh_obj.rotation_euler = (0.0, 0.0, math.radians(ROT_Z_DEG))
    bpy.ops.object.transform_apply(rotation=True)

    mat = bpy.data.materials.new("HeroSculptClay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.72, 0.68, 0.64, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.55
        bsdf.inputs["Metallic"].default_value = 0.0
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)

    bpy.context.view_layer.update()
    dims = mesh_obj.dimensions
    vc = len(mesh_obj.data.vertices)
    pc = len(mesh_obj.data.polygons)
    print(f">>> HERO SCULPT STATS: X={dims.x:.2f} Y={dims.y:.2f} Z={dims.z:.2f} "
          f"| verts={vc}, polys={pc} <<<")

    out_blend = Path(args.out_blend)
    out_obj = Path(args.out_obj)
    out_blend.parent.mkdir(parents=True, exist_ok=True)
    out_obj.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
    print(f">>> SAVED HERO SCULPT: {out_blend}")

    bpy.ops.wm.obj_export(
        filepath=str(out_obj),
        export_selected_objects=True,
        forward_axis="NEGATIVE_Z",
        up_axis="Y",
    )
    print(f">>> EXPORTED HERO SCULPT OBJ: {out_obj}")


if __name__ == "__main__":
    main()