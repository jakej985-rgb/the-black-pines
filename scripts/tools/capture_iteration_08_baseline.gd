extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 08 BASELINE (SASQUATCH) SCREENSHOTS ===")
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
    cam.fov = 65.0
    cam.current = true
    root.add_child(cam)
    
    var spot = SpotLight3D.new()
    spot.spot_range = 35.0
    spot.spot_angle = 45.0
    spot.light_energy = 3.5
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Sasquatch is at (-8.5, 0.0, -28.0) in forest.tscn
    # Shot 1: Full body framing
    cam.global_position = Vector3(-8.5, 1.8, -22.5)
    cam.look_at(Vector3(-8.5, 1.5, -28.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter08_baseline_sasquatch_full.png")
    print("[OK] Saved docs/graphics/iterations/iter08_baseline_sasquatch_full.png")
    
    # Shot 2: Head & Face Closeup
    cam.global_position = Vector3(-8.5, 2.3, -25.8)
    cam.look_at(Vector3(-8.5, 2.3, -28.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter08_baseline_sasquatch_head.png")
    print("[OK] Saved docs/graphics/iterations/iter08_baseline_sasquatch_head.png")
    
    # Shot 3: Atmospheric Stalking Silhouette in the Dark Pines
    cam.global_position = Vector3(-6.0, 1.6, -18.0)
    cam.look_at(Vector3(-8.5, 1.8, -28.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter08_baseline_sasquatch_stalking.png")
    print("[OK] Saved docs/graphics/iterations/iter08_baseline_sasquatch_stalking.png")
    
    print("=== CAPTURE COMPLETE ===")
    quit(0)
