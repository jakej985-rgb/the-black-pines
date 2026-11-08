extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 03 (FALLEN NURSE LOG OVERHAUL) SCREENSHOTS ===")
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
    
    # Shot 1: Forest Environment Overview (consistent vantage point across baseline, iter01, iter02, iter03)
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter03_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter03_forest_environment.png")
    
    # Shot 2: Close-up of Fallen Nurse Log (FallenLog1 is at (-3.2, 0.721, -7.5))
    cam.global_position = Vector3(-0.6, 1.9, -5.0)
    cam.look_at(Vector3(-3.2, 0.75, -7.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter03_fallen_log_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter03_fallen_log_closeup.png")
    
    # Shot 3: Side/Perspective angle showing root flare and splintered heartwood cavity
    cam.global_position = Vector3(-5.2, 1.5, -9.6)
    cam.look_at(Vector3(-3.2, 0.75, -7.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter03_fallen_log_roots.png")
    print("[OK] Saved docs/graphics/iterations/iter03_fallen_log_roots.png")
    
    print("=== ITERATION 03 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
