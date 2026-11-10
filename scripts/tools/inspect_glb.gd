extends SceneTree

func _init():
    var scn = load("res://scenes/world/tree_pine_tall.tscn")
    if not scn:
        print("ERROR: Failed to load tree_pine_tall.tscn")
        quit(1)
        return
    var inst = scn.instantiate()
    print("Tree loaded successfully! Name:", inst.name, "Children:", inst.get_child_count())
    var glb = inst.get_node("tree_pine_tall_v2")
    var trunk = glb.get_node("Pine_Trunk")
    var foliage = glb.get_node("Pine_Foliage")
    print("Trunk mat override:", trunk.get_surface_override_material(0))
    print("Foliage mat override:", foliage.get_surface_override_material(0))
    quit(0)
