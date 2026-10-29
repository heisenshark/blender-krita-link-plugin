import ast
import asyncio
import importlib
import logging
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_connection():
    package = types.ModuleType("KritaBlenderLink")
    package.__path__ = [str(ROOT / "KritaBlenderLink")]
    settings = types.ModuleType("KritaBlenderLink.settings")
    settings.Settings = types.SimpleNamespace(getSetting=lambda name: None)
    lb = types.ModuleType("KritaBlenderLink.lb")
    lb.shared_memory_context = None
    logger = types.ModuleType("KritaBlenderLink.logger")
    logger.logger = logging.getLogger("test")
    logger.configure_logger = lambda port: None
    krita = types.ModuleType("krita")
    krita.Krita = object
    modules = {"KritaBlenderLink": package, "KritaBlenderLink.settings": settings,
               "KritaBlenderLink.lb": lb, "KritaBlenderLink.logger": logger, "krita": krita}
    with patch.dict(sys.modules, modules):
        return importlib.import_module("KritaBlenderLink.connection")


class RequestTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_requests_ignore_unsolicited_and_match_ids(self):
        module = load_connection()
        module.ConnectionManager.listeners = []
        manager = module.ConnectionManager()
        manager.connection = True
        sent = []
        manager.send_message = lambda msg: sent.append(dict(msg))
        first = asyncio.create_task(manager.request({"type": "GET_IMAGES"}))
        second = asyncio.create_task(manager.request({"type": "GET_IMAGES"}))
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        manager.emit_message({"type": "GET_IMAGES", "requestId": -1, "data": []})
        manager.emit_message({"type": "GET_IMAGES", "requestId": sent[1]["requestId"], "data": [2]})
        manager.emit_message({"type": "GET_IMAGES", "requestId": sent[0]["requestId"], "data": [1]})
        self.assertEqual((await first)["data"], [1])
        self.assertEqual((await second)["data"], [2])

    async def test_nop_cancels_only_matching_request(self):
        module = load_connection()
        module.ConnectionManager.listeners = []
        manager = module.ConnectionManager()
        manager.connection = True
        sent = []
        manager.send_message = lambda msg: sent.append(dict(msg))
        task = asyncio.create_task(manager.request({"type": "MISSING"}))
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        manager.emit_message({"type": "nop", "requestId": sent[0]["requestId"], "data": None})
        with self.assertRaises(asyncio.CancelledError):
            await task


class RefreshTests(unittest.TestCase):
    def test_latest_update_waits_for_all_acknowledgements(self):
        tree = ast.parse((ROOT / "KritaBlenderLink/blender_krita_link.py").read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "BlenderKritaLink")
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in
                   {"send_pixels", "refresh_handle"}]
        module = ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name="Subject", bases=[], keywords=[],
                                                                           body=methods, decorator_list=[])], type_ignores=[]))
        class Doc:
            def width(self): return 1
            def height(self): return 1
            def colorDepth(self): return "U8"
            def pixelData(self, *args): return b"abcd"
        doc = Doc()
        class Connection:
            connection = True
            linked_images = {name: {"document": doc, "type": "document", "memoryObject": name}
                             for name in ("one", "two")}
            def __init__(self): self.messages = []; self.writes = []
            def get_image(self, name): return {"size": [1, 1]}
            def write_memory(self, pixels, memory): self.writes.append(memory)
            def send_message(self, message): self.messages.append(message)
        timer = types.SimpleNamespace(start=lambda delay: timer.calls.append(delay), calls=[])
        ns = {"Krita": types.SimpleNamespace(instance=lambda: types.SimpleNamespace(activeDocument=lambda: doc)),
              "logger": logging.getLogger("test")}
        exec(compile(module, "link", "exec"), ns)
        subject = ns["Subject"]()
        subject.connection = Connection()
        subject.refresh_in_flight = None
        subject.refresh_pending = False
        subject.next_refresh_id = -2
        subject.advancedRefresh = 0
        subject.send_pixels_timer = timer
        subject.send_pixels()
        subject.send_pixels()
        self.assertEqual(len(subject.connection.messages), 1)
        self.assertEqual(len(subject.connection.writes), 2)
        request_id = subject.connection.messages[0]["requestId"]
        subject.refresh_handle({"requestId": -99})
        subject.refresh_handle({"requestId": request_id})
        self.assertEqual(timer.calls, [])
        subject.refresh_handle({"requestId": request_id})
        self.assertEqual(timer.calls, [0])
        subject.send_pixels()
        self.assertEqual(len(subject.connection.messages), 2)


if __name__ == "__main__":
    unittest.main()
