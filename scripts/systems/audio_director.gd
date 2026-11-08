class_name AudioDirector
extends Node

## Procedural horror audio synthesizer for The Black Pines.
## Generates footsteps, wind ambient, branch snaps, and cryptid rumbles natively.

static var instance: AudioDirector = null

var wind_player: AudioStreamPlayer = null
var footstep_player: AudioStreamPlayer = null
var sfx_player: AudioStreamPlayer = null
var ambient_timer: float = 6.0

var footstep_stream: AudioStreamWAV = null
var branch_snap_stream: AudioStreamWAV = null
var cryptid_growl_stream: AudioStreamWAV = null
var click_stream: AudioStreamWAV = null
var pickup_stream: AudioStreamWAV = null

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
	footstep_player.stream = footstep_stream
	footstep_player.volume_db = -10.0
	add_child(footstep_player)

	# 2D SFX
	sfx_player = AudioStreamPlayer.new()
	sfx_player.volume_db = -4.0
	add_child(sfx_player)

func _process(delta: float) -> void:
	ambient_timer -= delta
	if ambient_timer <= 0.0:
		ambient_timer = randf_range(8.0, 18.0)
		_play_random_distant_snap()

func play_footstep(is_sprint: bool) -> void:
	if not footstep_player:
		return
	footstep_player.pitch_scale = randf_range(0.85, 1.15) if not is_sprint else randf_range(1.1, 1.3)
	footstep_player.volume_db = -8.0 if is_sprint else -12.0
	footstep_player.play()

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

func play_cryptid_roar(pos_3d: Vector3 = Vector3.ZERO) -> void:
	var player_3d = AudioStreamPlayer3D.new()
	player_3d.stream = cryptid_growl_stream
	player_3d.position = pos_3d
	player_3d.max_distance = 60.0
	player_3d.volume_db = 6.0
	player_3d.pitch_scale = randf_range(0.85, 1.0)
	add_child(player_3d)
	player_3d.play()
	player_3d.finished.connect(func(): player_3d.queue_free())

func _play_random_distant_snap() -> void:
	var player_3d = AudioStreamPlayer3D.new()
	player_3d.stream = branch_snap_stream
	# Place snap somewhere out in the trees 15-30m away
	var angle = randf() * TAU
	var dist = randf_range(16.0, 32.0)
	player_3d.position = Vector3(cos(angle) * dist, 1.0, sin(angle) * dist)
	player_3d.max_distance = 45.0
	player_3d.volume_db = 1.0
	add_child(player_3d)
	player_3d.play()
	player_3d.finished.connect(func(): player_3d.queue_free())

# ================= AUDIO SYNTHESIS =================

func _generate_audio_streams() -> void:
	footstep_stream = _synthesize_footstep()
	branch_snap_stream = _synthesize_branch_snap()
	cryptid_growl_stream = _synthesize_cryptid_roar()
	click_stream = _synthesize_click()
	pickup_stream = _synthesize_pickup()

func _synthesize_footstep() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.14
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var last_val: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 22.0)
		# Lowpass filtered noise for damp needle/dirt crunch
		var white: float = randf_range(-1.0, 1.0)
		last_val = lerp(last_val, white, 0.18)
		var val: float = last_val * env * 0.9
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav

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

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav

func _synthesize_cryptid_roar() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 1.6
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var lfo_phase: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		# Slow attack, sustained heavy rumble, long release
		var env: float = sin(t * PI)
		var freq: float = lerp(85.0, 48.0, t) # descending guttural pitch
		lfo_phase += (freq * TAU) / sample_rate
		var base_tone: float = sin(lfo_phase) + 0.45 * sin(lfo_phase * 2.0) + 0.25 * sin(lfo_phase * 0.5)
		# Add rough guttural distortion
		var growl_noise: float = randf_range(-0.35, 0.35) * env
		var val: float = (base_tone * 0.65 + growl_noise) * env * 0.95
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav

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

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav

func _synthesize_pickup() -> AudioStreamWAV:
	var sample_rate: int = 22050
	var duration: float = 0.22
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var env: float = exp(-t * 12.0)
		var tone1: float = sin(float(i) * (520.0 * TAU / sample_rate))
		var tone2: float = sin(float(i) * (780.0 * TAU / sample_rate))
		var val: float = (tone1 * 0.5 + tone2 * 0.5) * env * 0.7
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.data = data
	return wav

func _generate_wind_loop() -> AudioStreamWAV:
	var sample_rate: int = 11025
	var duration: float = 3.5
	var total_samples: int = int(sample_rate * duration)
	var data := PackedByteArray()
	data.resize(total_samples * 2)

	var filter_acc: float = 0.0
	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var white: float = randf_range(-1.0, 1.0)
		# Deep lowpass filter to mimic howling wind
		var cut: float = 0.04 + 0.02 * sin(t * TAU * 1.5)
		filter_acc = lerp(filter_acc, white, cut)
		var val: float = filter_acc * 0.8
		var sample: int = int(clamp(val * 32767.0, -32768.0, 32767.0))
		data.encode_s16(i * 2, sample)

	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.mix_rate = sample_rate
	wav.data = data
	return wav
