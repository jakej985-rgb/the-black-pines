#!/usr/bin/env python3
"""
The Black Pines - Automated Headless Visual QA & Graphics Scalability Profiler
Validates engine import stability, runs multi-preset graphics benchmarks, audits
PBR material resources, and checks for memory leaks.
"""

import argparse
import json
import os
import subprocess
import sys
import time

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REPORT_DIR = os.path.join(PROJECT_DIR, "reports")
REPORT_PATH = os.path.join(REPORT_DIR, "visual_qa_report.json")
RUNNER_SCRIPT = "scripts/tools/profile_runner.gd"

def run_command(cmd, timeout=30, check_returncode=True):
    print(f"\n[EXEC]: {' '.join(cmd)}")
    start = time.time()
    try:
        res = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        return res.returncode, res.stdout, res.stderr, elapsed
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds.")
        return 124, "", "TIMEOUT", timeout

def check_headless_import():
    print("\n------------------------------------------------------------")
    print("STEP 1: Validating Godot Headless Editor Import...")
    print("------------------------------------------------------------")
    code, stdout, stderr, elapsed = run_command(["godot", "--headless", "--editor", "--quit"], timeout=120)
    print(f"Editor import completed in {elapsed:.2f}s with code {code}.")
    
    # Check for fatal compilation errors
    has_error = False
    for line in (stdout + stderr).splitlines():
        if "SCRIPT ERROR" in line or "Parse Error" in line or "Compilation failed" in line:
            print(f"  [ERROR]: {line}")
            has_error = True
            
    if code != 0 or has_error:
        print("FAILED: Headless editor import encountered errors.")
        return False
    print("PASSED: Zero import or script compilation errors.")
    return True

def run_profiler():
    print("\n------------------------------------------------------------")
    print("STEP 2: Executing Graphics Scalability Profiler...")
    print("------------------------------------------------------------")
    code, stdout, stderr, elapsed = run_command(["godot", "--headless", "-s", RUNNER_SCRIPT], timeout=35)
    print(stdout)
    if stderr.strip():
        print("STDERR:\n" + stderr)

    if code != 0:
        print(f"FAILED: Profile runner exited with code {code}.")
        return False, None

    if not os.path.exists(REPORT_PATH):
        print(f"FAILED: Expected report file not generated at {REPORT_PATH}")
        return False, None

    with open(REPORT_PATH, "r") as f:
        data = json.load(f)

    return True, data

def check_runtime_stability():
    print("\n------------------------------------------------------------")
    print("STEP 3: Testing Runtime Headless Game Stability (5s)...")
    print("------------------------------------------------------------")
    code, stdout, stderr, elapsed = run_command(["timeout", "5s", "godot", "--headless", "--path", "."], timeout=10, check_returncode=False)
    # timeout utility returns 124 when process is stopped after 5s
    if code in (0, 124):
        print(f"PASSED: Game engine ran stably for {elapsed:.1f}s without crashes or memory faults.")
        return True
    else:
        print(f"FAILED: Game crashed or exited unexpectedly with code {code}.")
        print("STDERR:\n", stderr)
        return False

def display_report_table(report_data):
    print("\n================================================================================")
    print("                  GRAPHICS SCALABILITY QA BENCHMARK REPORT                      ")
    print("================================================================================")
    print(f"Timestamp:     {report_data.get('timestamp', 'N/A')}")
    print(f"Godot Version: {report_data.get('godot_version', 'N/A')}")
    print(f"Overall Pass:  {report_data.get('overall_passed', False)}")

    audit = report_data.get("resource_audit", {})
    print(f"Resources:     {audit.get('passed', 0)} / {audit.get('total_checked', 0)} passed clean ({audit.get('failed', 0)} broken)")

    mem = report_data.get("memory_leak_check", {})
    delta_mb = mem.get("delta_bytes", 0) / (1024.0 * 1024.0)
    print(f"Memory Delta:  {delta_mb:+.2f} MB (Budget: 8.00 MB) -> {'PASS' if mem.get('passed') else 'FAIL'}")

    presets = report_data.get("presets", {})
    print("\n| Preset | Scale | Fog | Shadows | SSAO | SSIL | Frame Time | Est FPS | Memory |")
    print("|--------|-------|-----|---------|------|------|------------|---------|--------|")
    for name in ["Low", "Medium", "High", "Ultra"]:
        if name in presets:
            p = presets[name]
            fog_str = "ON" if p["volumetric_fog"] else "OFF"
            ssao_str = "ON" if p["ssao_enabled"] else "OFF"
            ssil_str = "ON" if p["ssil_enabled"] else "OFF"
            print(f"| {name:<6} | {p['render_scale']:<5.2f} | {fog_str:<3} | {p['shadow_atlas_size']:<7} | {ssao_str:<4} | {ssil_str:<4} | {p['avg_frame_time_ms']:>6.2f} ms | {p['estimated_fps']:>7.1f} | {p['memory_used_mb']:>5.1f}M |")
    print("================================================================================\n")

def main():
    parser = argparse.ArgumentParser(description="The Black Pines Visual QA & Profiler")
    parser.add_argument("--all", action="store_true", default=True, help="Run all verification steps (default)")
    parser.add_argument("--profile-only", action="store_true", help="Run only the graphics preset profiler")
    parser.add_argument("--import-only", action="store_true", help="Run only the editor import validation")
    parser.add_argument("--runtime-only", action="store_true", help="Run only the runtime stability test")
    args = parser.parse_args()

    overall_success = True

    if args.import_only:
        success = check_headless_import()
        sys.exit(0 if success else 1)

    if args.runtime_only:
        success = check_runtime_stability()
        sys.exit(0 if success else 1)

    if args.profile_only:
        success, data = run_profiler()
        if success and data:
            display_report_table(data)
        sys.exit(0 if success else 1)

    # Full CI / QA Suite
    print("================================================================================")
    print("     STARTING COMPLETE VISUAL QA & GRAPHICS SCALABILITY TEST SUITE              ")
    print("================================================================================")

    import_ok = check_headless_import()
    if not import_ok:
        overall_success = False

    profile_ok, report_data = run_profiler()
    if not profile_ok or not report_data:
        overall_success = False
    else:
        display_report_table(report_data)
        if not report_data.get("overall_passed", False):
            overall_success = False

    runtime_ok = check_runtime_stability()
    if not runtime_ok:
        overall_success = False

    print("================================================================================")
    if overall_success:
        print(">> ALL QA GATES PASSED: PBR MATERIALS, SCALABILITY & STABILITY VERIFIED <<")
        sys.exit(0)
    else:
        print(">> QA FAILED: ONE OR MORE VALIDATION GATES FAILED <<")
        sys.exit(1)

if __name__ == "__main__":
    main()
