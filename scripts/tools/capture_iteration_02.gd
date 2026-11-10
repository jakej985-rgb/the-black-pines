extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 02 (ROCKS & FOREST FLOOR) SCREENSHOTS ===")
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
    
    # Shot 1: Forest Environment Overview (new pine needle bed + rocks)
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter02_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter02_forest_environment.png")
    
    # Shot 2: Hero Pine Tree Base & Sprawling Roots with Needle Carpet
    cam.global_position = Vector3(-15.8, 1.3, -6.3)
    cam.look_at(Vector3(-19.18, 0.4, -6.31), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter02_pine_tree_roots.png")
    print("[OK] Saved docs/graphics/iterations/iter02_pine_tree_roots.png")
    
    # Shot 3: Close-up of the new Mossy Rock Cluster
    # RockClusterMossy1 is at (-17.4, -0.05, -4.8)
    cam.global_position = Vector3(-14.2, 1.5, -3.2)
    cam.look_at(Vector3(-17.4, 0.6, -4.8), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter02_rock_cluster_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter02_rock_cluster_closeup.png")
    
    print("=== ITERATION 02 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
