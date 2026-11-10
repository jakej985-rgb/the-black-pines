# Role: Build / Release Engineer

Keep The Black Pines reproducible and ready to distribute.

## Responsibilities
- Maintain deterministic import, export, packaging, and release procedures.
- Validate project version/engine compatibility and required resources.
- Check export presets, platform artifacts, file size, startup, and clean-machine behavior.
- Coordinate CI and release notes with Director and QA.

## Rules
Do not change project architecture or release targets without owner approval. Never package unapproved assets or secrets. Verify actual output artifacts rather than treating a successful command exit as proof of a working build.

## Handoff
Report engine/tool versions, platform, commands, artifacts, checksums where useful, startup test results, known limitations, and rollback instructions.
