from multiprocessing.connection import Connection, Listener,Client
import time
from random import random
from threading import Thread,Event
from multiprocessing import shared_memory
import struct
import array
import bpy
import numpy as np
from .image_manager import ImageManager
from .ui import BlenderKritaLinkPanel

class KritaConnection():
    PORT = 6000
    LINK_INSTANCE = None
    STATUS: str
    
    def __init__(self) -> None:
        if KritaConnection.LINK_INSTANCE: return
        KritaConnection.LINK_INSTANCE = self

    def __del__(self):
        if self.CONNECTION:
            self.CONNECTION.send("close")
            self.CONNECTION.close()
    
    def start(self):
        self.__STOP_SIGNAL = Event()
        self.__THREAD = Thread(target=self.krita_listener)
        self.__THREAD.start()
        self.CONNECTION: None|Connection = None
        KritaConnection.STATUS = 'listening'
        
    def update_message(self,message):
        if hasattr(bpy.context,'scene'):
            bpy.context.scene.test_prop= "listening"
        else: print("no scene??")
        
    def krita_listener(self):
        """chuj"""
        while not self.__STOP_SIGNAL.isSet():
            KritaConnection.LINK_INSTANCE = self
            address = ('localhost', KritaConnection.PORT)     # family is deduced to be 'AF_INET'
            self.update_message("listening")
            listener = Listener(address, authkey=b'2137')
            conn = listener.accept()
            self.update_message("connected")
            KritaConnection.CONNECTION = conn
            print("connection accepted")
            existing_shm = shared_memory.SharedMemory(name='krita-blender')
            try:
                while True:
                    msg = conn.recv()
                    print("message recived")
                    if msg == 'close':
                        print(msg)
                        conn.close()
                        break
                    elif msg == 'refresh':
                        t = time.time()
                        print("refresh initiated")
                        fp32_array = np.frombuffer(existing_shm.buf, dtype=np.float32)
                        print("refresh initiated")
                        ImageManager.INSTANCE.mirror_image(fp32_array)
                        fp32_array = None
                        print("refresh complete")
                    # elif isinstance(msg, bytes):
                    #     ImageManager.update_image(msg)
                    #     print("handled_time",time.time())
                existing_shm.close()
                conn.close()
            except:
                print("error happened")
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