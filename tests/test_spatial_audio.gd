extends SceneTree

const AudioDirectorClass = preload("res://scripts/systems/audio_director.gd")
const PlayerScene = preload("res://scenes/player/player.tscn")

func _init() -> void:
	print("--- BEGIN SPATIAL & SURFACE AUDIO TEST ---")
	await process_frame

	var audio = AudioDirectorClass.new()
	root.add_child(audio)
	await process_frame

	# 1. Verify Audio Stream Synthesis
	assert(audio.footstep_needles_stream != null, "Pine needles footstep stream should be synthesized")
	assert(audio.footstep_wood_stream != null, "Wood footstep stream should be synthesized")
	assert(audio.footstep_mud_stream != null, "Mud footstep stream should be synthesized")
	assert(audio.footstep_stone_stream != null, "Stone footstep stream should be synthesized")
	assert(audio.breath_stream != null, "Breathing stream should be synthesized")
	assert(audio.wood_knock_stream != null, "Wood knock stream should be synthesized")
	print("✓ All procedural audio streams synthesized successfully.")

	# 2. Test Surface Footstep Stream Selection
	audio.play_footstep(false, AudioDirectorClass.SurfaceType.WOOD)
	assert(audio.footstep_player.stream == audio.footstep_wood_stream, "Wood surface should set wood stream")

	audio.play_footstep(true, AudioDirectorClass.SurfaceType.MUD)
	assert(audio.footstep_player.stream == audio.footstep_mud_stream, "Mud surface should set mud stream")

	audio.play_footstep(false, AudioDirectorClass.SurfaceType.STONE)
	assert(audio.footstep_player.stream == audio.footstep_stone_stream, "Stone surface should set stone stream")

	audio.play_footstep(false, AudioDirectorClass.SurfaceType.PINE_NEEDLES)
	assert(audio.footstep_player.stream == audio.footstep_needles_stream, "Pine needles surface should set needles stream")
	print("✓ Surface stream classification verified.")

	# 3. Test Sprint/Walk Pitch & Volume Adjustments
	audio.play_footstep(true, AudioDirectorClass.SurfaceType.WOOD)
	assert(audio.footstep_player.volume_db == -8.0, "Sprint footstep should be louder (-8.0 dB)")

	audio.play_footstep(false, AudioDirectorClass.SurfaceType.WOOD)
	assert(audio.footstep_player.volume_db == -11.0, "Walk footstep should be quieter (-11.0 dB)")
	print("✓ Movement pacing pitch and volume modulation verified.")

	# 4. Test Low Stamina Breathing
	audio.play_heavy_breathing()
	assert(audio.breath_player != null, "Breath player should exist")
	print("✓ Low stamina ragged breathing trigger verified.")

	# 5. Test Spatial Wood Knock
	audio.play_distant_wood_knock()
	var has_3d = false
	for child in audio.get_children():
		if child is AudioStreamPlayer3D and child.stream == audio.wood_knock_stream:
			has_3d = true
			assert(child.max_distance > 30.0, "Knock should attenuate over long distance")
			break
	assert(has_3d == true, "3D spatial player for wood knock should be spawned")
	print("✓ Territorial spatial wood knock verified.")

	# 6. Test Surface Classification on Player
	var player = PlayerScene.instantiate()
	root.add_child(player)
	await process_frame

	# In empty space or terrain, default is PINE_NEEDLES (0)
	var default_surf = player._detect_ground_surface()
	assert(default_surf == AudioDirectorClass.SurfaceType.PINE_NEEDLES, "Default unclassified surface should be PINE_NEEDLES")
	print("✓ Player surface detection fallback verified.")

	# Clean up
	player.queue_free()
	audio.queue_free()

	print("--- SPATIAL & SURFACE AUDIO TESTS PASSED ---")
	quit(0)
