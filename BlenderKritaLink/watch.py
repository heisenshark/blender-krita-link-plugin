from time import time
import bpy
from BlenderKritaLink.connection import KritaConnection
from BlenderKritaLink.uv_extractor import get_fast_hash, getUvOverlay

from .image_manager import ImageManager

class UvWatch:
    last_hash = None
    instance = None
    def __init__(self) -> None:
        UvWatch.instance= self
    
    def check_for_changes(self):
        toggle = bpy.context.scene.global_store.sync_toggle
        interval = bpy.context.scene.global_store.sync_interval
        if not toggle or KritaConnection.CONNECTION is None:
            self.last_hash = None
            return interval
        t = time()
        try:
            ImageManager.UPDATING_IMAGE.acquire()
            print(f"hello, perfcheck{time()-t}", )
            new_hash = get_fast_hash()
            print(f"hello, perfcheck{time()-t}")
            print("hashing func", new_hash, self.last_hash)
            if new_hash != self.last_hash and KritaConnection.CONNECTION != None:
                dd = getUvOverlay() 
                print("uv data changed, sending overlay")
                KritaConnection.CONNECTION.send(
                            {
                                "type": "GET_UV_OVERLAY",
                                "data": dd,
                                "noshow": True,
                                "requestId": -1,
                            }
                        )
            self.last_hash = new_hash
        finally:
            
            ImageManager.UPDATING_IMAGE.release()
            print(interval)
            return interval

class ImagesStateWatch():
    instance = None
    last_hash= None
    def __init__(self) -> None:
        ImagesStateWatch.instance = self
        
    def check_for_changes(self):
        toggle = bpy.context.scene.global_store.sync_toggle
        interval = bpy.context.scene.global_store.sync_interval
        if not toggle:
            return interval

        data = set()
        for image in bpy.data.images:
            data.add(frozenset(
                {
                    image.name,
                    bpy.path.abspath(
                        image.filepath
                    ),
                    image.size[0], 
                    image.size[1],
                    ImageManager.INSTANCE.IMAGE_NAME == image.name,
                })
            )

        new_hash = hash(frozenset(data))
        if new_hash != self.last_hash and KritaConnection.CONNECTION != None:
            data = []
            for image in bpy.data.images:
                data.append(
                    {
                        "name": image.name,
                        "path": bpy.path.abspath(
                            image.filepath
                        ),
                        "size": [image.size[0], image.size[1]],
                    }
                )
            self.last_hash = new_hash
            KritaConnection.CONNECTION.send(
                {
                    "type": "GET_IMAGES",
                    "data": data,
                    "requestId": -1,
                }
            )
        return interval 
