# Cryptid Visual Roster & Creature Design Standards
**The Black Pines (Pacific Northwest Cryptid Survival Horror)**  
*Document Version: 1.0 — Phase 2 Quality Standard*

---

## 1. Design Philosophy & Grounded Horror Principles
*The Black Pines* rejects generic monster tropes, cartoonish proportions, and supernatural bullet sponges. All cryptids inhabiting the Black Pine Wilderness are designed as relict apex organisms whose folklore origins reflect plausible biological adaptations to the dense, wet, temperate rainforests of the Pacific Northwest.

### Core Creature Tenets:
1. **Grounded Biological Realism**: Cryptids have weight, anatomical skeletal structures, muscle mass, breathing rhythms, and realistic center-of-gravity shifts during movement.
2. **Distinctive Silhouettes at Distance**: In heavy volumetric fog and dim moonlight, creatures must be instantly distinguishable by silhouette, posture, limb proportions, and gait alone.
3. **No Reskins or Mesh Clones**: Future creatures **strictly forbidden** from reusing the Sasquatch mesh or rig with palette swaps. Every creature requires distinct base geometry, armature, material shaders, and animation sets.
4. **Forensic Evidence Consistency**: Every creature must leave unique physical signatures in the game world—specific footprint anatomy, tree rub/gouge patterns, vocalization frequencies, and carcass mutilation styles.

---

## 2. Creature Implementation Status Matrix

| Creature Designation | Folklore / Archetype | Implementation Status | Scale / Mass | Locomotion | Primary Threat Profile |
|---|---|---|---|---|---|
| **Sasquatch** (*Gigantopithecus pacifica*) | Pacific Northwest Forest Giant | **Implemented & Verified** | 2.95m tall / ~380kg | Upright heavy bipedal walk, bent-knee stalk, lunging sprint | Territorial ambush, tree knocks, infrasound roar, bone marrow feeding |
| **Pine Ridge Ghoul** (*Cascadian Wendigo*) | Emaciated Winter Strigoi | **Planned (Phase 3)** | 2.45m tall / ~85kg | Spidery loping quadruped/biped hybrid, vertical tree climbing | Silent canopy stalking, auditory voice mimicry, blinding sprint flank |
| **The Black Ridge Howler** (*Ozark-Cascades Chimera*) | Quadrupedal Horned Predator | **Conceptual (Future DLC)** | 1.4m at shoulder / ~160kg | Low quadrupedal prowl, leaping pounce | Underbrush stalking, low vibrational thrum, pack herding behavior |

---

## 3. Primary Creature: The Sasquatch (*The Black Pine Stalker*)

### 3.1 Anatomical Specifications & Silhouette
- **Height**: 2.95 meters (9 ft 8 in).
- **Shoulder Breadth**: 1.35 meters; barrel-chested torso with minimal neck transition directly into the trapezius.
- **Silhouette Signature**: Patterson-Gimlin inspired heavy trapezoidal torso, sagittal crest giving the skull a conical dome, long heavy arms extending past mid-thigh, forward-hunched cervical spine, and wide broad-soled flat feet.
- **Head & Facial Structure**: Heavy brow ridge, deeply recessed orbital sockets with amber tapetum lucidum eye reflection, snarling black leathery lips exposing yellowed bone-hued fangs (`mat_weathered_bone.tres`).

### 3.2 Material & Shader Pipeline
- **Material**: `assets/materials/mat_beast_fur.tres` backed by `sasquatch_fur.gdshader`.
- **Albedo / Shading**: Deep matte forest-floor umber (`#1c1712` albedo) with multi-octave pseudo-random procedural hair strand noise.
- **Roughness & Specular**: High organic roughness (0.84 to 0.94), 0.0 metallic, and **zero clearcoat** to prevent plastic shine under spotlight illumination.
- **Subsurface / Rim Scatter**: Soft backward rim scattering simulating dense, wet undercoat and outer guard hairs.
- **Eye Glow**: Dual `OmniLight3D` sockets (`Visuals/Torso/Head/EyeLeft` and `EyeRight`) set to amber emission (`Color(1.0, 0.82, 0.25)`), projecting an intense retroreflective glare when caught in player flashlight beams.

### 3.3 Locomotion & Animation States
- **Idle**: Heavy diaphragm chest breathing (scale expansion `1.0` -> `1.04`), subtle neck micro-twitches scanning the treeline.
- **Stalking**: Low-profile bent-knee creeping gait, arms swaying in wide contralateral arches, keeping trees between itself and the player.
- **Alerted / Intimidation**: Upright posturing, violent double hand raise, ground thumping, and deep guttural roar.
- **Charge**: Devastating forward sprint with upper torso leaning forward 35°, snapping underbrush, and flashing glowing eyes.
- **Retreat**: Cautious backward retreat into deep fog, maintaining unbroken eye contact with the player while fading into the volumetric mist.

### 3.4 Forensic Clue Profile (Mission 01 Integration)
- **Footprints**: 48 cm long, five-toed plaster cast imprint found at the trailhead (`prop_plaster_footprint.obj`).
- **Tree Markings**: Cedar tree gouged 2.7m above ground level, shredded inner bark with amber sap oozing from deep puncture channels (`clue_clawed_tree.tscn`).
- **Carcass Damage**: Fully fractured adult bull elk ribcage with missing marrow bones and torn muscle tissue (`clue_carcass.tscn`).
- **Hair Samples**: Coarse, hollow-core dark brown fur tufts collected in evidence jar (`prop_evidence_jar.obj`).

---

## 4. Planned Secondary Creature: The Pine Ridge Ghoul (*Cascadian Wendigo*)

### 4.1 Anatomical Specifications & Silhouette
- **Height**: 2.45 meters; severely emaciated skeletal frame with paper-thin parchment skin stretched taut over a protruding ribcage and spine.
- **Limb Proportions**: Hyper-elongated forearms and fingers (hands measure 42 cm with sharp black keratin claws). Legs have pronounced double-jointed digitigrade appearance.
- **Head & Face**: Narrow, elongated skull with sunken eyes, vestigial nose cavity, razor-sharp needle dentition, and cracked deer-antler protrusions emerging from the parietal plates.
- **Locomotion**: Creepy, insectoid agility; capable of scaling vertical Douglas fir trunks in complete silence and dropping directly behind the investigator.

### 4.2 Material & Visual Language
- **Base Shader**: Translucent parchment skin shader with subsurface scattering showing dark coagulated venous networks beneath the dermis.
- **Roughness**: Uneven wet-damp patches (roughness 0.45 on raw flesh lesions; 0.85 on dry stretched skin).
- **Color Palette**: Ashen pale gray (`#6b6d68`) transitioning to frostbitten black at fingertips, toes, and lips.
- **Eye Reflection**: Piercing pale icy blue (`#70c4ff`) pinpoint tapetum reflection that dims when observed directly, simulating optical camouflage.

### 4.3 Behavioral Cues & Audio Ecology
- **Auditory Mimicry**: Emits faint, garbled fragments of human distress calls recorded from previous missing park wardens ("Help me", "Over here").
- **Hunting Pattern**: Does not charge head-on like the Sasquatch. It stalks along the upper branches (8–14m elevation), dislodging needles and pinecones to draw the player's flashlight upward before striking from a flank.

---

## 5. Anti-Reskin Enforcement & Technical Standards

To preserve artistic integrity and critical praise:

1. **Unique Mesh Topologies**:
   - Every cryptid must be authored with an original base mesh.
   - Using `sasquatch_torso.obj` or any variant as a base for another creature will automatically fail asset review.
2. **Dedicated Skeletal Rigs & Animation Sets**:
   - Each creature must feature distinct bone hierarchies reflecting its unique locomotion (e.g. bipedal plantar ape vs. digitigrade climbing ghoul).
3. **Rigorous Four-Condition Visual QA Gate**:
   Before any cryptid model is merged into production, it must be rendered and captured under four standard lighting profiles:
   - **Condition A (Forest Moonlight)**: High contrast, silhouette readability against distant fog.
   - **Condition B (Flashlight Direct Beam)**: PBR micro-roughness, specular breakup, tapetum lucidum eye reflection.
   - **Condition C (Volumetric Fog / Occlusion)**: Dread, depth cueing, soft volumetric shadows cast through tree trunks.
   - **Condition D (Inspection / Neutral Light)**: Detail inspection of anatomical joints, musculature, fur cards, and facial features.

---

## 6. Asset Provenance & Licensing Standards

1. **Original Content Guarantee**: All meshes, textures, materials, and scripts in *The Black Pines* repository are custom-authored specifically for this project or derived from public domain / permissively licensed assets.
2. **Shader Architecture**: All GLSL/GDShader code is written in-house without proprietary external shader libraries.
3. **Audio Attribution**: Any future creature vocalizations, Foley audio, or ambient effects must maintain strict attribution logs under `assets/audio/ATTRIBUTION.md`.

---
*Maintained by the Black Pines Core Graphics & Creature Engineering Team.*
