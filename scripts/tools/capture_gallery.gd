extends SceneTree

var targets = [
    {
        "name": "01_elk_carcass_overview",
        "cam_pos": Vector3(-10.5, 1.8, -15.2),
        "look_at": Vector3(-10.5, 0.4, -18.0)
    },
    {
        "name": "02_elk_carcass_closeup",
        "cam_pos": Vector3(-11.2, 1.1, -16.8),
        "look_at": Vector3(-10.8, 0.35, -18.0)
    },
    {
        "name": "03_cabin_exterior_perspective",
        "cam_pos": Vector3(4.5, 2.2, 18.5),
        "look_at": Vector3(0.0, 1.8, 12.0)
    },
    {
        "name": "04_cabin_porch_entrance",
        "cam_pos": Vector3(0.0, 1.6, 16.5),
        "look_at": Vector3(0.0, 1.6, 12.6)
    },
    {
        "name": "05_sasquatch_flashlight",
        "cam_pos": Vector3(-8.5, 2.0, -25.2),
        "look_at": Vector3(-8.5, 1.85, -28.0)
    },
    {
        "name": "06_cabin_interior_overview",
        "cam_pos": Vector3(0.0, 1.55, 12.2),
        "look_at": Vector3(-0.3, 1.4, 9.2)
    },
    {
        "name": "07_cabin_desk_investigation",
        "cam_pos": Vector3(-1.3, 1.6, 10.3),
        "look_at": Vector3(-1.95, 1.05, 9.25)
    },
    {
        "name": "08_document_evacuation_notice",
        "cam_pos": Vector3(0.95, 1.72, 13.50),
        "look_at": Vector3(0.95, 1.72, 12.76)
    }
]



func _init():
    print("--- STARTING IN-ENGINE ASSET GALLERY CAPTURE ---")
    var forest_scene = load("res://scenes/world/forest.tscn")
    if not forest_scene:
        print("ERROR: Failed to load forest.tscn")
        quit(1)
        return
        
    var forest = forest_scene.instantiate()
    root.add_child(forest)
    
    var cam = Camera3D.new()
    cam.current = true
    cam.fov = 65.0
    root.add_child(cam)
    await process_frame

    # Ensure output directory exists
    DirAccess.make_dir_recursive_absolute("reports/visual_review")

    # Add a player-style flashlight attached to the camera for illuminated beauty shots
    var spot = SpotLight3D.new()
    spot.spot_range = 35.0
    spot.spot_angle = 36.0
    spot.spot_attenuation = 1.0
    spot.light_energy = 3.2
    spot.light_color = Color(0.98, 0.95, 0.88)
    spot.shadow_enabled = true
    cam.add_child(spot)

    for target in targets:
        cam.global_position = target["cam_pos"]
        cam.look_at(target["look_at"], Vector3.UP)
        
        # Settle frame buffers and volumetric fog
        for f in range(25):
            await process_frame
            
        var img = root.get_viewport().get_texture().get_image()
        if img:
            var path = "reports/visual_review/" + target["name"] + ".png"
            img.save_png(path)
            print("Captured: ", path)
        else:
            print("ERROR: Failed to grab viewport image for ", target["name"])
            
    print("--- GALLERY CAPTURE COMPLETED SUCCESSFULLY ---")
    quit(0)
