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
from .uv_extractor import getUvData


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
        
class GetUvsOperator(bpy.types.Operator):
    bl_idname = "object.get_uvs_operator"
    bl_label = "Minimal Operator"

    def execute(self, context):
        uvs = getUvData(context)
        KritaConnection.UVS = uvs
        print("Hello World")
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return False
    
class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        print("TIMER TRIGGERED")
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            print("TIMER TRIGGERED")
            if KritaConnection.UVS == None:
                print("SENDING UVS")
                KritaConnection.sendUVSObject['data'] = getUvData(context)
                KritaConnection.send_message(KritaConnection.sendUVSObject)
                KritaConnection.UVS = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.2, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(HelloWorldOperator)
    bpy.utils.register_class(GetUvsOperator)
    bpy.utils.register_class(BlenderKritaLinkPanel)

def unregister():
    connection_instance = None
    image_manager_instance = None
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.utils.unregister_class(HelloWorldOperator)
    bpy.utils.unregister_class(GetUvsOperator)
    bpy.utils.unregister_class(BlenderKritaLinkPanel)
    # del bpy.types.Scene.connection_status
    del bpy.types.Scene.test_prop

if __name__ == "__main__":
    register()

connection_instance = KritaConnection()
print(dir(connection_instance))
connection_instance.start()
image_manager_instance = ImageManager()
# bpy.ops.wm.modal_timer_operator()
