from multiprocessing.connection import Connection, Listener, Client
import time
from random import random
from threading import Thread, Event
from multiprocessing import shared_memory
import bpy
import numpy as np
from .image_manager import ImageManager
from .ui import BlenderKritaLinkPanel


class KritaConnection():
    PORT = 6000
    LINK_INSTANCE = None
    STATUS: str

    def __init__(self) -> None:
        if KritaConnection.LINK_INSTANCE:
            return
        KritaConnection.LINK_INSTANCE = self

    def __del__(self):
        if self.CONNECTION:
            self.CONNECTION.send("close")
            self.CONNECTION.close()

    def start(self):
        self.__STOP_SIGNAL = Event()
        self.__THREAD = Thread(target=self.krita_listener)
        self.__THREAD.start()
        self.CONNECTION: None | Connection = None
        KritaConnection.STATUS = 'listening'

    def update_message(self, message):
        if hasattr(bpy.context, 'scene') and hasattr(bpy.context.scene, 'test_prop') and bpy.context.scene.test_prop:
            bpy.context.scene.test_prop = message
        else:
            print("no scene??")

    def krita_listener(self):
        """chuj"""
        while not self.__STOP_SIGNAL.isSet():
            self.update_message("listening")
            KritaConnection.LINK_INSTANCE = self
            # family is deduced to be 'AF_INET'
            address = ('localhost', KritaConnection.PORT)
            self.update_message("listening")
            listener = Listener(address, authkey=b'2137')
            conn = listener.accept()
            # self.update_message("connected")
            KritaConnection.CONNECTION = conn
            print("connection accepted")
            existing_shm = shared_memory.SharedMemory(name='krita-blender')
            try:
                while True:
                    print("listening for message")
                    self.update_message("connected")
                    msg = conn.recv()
                    self.update_message("message recived")
                    print(msg)
                    if msg == 'close':
                        print(msg)
                        conn.close()
                        self.update_message("closed")
                        break
                    elif isinstance(msg, object):
                        print("message is object UwU")
                        if "type" in msg and 'requestId' in msg:
                            type = msg["type"]
                            match type:
                                case "REFRESH":
                                    print("refresh initiated")
                                    self.update_message("got The Image")
                                    pixels_array = None
                                    match msg["depth"]:
                                        case "F32":
                                            pixels_array = np.frombuffer(
                                                existing_shm.buf, dtype=np.float32)
                                        case "F16":
                                            pixels_array = np.frombuffer(
                                                existing_shm.buf, dtype=np.float16)
                                        case "U8":
                                            pixels_array = np.frombuffer(
                                                existing_shm.buf, dtype=np.uint8)
                                        case "U16":
                                            pixels_array = np.frombuffer(
                                                existing_shm.buf, dtype=np.uint16)
                                    
                                    print("refresh initiated")
                                    ImageManager.INSTANCE.mirror_image(pixels_array)
                                    pixels_array = None
                                    print("refresh complete")
                                    self.update_message("connected")
                                    conn.send({
                                        "type": "REFRESH",
                                        "depth": msg["depth"],
                                        "requestId": msg['requestId']
                                    })

                                case "GET_IMAGES":
                                    data = []
                                    for image in bpy.data.images:
                                        data.append({
                                            "name": image.name,
                                            "path": bpy.path.abspath(image.filepath),
                                            "size": [image.size[0], image.size[1]],
                                            "isActive": ImageManager.INSTANCE.IMAGE == image.name
                                        })

                                    print(msg)
                                    conn.send({
                                        "type": "GET_IMAGES",
                                        "data": data,
                                        "requestId": msg['requestId']
                                    })
                                    print("message sent")

                                case "OPEN":
                                    print("dupaopen")
                                    conn.send({
                                        "type": "OPEN",
                                        "data": "",
                                        "requestId": msg['requestId']
                                    })

                                case "OVERRIDE_IMAGE":
                                    print("overriding image: ",
                                          msg['data']['name'])
                                    ImageManager.INSTANCE.set_image_name(
                                        msg['data']['name'])
                                    conn.send({
                                        "type": "OVERRIDE_IMAGE",
                                        "data": "",
                                        "requestId": msg['requestId']
                                    })
                                case "RECREATE_MEMORY":
                                    existing_shm = shared_memory.SharedMemory(
                                        name='krita-blender')
                                    conn.send({
                                        "type": "RECREATE_MEMORY",
                                        "data": "",
                                        "requestId": msg['requestId']
                                    })
                                    
                                case "CLOSE_MEMORY":
                                    existing_shm.close()
                                    conn.send({
                                        "type": "CLOSE_MEMORY",
                                        "data": "",
                                        "requestId": msg['requestId']
                                    })

                                case _:
                                    conn.send({
                                        "type": "nop",
                                        "data": None,
                                        "requestId": msg['requestId']
                                    })

                conn.send('close')
                existing_shm.close()
                conn.close()
            except Exception as e:
                print("error happened", e)
                if self.CONNECTION != None:
                    self.CONNECTION.send("close")
                    self.CONNECTION.close()
                self.CONNECTION = None
            # existing_shm.close()
            listener.close()
            if self.__STOP_SIGNAL.is_set():
                KritaConnection.STATUS = "listening"
                self.redraw_uis()
                return
