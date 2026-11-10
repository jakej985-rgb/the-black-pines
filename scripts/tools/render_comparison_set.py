#!/usr/bin/env python3
"""
Reference-aware comparison set renderer (issue #30).

For a given creature source (.blend/.glb/.obj), produces under --out:
  silhouette_*.png   - flat-shaded Workbench silhouette views (front, side,
                       rear, threequarter, bust) with identical camera rigs
  comparison_*.png   - side-by-side sheet: reference concept | clay render |
                       silhouette, per view
  comparison_sheet.png - all views in one grid for quick human review
  comparison_manifest.json - view list + source + timestamp

Usage:
  python3 scripts/tools/render_comparison_set.py --asset sasquatch \
      --source assets/creatures/sasquatch/source/blockout.blend \
      --clay-dir assets/creatures/sasquatch/qa/stage_reviews/blockout_review/diagnostic \
      --out    assets/creatures/sasquatch/qa/stage_reviews/blockout_review/comparison

The reference image is NOT modified; it is composited unchanged.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VIEWS = ["front", "side", "rear", "threequarter", "bust"]

# ---------------------------------------------------------------------------
# Phase 1 (runs inside Blender): flat Workbench silhouette renders
# ---------------------------------------------------------------------------
BLENDER_SNIPPET = r'''
import bpy, sys, json
from mathutils import Vector
from pathlib import Path

argv = sys.argv[sys.argv.index("--") + 1:]
import argparse
p = argparse.ArgumentParser()
p.add_argument("--source", required=True)
p.add_argument("--out", required=True)
a = p.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
src = Path(a.source)
if src.suffix.lower() == ".blend":
    with bpy.data.libraries.load(str(src), link=False) as (df, dt):
        dt.objects = df.objects
    for o in dt.objects:
        if o is not None:
            bpy.context.scene.collection.objects.link(o)
elif src.suffix.lower() in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=str(src))
else:
    bpy.ops.wm.obj_import(filepath=str(src))

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    raise RuntimeError("no meshes in source")

corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
center = (lo + hi) * 0.5
height = hi.z - lo.z

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "FLAT"
scene.display.shading.color_type = "SINGLE"
scene.display.shading.single_color = (0.02, 0.02, 0.02)
scene.display.shading.show_shadows = False
scene.display.shading.show_cavity = False
scene.display.shading.background_type = "VIEWPORT"
scene.display.shading.background_color = (1.0, 1.0, 1.0)
scene.render.resolution_x = 1280
scene.render.resolution_y = 1280
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"

cam_data = bpy.data.cameras.new("SilCam")
cam_data.lens = 85
cam = bpy.data.objects.new("SilCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

dist = max(height * 2.9, 7.0)
views = {
    "front":        (Vector((center.x, center.y + dist, center.z)), Vector((center.x, center.y, center.z))),
    "side":         (Vector((center.x - dist, center.y, center.z)), Vector((center.x, center.y, center.z))),
    "rear":         (Vector((center.x, center.y - dist, center.z)), Vector((center.x, center.y, center.z))),
    "threequarter": (Vector((center.x - dist * 0.72, center.y + dist * 0.72, center.z + 0.3)), Vector((center.x, center.y, center.z))),
    "bust":         (Vector((center.x - 0.25, center.y + 1.85, center.z + 1.15)), Vector((center.x, center.y + 0.15, center.z + 1.15))),
}
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
for name, (pos, tgt) in views.items():
    cam.location = pos
    cam.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(out / f"silhouette_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[OK] silhouette_{name}.png")
'''


def run_blender_silhouettes(source: Path, out_dir: Path) -> None:
    snippet = out_dir / "_silhouette_pass.py"
    out_dir.mkdir(parents=True, exist_ok=True)
    snippet.write_text(BLENDER_SNIPPET)
    cmd = [
        "blender", "--background",
        "--python", str(snippet),
        "--", "--source", str(source.resolve()), "--out", str(out_dir.resolve()),
    ]
    print(f"[EXEC] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout[-3000:])
    if res.returncode != 0:
        print(res.stderr[-3000:])
        sys.exit(f"Blender silhouette pass failed ({res.returncode})")
    snippet.unlink(missing_ok=True)


def composite_phase(asset: str, clay_dir: Path, out_dir: Path) -> None:
    from PIL import Image, ImageDraw

    clay_dir = clay_dir.resolve()
    out_dir = out_dir.resolve()

    ref_path = PROJECT_ROOT / "assets" / "creatures" / asset / "references" / "classic_bigfoot_concept.png"
    if not ref_path.exists():
        sys.exit(f"Reference image not found: {ref_path}")
    ref = Image.open(ref_path).convert("RGB")

    out_dir.mkdir(parents=True, exist_ok=True)
    cell_w, label_h, pad = 420, 28, 12

    sheets = []
    manifest_views = []
    for view in VIEWS:
        clay_path = clay_dir / f"render_{view}.png"
        sil_path = out_dir / f"silhouette_{view}.png"
        if not clay_path.exists():
            print(f"[SKIP] missing clay view {clay_path}")
            continue
        if not sil_path.exists():
            print(f"[SKIP] missing silhouette {sil_path}")
            continue

        clay = Image.open(clay_path).convert("RGB")
        sil = Image.open(sil_path).convert("RGB")
        h = cell_w  # square cells, uniform framing for comparison
        clay_r = clay.resize((cell_w, cell_w), Image.LANCZOS)
        sil_r = sil.resize((cell_w, cell_w), Image.LANCZOS)
        ref_r = ref.resize((cell_w, int(cell_w * ref.height / ref.width)), Image.LANCZOS)

        # Per-view sheet: reference on top, clay + silhouette below
        sheet_h = label_h + ref_r.height + pad + cell_w + label_h + pad
        sheet = Image.new("RGB", (cell_w * 2 + pad * 3, sheet_h), (24, 24, 28))
        d = ImageDraw.Draw(sheet)
        x = pad
        d.text((x, 6), f"REFERENCE - {view}", fill=(230, 230, 230))
        sheet.paste(ref_r, (x, label_h))
        y2 = label_h + ref_r.height + pad
        d.text((x, y2 + 6), f"CLAY - {view}", fill=(200, 200, 200))
        sheet.paste(clay_r, (x, y2 + label_h))
        x2 = x + cell_w + pad
        d.text((x2, y2 + 6), f"SILHOUETTE - {view}", fill=(200, 200, 200))
        sheet.paste(sil_r, (x2, y2 + label_h))

        fname = f"comparison_{view}.png"
        sheet.save(out_dir / fname)
        sheets.append(sheet)
        manifest_views.append({
            "view": view,
            "clay": str(clay_path.relative_to(PROJECT_ROOT)),
            "silhouette": str(sil_path.relative_to(PROJECT_ROOT)),
            "comparison": str((out_dir / fname).relative_to(PROJECT_ROOT)),
        })
        print(f"[OK] comparison_{view}.png")

    if sheets:
        w = max(s.width for s in sheets)
        h = sum(s.height for s in sheets) + pad * (len(sheets) - 1)
        grid = Image.new("RGB", (w, h), (24, 24, 28))
        y = 0
        for s in sheets:
            grid.paste(s, (0, y))
            y += s.height + pad
        grid.save(out_dir / "comparison_sheet.png")
        print("[OK] comparison_sheet.png")

    manifest = {
        "asset": asset,
        "reference": str(ref_path.relative_to(PROJECT_ROOT)),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "views": manifest_views,
    }
    (out_dir / "comparison_manifest.json").write_text(json.dumps(manifest, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asset", default="sasquatch")
    ap.add_argument("--source", required=True, help=".blend/.glb/.obj to silhouette")
    ap.add_argument("--clay-dir", required=True, help="dir with render_<view>.png clay views")
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-blender", action="store_true",
                    help="reuse existing silhouette_*.png in --out")
    args = ap.parse_args()

    out_dir = Path(args.out)
    if not args.skip_blender:
        run_blender_silhouettes(Path(args.source), out_dir)
    composite_phase(args.asset, Path(args.clay_dir), out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
