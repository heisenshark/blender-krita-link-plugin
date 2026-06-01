from KritaBlenderLink.settings import Settings
from krita import Krita
from threading import Thread
from multiprocessing.connection import Client
from multiprocessing import shared_memory
import asyncio
import traceback
from .lb import shared_memory_context, check_shared_memory_exists
from .logger import logger, configure_logger


# link_dict = {
#     "image1":{
#         "type":"grouplayer"|"layer"|"document",
#         "document":document,
#
#         "memoryObject": shmshit,
#     },
#     "image2":{
#         "type":"grouplayer"|"layer"|"document",
#         "obj":grouplayer,
#         "document":document,
#         "layer":layer,
#     },
#     "image3":{
#         "type":"grouplayer"|"layer"|"document",
#         "obj":layer,
#     }
# }

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
    port = 65431
    connection = None
    shm = None
    listeners: list[MessageListener] = []
    requestId = 0
    linked_document = None
    linked_image = None
    images = []
    linked_images = {}

    def __init__(self) -> None:
        if Settings.getSetting("port") is not None:
            ConnectionManager.port = Settings.getSetting("port") 
        configure_logger(ConnectionManager.port)
        MessageListener("GET_IMAGES", lambda message: self.set_images(message["data"]))

    def set_images(self, images):
        self.images = images

    def change_adress(self, adr):
        self.port = adr
        configure_logger(adr)

    def connect(self, on_connect, on_disconnect):
        self.on_disconnect = on_disconnect
        if self.connection:
            return
        else:
            logger.debug("connection instance status: %s", self.connection)
        logger.info("connecting to port: %s", self.port)
        configure_logger(self.port)
        def thread():
            try:
                with Client(("localhost", self.port), authkey=b"2137") as connection:
                    logger.info("connection client created")
                    self.connection = connection
                    on_connect()
                    while True:
                        try:
                            message_available = self.connection.poll(0.5)
                            if not message_available:
                                continue
                            if self.connection is None or self.connection.closed:
                                break
                            message = self.connection.recv()
                            if message == "close":
                                logger.info("closing connection message received")
                                break
                            if "imageData" not in message:
                                logger.debug("received message: %s", format_message(message))
                            self.emit_message(message)
                        except Exception as e:
                            logger.error("Error on receiving messages: %s\n%s", e, traceback.format_exc())
                            self.connection = None
                            for img_name,img in self.linked_images.items():
                                if img["memoryObject"] and check_shared_memory_exists("krita-blender"+str(ConnectionManager.port)+"_"+str(img_name)):
                                    img["memoryObject"].unlink()
                                    img["memoryObject"]= None
                            break
            except Exception as conn_err:
                logger.error("Failed to establish connection to Blender on port %s: %s", self.port, conn_err)
            on_disconnect()

        t1 = Thread(target=thread)
        t1.start()

    def disconnect(self):
        """gets called when user closes connection"""

        for img_name,img in self.linked_images.items():
            if img["memoryObject"] and check_shared_memory_exists("krita-blender"+str(ConnectionManager.port)+"_"+str(img_name)):
                img["memoryObject"].unlink()
        self.linked_images = {}
        if self.connection:
            self.connection.close()
            self.connection = None
            if self.on_disconnect:
                self.on_disconnect()
        else:
            logger.warning("there is no connection to disconnect")

    def emit_message(self, message):
        """emits a message to all listeners inside this object"""
        if isinstance(message, object) and "type" in message and "data" in message:
            logger.debug("emitting message: listeners=%s msg=%s", ConnectionManager.listeners, format_message(message))
            event_type = message["type"]
            for listener in ConnectionManager.listeners:
                if listener.event_type == event_type:
                    listener.recieve_message(message=message)

    def resize_memory(self, canvas_bytes_len:int,image_name:str):
        logger.debug("unlink memory for %s", image_name)
        linked_image = self.linked_images[image_name]
        try:
            if linked_image["memoryObject"]:
                linked_image["memoryObject"].unlink()

        except Exception as e:
            logger.debug("memory unlink exception: %s", e)
        name ="krita-blender"+str(ConnectionManager.port)+"_"+str(image_name)

        if linked_image["memoryObject"] and check_shared_memory_exists(name):
            linked_image["memoryObject"].unlink()
            linked_image["memoryObject"] = None

        try:
            linked_image["memoryObject"] = shared_memory.SharedMemory(
                name=name, create=True, size=canvas_bytes_len
            )
            logger.info("shared memory created: %s", name)
        except Exception as e:
            logger.debug("shared memory creation failed (file might exist), attempting attach: %s", e)
            linked_image["memoryObject"] = shared_memory.SharedMemory(
                name=name, create=False, size=canvas_bytes_len
            )

    def send_message(self, message):
        if self.connection:
            self.connection.send(message)
        else:
            logger.warning("no connection available to send message")

    def write_memory(self, bts,shm):
        logger.debug("write_memory: shm=%s, size=%s", shm, len(bts))
        if shm is None:
            logger.warning("no memory object to write into")
            return
        shm.buf[: len(bts)] = bts

    def remove_link(self,image_name:str):
        keys = [x for x in self.linked_images.keys()]
        if image_name in keys:
            self.linked_images[image_name]["memoryObject"].unlink()
            del self.linked_images[image_name]
        asyncio.run(self.request({"data": "", "type": "GET_IMAGES"}))

    def get_image(self,image_name:str):
        return next(filter(lambda x: x["name"]==image_name,self.images))


    async def request(self, payload):
        if self.connection:
            event_loop = asyncio.get_event_loop()
            future = event_loop.create_future()
            requestId = ConnectionManager.requestId
            payload["requestId"] = requestId
            ConnectionManager.requestId += 1

            async def task():
                def on_nop(msg):
                    logger.debug("future cancelled: request nop response received")
                    if msg["requestId"] == self.requestId:
                        future.cancel()

                def on_success(msg):
                    logger.debug("future success: request response received")
                    event_loop.call_soon_threadsafe(future.set_result, msg)

                failure_listener = MessageListener("nop", on_nop)
                success_listener = MessageListener(payload["type"], on_success)
                future.add_done_callback(
                    lambda fut: (failure_listener.destroy(), success_listener.destroy())
                )
                self.send_message(payload)
                logger.debug("request message sent: waiting for response")

            await asyncio.create_task(task())
            res = await asyncio.wait_for(future, 3.0)
            logger.debug("request/response complete")
            return res
        return None


# on link function, here the shm is created
def link_image(image, conn_manager: ConnectionManager): 
    doc = Krita.instance().activeDocument()
    depth = int(doc.colorDepth()[1:]) // 2
    size = [doc.width(), doc.height()]
    conn_manager.linked_images[image["name"]] = {
        "type":"document",
        "document":doc,
        "memoryObject":None
    }
    logger.info(
        "linking image size=%s memsize=%s depth=%s colorDepth=%s image=%s",
        size,
        size[0] * size[1] * depth,
        depth,
        doc.colorDepth()[1:],
        image,
    )
    logger.info("resizing memory for linked image")
    conn_manager.resize_memory(size[0] * size[1] * depth,image["name"])

    asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))


def link_layer(image, conn_manager: ConnectionManager): 
    doc = Krita.instance().activeDocument()
    depth = int(doc.colorDepth()[1:]) // 2
    size = [doc.width(), doc.height()]
    logger.info("linking active layer: %s", doc.activeNode().name() if doc.activeNode() else "None")

    conn_manager.linked_images[image["name"]] = {
        "type":"layer",
        "document":doc,
        "layer":doc.activeNode(),
        "memoryObject":None
    }
    conn_manager.resize_memory(size[0] * size[1] * depth,image["name"])
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
    logger.info(
        "creating new layer from blender: size=%sx%s pixel_size=%s total_bytes=%s",
        image_object["size"][0],
        image_object["size"][1],
        pixel_size,
        image_object["size"][0] * image_object["size"][1] * pixel_size * 4,
    )
    with shared_memory_context(
        name="blender-krita"+str(ConnectionManager.port),
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

def open_as_new_document(image, conn_manager: ConnectionManager, link:bool = False):
    x,y = image["size"]
    newDocument = Krita.instance().createDocument(x, y, image["name"], "RGBA", "U8", "", 300.0)
    bckg = newDocument.nodeByName("Background")
    if bckg is not None:
        bckg.remove()
    Krita.instance().activeWindow().addView(newDocument)
    blender_image_as_new_layer(image,conn_manager)
    if link: 
        asyncio.run(conn_manager.request({"type": "GET_UV_OVERLAY"}))
        link_image(image,conn_manager)  
        

def change_memory(conn_manager: ConnectionManager):
    """function to resize memory if image data is changed"""
    for image_name,link_object in conn_manager.linked_images.items():
        logger.debug("change memory check")
        doc = link_object["document"]
        size = [doc.width(), doc.height()]
        depth = int(doc.colorDepth()[1:]) // 2
        active_image = conn_manager.get_image(image_name)
        if not conn_manager.connection:
            return
        elif not active_image or active_image["size"] != size:
            asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))

        if image_name not in conn_manager.linked_images.keys():
            return

        logger.info(
            "resizing active linked image dimensions changed: size=%s depth=%s colorDepth=%s",
            size,
            depth,
            doc.colorDepth()[1:],
        )
        conn_manager.resize_memory(size[0] * size[1] * depth,image_name)
    asyncio.run(conn_manager.request({"data": "", "type": "GET_IMAGES"}))

def format_message(msg: object):
    """function that removes data if "noshow" flag is present, useful for not clogging terminal"""
    if msg is None:
        return {}
    if hasattr(msg, "noshow") or "noshow" in msg:
        return {
            "type": msg["type"],
            "requestId": msg["requestId"],
            "formattedMessage": True,
        }
    else:
        msg["formattedMessage"] = True
        return msg
