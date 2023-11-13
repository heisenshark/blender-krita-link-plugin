from multiprocessing.connection import Listener,Client
import time
from random import random
from threading import Thread, Timer
from multiprocessing import shared_memory
import struct
import array
import bpy
import numpy as np
from .ui  import BlenderKritaLinkPanel
from .image_manager import ImageManager
from .connection import KritaConnection 


bl_info = {
    "name": "Blender Krita link",
    "blender": (2, 80, 0),
    "category": "Object",
}

#t1 = Thread(target=krita_listener)
#t1.start()
T1 = None

def update_gui():
    print("siema")
    for area in bpy.context.screen.areas:area.tag_redraw()
    print("elo")

        
        
class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Minimal Operator"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return False
    
def register():
    bpy.utils.register_class(HelloWorldOperator)
    bpy.utils.register_class(BlenderKritaLinkPanel)


def unregister():
    connection_instance = None
    image_manager_instance = None
    bpy.utils.unregister_class(HelloWorldOperator)
    bpy.utils.unregister_class(BlenderKritaLinkPanel)
    # del bpy.types.Scene.connection_status
    del bpy.types.Scene.test_prop

if __name__ == "__main__":
    register()

connection_instance = KritaConnection()
print(dir(connection_instance))
connection_instance.start()
image_manager_instance = ImageManager()