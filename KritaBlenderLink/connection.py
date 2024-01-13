from email import message
from krita import *
from threading import Timer, Thread
from multiprocessing import shared_memory
from multiprocessing.connection import Client
import asyncio
from pprint import pprint
from contextlib import contextmanager

@contextmanager
def shared_memory_context(name:str,size:int,destroy:bool,create=bool):
    shm = None
    if size == None:
        shm = shared_memory.SharedMemory(name=name,create=create)
    else:
        shm = shared_memory.SharedMemory(name=name,create=create,size=size)
    
    try:
        yield shm
    finally:
        if destroy:
            shm.unlink()
        else:
            shm.close()


class MessageListener:
    def __init__(self, event_type, fn, once=False) -> None:
        self.event_type = event_type
        self.fn = fn
        self.once = once
        ConnectionManager.listeners.append(self)

    def destroy(self):
        ConnectionManager.listeners.remove(self)

    def recieve_message(self, message):
        self.fn(message)
        if self.once:
            self.destroy()


class ConnectionManager:
    adress = 6000
    connection = None
    shm = None
    listeners: list[MessageListener] = []
    requestId = 0
    linked_document = None
    linked_image = None
    images = []

    def __init__(self) -> None:
        MessageListener("GET_IMAGES", lambda message: self.set_images(message["data"]))

    def set_images(self, images):
        self.images = images

    def get_active_image(self):
        return next(filter(lambda x: x["isActive"], self.images), None)

    def change_adress(self, adr):
        self.adress = adr

    def connect(self, canvas_bytes_len, on_connect, on_disconnect):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        if self.connection:
            return
        else:
            print(self.connection)
        
        def thread():
            with Client(("localhost", self.adress), authkey=b"2137") as connection:
                print("client created")
                self.connection = connection
                on_connect()
                while True:
                    try:
                        message = self.connection.recv()
                        if("imageData" not in message):
                            print("recived message", message)
                        self.emit_message(message)
                    except Exception as e:
                        print("Error on reciving messages", e)
                        self.connection = None
                        if self.shm:
                            # self.shm.close()
                            self.shm.unlink()
                        on_disconnect()
                        break

        t1 = Thread(target=thread)
        t1.start()

    def disconnect(self):
        if self.shm:
            self.shm.close()
            self.shm.unlink()
        if self.connection:
            self.connection.send("close")
            self.connection.close()
            self.connection = None
            if self.on_disconnect:
                self.on_disconnect()
        else:
            print("there is no connection")

    def emit_message(self, message):
        if isinstance(message, object) and "type" in message and "data" in message:
            print(ConnectionManager.listeners, print(message))
            event_type = message["type"]
            for listener in ConnectionManager.listeners:
                if listener.event_type == event_type:
                    listener.recieve_message(message=message)

    def resize_memory(self, canvas_bytes_len):
        print("unlink")
        if self.shm != None:
            self.shm.unlink()
        # self.shm.close()
        asyncio.run(self.request({"type": "CLOSE_MEMORY", "data": ""}))
        try:
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=True, size=canvas_bytes_len
            )
            print("memory  created")
        except:
            print("file exists, trying another way")
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=False, size=canvas_bytes_len
            )
        asyncio.run(self.request({"type": "RECREATE_MEMORY", "data": ""}))

    def send_message(self, message):
        if self.connection:
            self.connection.send(message)
        else:
            print("there is no connection")

    def write_memory(self, bts):
        print(self.shm, len(bts))
        if self.shm == None:
            print("no memory to write")
            return
        self.shm.buf[: len(bts)] = bts

    def remove_link(self):
        self.linked_document = None
        asyncio.run(self.request({"data": "", "type": "REMOVE_LINK"}))
        asyncio.run(self.request({"data": "", "type": "GET_IMAGES"}))
        
    async def request(self, payload):
        if self.connection:
            event_loop = asyncio.get_event_loop()
            future = event_loop.create_future()
            requestId = ConnectionManager.requestId
            payload["requestId"] = requestId
            ConnectionManager.requestId += 1

            async def chuj():
                def on_nop(msg):
                    print("future cancelled")
                    if msg["requestId"] == self.requestId:
                        future.cancel()

                def on_success(msg):
                    print("future success")
                    event_loop.call_soon_threadsafe(future.set_result, msg)

                failure_listener = MessageListener("nop", on_nop)
                success_listener = MessageListener(payload["type"], on_success)
                future.add_done_callback(
                    lambda fut: (failure_listener.destroy(), success_listener.destroy())
                )
                self.send_message(payload)
                print("future before")

            await asyncio.create_task(chuj())
            res = await asyncio.wait_for(future, 1.0)
            print("future done")
            return res
        return None


def override_image(image, conn_manager):
    doc = Krita.instance().activeDocument()
    depth = int(doc.colorDepth()[1:]) // 2
    size = [doc.width(), doc.height()]
    conn_manager.linked_document = doc
    print(
        size,
        "memsize",
        size[0] * size[1] * depth,
        depth,
        doc.colorDepth()[1:],
        image,
        conn_manager.linked_document
    )
    print("resizing")
    conn_manager.resize_memory(size[0] * size[1] * depth)
    asyncio.run(conn_manager.request({"data": image, "type": "OVERRIDE_IMAGE"}))
    asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))

def blender_image_as_new_layer(image_object, conn_manager):
    depth = Krita.instance().activeDocument().colorDepth()
    images = asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))
    data = asyncio.run(conn_manager.request({"data": {"image":image_object,"depth":depth}, "type": "IMAGE_TO_LAYER"}))
    image = None
    
    for i in images:
        if i['name'] == image_object['name']:
            image = i
    if not image: 
        return    
    
    with shared_memory_context(name='blender-krita',destroy=True, size=image["size"][0]*image["size"][1]*4,create=False) as new_shm:
        mv = memoryview(new_shm.buf).cast('f')
        krita_instance = Krita.instance()
        document = krita_instance.activeDocument()
        if document:

            new_layer = document.createNode(image['name']+"__from_blender", "paintLayer")
            document.rootNode().addChildNode(new_layer, None)
            new_layer.setPixelData(mv.tobytes(), 0, 0, image["size"][0],image["size"][1])
            # document.refreshProjection() #Probably is slow af 

        mv = None

def change_memory(conn_manager: ConnectionManager):
    doc = Krita.instance().activeDocument()
    size = [doc.width(), doc.height()]
    depth = int(doc.colorDepth()[1:]) // 2
    active_image = conn_manager.get_active_image()
    if not conn_manager.connection:
        return
    elif not active_image or active_image['size'] != size:
        asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))

    ConnectionManager.linked_document = doc

    print(
        size,
        "memsize",
        size[0] * size[1] * depth,
        depth,
        doc.colorDepth()[1:],
    )
    print("resizing")
    conn_manager.resize_memory(size[0] * size[1] * depth)
    asyncio.run(conn_manager.request({"data": active_image, "type": "OVERRIDE_IMAGE"}))
    asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))
