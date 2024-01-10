import bpy
from .ui  import _PT_BlenderKritaLinkPanel
from .image_manager import ImageManager
from .connection import KritaConnection 

bl_info = {
    "name": "Blender Krita link",
    "blender": (2, 80, 0),
    "category": "Object",
}
                

def register():
    bpy.utils.register_class(_PT_BlenderKritaLinkPanel)

def unregister():
    connection_instance = None
    image_manager_instance = None
    bpy.utils.unregister_class(_PT_BlenderKritaLinkPanel)
    del bpy.types.Scene.test_prop

if __name__ == "__main__":
    register()

connection_instance = KritaConnection()
print(dir(connection_instance))
connection_instance.start()
image_manager_instance = ImageManager()