extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 07 BASELINE (CABIN EXTERIOR PROPS) ===")
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
    spot.spot_range = 30.0
    spot.spot_angle = 50.0
    spot.light_energy = 3.5
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Shot 1: Generator and Firewood side-by-side beside Ranger Station
    cam.global_position = Vector3(6.8, 1.8, 12.2)
    cam.look_at(Vector3(4.1, 0.8, 10.1), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter07_baseline_props_overview.png")
    print("[OK] Saved docs/graphics/iterations/iter07_baseline_props_overview.png")
    
    # Shot 2: Generator Closeup
    cam.global_position = Vector3(5.8, 1.3, 10.8)
    cam.look_at(Vector3(4.8, 0.7, 9.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter07_baseline_generator.png")
    print("[OK] Saved docs/graphics/iterations/iter07_baseline_generator.png")
    
    # Shot 3: Firewood Stack Closeup
    cam.global_position = Vector3(4.5, 1.1, 12.3)
    cam.look_at(Vector3(3.4, 0.5, 10.8), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter07_baseline_firewood.png")
    print("[OK] Saved docs/graphics/iterations/iter07_baseline_firewood.png")
    
    print("=== CAPTURE COMPLETE ===")
    quit(0)
