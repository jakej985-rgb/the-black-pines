extends SceneTree

func _init():
    print("=== CAPTURING ITERATION 07 (CABIN EXTERIOR PROPS OVERHAUL) SCREENSHOTS ===")
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
    cam.global_position = Vector3(7.4, 1.8, 12.0)
    cam.look_at(Vector3(4.2, 0.9, 10.0), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/iter07_props_overview.png")
    print("[OK] Saved docs/graphics/iterations/iter07_props_overview.png")
    
    # Shot 2: Generator Closeup
    cam.global_position = Vector3(6.2, 1.4, 10.2)
    cam.look_at(Vector3(5.0, 0.8, 8.8), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/iter07_generator_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter07_generator_closeup.png")
    
    # Shot 3: Firewood Stack Closeup
    cam.global_position = Vector3(5.6, 1.1, 11.2)
    cam.look_at(Vector3(3.75, 0.6, 11.2), Vector3.UP)
    for i in range(15):
        await process_frame
    var img3 = root.get_viewport().get_texture().get_image()
    img3.save_png("docs/graphics/iterations/iter07_firewood_closeup.png")
    print("[OK] Saved docs/graphics/iterations/iter07_firewood_closeup.png")
    
    # Shot 4: Broad Cabin Exterior contextual view showing Ranger Station with both props
    cam.global_position = Vector3(5.5, 2.2, 18.0)
    cam.look_at(Vector3(2.0, 1.6, 10.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img4 = root.get_viewport().get_texture().get_image()
    img4.save_png("docs/graphics/iterations/iter07_cabin_context.png")
    print("[OK] Saved docs/graphics/iterations/iter07_cabin_context.png")
    
    print("=== CAPTURE COMPLETE ===")
    quit(0)
