#!/usr/bin/env python3
"""
Creature asset stage-gate manager (issue #31).

Tracks progression through:
  reference_locked -> blockout_review -> sculpt_review -> retopo_uv_bake
  -> materials_fur -> rig_animation -> godot_validation -> approved

Usage:
  asset_stage_gate.py --asset sasquatch status
  asset_stage_gate.py --asset sasquatch check blockout_review   # exit 0 iff approved
  asset_stage_gate.py --asset sasquatch set blockout_review approved \
      --reviewer "name" --evidence path1 path2 --notes "..."
  asset_stage_gate.py --asset sasquatch set blockout_review rejected \
      --reviewer "name" --notes "reason"

Rules:
  - 'approved' requires every earlier stage to be 'approved'.
  - 'rejected' and 'in_progress' may be set at any time.
  - 'pending' resets evidence/reviewer.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

STAGES = [
    "reference_locked",
    "blockout_review",
    "sculpt_review",
    "retopo_uv_bake",
    "materials_fur",
    "rig_animation",
    "godot_validation",
    "approved",
]
STATUSES = {"pending", "in_progress", "approved", "rejected", "skipped"}

ASSETS_ROOT = Path(__file__).resolve().parent.parent.parent / "assets" / "creatures"


def state_path(asset: str) -> Path:
    return ASSETS_ROOT / asset / "pipeline_state.yaml"


def load(asset: str) -> dict:
    p = state_path(asset)
    if not p.exists():
        sys.exit(f"No pipeline_state.yaml for asset '{asset}' at {p}")
    return yaml.safe_load(p.read_text())


def save(asset: str, state: dict) -> None:
    state["updated"] = str(date.today())
    state_path(asset).write_text(yaml.safe_dump(state, sort_keys=False, width=100))


def stage_status(state: dict, stage: str) -> str:
    return state.get("stages", {}).get(stage, {}).get("status", "pending")


def cmd_status(asset: str, _args) -> int:
    state = load(asset)
    print(f"Asset: {state.get('asset_id', asset)}  (updated {state.get('updated')})")
    for s in STAGES:
        st = stage_status(state, s)
        marker = {"approved": "[x]", "rejected": "[!",
                  "in_progress": "[~", "pending": "[ ]", "skipped": "[-"}[st]
        print(f"  {marker}] {s}: {st}")
    return 0


def cmd_check(asset: str, args) -> int:
    if args.stage not in STAGES:
        sys.exit(f"Unknown stage '{args.stage}'. Valid: {', '.join(STAGES)}")
    ok = stage_status(load(asset), args.stage) == "approved"
    return 0 if ok else 1


def cmd_set(asset: str, args) -> int:
    if args.stage not in STAGES:
        sys.exit(f"Unknown stage '{args.stage}'. Valid: {', '.join(STAGES)}")
    if args.status not in STATUSES:
        sys.exit(f"Unknown status '{args.status}'. Valid: {', '.join(sorted(STATUSES))}")

    state = load(asset)
    stages = state.setdefault("stages", {})

    if args.status == "approved":
        idx = STAGES.index(args.stage)
        blockers = [s for s in STAGES[:idx] if stage_status(state, s) != "approved"]
        if blockers:
            sys.exit(
                f"Cannot approve '{args.stage}': earlier stages not approved: "
                + ", ".join(blockers)
            )

    entry = stages.setdefault(args.stage, {})
    entry["status"] = args.status
    if args.status == "pending":
        entry["evidence"] = []
        entry["reviewer"] = None
        entry["notes"] = ""
    else:
        if args.evidence:
            entry["evidence"] = args.evidence
        if args.reviewer is not None:
            entry["reviewer"] = args.reviewer
        if args.notes is not None:
            entry["notes"] = args.notes
    save(asset, state)
    print(f"{asset}: {args.stage} -> {args.status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asset", default="sasquatch", help="Asset dir under assets/creatures/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")

    p_check = sub.add_parser("check")
    p_check.add_argument("stage")

    p_set = sub.add_parser("set")
    p_set.add_argument("stage")
    p_set.add_argument("status", choices=sorted(STATUSES))
    p_set.add_argument("--reviewer", default=None)
    p_set.add_argument("--evidence", nargs="*", default=None)
    p_set.add_argument("--notes", default=None)

    args = ap.parse_args()
    return {"status": cmd_status, "check": cmd_check, "set": cmd_set}[args.cmd](args.asset, args)


if __name__ == "__main__":
    sys.exit(main())
