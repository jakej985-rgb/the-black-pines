class_name ForestTerrain
extends StaticBody3D

## Manages procedural undulating terrain mesh and trimesh collision.

@onready var mesh_instance: MeshInstance3D = $MeshInstance3D
@onready var col_shape: CollisionShape3D = $CollisionShape3D

func _ready() -> void:
	if mesh_instance and mesh_instance.mesh:
		col_shape.transform = Transform3D.IDENTITY
		col_shape.shape = mesh_instance.mesh.create_trimesh_shape()
