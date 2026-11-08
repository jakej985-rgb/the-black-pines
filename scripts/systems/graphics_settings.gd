class_name GraphicsSettingsManager
extends Node

## Graphics Scalability & Quality Preset Manager for The Black Pines.
## Controls render scaling, volumetric fog, shadows, SSAO, SSIL, and anti-aliasing.

enum Preset {
	LOW = 0,
	MEDIUM = 1,
	HIGH = 2,
	ULTRA = 3,
	CUSTOM = 4
}

const PRESET_NAMES = {
	Preset.LOW: "Low",
	Preset.MEDIUM: "Medium",
	Preset.HIGH: "High",
	Preset.ULTRA: "Ultra",
	Preset.CUSTOM: "Custom"
}

const CONFIG_PATH = "user://graphics_settings.cfg"

signal preset_applied(preset: Preset, preset_name: String)
signal setting_changed(setting_name: String, value: Variant)

static var instance: GraphicsSettingsManager = null

var current_preset: Preset = Preset.HIGH

# Active configuration state
var render_scale: float = 1.0
var scaling_3d_mode: Viewport.Scaling3DMode = Viewport.SCALING_3D_MODE_BILINEAR
var msaa_3d: Viewport.MSAA = Viewport.MSAA_2X
var screen_space_aa: Viewport.ScreenSpaceAA = Viewport.SCREEN_SPACE_AA_FXAA

var shadow_atlas_size: int = 4096
var shadow_filter_quality: RenderingServer.ShadowQuality = RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM
var directional_shadow_distance: float = 75.0

var volumetric_fog_enabled: bool = true
var volumetric_fog_density: float = 0.016
var volumetric_fog_length: float = 72.0

var ssao_enabled: bool = true
var ssao_radius: float = 2.0
var ssao_intensity: float = 2.2

var ssil_enabled: bool = true
var ssil_radius: float = 3.5
var ssil_intensity: float = 0.5

var glow_enabled: bool = true

func _init() -> void:
	if instance == null:
		instance = self

func _ready() -> void:
	load_settings()
	apply_preset(current_preset, false)
	# Automatically discover and apply to active world environment
	call_deferred("apply_all")

## Apply a named or enumerated quality preset.
func apply_preset(preset: Preset, save_to_disk: bool = true) -> void:
	current_preset = preset
	match preset:
		Preset.LOW:
			render_scale = 0.65
			scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
			msaa_3d = Viewport.MSAA_DISABLED
			screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
			shadow_atlas_size = 1024
			shadow_filter_quality = RenderingServer.SHADOW_QUALITY_HARD
			directional_shadow_distance = 40.0
			volumetric_fog_enabled = false
			volumetric_fog_density = 0.008
			volumetric_fog_length = 40.0
			ssao_enabled = false
			ssil_enabled = false
			glow_enabled = true
		Preset.MEDIUM:
			render_scale = 0.80
			scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR
			msaa_3d = Viewport.MSAA_DISABLED
			screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
			shadow_atlas_size = 2048
			shadow_filter_quality = RenderingServer.SHADOW_QUALITY_SOFT_LOW
			directional_shadow_distance = 55.0
			volumetric_fog_enabled = true
			volumetric_fog_density = 0.014
			volumetric_fog_length = 55.0
			ssao_enabled = true
			ssao_radius = 1.8
			ssao_intensity = 1.8
			ssil_enabled = false
			glow_enabled = true
		Preset.HIGH:
			render_scale = 1.00
			scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
			msaa_3d = Viewport.MSAA_2X
			screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
			shadow_atlas_size = 4096
			shadow_filter_quality = RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM
			directional_shadow_distance = 75.0
			volumetric_fog_enabled = true
			volumetric_fog_density = 0.016
			volumetric_fog_length = 72.0
			ssao_enabled = true
			ssao_radius = 2.0
			ssao_intensity = 2.2
			ssil_enabled = true
			ssil_radius = 3.5
			ssil_intensity = 0.5
			glow_enabled = true
		Preset.ULTRA:
			render_scale = 1.00
			scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
			msaa_3d = Viewport.MSAA_4X
			screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
			shadow_atlas_size = 8192
			shadow_filter_quality = RenderingServer.SHADOW_QUALITY_SOFT_ULTRA
			directional_shadow_distance = 85.0
			volumetric_fog_enabled = true
			volumetric_fog_density = 0.018
			volumetric_fog_length = 80.0
			ssao_enabled = true
			ssao_radius = 2.2
			ssao_intensity = 2.4
			ssil_enabled = true
			ssil_radius = 4.0
			ssil_intensity = 0.6
			glow_enabled = true
		Preset.CUSTOM:
			pass

	_apply_rendering_server_settings()
	_apply_viewport_settings()
	apply_all()

	preset_applied.emit(current_preset, get_preset_name())
	if save_to_disk:
		save_settings()

func apply_preset_by_name(p_name: String, save_to_disk: bool = true) -> bool:
	var clean_name = p_name.strip_edges().to_lower()
	for p_enum in PRESET_NAMES:
		if PRESET_NAMES[p_enum].to_lower() == clean_name:
			apply_preset(p_enum, save_to_disk)
			return true
	return false

func get_preset_name() -> String:
	return PRESET_NAMES.get(current_preset, "Custom")

## Apply low-level RenderingServer quality properties.
func _apply_rendering_server_settings() -> void:
	RenderingServer.directional_shadow_atlas_set_size(shadow_atlas_size, true)
	RenderingServer.directional_soft_shadow_filter_set_quality(shadow_filter_quality)
	RenderingServer.positional_soft_shadow_filter_set_quality(shadow_filter_quality)

## Apply viewport resolution scaling and anti-aliasing.
func _apply_viewport_settings() -> void:
	if not is_inside_tree():
		return
	var vp = get_viewport()
	if vp:
		vp.scaling_3d_scale = render_scale
		vp.scaling_3d_mode = scaling_3d_mode
		vp.msaa_3d = msaa_3d
		vp.screen_space_aa = screen_space_aa

## Apply active settings to a WorldEnvironment's Environment resource.
func apply_to_environment(env: Environment) -> void:
	if not env:
		return
	env.volumetric_fog_enabled = volumetric_fog_enabled
	env.volumetric_fog_density = volumetric_fog_density
	env.volumetric_fog_length = volumetric_fog_length
	env.ssao_enabled = ssao_enabled
	if ssao_enabled:
		env.ssao_radius = ssao_radius
		env.ssao_intensity = ssao_intensity
	env.ssil_enabled = ssil_enabled
	if ssil_enabled:
		env.ssil_radius = ssil_radius
		env.ssil_intensity = ssil_intensity
	env.glow_enabled = glow_enabled

## Apply active settings to a DirectionalLight3D node.
func apply_to_directional_light(light: DirectionalLight3D) -> void:
	if not light:
		return
	light.directional_shadow_max_distance = directional_shadow_distance

## Walk scene tree and apply settings to all WorldEnvironments and DirectionalLight3Ds.
func apply_all(root_node: Node = null) -> void:
	_apply_rendering_server_settings()
	_apply_viewport_settings()
	
	if root_node == null:
		if not is_inside_tree():
			return
		var tree = get_tree()
		if tree and tree.root:
			root_node = tree.root
		else:
			return

	var env_nodes = _find_nodes_of_type(root_node, "WorldEnvironment")
	for we in env_nodes:
		if we is WorldEnvironment and we.environment:
			apply_to_environment(we.environment)

	var light_nodes = _find_nodes_of_type(root_node, "DirectionalLight3D")
	for light in light_nodes:
		if light is DirectionalLight3D:
			apply_to_directional_light(light)

func _find_nodes_of_type(parent: Node, type_name: String) -> Array:
	var results: Array = []
	if parent.is_class(type_name):
		results.append(parent)
	for child in parent.get_children():
		results.append_array(_find_nodes_of_type(child, type_name))
	return results

# Individual setting setters (switch to CUSTOM preset)
func set_render_scale(scale: float) -> void:
	render_scale = clamp(scale, 0.5, 2.0)
	current_preset = Preset.CUSTOM
	_apply_viewport_settings()
	setting_changed.emit("render_scale", render_scale)

func set_volumetric_fog_enabled(enabled: bool) -> void:
	volumetric_fog_enabled = enabled
	current_preset = Preset.CUSTOM
	apply_all()
	setting_changed.emit("volumetric_fog_enabled", volumetric_fog_enabled)

func set_shadow_quality(quality: RenderingServer.ShadowQuality, atlas_size: int = 4096) -> void:
	shadow_filter_quality = quality
	shadow_atlas_size = atlas_size
	current_preset = Preset.CUSTOM
	_apply_rendering_server_settings()
	setting_changed.emit("shadow_quality", quality)

func set_ssao_enabled(enabled: bool) -> void:
	ssao_enabled = enabled
	current_preset = Preset.CUSTOM
	apply_all()
	setting_changed.emit("ssao_enabled", ssao_enabled)

func set_ssil_enabled(enabled: bool) -> void:
	ssil_enabled = enabled
	current_preset = Preset.CUSTOM
	apply_all()
	setting_changed.emit("ssil_enabled", ssil_enabled)

## Persist graphics configuration to user config file.
func save_settings() -> void:
	var config = ConfigFile.new()
	config.set_value("graphics", "preset", int(current_preset))
	config.set_value("graphics", "render_scale", render_scale)
	config.set_value("graphics", "scaling_3d_mode", int(scaling_3d_mode))
	config.set_value("graphics", "msaa_3d", int(msaa_3d))
	config.set_value("graphics", "screen_space_aa", int(screen_space_aa))
	config.set_value("graphics", "shadow_atlas_size", shadow_atlas_size)
	config.set_value("graphics", "shadow_filter_quality", int(shadow_filter_quality))
	config.set_value("graphics", "directional_shadow_distance", directional_shadow_distance)
	config.set_value("graphics", "volumetric_fog_enabled", volumetric_fog_enabled)
	config.set_value("graphics", "volumetric_fog_density", volumetric_fog_density)
	config.set_value("graphics", "volumetric_fog_length", volumetric_fog_length)
	config.set_value("graphics", "ssao_enabled", ssao_enabled)
	config.set_value("graphics", "ssao_radius", ssao_radius)
	config.set_value("graphics", "ssao_intensity", ssao_intensity)
	config.set_value("graphics", "ssil_enabled", ssil_enabled)
	config.set_value("graphics", "ssil_radius", ssil_radius)
	config.set_value("graphics", "ssil_intensity", ssil_intensity)
	config.set_value("graphics", "glow_enabled", glow_enabled)
	config.save(CONFIG_PATH)

## Load graphics configuration from user config file.
func load_settings() -> void:
	var config = ConfigFile.new()
	var err = config.load(CONFIG_PATH)
	if err != OK:
		# Use default HIGH preset on first launch
		current_preset = Preset.HIGH
		return
	
	current_preset = config.get_value("graphics", "preset", Preset.HIGH) as Preset
	render_scale = config.get_value("graphics", "render_scale", 1.0)
	scaling_3d_mode = config.get_value("graphics", "scaling_3d_mode", Viewport.SCALING_3D_MODE_BILINEAR) as Viewport.Scaling3DMode
	msaa_3d = config.get_value("graphics", "msaa_3d", Viewport.MSAA_2X) as Viewport.MSAA
	screen_space_aa = config.get_value("graphics", "screen_space_aa", Viewport.SCREEN_SPACE_AA_FXAA) as Viewport.ScreenSpaceAA
	shadow_atlas_size = config.get_value("graphics", "shadow_atlas_size", 4096)
	shadow_filter_quality = config.get_value("graphics", "shadow_filter_quality", RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM) as RenderingServer.ShadowQuality
	directional_shadow_distance = config.get_value("graphics", "directional_shadow_distance", 60.0)
	volumetric_fog_enabled = config.get_value("graphics", "volumetric_fog_enabled", true)
	volumetric_fog_density = config.get_value("graphics", "volumetric_fog_density", 0.012)
	volumetric_fog_length = config.get_value("graphics", "volumetric_fog_length", 60.0)
	ssao_enabled = config.get_value("graphics", "ssao_enabled", true)
	ssao_radius = config.get_value("graphics", "ssao_radius", 2.2)
	ssao_intensity = config.get_value("graphics", "ssao_intensity", 2.6)
	ssil_enabled = config.get_value("graphics", "ssil_enabled", true)
	ssil_radius = config.get_value("graphics", "ssil_radius", 4.0)
	ssil_intensity = config.get_value("graphics", "ssil_intensity", 0.8)
	glow_enabled = config.get_value("graphics", "glow_enabled", true)
