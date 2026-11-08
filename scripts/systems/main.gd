class_name MainGame
extends Node3D

## Main game manager linking player, world, and HUD.

@onready var player: Player = $Player
@onready var hud: HUD = $HUD

func _ready() -> void:
	if player and hud:
		hud.setup_player(player)
		# Initial mission prompt
		get_tree().create_timer(1.0).timeout.connect(func():
			if player:
				player.show_notification("Mission: Investigate the sightings around Ranger Station #04")
		)
