from BlenderKritaLink.connection import KritaConnection
import bpy 

class _PT_BlenderKritaLinkPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_KRITA"
    bl_label = "Krita Link"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Blender Krita Link"
    INSTANCE = None
        
    def draw(self, context):
        self.layout.label(text="Connection: "  + KritaConnection.STATUS)
        self.layout.prop(bpy.context.scene.global_store, "connection_port")
        self.layout.operator("object.disconnect_operator")
        self.layout.prop(bpy.context.scene.global_store, "sync_toggle")
        self.layout.prop(bpy.context.scene.global_store, "sync_interval")

