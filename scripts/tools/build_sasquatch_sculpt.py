#!/usr/bin/env python3
"""
Sasquatch Hero Sculpt Builder (Phase 2 / Issue #29 & #6).

REWORKED (iteration 3):

The previous generator (build_sasquatch_sculpt.py v1) displaced a weight-less,
re-remeshed blockout by hard-coded GLOBAL-Z trig functions. The blockout never
actually posed the rig (it only translated verts by weight), so the promised
"forward-leaning bent-knee crouch" never happened and the global-Z facial
features landed as flat plates over a hollow chest.

This generator derives the sculpt from the rigged base mesh and (a) shapes
anatomy in REST pose, then (b) poses the rig using real skinning (pose bones +
Armature modifier), then (c) voxel-remeshes to a single continuous surface.

  1. Import source/base_mesh.glb (rigged biped, faces +X, arms along Y)
  2. Scale to hero size, subdivide for shaping resolution
  3. Shape anatomy in REST pose (broad trapezius/shoulders, deep barrel chest,
     thick long arms, large plantigrade feet, ape cranium + face features)
  4. POSE the rig into the reference's forward-leaning, bent-knee stalking
     crouch with long arms hanging down/forward (proper armature skinning)
  5. Bake the pose, voxel-remesh to one watertight surface, smooth, ground
  6. Save source/hero_sculpt.blend, export build/hero_sculpt.obj

`--out-blend` / `--out-obj` allow writing to a scratch location while iterating.
"""

import argparse
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Quaternion

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_GLB = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source" / "base_mesh.glb"
SOURCE_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "source"
BUILD_DIR = PROJECT_ROOT / "assets" / "creatures" / "sasquatch" / "build"

# Design space (rest pose): +X is FORWARD (face/chest/toes), +Y is the
# character's left, +Z is up. Whole body is authored here, posed, then rotated
# so the face points +Y (the diagnostic render convention).
SCALE = 1.40
VOXEL = 0.011
ROT_Z_DEG = 90.0


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

        wt = w_torso(v)
        wtrap = w_trap(v)
        if wt > 0.02 or wtrap > 0.02:
            co.y *= (1.0 + 0.62 * wt + 0.62 * wtrap)      # broad shoulders / lats
            co.x *= (1.0 + 0.68 * wt)                     # deep barrel chest/back
            if x > 0.0:
                co.x += 0.12 * wt                         # anterior belly/chest fullness
        if wtrap > 0.02 and z > 1.05:                     # trapezius hump
            hump = min(1.0, (z - 1.05) / 0.45)
            co.z += 0.15 * hump * wtrap
            co.x -= 0.06 * hump * wtrap

        wau, wal, wh = w_armup(v), w_armlo(v), w_hand(v)
        if wau > 0.02:
            co.y *= (1.0 + 0.48 * wau)
            co.x *= (1.0 + 0.42 * wau)
        if wal > 0.02:
            co.y *= (1.0 + 0.70 * wal)
            co.x *= (1.0 + 0.55 * wal)
        if wh > 0.02:
            co.y *= (1.0 + 0.75 * wh)
            co.x *= (1.0 + 0.55 * wh)
            co.z -= 0.10 * wh

        wth, wsh, wft = w_thigh(v), w_shin(v), w_foot(v)
        if wth > 0.02:
            co.y *= (1.0 + 0.42 * wth)
            co.x *= (1.0 + 0.32 * wth)
        if wsh > 0.02:
            co.y *= (1.0 + 0.38 * wsh)
            co.x *= (1.0 + 0.30 * wsh)
        if wft > 0.02:
            co.y *= (1.0 + 0.55 * wft)
            co.x *= (1.0 + 0.40 * wft)
            co.z *= (1.0 - 0.25 * wft)

        whd = w_head(v)
        if whd > 0.02:
            co.y *= (1.0 + 0.42 * whd)

    # Cranium & face relative to actual head bounds
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
        # Enlarge the whole head (ref: big ape skull) about its own centre.
        cx = (min(hx) + max(hx)) * 0.5
        cy = (min(hy) + max(hy)) * 0.5
        cz = (min(hz) + max(hz)) * 0.5
        for v in head_verts:
            v.co.x = cx + (v.co.x - cx) * 1.16
            v.co.y = cy + (v.co.y - cy) * 1.24
            v.co.z = cz + (v.co.z - cz) * 1.16
        hx = [v.co.x for v in head_verts]
        hy = [v.co.y for v in head_verts]
        hz = [v.co.z for v in head_verts]
        hxmax = max(hx)
        hyc = (min(hy) + max(hy)) * 0.5
        hzmin, hzmax = min(hz), max(hz)
        hr = max(hzmax - hzmin, 1e-4)
        front = hxmax
        hxmin = min(hx)
        hxr = max(hxmax - hxmin, 1e-4)          # head depth (back->front)
        half_w = max(max(hy) - min(hy), 1e-4) * 0.5

        def g(a, s):
            return math.exp(-(a * a) / (s * s))

        for v in head_verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            # Normalised head coords: fx 0(back)..1(front), sy -1..1 side, wz 0(bottom)..1(top)
            fx = (x - hxmin) / hxr
            sy = (y - hyc) / half_w
            wz = (z - hzmin) / hr
            fm = min(1.0, max(0.0, (fx - 0.45) / 0.40))   # face-only mask
            fm = fm * fm * (3.0 - 2.0 * fm)               # smoothstep

            # --- Sagittal crest: low ridge, swept backward ---
            t = min(1.0, max(0.0, (z - (hzmax - 0.22)) / 0.22))
            if t > 0.0 and abs(y - hyc) < 0.18:
                v.co.z += 0.05 * t
                v.co.x -= 0.16 * t
                v.co.y = hyc + (y - hyc) * (1.0 - 0.45 * t)

            # Forward displacement accumulated from facial features
            dxn = 0.0
            # 1. Heavy supraorbital brow ridge (glabella dips at centre)
            dxn += 0.22 * hxr * g(wz - 0.66, 0.06) * (1.0 - 0.55 * g(sy, 0.22))
            # 2. Deep-set orbital sockets (under the brow, either side)
            dxn -= 0.15 * hxr * g(wz - 0.57, 0.055) * (g(sy - 0.36, 0.17) + g(sy + 0.36, 0.17))
            # 3. Eyeball domes inside the sockets
            dxn += 0.06 * hxr * g(wz - 0.57, 0.035) * (g(sy - 0.34, 0.09) + g(sy + 0.34, 0.09))
            # 4. Nasal bridge between the eyes
            dxn += 0.09 * hxr * g(sy, 0.10) * g(wz - 0.50, 0.10)
            # 5. Broad flat simian nose with flared alar wings
            dxn += 0.08 * hxr * g(wz - 0.42, 0.05) * (g(sy, 0.14)
                                                      + 0.8 * g(sy - 0.20, 0.09)
                                                      + 0.8 * g(sy + 0.20, 0.09))
            # 6. Nostril recesses
            dxn -= 0.05 * hxr * g(wz - 0.40, 0.03) * (g(sy - 0.13, 0.05) + g(sy + 0.13, 0.05))
            # 7. Prognathic muzzle (upper lip juts forward)
            dxn += 0.20 * hxr * g(wz - 0.32, 0.10) * g(sy, 0.55)
            # 8. Closed-mouth line groove
            dxn -= 0.10 * hxr * g(wz - 0.28, 0.022) * g(sy, 0.45)
            # 9. Lower lip / chin mass
            dxn += 0.10 * hxr * g(wz - 0.18, 0.08) * g(sy, 0.45)

            v.co.x += dxn * fm

    mesh.update()


# ---------------------------------------------------------------------------
# Fur volume (silhouette-breaking clumps)
# ---------------------------------------------------------------------------
def fur_volume(mesh_obj, strength=0.003, strands=46.0):
    """Push shaggy fur clumps out along the surface normal to break the
    silhouette on the body, shoulders and back (kept short on the face/crest
    and feet). Uses vertex normals, so no vertex groups are needed."""
    mesh = mesh_obj.data
    verts = mesh.vertices
    n = len(verts)
    if n == 0:
        return
    # Snapshot positions and normals first: reading v.normal inside a loop that
    # also writes v.co forces Blender to recompute ALL normals every iteration.
    cos = [v.co.copy() for v in verts]
    nrm = [v.normal.copy() for v in verts]
    cx = sum(c.x for c in cos) / n
    cy = sum(c.y for c in cos) / n
    zmin = min(c.z for c in cos)
    zmax = max(c.z for c in cos)
    h = max(zmax - zmin, 1e-4)
    for i in range(n):
        c = cos[i]
        tz = (c.z - zmin) / h
        if tz > 0.80 or tz < 0.06:            # keep face/crest and feet smooth
            continue
        theta = math.atan2(c.y - cy, c.x - cx)
        # irregular vertical fur strands (jittered so they don't look pleated)
        strand = 0.5 + 0.5 * math.sin(theta * strands + 2.0 * math.sin(c.z * 3.1))
        clump = 0.5 + 0.5 * math.sin(theta * strands * 0.5 + c.z * 7.0
                                     + 1.6 * math.sin(theta * 3.0))
        region = 1.35 if 0.55 < tz < 0.82 else 1.0   # extra volume on shoulders/back
        amt = strength * region * (0.35 * strand + 0.65 * clump)
        verts[i].co = c + nrm[i] * amt
    mesh.update()
    print("[OK] fur volume clumps applied")


# ---------------------------------------------------------------------------
# Pose via the armature (proper skinning)
# ---------------------------------------------------------------------------
def set_bone_rot(arm_obj, name, rots):
    """Rotate a pose bone by a list of REST-space (axis, degrees) rotations."""
    pb = arm_obj.pose.bones.get(name)
    if pb is None:
        print(f"[WARN] missing bone {name}")
        return
    rest3 = pb.bone.matrix_local.to_3x3()
    R = Quaternion((1, 0, 0), 0.0)
    for axis, deg in rots:
        R = Quaternion(Vector(axis).normalized(), math.radians(deg)) @ R
    local = rest3.inverted() @ R.to_matrix() @ rest3
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = local.to_quaternion()


def pose_rig(arm_obj):
    # +X forward, +Y left, +Z up (rest space). Rotation about Y pitches forward.
    for bone, deg in (("spine.001", 7.0), ("spine.002", 9.0),
                      ("spine.003", 11.0), ("spine.005", 10.0)):
        set_bone_rot(arm_obj, bone, [((0, 1, 0), deg)])
    # Knees bend: thigh forward, shin back -> bent-knee crouch.
    for s in ("L", "R"):
        set_bone_rot(arm_obj, f"thigh.{s}", [((0, 1, 0), -38.0)])
        set_bone_rot(arm_obj, f"shin.{s}", [((0, 1, 0), 52.0)])
        set_bone_rot(arm_obj, f"foot.{s}", [((0, 1, 0), -14.0)])
    # Arms hang down (shoulder rotates too so the armpit skin follows the arm and
    # does not stretch into a web); slight outward + forward.
    for s, sign in (("L", -1.0), ("R", 1.0)):
        set_bone_rot(arm_obj, f"shoulder.{s}", [((1, 0, 0), 14.0 * sign)])
        set_bone_rot(arm_obj, f"upper_arm.{s}",
                     [((1, 0, 0), 30.0 * sign), ((0, 0, 1), 5.0 * sign)])
        set_bone_rot(arm_obj, f"forearm.{s}", [((1, 0, 0), 18.0 * sign)])


def main():
    args = parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    clean_scene()
    print("=" * 64)
    print(" AUTHORING CLASSIC BIGFOOT HERO SCULPT (v3 armature-pose rewrite)")
    print("=" * 64)

    bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))

    mesh_obj = None
    arm_obj = None
    for o in list(bpy.context.scene.objects):
        if o.type == "MESH" and o.name != "Icosphere":
            mesh_obj = o
        elif o.type == "ARMATURE":
            arm_obj = o
    if mesh_obj is None or arm_obj is None:
        raise RuntimeError("base_mesh.glb missing mesh or armature")

    for o in list(bpy.context.scene.objects):
        if o.name == "Icosphere":
            bpy.data.objects.remove(o, do_unlink=True)

    arm_name = arm_obj.name
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # Scale to hero size (rest space).
    for v in mesh_obj.data.vertices:
        v.co *= SCALE

    # Subdivide for shaping resolution.
    sub = mesh_obj.modifiers.new("PreShapeSubdiv", "SUBSURF")
    sub.levels = 2
    bpy.ops.object.modifier_apply(modifier="PreShapeSubdiv")
    print(f"[OK] base verts after subdiv: {len(mesh_obj.data.vertices)}")

    shape_anatomy(mesh_obj)
    print("[OK] anatomy shaped (rest pose)")

    pose_rig(arm_obj)
    print("[OK] rig posed (lean + bent knees + hanging arms)")

    # Bake the skinning into the mesh: move to rest mesh space, apply armature.
    bpy.context.view_layer.objects.active = mesh_obj
    for mod in list(mesh_obj.modifiers):
        if mod.type == "ARMATURE":
            bpy.ops.object.modifier_apply(modifier=mod.name)
    # Clear parent keep transform.
    mw = mesh_obj.matrix_world.copy()
    mesh_obj.parent = None
    mesh_obj.matrix_world = mw
    if arm_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[arm_name], do_unlink=True)

    bpy.context.view_layer.update()
    d0 = mesh_obj.dimensions
    print(f">>> posed bounds: X={d0.x:.2f} Y={d0.y:.2f} Z={d0.z:.2f}")

    # Weld, then CLOSE the base mesh's open boundary edges. The rigged base mesh
    # is not watertight, so without filling holes the voxel remesh treats it as
    # an open thin shell and returns a porous sponge. Once closed, the voxel
    # remesh gives ONE continuous watertight solid and also fuses the armpit /
    # hip skin webbing produced by the pose.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0008)
    bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"[OK] welded/closed -> {len(mesh_obj.data.vertices)} verts")

    mesh_obj.data.remesh_voxel_size = args.voxel
    bpy.ops.object.voxel_remesh()
    print(f"[OK] voxel remesh -> {len(mesh_obj.data.vertices)} verts")

    sm = mesh_obj.modifiers.new("SculptSmooth", "SMOOTH")
    sm.factor = 0.5
    sm.iterations = 3
    bpy.ops.object.modifier_apply(modifier="SculptSmooth")

    sub2 = mesh_obj.modifiers.new("HeroSubsurf", "SUBSURF")
    sub2.levels = 1
    bpy.ops.object.modifier_apply(modifier="HeroSubsurf")
    print(f"[OK] smoothed/subdivided -> {len(mesh_obj.data.vertices)} verts")

    fur_volume(mesh_obj)

    # Light post-fur smooth: knocks down the fine fur grooves while leaving the
    # large (low-frequency) facial and muscular forms intact.
    sm2 = mesh_obj.modifiers.new("FurRelax", "SMOOTH")
    sm2.factor = 0.4
    sm2.iterations = 1
    bpy.ops.object.modifier_apply(modifier="FurRelax")

    bpy.context.view_layer.update()
    corners = [mesh_obj.matrix_world @ Vector(c) for c in mesh_obj.bound_box]
    min_z = min(c.z for c in corners)
    mesh_obj.location.z -= min_z
    bpy.ops.object.transform_apply(location=True)

    bpy.ops.object.shade_smooth()

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