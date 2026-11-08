extends SceneTree

const SasquatchScene = preload("res://scenes/creatures/sasquatch.tscn")
const PlayerScene = preload("res://scenes/player/player.tscn")

func _init() -> void:
	print("--- BEGIN SASQUATCH AI ENCOUNTER TEST ---")
	await process_frame

	var world = Node3D.new()
	world.name = "TestWorld"
	root.add_child(world)

	var player = PlayerScene.instantiate()
	player.name = "Player"
	world.add_child(player)
	player.global_position = Vector3(0, 0, 0)

	var sasquatch = SasquatchScene.instantiate() as Sasquatch
	world.add_child(sasquatch)
	sasquatch.global_position = Vector3(20, 0, 0)
	await process_frame
	await process_frame

	# 1. Verify Initial Stalking State
	assert(sasquatch.current_state == Sasquatch.State.STALKING, "Sasquatch should start in STALKING state")
	assert(sasquatch.get_current_state_name() == "STALKING", "State name should return STALKING")
	print("✓ Initial stalking state verified.")

	# 2. Test Noise/Sprint Investigation Stimulus
	player.is_sprinting = true
	sasquatch._process_stalking(0.1)
	assert(sasquatch.current_state == Sasquatch.State.INVESTIGATING, "Sprinting player within hearing radius should trigger INVESTIGATING")
	print("✓ Auditory sprint detection and INVESTIGATING transition verified.")

	# 3. Test Flanking Transition
	sasquatch.global_position = sasquatch.noise_target_pos + Vector3(1.0, 0, 0)
	sasquatch._process_investigating(0.1)
	assert(sasquatch.current_state == Sasquatch.State.FLANKING, "Reaching noise origin should transition to FLANKING")
	print("✓ Flanking transition verified.")

	# 4. Test Stare/Telegraph Alerted Phase
	sasquatch.global_position = player.global_position + Vector3(12.0, 0, 0) # within stalk_distance_trigger (14m)
	sasquatch._trigger_encounter()
	assert(sasquatch.current_state == Sasquatch.State.ALERTED, "Encounter trigger should place creature in ALERTED telegraph phase")
	print("✓ Encounter telegraph phase verified.")

	# 5. Test Attack Charge & Melee Strike Interface
	var initial_player_hp = player.health
	sasquatch.set_state(Sasquatch.State.ATTACK_CHARGE)
	sasquatch.global_position = player.global_position + Vector3(1.5, 0, 0) # within melee_range (2.0m)
	sasquatch._process_attack_charge(0.1)

	assert(player.health < initial_player_hp, "Melee attack must apply damage to player")
	assert(player.health == initial_player_hp - sasquatch.attack_damage, "Player should take exactly attack_damage (28.0)")
	assert(player.health_component.is_bleeding == true, "Claw strike must cause bleeding")
	assert(sasquatch.current_state == Sasquatch.State.RETREATING, "Creature must disengage and enter RETREATING state after strike")
	print("✓ Melee damage, hemorrhage infliction, and safe disengage verified.")

	# 6. Test Trap Stagger & Flare Fear
	sasquatch.apply_trap_stagger(3.0, 30.0)
	assert(sasquatch.current_state == Sasquatch.State.STAGGERED, "apply_trap_stagger must transition to STAGGERED")
	assert(sasquatch.stagger_timer == 3.0, "Stagger timer must be set")

	sasquatch.apply_flare_fear(Vector3(0, 0, 0), 5.0)
	assert(sasquatch.current_state == Sasquatch.State.FEARED, "apply_flare_fear must transition to FEARED")
	assert(sasquatch.fear_timer == 5.0, "Fear timer must be set")
	print("✓ Defensive tool reactions (trap stagger, flare fear) verified.")

	# Clean up
	world.queue_free()

	print("--- SASQUATCH AI ENCOUNTER TESTS PASSED ---")
	quit(0)
