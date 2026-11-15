#!/usr/bin/env python3
"""Read-only Blender audit of The Black Pines cabin asset baselines.

Usage:
  blender --background --python scripts/tools/audit_cabin_baseline.py -- \
    --project-root /path/to/the-black-pines

Writes only to working/cabin_refinement/baseline. Never saves or modifies sources.
"""
import bpy, json, hashlib, argparse, sys
from pathlib import Path
from mathutils import Vector

def args():
    raw = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", required=True)
    return p.parse_args(raw)

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    a = args()
    root = Path(a.project_root).resolve()
    out = root / "working/cabin_refinement/baseline"
    out.mkdir(parents=True, exist_ok=True)
    paths = [
        "assets/models/cabin_ranger_station.glb",
        "assets/models/furniture_ranger_desk.glb",
        "assets/models/furniture_woodstove.glb",
        "assets/models/furniture_cot.glb",
        "assets/models/furniture_shelving.glb",
        "assets/models/generator_industrial.glb",
        "assets/models/firewood_cord_stack.glb",
    ]
    hashes, inventory = {}, {}
    for rel in paths:
        p = root / rel
        if not p.exists():
            inventory[rel] = {"status": "MISSING"}
            continue
        hashes[rel] = {"sha256": sha(p), "bytes": p.stat().st_size}
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(p))
        deps = list(bpy.context.scene.objects)
        meshes = [o for o in deps if o.type == "MESH"]
        for o in meshes:
            bpy.context.view_layer.update()
        bounds = []
        if meshes:
            points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
            lo = [min(v[i] for v in points) for i in range(3)]
            hi = [max(v[i] for v in points) for i in range(3)]
            bounds = {"min": lo, "max": hi, "size": [hi[i]-lo[i] for i in range(3)]}
        tris = sum(sum(max(0, len(poly.vertices)-2) for poly in o.data.polygons) for o in meshes)
        inventory[rel] = {
            "status": "OK",
            "objects": len(deps),
            "mesh_objects": len(meshes),
            "vertices": sum(len(o.data.vertices) for o in meshes),
            "triangles": tris,
            "materials": sorted({m.name for o in meshes for m in o.data.materials if m}),
            "dimensions_world": bounds,
            "objects_detail": [
                {"name": o.name, "type": o.type,
                 "dimensions": [round(v, 5) for v in o.dimensions],
                 "location": [round(v, 5) for v in o.location],
                 "scale": [round(v, 5) for v in o.scale]}
                for o in deps
            ],
        }
    (out / "source_hashes.json").write_text(json.dumps(hashes, indent=2))
    (out / "inventory.json").write_text(json.dumps({
        "blender_version": bpy.app.version_string,
        "project_root": str(root),
        "assets": inventory,
    }, indent=2))
    print("[CABIN AUDIT] Wrote read-only inventory to", out)

if __name__ == "__main__":
    main()
