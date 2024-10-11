import bpy

from BlenderKritaLink.watch import UvWatch,ImagesStateWatch
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


def label_update(self, context):
    if context is None or context.area is None or context.area.regions is None:
        return
    for region in context.area.regions:
        if region.type == "UI":
            region.tag_redraw()
    return None

def port_update(self, context):
    print("updating port")
    new_port = int(context.scene.global_store.connection_port)
    if new_port == KritaConnection.PORT:
        return 
    if KritaConnection.CONNECTION is not None:
        KritaConnection.PORT = new_port
        KritaConnection.CONNECTION.close()
    elif KritaConnection.LINK_INSTANCE.listener is not None:
        KritaConnection.LINK_INSTANCE.timeout_listener()
        KritaConnection.PORT = new_port
    return 

def update_panel_watch():
    try:
        bpy.context.scene.global_store.label = KritaConnection.STATUS
    except Exception as e:
        print(e,"\n",traceback.print_exc())
        print(e)
    return 0.5


class GlobalStore(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(
        name="ConnectionStatus",
        description="Connection status",
        default="listening",
        update=label_update,
    )
    connection_port: bpy.props.IntProperty(
        name="connection port",
        description="port to connect to krita",
        default=65431,
        update=port_update,
    )
    sync_toggle: bpy.props.BoolProperty(
        name="sync uvs and images",
        description="toggle to sync uv preview and images at a interval",
        default=True,
    )
    sync_interval: bpy.props.FloatProperty(
        name="sync interval",
        description="sync interval in seconds",
        default=0.5,
        min=0.2,
        max=10
    )

class DisconnectOperator(bpy.types.Operator): 
    bl_idname = "object.disconnect_operator"
    bl_label = "Disconnect"

    @classmethod
    def pool(cls,context):
        return KritaConnection.CONNECTION is not None

    def execute(self, context):
        if KritaConnection.CONNECTION is not None:
            KritaConnection.CONNECTION.close()
        return {"FINISHED"}

def init_connection():
    print("init connection",bpy.context.scene.global_store.connection_port)
    KritaConnection.PORT = bpy.context.scene.global_store.connection_port
    connection_instance = KritaConnection()
    connection_instance.start()

def register():
    bpy.utils.register_class(_PT_BlenderKritaLinkPanel)
    bpy.utils.register_class(GlobalStore)
    bpy.types.Scene.global_store = bpy.props.PointerProperty(type=GlobalStore)
    ImageManager()
    bpy.utils.register_class(DisconnectOperator)
    bpy.app.timers.register(update_panel_watch, persistent=True)
    bpy.app.timers.register(init_connection,first_interval=0.2,persistent=True)

    UvWatch()
    ImagesStateWatch()
    bpy.app.timers.register(UvWatch.instance.check_for_changes, first_interval=0.5, persistent=True)
    bpy.app.timers.register(ImagesStateWatch.instance.check_for_changes, first_interval=0.5, persistent=True)


def unregister():
    KritaConnection.LINK_INSTANCE.cleanup()
    bpy.utils.unregister_class(GlobalStore)
    bpy.utils.unregister_class(_PT_BlenderKritaLinkPanel)
    bpy.utils.unregister_class(DisconnectOperator)
    if  bpy.app.timers.is_registered(update_panel_watch):
        bpy.app.timers.unregister(update_panel_watch)
    if  bpy.app.timers.is_registered(UvWatch.instance.check_for_changes):
        bpy.app.timers.unregister(UvWatch.instance.check_for_changes)
    if  bpy.app.timers.is_registered(ImagesStateWatch.instance.check_for_changes):
        bpy.app.timers.unregister(ImagesStateWatch.instance.check_for_changes)
    del bpy.types.Scene.global_store 

if __name__ == "__main__":
    register()
