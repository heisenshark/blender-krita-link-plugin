from multiprocessing.connection import Connection, Listener,Client
import time
from random import random
from threading import Thread,Event
from multiprocessing import shared_memory
import struct
import array

from click import launch
import bpy
import numpy as np
from .image_manager import ImageManager

class KritaConnection():
    PORT = 6000
    LINK_INSTANCE = None
    STATUS: str
    
    def __init__(self) -> None:
        if KritaConnection.LINK_INSTANCE: return
        KritaConnection.LINK_INSTANCE = self
        self.__THREAD = Thread(target=self.krita_listener)
        self.__THREAD.start()
        self.__STOP_SIGNAL = Event()
        self.CONNECTION: None|Connection = None
        KritaConnection.STATUS = 'listening'

    def __del__(self):
        self.__STOP_SIGNAL.set()
        if self.CONNECTION:
            self.CONNECTION.send("close")
            self.CONNECTION.close()
            
    def krita_listener(self):
        """chuj"""
        while True:
            KritaConnection.LINK_INSTANCE = self
            address = ('localhost', KritaConnection.PORT)     # family is deduced to be 'AF_INET'
            KritaConnection.STATUS = "listening"
            listener = Listener(address, authkey=b'2137')
            conn = listener.accept()
            KritaConnection.STATUS = "connected"
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
                        existing_shm.close()
                        break
                    elif msg == 'refresh':
                        t = time.time()
                        print("refresh initiated")
                        fp32_array = np.frombuffer(existing_shm.buf, dtype=np.float32)
                        print("refresh initiated")
                        ImageManager.INSTANCE.mirror_image(fp32_array)
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
                existing_shm.close()
            listener.close()
            if self.__STOP_SIGNAL.is_set():
                break