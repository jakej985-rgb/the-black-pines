extends SceneTree

func _init():
    print("=== CAPTURING CAMPSITE BASELINE SCREENSHOT ===")
    DirAccess.make_dir_recursive_absolute("docs/graphics/iterations")
    
    var main_scene = load("res://scenes/main/main.tscn")
    if not main_scene:
        print("ERROR: Failed to load main.tscn")
        quit(1)
        return
        
    var main = main_scene.instantiate()
    root.add_child(main)
    
    for i in range(25):
        await process_frame
        
    var cam = Camera3D.new()
    cam.fov = 68.0
    cam.current = true
    root.add_child(cam)
    
    var spot = SpotLight3D.new()
    spot.spot_range = 30.0
    spot.spot_angle = 45.0
    spot.light_energy = 3.0
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)
    
    # AbandonedCamp is at (8.5, 0.0, -8.5)
    # Camera standing 4.5m away looking at tent, firepit, cooler
    cam.global_position = Vector3(12.5, 1.8, -5.5)
    cam.look_at(Vector3(8.5, 0.8, -8.5), Vector3.UP)
    for i in range(15):
        await process_frame
    var img1 = root.get_viewport().get_texture().get_image()
    img1.save_png("docs/graphics/iterations/camp_baseline_overview.png")
    print("[OK] Saved docs/graphics/iterations/camp_baseline_overview.png")
    
    # Close-up on the tent
    cam.global_position = Vector3(10.5, 1.4, -6.5)
    cam.look_at(Vector3(8.2, 0.9, -8.4), Vector3.UP)
    for i in range(15):
        await process_frame
    var img2 = root.get_viewport().get_texture().get_image()
    img2.save_png("docs/graphics/iterations/camp_baseline_tent.png")
    print("[OK] Saved docs/graphics/iterations/camp_baseline_tent.png")
    
    print("=== CAMPSITE BASELINE COMPLETE ===")
    quit(0)
