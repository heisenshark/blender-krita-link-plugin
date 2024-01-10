import bpy 

def update_gui():
    print("siema")
    if hasattr(bpy.context,'screen') and hasattr(bpy.context.screen,'areas') and bpy.context.screen.areas:
        for area in bpy.context.screen.areas:area.tag_redraw()
    print("elo")


class _PT_BlenderKritaLinkPanel(bpy.types.Panel):
    """Blender Krita Link Panel"""
    bl_label = "Krita Link"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Blender Krita Link'
    
        
    def __init__(self) -> None:
        super().__init__()
        print("panel instantiated")
        def prop_update(self,context):
            update_gui()
        bpy.types.Scene.test_prop = bpy.props.StringProperty(name="test_prop",default="listening",update=prop_update) 
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        # row.prop(scene, "connection_status", text="Connection Status")
        layout.label(text="Connection: " + scene.test_prop)
        # row.prop(property="connection", data=bpy.types.Scene.connection_status)
        # bpy.data.screens['Layout'].areas[3].regions[3].tag_redraw()
