extends SceneTree

func _init():
    var main_scene = load("res://scenes/main/main.tscn")
    var main = main_scene.instantiate()
    root.add_child(main)
    
    await process_frame
    await process_frame
    
    var camp = main.find_child("AbandonedCamp", true, false)
    if not camp:
        print("Could not find AbandonedCamp node!")
        quit(1)
        return
        
    var camp_pos = camp.global_position
    print("=== ABANDONED CAMP POS: ", camp_pos, " ===")
    
    check_tree(main, camp_pos)
    quit(0)

func check_tree(node: Node, target_pos: Vector3):
    if node is Node3D and node.name != "AbandonedCamp":
        var d = node.global_position.distance_to(target_pos)
        if d < 7.0 and node.get_parent() != null and node.get_parent().name != "AbandonedCamp":
            print("Node: ", node.name, " [", node.get_class(), "] at pos: ", node.global_position, " (dist: ", d, ")")
    for c in node.get_children():
        check_tree(c, target_pos)
