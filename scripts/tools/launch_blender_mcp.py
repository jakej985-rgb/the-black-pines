import bpy
import time

try:
    bpy.ops.preferences.addon_enable(module="mcp_connector_v2")
except Exception as e:
    pass

try:
    bpy.ops.mcp.start_server()
    print(">>> BLENDER MCP SERVER RUNNING ON PORT 9876 <<<", flush=True)
except Exception as e:
    print(f"Start server error: {e}", flush=True)

while True:
    time.sleep(1)
