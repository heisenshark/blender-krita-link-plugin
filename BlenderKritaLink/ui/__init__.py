from BlenderKritaLink.connection import KritaConnection
import bpy 

class _PT_BlenderKritaLinkPanel(bpy.types.Panel):
    """Blender Krita Link Panel"""
    bl_label = "Krita Link"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Blender Krita Link"
    INSTANCE = None
    
    def __init__(self) -> None:
        super().__init__()
        print("panel instantiated")
        if _PT_BlenderKritaLinkPanel.INSTANCE is None:
            _PT_BlenderKritaLinkPanel.INSTANCE = self
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Connection: " + KritaConnection.STATUS)
        layout.prop(bpy.context.scene.global_store, "connection_port")
        layout.operator("object.disconnect_operator")
        layout.prop(bpy.context.scene.global_store, "sync_toggle")
        layout.prop(bpy.context.scene.global_store, "sync_interval")
