import bpy
from .ui import _PT_BlenderKritaLinkPanel
from .image_manager import ImageManager
from .connection import KritaConnection

bl_info = {
    "name": "Blender Krita link",
    "author": "Heisenshark",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "category": "Paint",
    "description":"companion to blender krita link plugin, shows connection status and updates images"
}


def ui_update(self, context):
    if context is None or context.area is None or context.area.regions is None:
        return
    for region in context.area.regions:
        if region.type == "UI":
            region.tag_redraw()
    return None


def update_panel_loop():
    try:
        bpy.context.scene.global_store.label = KritaConnection.STATUS
    except Exception as e:
        print(e)
    return 0.5


class GlobalStore(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(
        name="ConnectionStatus",
        description="Connection status",
        default="listening",
        update=ui_update,
    )


def register():
    bpy.utils.register_class(_PT_BlenderKritaLinkPanel)
    bpy.utils.register_class(GlobalStore)
    connection_instance = KritaConnection()
    connection_instance.start()
    ImageManager()
    bpy.types.Scene.global_store = bpy.props.PointerProperty(type=GlobalStore)
    bpy.app.timers.register(update_panel_loop, persistent=True)


def unregister():
    KritaConnection.LINK_INSTANCE.dell()
    bpy.utils.unregister_class(GlobalStore)
    bpy.utils.unregister_class(_PT_BlenderKritaLinkPanel)
    bpy.app.timers.unregister(update_panel_loop)
    del bpy.types.Scene.global_store


if __name__ == "__main__":
    register()
