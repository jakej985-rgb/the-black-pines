extends SceneTree

func _init():
    var torso = load("res://assets/models/sasquatch_torso.obj") as ArrayMesh
    if torso:
        var aabb = torso.get_aabb()
        print("TORSO AABB: pos=", aabb.position, " size=", aabb.size)
    var head = load("res://assets/models/sasquatch_head.obj") as ArrayMesh
    if head:
        var aabb = head.get_aabb()
        print("HEAD AABB: pos=", aabb.position, " size=", aabb.size)
    quit()
