# Classic Bigfoot — Visual Target Checklist

Reference: `classic_bigfoot_concept.png` (primary), plus `front_reference.png`,
`side_reference.png`, `rear_reference.png`.

Derived from `asset_spec.yaml` (`design.key_features`, scale 2.85 m,
`posture: forward_leaning_bent_knee`) and issues #6/#11/#28. **A human must
verify each item against the actual reference image** — the generating agent
cannot view images, so items marked *(verify)* need eyeball confirmation.

## Silhouette & posture
- [ ] Massive humanoid-ape silhouette; reads as heavy cryptid, not a man in a suit
- [ ] Forward-leaning, bent-knee stalking crouch (~2.85 m tall equivalent mass)
- [ ] No visible primitive intersections, floating parts, or seam gaps
- [ ] Continuous anatomy: neck flows into trapezius; no "stack of spheres" look

## Head & face
- [ ] Conical sagittal crest cranium, sloping backward *(verify)*
- [ ] Heavy supraorbital brow shelf over deep-set orbital sockets *(verify)*
- [ ] Broad flat simian nose, closed lips, prognathic ape muzzle *(verify)*
- [ ] Volumetric chin beard / jaw fringe framing dark face mask *(verify)*
- [ ] Small dark eyes; no constant artificial glow at distance *(verify)*

## Torso
- [ ] Colossal trapezius hump rising above the "neck" line, sloping into deltoids
- [ ] Broad barrel chest, flat pectorals, defined serratus/rib transition
- [ ] Latissimus dorsi tapering continuously into pelvis — no flat cutoff

## Limbs
- [ ] Long muscular arms reaching past mid-thigh; vascular forearms
- [ ] Outer forearm hair frills *(verify)*
- [ ] Bowed muscular legs; plantigrade wide feet (~18 in / ~0.45 m) *(verify)*
- [ ] 5-fingered hands in stalking grip, blunt ape fingernails *(verify)*
- [ ] Toes/feet broad and splayed, not human-slim *(verify)*

## Fur
- [ ] Dark chestnut brown; volume breaks silhouette (shoulders, back, forearms)
- [ ] Direction flows with muscle forms; no flat card strips or repetitive tiling
- [ ] Clumping at silhouette edges; shorter on face/hands *(verify)*

## Distinctive reference traits (fill in after human looks at concept)
- [ ] *(pending human identification of 2-3 signature traits)*

## Stage-gate usage
- Blockout review: check silhouette/posture/overall mass items only.
- Sculpt review: full checklist incl. face, hands, feet, fur direction.
- Each review records verdict pass/revise/reject + evidence path in
  `pipeline_state.yaml` via `scripts/tools/asset_stage_gate.py`.
