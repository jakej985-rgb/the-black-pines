extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 05 (ABANDONED CAMPSITE OVERHAUL) SCREENSHOTS ===")
    DirAccess.make_dir_recursive_absolute("docs/graphics/iterations")
    
    var main_scene = load("res://scenes/main/main.tscn")
    if not main_scene:
        print("ERROR: Failed to load main.tscn")
        quit(1)
        return
        
    var main = main_scene.instantiate()
    root.add_child(main)
    
    # Let shaders compile and volumetric fog settle
    for i in range(25):
        await process_frame
        
    var cam = Camera3D.new()
    cam.fov = 68.0
    cam.current = true
    root.add_child(cam)
    
    var spot = SpotLight3D.new()
    spot.spot_range = 35.0
    spot.spot_angle = 42.0
    spot.light_energy = 3.0
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Shot 1: Forest Environment Overview (consistent across all iterations)
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter05_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter05_forest_environment.png")
    
    # Shot 2: Campsite Overview (exact 1:1 angle with camp_baseline_overview.png)
    cam.global_position = Vector3(12.5, 1.8, -5.5)
    cam.look_at(Vector3(8.5, 0.8, -8.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter05_camp_overview.png")
    print("[OK] Saved docs/graphics/iterations/iter05_camp_overview.png")
    
    # Shot 3: Tent & Campfire Close-up (exact 1:1 angle with camp_baseline_tent.png)
    cam.global_position = Vector3(10.5, 1.4, -6.5)
    cam.look_at(Vector3(8.2, 0.9, -8.4), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter05_camp_tent_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter05_camp_tent_closeup.png")
    
    print("=== ITERATION 05 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
