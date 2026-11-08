extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 04 (WESTERN SWORD FERN OVERHAUL) SCREENSHOTS ===")
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
    spot.light_energy = 3.2
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # Shot 1: Forest Environment Overview (consistent vantage point across baseline, iter01-04)
    cam.global_position = Vector3(12.0, 3.5, 10.0)
    cam.look_at(Vector3(-15.0, 1.5, -20.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter04_forest_environment.png")
    print("[OK] Saved docs/graphics/iterations/iter04_forest_environment.png")
    
    # Shot 2: Close-up of Western Sword Fern cluster beside nurse log (at -5.5, 0.68, -6.8)
    cam.global_position = Vector3(-3.8, 1.4, -5.2)
    cam.look_at(Vector3(-5.5, 0.75, -6.8), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter04_fern_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter04_fern_closeup.png")
    
    # Shot 3: Forest Undergrowth Ecosystem (Rock Cluster + Hero Pine Roots + Sword Fern)
    cam.global_position = Vector3(-12.8, 1.3, -2.2)
    cam.look_at(Vector3(-16.4, 0.65, -4.6), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter04_fern_rock_ecosystem.png")
    print("[OK] Saved docs/graphics/iterations/iter04_fern_rock_ecosystem.png")
    
    print("=== ITERATION 04 CAPTURE COMPLETED SUCCESSFULLY ===")
    quit(0)
