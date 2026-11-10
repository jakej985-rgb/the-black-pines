extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 01 (PINE TREE OVERHAUL) SCREENSHOTS ===")
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
        
    var player = main.get_node_or_null("Player")
    var player_cam = null
    if player:
        player_cam = player.find_child("Camera3D", true, false)
        if player_cam:
            player_cam.current = true
            
    for i in range(15):
        await process_frame
        
    # Shot 1: Player Camera View
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter01_player_camera_view.png")
    print("[OK] Saved docs/graphics/iterations/iter01_player_camera_view.png")
    
    # Create capture camera with spotlight
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
    
    # Shot 2: Forest Environment View (overview towards clearing and treeline)
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter01_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter01_forest_environment.png")
    
    # Shot 3: Hero Pine Tree Close-up View (directly facing PineTree_070 at -19.18, -0.06, -6.31)
    cam.global_position = Vector3(-14.2, 2.4, -6.3)
    cam.look_at(Vector3(-19.18, 5.0, -6.31), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter01_pine_tree_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter01_pine_tree_closeup.png")
    
    # Shot 4: Hero Pine Tree Trunk Base & Roots Close-up
    cam.global_position = Vector3(-16.0, 1.2, -6.3)
    cam.look_at(Vector3(-19.18, 0.5, -6.31), Vector3.UP)
    for i in range(15):
        await process_frame
    var img4 = root.get_viewport().get_texture().get_image()
    img4.save_png("docs/graphics/iterations/iter01_pine_tree_roots.png")
    print("[OK] Saved docs/graphics/iterations/iter01_pine_tree_roots.png")
    
    print("=== ITERATION 01 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
