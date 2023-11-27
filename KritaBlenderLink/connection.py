from email import message
from krita import *
from threading import Timer, Thread
from multiprocessing import shared_memory
from multiprocessing.connection import Client
import asyncio


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


class ConnectionManager():
    adress = 6000
    connection = None
    shm = None
    listeners: list[MessageListener] = []
    requestId = 0
    linked_document = None

    def __init__(self) -> None:
        MessageListener("GET_IMAGES", lambda x: print("dupa dupa chuj"))

    def change_adress(self, adr):
        self.adress = adr

    def connect(self, canvas_bytes_len, on_connect, on_disconnect):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        if (self.connection):
            return
        else:
            print(self.connection)
        try:
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=True, size=canvas_bytes_len)
        except:
            print("file exists, trying another way")
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=False, size=canvas_bytes_len)

        def thread():
            with Client(("localhost", self.adress), authkey=b'2137') as connection:
                print("client created")
                self.connection = connection
                on_connect()
                # t2 = Thread(target=thread2)
                # t2.start()
                while True:
                    try:
                        message = self.connection.recv()
                        print("recived message", message)
                        self.emit_message(message)
                    except Exception as e:
                        print("Error on reciving messages", e)
                        self.connection = None
                        if self.shm:
                            self.shm.close()
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
            self.connection.send('close')
            self.connection.close()
            self.connection = None
            if (self.on_disconnect):
                self.on_disconnect()
        else:
            print("there is no connection")

    def emit_message(self, message):
        if isinstance(message, object) and "type" in message and 'data' in message:
            print(ConnectionManager.listeners, print(message))
            event_type = message['type']
            for listener in ConnectionManager.listeners:
                if listener.event_type == event_type:
                    listener.recieve_message(message=message)

    def resize_memory(self, canvas_bytes_len):
        print("unlink")
        self.shm.unlink()
        self.shm.close()
        asyncio.run(self.request({"type": "CLOSE_MEMORY", "data": ""}))
        try:
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=True, size=canvas_bytes_len)
            print("memory  created")
        except:
            print("file exists, trying another way")
            self.shm = shared_memory.SharedMemory(
                name="krita-blender", create=False, size=canvas_bytes_len)
        asyncio.run(self.request({"type": "RECREATE_MEMORY", "data": ""}))

#  def on_disconnect():
#   print("disconnected from blender")

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
        self.shm.buf[:len(bts)] = bts

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
                    if msg['requestId'] == self.requestId:
                        future.cancel()

                def on_success(msg):
                    print("future success")
                    event_loop.call_soon_threadsafe(future.set_result, msg)
                failure_listener = MessageListener(
                    "nop", on_nop)
                success_listener = MessageListener(
                    payload['type'], on_success)
                future.add_done_callback(lambda fut: (
                    failure_listener.destroy(), success_listener.destroy()))
                self.send_message(payload)
                print("future before")

            await asyncio.create_task(chuj())
            res = await asyncio.wait_for(future, 1.0)
            print("future done")
            return res
        return None


def override_image(image, conn_manager):
    doc = Krita.instance().activeDocument()
    size = [doc.width(), doc.height()]
    ConnectionManager.linked_document = doc
    print(size, "memsize", conn_manager.shm.size, size[0]*size[1]*16)
    # if size[0]*size[1]*16 > conn_manager.shm.size:
    print("resizing")
    conn_manager.resize_memory(size[0]*size[1]*16)
    asyncio.run(conn_manager.request(
                {"data": image, "type": "OVERRIDE_IMAGE"}))
    asyncio.run(conn_manager.request(
                {"data": "", "type": "GET_IMAGES"}))
