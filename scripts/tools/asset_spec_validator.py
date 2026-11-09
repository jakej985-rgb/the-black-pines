#!/usr/bin/env python3
"""
The Black Pines - Asset Specification & Directory Architecture Validator
Ensures 3D asset packages conform to reference-driven pipeline requirements,
directory standards, and hardware performance budgets before production modeling.
"""

import argparse
import os
import sys

try:
    import yaml
except ImportError:
    # Minimal fallback parser if pyyaml is not installed
    yaml = None


def parse_simple_yaml(file_path):
    """Fallback rudimentary YAML parser for basic nested structures if pyyaml is unavailable."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    data = {}
    current_section = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  ") and current_section:
            subparts = stripped.split(":", 1)
            if len(subparts) == 2:
                sub_k = subparts[0].strip()
                sub_v = subparts[1].strip()
                # Parse basic types
                if sub_v.lower() == "true":
                    sub_v = True
                elif sub_v.lower() == "false":
                    sub_v = False
                elif sub_v.isdigit():
                    sub_v = int(sub_v)
                data[current_section][sub_k] = sub_v
            elif stripped.startswith("-"):
                val = stripped.lstrip("-").strip()
                if not isinstance(data[current_section], list):
                    if not data[current_section]:
                        data[current_section] = []
                    else:
                        continue
                data[current_section].append(val)
        else:
            parts = stripped.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip() if len(parts) > 1 else ""
            if not v:
                data[k] = {}
                current_section = k
            else:
                if v.lower() == "true":
                    v = True
                elif v.lower() == "false":
                    v = False
                elif v.isdigit():
                    v = int(v)
                data[k] = v
                current_section = None
    return data


def load_yaml(file_path):
    if yaml is not None:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return parse_simple_yaml(file_path)


REQUIRED_DIRECTORIES = ["references", "source", "working", "exports", "materials", "qa"]
VALID_ASSET_TYPES = ["organic_creature", "environment_prop", "procedural_scatter"]
VALID_QUALITY_TIERS = ["hero", "standard", "background"]


def validate_asset_spec(spec_path):
    spec_path = os.path.abspath(spec_path)
    if not os.path.exists(spec_path):
        print(f"[FAIL] Spec file not found: {spec_path}")
        return False

    asset_dir = os.path.dirname(spec_path)
    print(f"\n============================================================")
    print(f" Validating Asset Spec: {os.path.basename(spec_path)}")
    print(f" Asset Path: {asset_dir}")
    print(f"============================================================")

    # 1. Directory Structure Check
    missing_dirs = []
    for d in REQUIRED_DIRECTORIES:
        expected_dir = os.path.join(asset_dir, d)
        if not os.path.isdir(expected_dir):
            missing_dirs.append(d)

    if missing_dirs:
        print(f"[ERROR] Missing required standard directories: {missing_dirs}")
        return False
    print(f"[PASS] All 6 standard subdirectories verified ({', '.join(REQUIRED_DIRECTORIES)})")

    # 2. YAML Syntax & Root Schema Check
    try:
        spec = load_yaml(spec_path)
    except Exception as e:
        print(f"[ERROR] Failed to parse YAML file: {e}")
        return False

    required_keys = ["asset_id", "asset_type", "quality_tier", "reference", "design", "budget", "requirements"]
    for k in required_keys:
        if k not in spec:
            print(f"[ERROR] Missing required top-level key: '{k}'")
            return False
    print(f"[PASS] Schema root structure complete.")

    # 3. Enum & Constraints Check
    asset_type = spec.get("asset_type")
    if asset_type not in VALID_ASSET_TYPES:
        print(f"[ERROR] Invalid asset_type '{asset_type}'. Must be one of {VALID_ASSET_TYPES}")
        return False

    quality_tier = spec.get("quality_tier")
    if quality_tier not in VALID_QUALITY_TIERS:
        print(f"[ERROR] Invalid quality_tier '{quality_tier}'. Must be one of {VALID_QUALITY_TIERS}")
        return False

    # 4. Reference Files Existence Check
    references = spec.get("reference", {})
    if not references:
        print("[ERROR] 'reference' section is empty. At least 'primary' reference must be specified.")
        return False

    missing_refs = []
    checked_refs = []
    for ref_name, rel_path in references.items():
        if not isinstance(rel_path, str):
            continue
        full_ref_path = os.path.join(asset_dir, rel_path)
        if not os.path.isfile(full_ref_path):
            missing_refs.append(f"{ref_name}: {rel_path}")
        else:
            checked_refs.append(f"{ref_name} ({rel_path})")

    if missing_refs:
        print(f"[ERROR] Referenced media files do not exist on disk:\n  " + "\n  ".join(missing_refs))
        return False
    print(f"[PASS] Visual references verified on disk:\n  " + "\n  ".join(checked_refs))

    # 5. Hardware Budget Adherence (GTX 960 Limits)
    budget = spec.get("budget", {})
    max_triangles = budget.get("max_triangles", 0)
    max_tex = budget.get("max_texture_resolution", 0)

    if asset_type == "organic_creature" and quality_tier == "hero":
        if max_triangles > 16000:
            print(f"[ERROR] max_triangles ({max_triangles}) exceeds hero creature limit of 16,000 tris.")
            return False
    elif asset_type == "environment_prop":
        if max_triangles > 22000:
            print(f"[ERROR] max_triangles ({max_triangles}) exceeds prop/cabin limit of 22,000 tris.")
            return False

    if max_tex > 2048:
        print(f"[ERROR] max_texture_resolution ({max_tex}) exceeds maximum GTX 960 VRAM budget of 2048.")
        return False

    print(f"[PASS] Budget constraints pass GTX 960 rules (Max Tris: {max_triangles}, Max Tex: {max_tex}px)")
    print(f"\n>>> [ASSET SPEC VALIDATION PASSED] Ready for 3D modeling pipeline <<<\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate asset specification and directory setup.")
    parser.add_argument("--spec", required=True, help="Path to asset_spec.yaml")
    args = parser.parse_args()

    passed = validate_asset_spec(args.spec)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
