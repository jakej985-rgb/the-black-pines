#!/usr/bin/env python3
"""
Poly Haven Asset Sourcing Tool for The Black Pines
Searches and downloads CC0 PBR textures, models, and HDRIs from Poly Haven's public API.
Enforces performance budgets suitable for GTX 960 (default 1k/2k textures, optimized formats).
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.polyhaven.com"
USER_AGENT = "TheBlackPines-AssetTool/1.0"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def http_get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_file(url: str, dest_path: Path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out:
        chunk_size = 64 * 1024
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out.write(chunk)


def search_assets(query: str, asset_type: str = "all", limit: int = 10):
    types_to_search = ["textures", "models", "hdris"] if asset_type == "all" else [asset_type]
    results = []
    q = query.lower().strip()

    for t in types_to_search:
        try:
            data = http_get_json(f"{API_BASE}/assets?t={t}")
            for asset_id, info in data.items():
                name = info.get("name", asset_id)
                categories = info.get("categories", [])
                tags = info.get("tags", [])
                text_to_match = f"{asset_id} {name} {' '.join(categories)} {' '.join(tags)}".lower()
                if not q or q in text_to_match:
                    results.append({
                        "id": asset_id,
                        "name": name,
                        "type": t,
                        "categories": categories,
                        "tags": tags[:5]
                    })
        except Exception as e:
            print(f"[ERROR] Failed to query Poly Haven for type '{t}': {e}", file=sys.stderr)

    results.sort(key=lambda r: 0 if q == r["id"].lower() else (1 if q in r["name"].lower() else 2))
    return results[:limit]


def get_asset_info(asset_id: str):
    info_url = f"{API_BASE}/files/{asset_id}"
    return http_get_json(info_url)


def generate_godot_material(asset_id: str, texture_paths: dict, material_path: Path):
    """
    Generate a Godot 4 StandardMaterial3D resource file (.tres) for the downloaded PBR textures.
    """
    material_path.parent.mkdir(parents=True, exist_ok=True)

    def rel_godot_path(p: Path) -> str:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        return f"res://{rel}"

    diffuse_res = rel_godot_path(texture_paths["diffuse"]) if "diffuse" in texture_paths else ""
    normal_res = rel_godot_path(texture_paths["normal"]) if "normal" in texture_paths else ""
    rough_res = rel_godot_path(texture_paths["rough"]) if "rough" in texture_paths else ""
    ao_res = rel_godot_path(texture_paths["ao"]) if "ao" in texture_paths else ""

    content = f"""; Auto-generated PBR StandardMaterial3D from Poly Haven: {asset_id}
[gd_resource type="StandardMaterial3D" load_steps=5 format=3]

"""
    load_step = 1
    ext_resources = []
    mat_props = [
        "roughness = 0.85",
        "texture_filter = 5  # Linear Mipmap Anisotropic"
    ]

    if diffuse_res:
        ext_resources.append(f'[ext_resource type="Texture2D" path="{diffuse_res}" id="{load_step}_albedo"]')
        mat_props.append(f'albedo_texture = ExtResource("{load_step}_albedo")')
        load_step += 1

    if normal_res:
        ext_resources.append(f'[ext_resource type="Texture2D" path="{normal_res}" id="{load_step}_norm"]')
        mat_props.append("normal_enabled = true")
        mat_props.append(f'normal_texture = ExtResource("{load_step}_norm")')
        load_step += 1

    if rough_res:
        ext_resources.append(f'[ext_resource type="Texture2D" path="{rough_res}" id="{load_step}_rough"]')
        mat_props.append(f'roughness_texture = ExtResource("{load_step}_rough")')
        mat_props.append("roughness_texture_channel = 0")
        load_step += 1

    if ao_res:
        ext_resources.append(f'[ext_resource type="Texture2D" path="{ao_res}" id="{load_step}_ao"]')
        mat_props.append("ao_enabled = true")
        mat_props.append(f'ao_texture = ExtResource("{load_step}_ao")')
        load_step += 1

    header = f'[gd_resource type="StandardMaterial3D" load_steps={load_step} format=3]\n\n'
    full_content = header + "\n".join(ext_resources) + "\n\n[resource]\n" + "\n".join(mat_props) + "\n"

    with open(material_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"[OK] Generated Godot Material: {material_path.relative_to(PROJECT_ROOT)}")


def download_texture_asset(asset_id: str, files_meta: dict, resolution: str = "1k", img_fmt: str = "jpg"):
    out_dir = PROJECT_ROOT / "assets" / "textures" / "polyhaven" / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_textures = {}

    map_types = {
        "diffuse": ["Diffuse", "diffuse"],
        "normal": ["nor_gl", "nor_dx"],
        "rough": ["Rough", "rough"],
        "ao": ["AO", "ao", "arm"]
    }

    for map_key, source_keys in map_types.items():
        chosen_key = None
        for sk in source_keys:
            if sk in files_meta:
                chosen_key = sk
                break
        if not chosen_key:
            continue

        res_dict = files_meta[chosen_key]
        target_res = resolution if resolution in res_dict else ("1k" if "1k" in res_dict else list(res_dict.keys())[-1])
        fmt_dict = res_dict.get(target_res, {})

        target_fmt = img_fmt if img_fmt in fmt_dict else ("png" if "png" in fmt_dict else list(fmt_dict.keys())[0])
        file_info = fmt_dict.get(target_fmt)
        if not file_info:
            continue

        download_url = file_info.get("url")
        file_name = f"{asset_id}_{map_key}_{target_res}.{target_fmt}"
        dest = out_dir / file_name

        print(f"  Downloading {map_key} ({target_res} {target_fmt}) -> {dest.name}...")
        download_file(download_url, dest)
        saved_textures[map_key] = dest

    mat_file = PROJECT_ROOT / "assets" / "materials" / "polyhaven" / f"mat_{asset_id}.tres"
    generate_godot_material(asset_id, saved_textures, mat_file)
    return saved_textures, mat_file


def download_model_asset(asset_id: str, files_meta: dict, resolution: str = "1k"):
    out_dir = PROJECT_ROOT / "assets" / "models" / "polyhaven" / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)

    gltf_entry = files_meta.get("gltf", {})
    target_res = resolution if resolution in gltf_entry else ("1k" if "1k" in gltf_entry else list(gltf_entry.keys())[-1])
    gltf_info = gltf_entry.get(target_res, {}).get("gltf", {})

    main_url = gltf_info.get("url")
    if not main_url:
        print(f"[ERROR] No GLTF URL found for model {asset_id}", file=sys.stderr)
        return

    main_gltf_path = out_dir / f"{asset_id}_{target_res}.gltf"
    print(f"  Downloading GLTF root -> {main_gltf_path.name}...")
    download_file(main_url, main_gltf_path)

    # Download includes (bin files, textures)
    includes = gltf_info.get("include", {})
    for rel_path, inc_info in includes.items():
        inc_url = inc_info.get("url")
        inc_dest = out_dir / rel_path
        print(f"  Downloading include -> {rel_path}...")
        download_file(inc_url, inc_dest)

    print(f"[OK] Model downloaded to: {out_dir.relative_to(PROJECT_ROOT)}")


def download_hdri_asset(asset_id: str, files_meta: dict, resolution: str = "1k"):
    out_dir = PROJECT_ROOT / "assets" / "textures" / "hdris"
    out_dir.mkdir(parents=True, exist_ok=True)

    hdri_entry = files_meta.get("hdri", {})
    target_res = resolution if resolution in hdri_entry else ("1k" if "1k" in hdri_entry else list(hdri_entry.keys())[-1])
    res_info = hdri_entry.get(target_res, {})
    fmt = "hdr" if "hdr" in res_info else ("exr" if "exr" in res_info else list(res_info.keys())[0])

    url = res_info[fmt].get("url")
    dest = out_dir / f"{asset_id}_{target_res}.{fmt}"
    print(f"  Downloading HDRI ({target_res} {fmt}) -> {dest.name}...")
    download_file(url, dest)
    print(f"[OK] HDRI downloaded to: {dest.relative_to(PROJECT_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Poly Haven Asset Sourcing Tool for The Black Pines")
    parser.add_argument("--search", type=str, help="Search keywords (e.g. 'bark', 'pine', 'rock', 'cabin')")
    parser.add_argument("--type", choices=["textures", "models", "hdris", "all"], default="all", help="Asset type filter")
    parser.add_argument("--limit", type=int, default=10, help="Max results to display")
    parser.add_argument("--info", type=str, help="Asset ID to inspect")
    parser.add_argument("--download", type=str, help="Asset ID to download")
    parser.add_argument("--res", choices=["1k", "2k", "4k"], default="1k", help="Resolution (default: 1k for GTX 960 budget)")
    parser.add_argument("--fmt", choices=["jpg", "png"], default="jpg", help="Texture format (default: jpg)")

    args = parser.parse_args()

    if args.search is not None:
        results = search_assets(args.search, args.type, args.limit)
        print(f"\n--- Poly Haven Search: '{args.search}' (Type: {args.type}) ---")
        if not results:
            print("No matching assets found.")
            return
        for r in results:
            cats = ", ".join(r["categories"]) if r["categories"] else "-"
            tags = ", ".join(r["tags"]) if r["tags"] else "-"
            print(f"  [{r['type'].upper():8}] {r['id']:<28} | {r['name']:<24} | Cats: {cats}")
        print()

    elif args.info:
        meta = get_asset_info(args.info)
        print(f"\n--- Poly Haven Asset: {args.info} ---")
        print("Available Maps / Formats:", list(meta.keys()))
        for k in ["Diffuse", "nor_gl", "Rough", "AO", "gltf", "hdri"]:
            if k in meta:
                print(f"  {k}: {list(meta[k].keys())}")
        print()

    elif args.download:
        asset_id = args.download
        meta = get_asset_info(asset_id)
        if args.type == "textures" or (args.type == "all" and "Diffuse" in meta and "gltf" not in meta):
            print(f"[+] Downloading PBR Texture asset: {asset_id} ({args.res} {args.fmt})...")
            download_texture_asset(asset_id, meta, args.res, args.fmt)
        elif args.type == "hdris" or (args.type == "all" and "hdri" in meta):
            print(f"[+] Downloading HDRI asset: {asset_id} ({args.res})...")
            download_hdri_asset(asset_id, meta, args.res)
        elif "gltf" in meta:
            print(f"[+] Downloading 3D Model asset: {asset_id} ({args.res})...")
            download_model_asset(asset_id, meta, args.res)
        else:
            print(f"[+] Downloading PBR Texture asset: {asset_id} ({args.res} {args.fmt})...")
            download_texture_asset(asset_id, meta, args.res, args.fmt)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
