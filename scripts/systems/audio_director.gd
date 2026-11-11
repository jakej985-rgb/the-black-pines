class_name AudioDirector
extends Node

## Procedural horror audio synthesizer for The Black Pines.
## Synthesizes surface-aware footsteps (needles, wood, mud, stone), wind ambient,
## branch snaps, cryptid roars, heavy stamina breathing, and territorial wood knocks.

static var instance: AudioDirector = null

enum SurfaceType {
	PINE_NEEDLES = 0,
	WOOD = 1,
	MUD = 2,
	STONE = 3
}

var wind_player: AudioStreamPlayer = null
var footstep_player: AudioStreamPlayer = null
var breath_player: AudioStreamPlayer = null
var sfx_player: AudioStreamPlayer = null
var ambient_timer: float = 6.0
var knock_timer: float = 14.0

var footstep_needles_stream: AudioStreamWAV = null
var footstep_wood_stream: AudioStreamWAV = null
var footstep_mud_stream: AudioStreamWAV = null
var footstep_stone_stream: AudioStreamWAV = null

var branch_snap_stream: AudioStreamWAV = null
var cryptid_growl_stream: AudioStreamWAV = null
var click_stream: AudioStreamWAV = null
var pickup_stream: AudioStreamWAV = null
var breath_stream: AudioStreamWAV = null
var wood_knock_stream: AudioStreamWAV = null

func _enter_tree() -> void:
	instance = self

func _ready() -> void:
	_generate_audio_streams()
	_setup_audio_players()

func _setup_audio_players() -> void:
	# Continuous wind loop
	wind_player = AudioStreamPlayer.new()
	wind_player.stream = _generate_wind_loop()
	wind_player.volume_db = -12.0
	wind_player.autoplay = true
	add_child(wind_player)
	wind_player.play()

	# Footsteps
	footstep_player = AudioStreamPlayer.new()
	footstep_player.volume_db = -10.0
	add_child(footstep_player)

	# Stamina Breathing
	breath_player = AudioStreamPlayer.new()
	breath_player.stream = breath_stream
	breath_player.volume_db = -14.0
	add_child(breath_player)

	# 2D SFX
	sfx_player = AudioStreamPlayer.new()
	sfx_player.volume_db = -4.0
	add_child(sfx_player)

func _process(delta: float) -> void:
	ambient_timer -= delta
	if ambient_timer <= 0.0:
		ambient_timer = randf_range(9.0, 20.0)
		_play_random_distant_snap()

	knock_timer -= delta
	if knock_timer <= 0.0:
		knock_timer = randf_range(18.0, 38.0)
		play_distant_wood_knock()

func play_footstep(is_sprint: bool, surface: SurfaceType = SurfaceType.PINE_NEEDLES) -> void:
	if not footstep_player:
		return

	match surface:
		SurfaceType.WOOD:
			footstep_player.stream = footstep_wood_stream
		SurfaceType.MUD:
			footstep_player.stream = footstep_mud_stream
		SurfaceType.STONE:
			footstep_player.stream = footstep_stone_stream
		_:
			footstep_player.stream = footstep_needles_stream

	footstep_player.pitch_scale = randf_range(0.88, 1.12) if not is_sprint else randf_range(1.10, 1.28)
	footstep_player.volume_db = -8.0 if is_sprint else -11.0
	footstep_player.play()

func play_heavy_breathing() -> void:
	if breath_player and not breath_player.playing:
		breath_player.pitch_scale = randf_range(0.92, 1.05)
		breath_player.play()

func play_click() -> void:
	if sfx_player and click_stream:
		sfx_player.stream = click_stream
		sfx_player.pitch_scale = randf_range(0.95, 1.05)
		sfx_player.volume_db = -6.0
		sfx_player.play()

func play_pickup() -> void:
	if sfx_player and pickup_stream:
		sfx_player.stream = pickup_stream
		sfx_player.pitch_scale = randf_range(0.98, 1.02)
		sfx_player.volume_db = -4.0
		sfx_player.play()

# Optimization: Persistent pooled 3D audio players to eliminate heap allocations and queue_free churn
var _cryptid_roar_player_3d: AudioStreamPlayer3D = null
var _wood_knock_player_3d: AudioStreamPlayer3D = null
var _distant_snap_player_3d: AudioStreamPlayer3D = null

func play_cryptid_roar(pos_3d: Vector3 = Vector3.ZERO) -> void:
	# Optimization: Reuse a persistent AudioStreamPlayer3D instance rather than allocating
	# a new node, adding it to the SceneTree, connecting a signal lambda, and queuing free on every roar.
	# Expected performance impact: Eliminates heap node allocation and garbage churn during encounter triggers.
	if not _cryptid_roar_player_3d or not is_instance_valid(_cryptid_roar_player_3d):
		_cryptid_roar_player_3d = AudioStreamPlayer3D.new()
		_cryptid_roar_player_3d.stream = cryptid_growl_stream
		_cryptid_roar_player_3d.max_distance = 65.0
		_cryptid_roar_player_3d.volume_db = 6.0
		add_child(_cryptid_roar_player_3d)

	var pitch = randf_range(0.85, 1.0)
	if _cryptid_roar_player_3d.playing:
		# Pooled player busy: spawn a temporary one so the current roar is not cut off
		var temp = AudioStreamPlayer3D.new()
		temp.stream = cryptid_growl_stream
		temp.max_distance = 65.0
		temp.volume_db = 6.0
		temp.position = pos_3d
		temp.pitch_scale = pitch
		add_child(temp)
		temp.play()
		temp.finished.connect(func(): temp.queue_free())
		return

	_cryptid_roar_player_3d.position = pos_3d
	_cryptid_roar_player_3d.pitch_scale = pitch
	_cryptid_roar_player_3d.play()

func play_distant_wood_knock() -> void:
	if not _wood_knock_player_3d or not is_instance_valid(_wood_knock_player_3d):
		_wood_knock_player_3d = AudioStreamPlayer3D.new()
		_wood_knock_player_3d.stream = wood_knock_stream
		_wood_knock_player_3d.max_distance = 60.0
		_wood_knock_player_3d.volume_db = 4.0
		add_child(_wood_knock_player_3d)

	var angle = randf() * TAU
	var dist = randf_range(28.0, 50.0)
	var pos = Vector3(cos(angle) * dist, 2.0, sin(angle) * dist)
	if _wood_knock_player_3d.playing:
		# Pooled player busy: spawn a temporary one so the current knock isn't cut off
		var temp = AudioStreamPlayer3D.new()
		temp.stream = wood_knock_stream
		temp.max_distance = 60.0
		temp.volume_db = 4.0
		temp.position = pos
		add_child(temp)
		temp.play()
		temp.finished.connect(func(): temp.queue_free())
		return
	_wood_knock_player_3d.position = pos
	_wood_knock_player_3d.play()

func _play_random_distant_snap() -> void:
	if not _distant_snap_player_3d or not is_instance_valid(_distant_snap_player_3d):
		_distant_snap_player_3d = AudioStreamPlayer3D.new()
		_distant_snap_player_3d.stream = branch_snap_stream
		_distant_snap_player_3d.max_distance = 45.0
		_distant_snap_player_3d.volume_db = 1.0
		add_child(_distant_snap_player_3d)

	var angle = randf() * TAU
	var dist = randf_range(16.0, 32.0)
	var pos = Vector3(cos(angle) * dist, 1.0, sin(angle) * dist)
	if _distant_snap_player_3d.playing:
		# Pooled player busy: spawn a temporary one so the current snap isn't cut off
		var temp = AudioStreamPlayer3D.new()
		temp.stream = branch_snap_stream
		temp.max_distance = 45.0
		temp.volume_db = 1.0
		temp.position = pos
		add_child(temp)
		temp.play()
		temp.finished.connect(func(): temp.queue_free())
		return
	_distant_snap_player_3d.position = pos
	_distant_snap_player_3d.play()

# ================= AUDIO SYNTHESIS =================

func _generate_audio_streams() -> void:
	footstep_needles_stream = _synthesize_needles_footstep()
	footstep_wood_stream = _synthesize_wood_footstep()
	footstep_mud_stream = _synthesize_mud_footstep()
	footstep_stone_stream = _synthesize_stone_footstep()

	branch_snap_stream = _synthesize_branch_snap()
	cryptid_growl_stream = _synthesize_cryptid_roar()
	click_stream = _synthesize_click()
	pickup_stream = _synthesize_pickup()
	breath_stream = _synthesize_breathing()
	wood_knock_stream = _synthesize_wood_knock()

func _synthesize_needles_footstep() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.14
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 22.0)
		var white: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, white, 0.18)
		var val: float = last_val * env * 0.9
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_wood_footstep() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.16
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var phase: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 18.0)
		# Hollow 160Hz body tone + sharp click transient
		phase += (160.0 * TAU) / sample_rate
		var tone: float = sin(phase) * 0.7 + sin(phase * 2.2) * 0.3
		var transient: float = randf_range(-0.5, 0.5) * exp(-t * 80.0)
		var val: float = (tone * 0.7 + transient) * env * 0.95
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_mud_footstep() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.18
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		# Squelch suction envelope: attack, squish, slow suction pull
		var env: float = (sin(t * PI) if t < 0.3 else exp(-t * 12.0))
		var freq: float = lerp(130.0, 70.0, t)
		var squelch_noise: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, squelch_noise, 0.08)
		var val: float = (last_val * 0.6 + sin(float(i) * freq * TAU / sample_rate) * 0.4) * env * 0.9
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_stone_footstep() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.12
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 28.0)
		var white: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, white, 0.45) # Higher frequency grit
		var val: float = last_val * env * 0.95
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_breathing() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 1.4
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		# Inhale (0.0 to 0.6) and Exhale (0.7 to 1.3)
		var swell: float = sin(t * TAU * 0.8)
		var env: float = max(0.0, swell) * 0.7
		var white: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, white, 0.12)
		var val: float = last_val * env * 0.75
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_wood_knock() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.9
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	for i in range(total_samples):
		var t: float = float(i) / float(sample_rate)
		var val: float = 0.0

		# Knock 1 at t=0.0
		if t < 0.35:
			var env1: float = exp(-t * 26.0)
			val += sin(t * 230.0 * TAU) * env1 * 0.85
		# Knock 2 at t=0.38
		if t >= 0.38:
			var t2 = t - 0.38
			var env2: float = exp(-t2 * 24.0)
			val += sin(t2 * 210.0 * TAU) * env2 * 0.9

		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_branch_snap() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.28
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var snap_env: float = exp(-t * 35.0)
		var crackle_env: float = exp(-t * 12.0) * (1.0 if randf() > 0.65 else 0.0)
		var white: float = randf_range(-1.0, 1.0)
		var val: float = (white * snap_env * 0.95) + (randf_range(-0.6, 0.6) * crackle_env * 0.4)
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_cryptid_roar() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 1.6
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var lfo_phase: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = sin(t * PI)
		var freq: float = lerp(85.0, 48.0, t)
		lfo_phase += (freq * TAU) / sample_rate
		var base_tone: float = sin(lfo_phase) + 0.45 * sin(lfo_phase * 2.0) + 0.25 * sin(lfo_phase * 0.5)
		var growl_noise: float = randf_range(-0.35, 0.35) * env
		var val: float = (base_tone * 0.65 + growl_noise) * env * 0.95
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_click() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.03
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 80.0)
		var val: float = sin(float(i) * 0.8) * env * 0.9
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _synthesize_pickup() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.12
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var phase: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 16.0)
		var freq: float = lerp(480.0, 760.0, t)
		phase += (freq * TAU) / sample_rate
		var val: float = sin(phase) * env * 0.9
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	return _create_wav(data, sample_rate)

func _generate_wind_loop() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 4.0
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var mod: float = 0.65 + 0.35 * sin(t * TAU * 1.5)
		var white: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, white, 0.035)
		var val: float = last_val * mod * 0.7
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	var wav = _create_wav(data, sample_rate)
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.loop_end = total_samples
	return wav

func _create_wav(data: PackedByteArray, sample_rate: int) -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav
