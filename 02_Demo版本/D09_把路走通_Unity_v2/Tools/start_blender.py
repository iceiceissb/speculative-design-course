import bpy, sys
addon_path = r'C:\Users\22602\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons'
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)
import blender_mcp
if not hasattr(bpy.types.Scene, 'blendermcp_port'):
    blender_mcp.register()
if not getattr(bpy.types, 'blender_mcp_server', None):
    bpy.types.blender_mcp_server = blender_mcp.BlenderMCPServer(host='127.0.0.1', port=9876)
    bpy.types.blender_mcp_server.start()
print('SUNNY_PATH_BLENDER_READY', flush=True)
