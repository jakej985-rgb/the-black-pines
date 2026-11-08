extends SceneTree

func _init():
    print("=== CAPTURING BASELINE SCREENSHOTS ===")
    DirAccess.make_dir_recursive_absolute("docs/graphics/baseline")
    
    var main_scene = load("res://scenes/main/main.tscn")
    if not main_scene:
        print("ERROR: Failed to load main.tscn")
        quit(1)
        return
        
    var main = main_scene.instantiate()
    root.add_child(main)
    
    # Let scene initialize, shaders compile, volumetric fog settle
    for i in range(25):
        await process_frame
        
    var player = main.get_node_or_null("Player")
    var player_cam = null
    if player:
        player_cam = player.find_child("Camera3D", true, false)
        if player_cam:
            player_cam.current = true
            
    # Frame settle
    for i in range(15):
        await process_frame
        
    # Shot 1: Player Camera View
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/baseline/01_player_camera_view.png")
    print("[OK] Saved docs/graphics/baseline/01_player_camera_view.png")
    
    # Create capture camera for forest and tree inspection
    var cam = Camera3D.new()
    cam.fov = 70.0
    cam.current = true
    root.add_child(cam)
    
    var spot = SpotLight3D.new()
    spot.spot_range = 40.0
    spot.spot_angle = 38.0
    spot.light_energy = 2.0
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Shot 2: Forest Environment View
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/baseline/02_forest_environment.png")
    print("[OK] Saved docs/graphics/baseline/02_forest_environment.png")
    
    # Shot 3: Pine Tree Close-up View (looking at one representative mature pine)
    cam.global_position = Vector3(3.5, 2.2, -6.0)
    cam.look_at(Vector3(0.0, 4.0, -14.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/baseline/03_pine_tree_closeup.png")
    print("[OK] Saved docs/graphics/baseline/03_pine_tree_closeup.png")
    
    print("=== BASELINE CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
