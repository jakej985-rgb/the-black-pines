# Bolt's Performance Journal

## 2026-11-10 - Throttle continuous state signals driving UI updates
**Learning:** In continuous physics update loops (`_physics_process`), emitting signals on every single frame for slowly changing float values (such as flashlight battery drain at 0.8%/sec) forces connected UI observers (like HUD labels and panels) to reformat strings, allocate memory, and recalculate text layouts at 60 FPS (3,600 times/minute). Because the UI only displays integer percentages, emitting only when `int(current) != int(previous)` or when edge states (like depletion or reload) occur reduces signal dispatch and string layout overhead by ~98.6% without any visual loss in accuracy.
**Action:** When connecting continuous simulation properties to UI elements, throttle signal emissions to discrete perceptually relevant boundaries (e.g., integer percent changes or threshold crossings) rather than dispatching every physics tick.
