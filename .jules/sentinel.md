# Sentinel's Security Journal

## 2026-11-19 - Save file path traversal and arbitrary filesystem overwrite protection
**Vulnerability:** `SaveManager` accepted unvalidated string paths in file operations (`FileAccess.open` with `WRITE`/`READ`, and `DirAccess.remove_absolute`), allowing path traversal sequences (such as `user://../` or absolute OS paths) to access, overwrite, or delete arbitrary files outside the user save directory.
**Learning:** In Godot applications, relying solely on high-level APIs or convention without strictly validating that target save paths begin with `user://`, do not contain directory traversal sequences (`..` or `\`), and end in `.json` can expose user data and engine resources to arbitrary file manipulation.
**Prevention:** Always enforce strict path validation (`is_valid_save_path()`) before performing file read, write, or deletion operations, rejecting paths that escape sandboxed prefixes (`user://`) or contain directory traversal indicators.
