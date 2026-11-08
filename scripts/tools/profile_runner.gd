extends SceneTree

## Headless Graphics Scalability Profiler & Visual QA Runner.
## Measures frame time, draw calls, memory, and verifies zero broken resources/leaks.

const REPORT_PATH = "reports/visual_qa_report.json"
const FRAMES_WARMUP = 15
const FRAMES_SAMPLE = 60

var results: Dictionary = {
	"timestamp": "",
	"godot_version": "",
	"presets": {},
	"resource_audit": {
		"total_checked": 0,
		"passed": 0,
		"failed": 0,
		"broken_resources": []
	},
	"memory_leak_check": {
		"initial_memory_bytes": 0,
		"final_memory_bytes": 0,
		"delta_bytes": 0,
		"passed": true
	},
	"overall_passed": true
}

func _init() -> void:
	_run_qa()

func _run_qa() -> void:
	print("================================================================")
	print("   THE BLACK PINES - GRAPHICS PROFILING & VISUAL QA RUNNER      ")
	print("================================================================")
	
	results["timestamp"] = Time.get_datetime_string_from_system()
	results["godot_version"] = Engine.get_version_info()["string"]

	# Run resource integrity audit first
	_audit_resources()

	# Run graphics scalability profiling
	await _run_preset_benchmarks()

	# Verify memory stability
	await _check_memory_leaks()

	# Save report
	_save_report()

	print("\n================================================================")
	if results["overall_passed"]:
		print("   [QA RESULT]: ALL GRAPHICS BENCHMARKS & AUDITS PASSED         ")
	else:
		print("   [QA RESULT]: FAILURES DETECTED IN QA RUN                     ")
	print("================================================================")
	
	quit(0 if results["overall_passed"] else 1)

func _audit_resources() -> void:
	print("\n[1/3] Auditing Project Resources & PBR Materials...")
	var resources_to_check = [
		"res://assets/materials/mat_craggy_rock.tres",
		"res://assets/materials/mat_pine_bark.tres",
		"res://assets/materials/mat_cabin_wood.tres",
		"res://assets/materials/mat_cabin_roof.tres",
		"res://assets/materials/mat_exposed_wood.tres",
		"res://assets/materials/mat_terrain_ground.tres",
		"res://assets/materials/mat_forest_ground.tres",
		"res://assets/materials/mat_weathered_bone.tres",
		"res://assets/materials/mat_gore_blood.tres",
		"res://assets/materials/mat_tent_canvas.tres",
		"res://assets/materials/mat_rusted_metal.tres",
		"res://assets/materials/mat_painted_metal.tres",
		"res://assets/materials/rock_weathered.gdshader",
		"res://assets/materials/wood_weathered.gdshader",
		"res://assets/materials/terrain_ground.gdshader",
		"res://assets/materials/foliage_wind.gdshader",
		"res://scenes/world/forest.tscn",
		"res://scenes/world/forest_terrain.tscn",
		"res://scenes/world/pine_tree.tscn",
		"res://scenes/world/tree_douglas_fir.tscn",
		"res://scenes/world/tree_pine_tall.tscn",
		"res://scenes/world/tree_snag_dead.tscn",
		"res://scenes/world/tree_sapling.tscn",
		"res://scenes/world/pine_roots.tscn",
		"res://scenes/world/rock_cluster.tscn",
		"res://scenes/world/rock_outcrop.tscn",
		"res://scenes/world/rock_craggy.tscn",
		"res://scenes/world/rock_flat_slab.tscn",
		"res://scenes/world/cabin_generator.tscn",
		"res://scenes/interactables/scrap_metal.tscn",
		"res://scenes/interactables/trail_marker.tscn",
		"res://scenes/interactables/clue_carcass.tscn",
		"res://scenes/interactables/clue_clawed_tree.tscn",
		"res://scenes/interactables/clue_footprint.tscn",
		"res://scenes/main/main.tscn"
	]

	var total = 0
	var passed = 0
	for path in resources_to_check:
		total += 1
		if ResourceLoader.exists(path):
			var res = ResourceLoader.load(path)
			if res != null:
				passed += 1
			else:
				results["resource_audit"]["broken_resources"].append(path + " (Failed to load)")
		else:
			results["resource_audit"]["broken_resources"].append(path + " (Does not exist)")

	results["resource_audit"]["total_checked"] = total
	results["resource_audit"]["passed"] = passed
	results["resource_audit"]["failed"] = total - passed
	if results["resource_audit"]["failed"] > 0:
		results["overall_passed"] = false
		print("  -> ERROR: Broken resources found: ", results["resource_audit"]["broken_resources"])
	else:
		print("  -> Resource audit clean: %d / %d resources loaded flawlessly." % [passed, total])

func _run_preset_benchmarks() -> void:
	print("\n[2/3] Benchmarking Graphics Scalability Presets (Low, Medium, High, Ultra)...")
	
	results["memory_leak_check"]["initial_memory_bytes"] = OS.get_static_memory_usage()

	# Instantiate Main scene for real-world GPU/CPU simulation
	var main_scene = load("res://scenes/main/main.tscn")
	if not main_scene:
		printerr("Failed to load main.tscn for benchmarking!")
		results["overall_passed"] = false
		return
	
	var main_instance = main_scene.instantiate()
	root.add_child(main_instance)

	var presets = [
		GraphicsSettingsManager.Preset.LOW,
		GraphicsSettingsManager.Preset.MEDIUM,
		GraphicsSettingsManager.Preset.HIGH,
		GraphicsSettingsManager.Preset.ULTRA
	]

	# Ensure GraphicsSettingsManager is initialized in standalone SceneTree
	var gfx_mgr: GraphicsSettingsManager = GraphicsSettingsManager.instance
	if gfx_mgr == null:
		gfx_mgr = GraphicsSettingsManager.new()
		gfx_mgr.name = "GraphicsSettings"
		root.add_child(gfx_mgr)

	# Allow all _ready() and deferred setup calls to complete before starting benchmarks
	await process_frame
	await process_frame

	for preset in presets:
		var preset_name = GraphicsSettingsManager.PRESET_NAMES[preset]
		print("  -> Profiling Preset: %s..." % preset_name)
		
		# Apply preset settings
		if gfx_mgr:
			gfx_mgr.apply_preset(preset, false)
			gfx_mgr.apply_all(main_instance)
		
		# Warmup frames
		for i in range(FRAMES_WARMUP):
			await process_frame

		# Sampling frames
		var frame_times: Array[float] = []
		var draw_calls_accum: float = 0.0
		var memory_samples: Array[int] = []

		for i in range(FRAMES_SAMPLE):
			var start_time = Time.get_ticks_usec()
			await process_frame
			var elapsed_ms = (Time.get_ticks_usec() - start_time) / 1000.0
			frame_times.append(elapsed_ms)
			
			draw_calls_accum += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
			memory_samples.append(int(Performance.get_monitor(Performance.MEMORY_STATIC)))

		# Metrics calculation
		var avg_frame_ms = _calculate_average(frame_times)
		var min_frame_ms = _calculate_min(frame_times)
		var max_frame_ms = _calculate_max(frame_times)
		var avg_draw_calls = draw_calls_accum / float(FRAMES_SAMPLE)
		var avg_memory_mb = (_calculate_average_int(memory_samples)) / (1024.0 * 1024.0)
		var est_fps = 1000.0 / avg_frame_ms if avg_frame_ms > 0.0 else 999.0

		var preset_data = {
			"render_scale": gfx_mgr.render_scale if gfx_mgr else 1.0,
			"volumetric_fog": gfx_mgr.volumetric_fog_enabled if gfx_mgr else true,
			"shadow_atlas_size": gfx_mgr.shadow_atlas_size if gfx_mgr else 4096,
			"ssao_enabled": gfx_mgr.ssao_enabled if gfx_mgr else true,
			"ssil_enabled": gfx_mgr.ssil_enabled if gfx_mgr else true,
			"avg_frame_time_ms": snapped(avg_frame_ms, 0.01),
			"min_frame_time_ms": snapped(min_frame_ms, 0.01),
			"max_frame_time_ms": snapped(max_frame_ms, 0.01),
			"estimated_fps": snapped(est_fps, 0.1),
			"avg_draw_calls": snapped(avg_draw_calls, 0.1),
			"memory_used_mb": snapped(avg_memory_mb, 0.1)
		}
		
		results["presets"][preset_name] = preset_data
		print("     Avg Time: %.2f ms | Est FPS: %.1f | Memory: %.1f MB | Fog: %s | Scale: %.2f | Shadows: %d" % [
			preset_data["avg_frame_time_ms"],
			preset_data["estimated_fps"],
			preset_data["memory_used_mb"],
			"ON" if preset_data["volumetric_fog"] else "OFF",
			preset_data["render_scale"],
			preset_data["shadow_atlas_size"]
		])

	# Cleanup instance
	main_instance.queue_free()
	for i in range(5):
		await process_frame

func _check_memory_leaks() -> void:
	print("\n[3/3] Verifying Memory Stability & Resource Deallocation...")
	# Allow deferred deallocations
	for i in range(15):
		await process_frame

	var final_mem = OS.get_static_memory_usage()
	results["memory_leak_check"]["final_memory_bytes"] = final_mem
	var delta = final_mem - results["memory_leak_check"]["initial_memory_bytes"]
	results["memory_leak_check"]["delta_bytes"] = delta
	
	# Tolerance of 8MB for Godot engine internal cache growth
	var max_allowed_leak = 8 * 1024 * 1024
	if delta > max_allowed_leak:
		results["memory_leak_check"]["passed"] = false
		results["overall_passed"] = false
		print("  -> ERROR: Significant memory retention detected: +%.2f MB" % (delta / (1024.0 * 1024.0)))
	else:
		print("  -> Memory leak check passed. Stable delta: %+.2f MB (within budget)." % (delta / (1024.0 * 1024.0)))

func _calculate_average(arr: Array[float]) -> float:
	if arr.is_empty():
		return 0.0
	var sum = 0.0
	for val in arr:
		sum += val
	return sum / float(arr.size())

func _calculate_average_int(arr: Array[int]) -> float:
	if arr.is_empty():
		return 0.0
	var sum = 0.0
	for val in arr:
		sum += float(val)
	return sum / float(arr.size())

func _calculate_min(arr: Array[float]) -> float:
	if arr.is_empty():
		return 0.0
	var m = arr[0]
	for val in arr:
		if val < m:
			m = val
	return m

func _calculate_max(arr: Array[float]) -> float:
	if arr.is_empty():
		return 0.0
	var m = arr[0]
	for val in arr:
		if val > m:
			m = val
	return m

func _save_report() -> void:
	var dir = DirAccess.open("res://")
	if not dir.dir_exists("reports"):
		dir.make_dir("reports")
	
	var file = FileAccess.open(REPORT_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(results, "\t"))
		file.close()
		print("\nQA Report written to: %s" % REPORT_PATH)
	else:
		printerr("Failed to write report to %s" % REPORT_PATH)
