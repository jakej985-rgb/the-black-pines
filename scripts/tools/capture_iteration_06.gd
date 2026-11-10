extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 06 (RANGER STATION OVERHAUL) SCREENSHOTS ===")
    DirAccess.make_dir_recursive_absolute("docs/graphics/iterations")
    
    var main_scene = load("res://scenes/main/main.tscn")
    if not main_scene:
        print("ERROR: Failed to load main.tscn")
        quit(1)
        return
        
    var main = main_scene.instantiate()
    root.add_child(main)
    
    # Wait for frame settlement and lighting
    for i in range(25):
        await process_frame
        
    var cam = Camera3D.new()
    cam.fov = 70.0
    cam.current = true
    root.add_child(cam)
    
    var spot = SpotLight3D.new()
    spot.spot_range = 35.0
    spot.spot_angle = 45.0
    spot.light_energy = 3.2
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Shot 1: Ranger Station Exterior & Porch (1:1 with ranger_station_baseline_exterior.png)
    cam.global_position = Vector3(3.5, 2.2, 17.5)
    cam.look_at(Vector3(0.0, 1.8, 11.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter06_cabin_exterior.png")
    print("[OK] Saved docs/graphics/iterations/iter06_cabin_exterior.png")
    
    # Shot 2: Porch Entrance & Evacuation Notice (1:1 with ranger_station_baseline_porch.png)
    cam.global_position = Vector3(0.5, 1.7, 14.2)
    cam.look_at(Vector3(0.95, 1.72, 12.76), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter06_cabin_porch.png")
    print("[OK] Saved docs/graphics/iterations/iter06_cabin_porch.png")
    
    # Shot 3: Interior Cabin Overview (1:1 with ranger_station_baseline_interior.png)
    cam.global_position = Vector3(0.0, 1.6, 12.2)
    cam.look_at(Vector3(0.0, 1.4, 8.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter06_cabin_interior.png")
    print("[OK] Saved docs/graphics/iterations/iter06_cabin_interior.png")
    
    # Shot 4: Standard Forest Environment Benchmark
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img4 = root.get_viewport().get_texture().get_image()
    img4.save_png("docs/graphics/iterations/iter06_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter06_forest_environment.png")
    
    print("=== ITERATION 06 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
