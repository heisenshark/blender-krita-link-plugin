"""Run with blender --background --factory-startup --python tests/blender_runtime_check.py."""
from multiprocessing import shared_memory
from pathlib import Path
import sys
import threading
import time
from multiprocessing.connection import Client

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import BlenderKritaLink as addon
from BlenderKritaLink.connection import KritaConnection
from BlenderKritaLink.image_manager import ImageManager

manager = ImageManager()
image = bpy.data.images.new("BKL test", width=1, height=1, float_buffer=True)
try:
    # Krita's integer buffers are BGRA. Updating must not mutate the source buffer.
    source = np.array([0, 32768, 65535, 65535], dtype=np.uint16)
    manager.update_image(source, image.name)
    np.testing.assert_array_equal(source, [0, 32768, 65535, 65535])
    np.testing.assert_allclose(list(image.pixels), [1, 32768 / 65535, 0, 1], atol=0.004)

    port = 59483
    KritaConnection.PORT = port
    memory = shared_memory.SharedMemory(name=f"blender-krita{port}", create=True, size=8)
    try:
        image.pixels.foreach_set(np.array([1, 0.5, 0, 1], dtype=np.float32))
        KritaConnection().export_image({"data": {"image": {"name": image.name}, "depth": "U16"}})
        actual = np.frombuffer(memory.buf, dtype=np.uint16).copy()
        np.testing.assert_allclose(actual, [0, 32768, 65535, 65535], atol=1)
    finally:
        memory.unlink()
        memory.close()
    KritaConnection.LINK_INSTANCE = None
    KritaConnection.PORT = 59484
    connection = KritaConnection()
    connection.start()
    result = []
    def client():
        for _ in range(100):
            try:
                peer = Client(("localhost", 59484), authkey=b"2137")
                break
            except ConnectionRefusedError:
                time.sleep(0.02)
        else:
            return
        with peer:
            peer.send({"type": "GET_IMAGES", "requestId": 42})
            if peer.poll(3):
                result.append(peer.recv())
    thread = threading.Thread(target=client)
    try:
        thread.start()
        deadline = time.monotonic() + 4
        while thread.is_alive() and time.monotonic() < deadline:
            connection.process_pending_messages()
            time.sleep(0.01)
        thread.join(timeout=1)
        assert result and result[0]["requestId"] == 42
        assert any(item["name"] == image.name for item in result[0]["data"])
    finally:
        connection.cleanup()
        KritaConnection.LINK_INSTANCE = None
    addon.register()
    addon.unregister()
    addon.register()
    addon.unregister()
    print("PASS: U16 round trip, queued connection, and repeated add-on registration")
finally:
    bpy.data.images.remove(image)
