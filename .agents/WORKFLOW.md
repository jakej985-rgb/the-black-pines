# Team Workflow

## Default feature sequence

```text
Owner intent
  -> Director: scope, priority, dependencies, acceptance criteria
  -> Game Design + Narrative (when player/lore intent changes)
  -> World/Level Design (when space or pacing changes)
  -> Art Director -> 3D Artist -> Technical Artist (for asset work)
  -> Gameplay Engineer / AI Engineer / Audio / UI-UX (by system)
  -> QA (technical and behavioral verification)
  -> Art Director (visual approval where applicable)
  -> Bolt (performance review for performance-sensitive changes)
  -> Release Engineer (when packaging/release is involved)
  -> Director integration and owner review
```

Roles may be combined for a small task, but approval boundaries remain separate. A single model can perform more than one role sequentially; label each perspective and do not claim independent review when it is not independent.

## GitHub issue conventions

Use labels where they exist: `role:design`, `role:art`, `role:engineering`, `role:qa`, `role:performance`, `role:release`, plus `priority:P0` through `priority:P3`. Do not create labels automatically if repository label policy is unknown; include the role/priority in the title and body.

Issue template:
- Objective / player value
- Current behavior or evidence
- Scope
- Out of scope
- Tasks
- Dependencies
- Acceptance criteria
- Validation / evidence
- Risks and rollback

## Pull request standard

- One coherent task per PR.
- Link issue(s); describe player impact.
- List files/assets changed.
- Include commands and exact results.
- Include before/after screenshots for visual work.
- Include performance measurements for costly systems/assets.
- Call out tests not run and why.
- Do not merge automatically; owner approval is required.

## Asset approval gates

`reference_locked -> blockout_review -> sculpt_review -> retopo_uv_bake -> materials_fur -> rig_animation -> godot_validation -> approved`

A rejection returns to the relevant earlier stage. Export success or automated structural checks cannot bypass visual approval. Preserve current production assets until the replacement has passed engine validation.
