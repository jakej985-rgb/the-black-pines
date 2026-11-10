extends SceneTree

func _init():
    print("=== SASQUATCH STUDIO CAPTURE ===")
    DirAccess.make_dir_recursive_absolute("docs/graphics/previews")
    
    var sasquatch = load("res://scenes/creatures/sasquatch.tscn").instantiate()
    root.add_child(sasquatch)
    
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.18, 0.2, 0.22)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.6, 0.62, 0.65)
    env.ambient_light_energy = 0.7
    var we := WorldEnvironment.new()
    we.environment = env
    root.add_child(we)
    
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-45, -30, 0)
    sun.light_energy = 1.6
    sun.shadow_enabled = true
    root.add_child(sun)
    
    var fill := OmniLight3D.new()
    fill.position = Vector3(2.5, 2.2, 3.0)
    fill.light_energy = 1.2
    fill.omni_range = 15.0
    root.add_child(fill)
    
    var cam := Camera3D.new()
    cam.fov = 50.0
    cam.current = true
    root.add_child(cam)
    
    var views := {
        "front": [Vector3(0, 1.7, 6.5), Vector3(0, 1.5, 0)],
        "threequarter": [Vector3(3.2, 2.0, 5.0), Vector3(0, 1.4, 0)],
        "side": [Vector3(6.5, 1.7, 0), Vector3(0, 1.5, 0)],
        "rear": [Vector3(0, 2.0, -6.5), Vector3(0, 1.5, 0)],
        "bust": [Vector3(0.6, 2.55, 2.2), Vector3(0, 2.2, -0.1)],
    }
    
    for i in range(10):
        await process_frame
    
    for name in views:
        var v: Array = views[name]
        cam.global_position = v[0]
        cam.look_at(v[1], Vector3.UP)
        for i in range(10):
            await process_frame
        var img = root.get_viewport().get_texture().get_image()
        img.save_png("docs/graphics/previews/sasquatch_studio_%s.png" % name)
        print("[OK] sasquatch_studio_%s.png" % name)
    
    print("=== STUDIO CAPTURE COMPLETE ===")
    quit(0)
