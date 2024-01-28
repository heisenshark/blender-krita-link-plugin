from BlenderKritaLink.connection import KritaConnection
import bpy 

def prop_update(self,context):
    print("siema")
    if hasattr(bpy.context,'screen') and hasattr(bpy.context.screen,'areas') and bpy.context.screen.areas:
        for area in bpy.context.screen.areas:
            area.tag_redraw()
    print("elo")

class _PT_BlenderKritaLinkPanel(bpy.types.Panel):
    """Blender Krita Link Panel"""
    bl_label = "Krita Link"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Blender Krita Link'
    INSTANCE = None
    my_string:bpy.props.StringProperty(name="test_prop",default="listening",update=prop_update)
    
    def __init__(self) -> None:
        super().__init__()
        print("panel instantiated")
        if _PT_BlenderKritaLinkPanel.INSTANCE is None:
            _PT_BlenderKritaLinkPanel.INSTANCE = self
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Connection: " + KritaConnection.STATUS)
        print("redrawing panel...")
