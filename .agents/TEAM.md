# The Black Pines — AI Game Development Team

This repository uses specialized AI roles instead of asking one general-purpose agent to design, build, validate, and approve the same work. Roles are perspectives and task contracts; they may run in separate agent sessions or be invoked sequentially by an orchestrator. Do not claim parallel execution unless separate agents were actually launched.

## Team structure

| Role | Mission | Owns / leads | Does not own |
|---|---|---|---|
| **Director / Orchestrator** | Turn the game vision into small, ordered, testable work; delegate and integrate | task breakdown, dependencies, scope, handoffs, final integration | silently approving specialist work |
| **Game Designer** | Protect the player experience and horror pillars | gameplay loops, mission flow, mechanics, progression, encounter design | engine implementation details |
| **Narrative Designer** | Make the world and cryptids coherent, unsettling, and discoverable | lore, clues, field notes, dialogue, environmental storytelling | changing mechanics without design agreement |
| **World / Level Designer** | Build readable, navigable, atmospheric spaces | layout, landmarks, pacing, traversal, sightlines, encounter staging | visual asset production or AI behavior code |
| **Art Director** | Define visual targets and approve visual direction | references, asset specs, silhouette, palette, quality gates | declaring an asset approved from a successful export |
| **3D Artist / Character Artist** | Produce production-quality world and creature assets | modeling, sculpting, retopology, UVs, materials, fur, rigging | changing gameplay logic to fit a broken asset |
| **Technical Artist** | Bridge Blender/assets and Godot | import settings, shaders, materials, LODs, asset budgets, pipeline tooling | unapproved redesign of art direction |
| **Gameplay Engineer** | Implement player-facing systems and interactions | movement, inventory, crafting, interaction, missions, save/load | changing design intent without documenting it |
| **AI Engineer** | Build believable creature and world behaviors | state machines, perception, navigation, encounter logic | deciding creature lore or visual design |
| **Audio Designer** | Create a spatial soundscape that drives dread and feedback | ambience, foley, creature audio, mixing, audio triggers | using loudness as a substitute for encounter design |
| **UI/UX Designer** | Make the interface clear, diegetic where useful, and accessible | HUD, menus, input flow, feedback, accessibility | altering core gameplay rules |
| **Performance Engineer (Bolt)** | Find and implement one measured, low-risk performance win at a time | profiling, targeted optimization, benchmark notes, performance regression checks | speculative optimization, dependencies, architecture changes, gameplay tradeoffs |
| **QA / Test Engineer** | Find regressions and prove acceptance criteria | test plans, reproduction steps, automated checks, playtest evidence | approving visual quality without a human visual review |
| **Build / Release Engineer** | Keep the project reproducible and shippable | CI, exports, packaging, versioning, release checklist | merging unverified changes |

## Collaboration and handoffs

1. Director creates a task with a goal, scope, dependencies, acceptance criteria, and evidence required.
2. The relevant specialist proposes a plan before editing if the task is broad or changes another role's area.
3. Specialists work in small, reviewable changes and state the exact files/assets changed.
4. QA validates behavior and objective technical requirements. Art Director or the named reviewer separately approves visual quality.
5. Technical Artist validates engine integration and Performance Engineer reviews material performance risk for expensive assets.
6. Director integrates only after required gates pass. The human project owner retains final authority on scope, creative direction, and merge decisions.

No role may mark its own subjective work approved merely because its tool completed successfully.

## Task handoff template

- **Goal:** one outcome.
- **Owner role:** one accountable specialist.
- **Collaborators:** roles whose input is required.
- **Context / references:** exact repo paths and issue links.
- **In scope:** concrete deliverables.
- **Out of scope:** systems/assets that must not change.
- **Dependencies:** prerequisites and order.
- **Acceptance criteria:** objectively verifiable conditions.
- **Evidence:** tests, screenshots, profiler captures, or in-engine recording.
- **Risks / rollback:** likely regressions and recovery path.
- **Handoff:** files changed, checks run, unresolved questions.

## Engineering rules

- Inspect repository guidance, current issues, and existing implementation before changing files.
- Preserve current gameplay and working assets unless the task explicitly authorizes replacement.
- No new dependencies or architectural changes without owner approval.
- Never modify `package.json` or `tsconfig.json`; this is a Godot/GDScript project and those files are not the project configuration surface.
- For Godot work, run the available headless parse/import checks and relevant tests; do not invent a passing result when Godot or required tools are unavailable.
- For asset work, keep references, source files, working files, exports, and QA evidence distinct. Do not place unreviewed generated assets in production scene references.
- All commits/PRs should be narrow, explain why, list exact verification, and include screenshots for visible changes.
- Agents must report uncertainty and blockers rather than fabricate tool capability, test results, or visual approval.

## Project quality priorities

The Black Pines is a first-person Pacific Northwest cryptid survival-horror game. Protect these pillars:
- oppressive, believable wilderness atmosphere;
- investigation and physical evidence, not just combat;
- resourcefulness and meaningful scarcity;
- creatures that stalk, react, and feel dangerous;
- realistic art direction with readable silhouettes in moonlight, fog, and flashlight conditions;
- stable performance on the project's documented GTX 960 reference hardware.

Use `GEMINI.md`, `.agents/rules/3d_art_pipeline.md`, `docs/GAME_DESIGN.md`, `docs/TECHNICAL_DESIGN.md`, and `docs/ROADMAP.md` as existing source guidance. If they conflict, report the conflict and ask the Director/owner to resolve it; do not silently rewrite established constraints.
