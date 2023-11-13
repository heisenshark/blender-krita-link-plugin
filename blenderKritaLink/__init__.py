from multiprocessing.connection import Listener,Client
import time
from random import random
from threading import Thread
from multiprocessing import shared_memory
import struct
import array
import bpy
import numpy as np
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

class BlenderKritaLinkPanel(bpy.types.Panel):
    """Blender Krita Link Panel"""
    bl_label = "Krita Link"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Blender Krita Link'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="connection: " + KritaConnection.STATUS)
        col = layout.column()
        for image in bpy.data.images:
            col.label(text=image.name)
        col = layout.column()
        col.operator(HelloWorldOperator.bl_idname,text="say hello",icon = "UV_FACESEL")

        
        
class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Minimal Operator"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return False
    
class LoadImage(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Minimal Operator"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return False

def siema():
    print("siema")


def register():
    bpy.utils.register_class(HelloWorldOperator)
    bpy.utils.register_class(BlenderKritaLinkPanel)
    # image_name = "Untitled"
    # image_src = bpy.data.images[image_name]
    # src_len = len(image_src.pixels)


def unregister():
    connection_instance = None
    image_manager_instance = None
    bpy.utils.unregister_class(HelloWorldOperator)
    bpy.utils.unregister_class(BlenderKritaLinkPanel)

if __name__ == "__main__":
    register()

connection_instance = KritaConnection()
image_manager_instance = ImageManager()
    