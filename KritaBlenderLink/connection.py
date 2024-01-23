from krita import Krita
from threading import Thread
from multiprocessing import shared_memory
from multiprocessing.connection import Client
import asyncio
from pprint import pprint
from contextlib import contextmanager


@contextmanager
def shared_memory_context(name: str, size: int, destroy: bool, create=bool):
    shm = None
    if size is None:
        shm = shared_memory.SharedMemory(name=name, create=create)
    else:
        shm = shared_memory.SharedMemory(name=name, create=create, size=size)

    try:
        yield shm
    finally:
        if destroy:
            shm.unlink()
        else:
            shm.close()


def check_shared_memory_exists(name):
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.close()
        return True
    except FileNotFoundError:
        return False


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
        self.on_disconnect = on_disconnect
        self.linked_document = None
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
                        message_available = self.connection.poll(0.5)
                        if not message_available:
                            continue
                        if self.connection.closed:
                            break
                        message = self.connection.recv()
                        if message == "close":
                            print("closing connection...")
                            break
                        if "imageData" not in message:
                            print("recived message", format_message(message))
                        self.emit_message(message)
                    except Exception as e:
                        print("Error on reciving messages", e)
                        self.connection = None
                        if self.shm and check_shared_memory_exists("krita-blender"):
                            self.shm.unlink()
                            self.shm = None
                        break
                self.linked_document = None
                on_disconnect()

        t1 = Thread(target=thread)
        t1.start()

    def disconnect(self):
        """gets called when user closes connection"""
        if self.shm and check_shared_memory_exists("krita-blender"):
            self.shm.unlink()
        if self.connection:
            self.connection.close()
            self.connection = None
            if self.on_disconnect:
                self.on_disconnect()
        else:
            print("there is no connection")

    def emit_message(self, message):
        """emits a message to all listeners inside this object"""
        if isinstance(message, object) and "type" in message and "data" in message:
            print(ConnectionManager.listeners, format_message(message))
            event_type = message["type"]
            for listener in ConnectionManager.listeners:
                if listener.event_type == event_type:
                    listener.recieve_message(message=message)

    def resize_memory(self, canvas_bytes_len):
        print("unlink")
        if self.shm and check_shared_memory_exists("krita-blender"):
            self.shm.unlink()
            self.shm = None

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
        if self.shm is None:
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

            async def task():
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

            await asyncio.create_task(task())
            res = await asyncio.wait_for(future, 3.0)
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
        conn_manager.linked_document,
    )
    print("resizing")
    conn_manager.resize_memory(size[0] * size[1] * depth)
    asyncio.run(conn_manager.request({"data": image, "type": "OVERRIDE_IMAGE"}))
    asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))


def refresh_document(doc):  # TODO: duplicated code, move somewhere else
    root_node = doc.rootNode()
    if root_node and len(root_node.childNodes()) > 0:
        test_layer = doc.createNode("DELME", "paintLayer")
        root_node.addChildNode(test_layer, root_node.childNodes()[0])
        test_layer.remove()


def blender_image_as_new_layer(image_object, conn_manager):
    depth = Krita.instance().activeDocument().colorDepth()
    images = asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))[
        "data"
    ]
    pixel_size = 0
    match depth:
        case "F32":
            pixel_size = 4
        case "F16":
            pixel_size = 2
        case "U16":
            pixel_size = 2
        case "U8":
            pixel_size = 1
    image = None
    for i in images:
        if i["name"] == image_object["name"]:
            image = i
    if not image:
        return
    print(
        image_object["size"][0],
        image_object["size"][1],
        pixel_size,
        image_object["size"][0] * image_object["size"][1] * pixel_size * 4,
    )
    with shared_memory_context(
        name="blender-krita",
        destroy=True,
        size=image_object["size"][0] * image_object["size"][1] * pixel_size * 4,
        create=True,
    ) as new_shm:
        asyncio.run(
            conn_manager.request(
                {
                    "data": {"image": image_object, "depth": depth},
                    "type": "IMAGE_TO_LAYER",
                }
            )
        )
        krita_instance = Krita.instance()
        document = krita_instance.activeDocument()
        if document:
            new_layer = document.createNode(
                image["name"] + "__from_blender", "paintLayer"
            )
            document.rootNode().addChildNode(new_layer, None)
            new_layer.setPixelData(
                new_shm.buf.tobytes(), 0, 0, image["size"][0], image["size"][1]
            )
            refresh_document(document)


def change_memory(conn_manager: ConnectionManager):
    """function to resize memory if image data is changed"""
    print("change memory", conn_manager.linked_document)
    doc = Krita.instance().activeDocument()
    size = [doc.width(), doc.height()]
    depth = int(doc.colorDepth()[1:]) // 2
    active_image = conn_manager.get_active_image()
    if not conn_manager.connection:
        return
    elif not active_image or active_image["size"] != size:
        asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))

    if conn_manager.linked_document is None:
        return
    print(conn_manager.linked_document)

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


def format_message(msg: object):
    """function that removes data if "noshow" flag is present, useful for not clogging terminal"""
    if hasattr(msg, "noshow") or "noshow" in msg:
        return {
            "type": msg["type"],
            "requestId": msg["requestId"],
            "formattedMessage": True,
        }
    else:
        msg["formattedMessage"] = True
        return msg
