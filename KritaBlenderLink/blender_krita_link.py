from krita import Extension
from threading import Timer, Thread
import os as os
import asyncio
from KritaBlenderLink.uvs_viewer import UvOverlay, get_q_view
from .connection import (
    ConnectionManager,
    MessageListener,
    change_memory,
    format_message,
)
from PyQt5 import uic, sip
from .ui.ImageList import ImageList
from .settings import Settings
from .ImageState import ImageState
from krita import Krita, DockWidget, Notifier
from PyQt5.QtWidgets import QColorDialog, QLineEdit, QSpinBox
from PyQt5.QtCore import QObject, QEvent, QTimer
from PyQt5.QtGui import QColor
import time

DOCKER_TITLE = "Blender Krita Link"


class Debouncer:
    def __init__(self, fn, time, non_debounced=lambda: None) -> None:
        self.fn = fn
        self.time = time
        self.last_time = 0
        self.finished = True
        self.non_debounced = non_debounced

    def cal(self):
        time_now = time.time()
        print("cal called", time_now, time.time())
        self.non_debounced()
        if time_now - self.last_time > self.time:

            def execute():
                if self.finished:
                    try:
                        self.finished = False
                        self.last_time = time_now
                        self.fn()
                    finally:
                        self.finished = True
                        print("finished", time_now, time.time())
                    
            if self.finished:
                execute()
                return

            t = Timer(self.time, execute)
            t.start()


class ClickFilter(QObject):
    def __init__(self, function):
        super().__init__()
        self.function = function

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.function:
                self.function()
            return True
        return super().eventFilter(obj, event)


class BlenderKritaLinkExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        window.createAction("sendImage")
        window.createAction("refreshUVs")
        window.createAction("UVsToggleOnOff")


class BlenderKritaLink(DockWidget):
    listen_to_canvas_change = True
    connection = None
    advancedRefresh = 0 # 0 1 2 0-off 1-on 2-full

    def __init__(self):
        super().__init__()
        print("Docker init!!!")
        print(Settings.getSetting("listenCanvas"))
        self.connection = ConnectionManager()
        self.avc_connected = False
        ImageState.instance.onImageDataChange.connect(
            lambda x: [change_memory(self.connection), print("image file changed")]
        )
        ImageState.instance.onPixelsChange.connect(
            lambda x: self.on_update_image(x) and print("drawed smh")
        )
        app_notifier: Notifier = Krita.instance().notifier()

        app_notifier.imageClosed.connect(lambda: print("image Closed"))
        app_notifier.imageCreated.connect(lambda: print("image Created"))

        app_notifier.viewCreated.connect(lambda: print("view Created"))
        app_notifier.windowCreated.connect(lambda: print("window Created"))
        app_notifier.applicationClosing.connect(lambda: print("app closing"))

        self.setWindowTitle("Blender Krita Link")
        self.central_widget = uic.loadUi(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "BlenderKritaLinkUI.ui"
            )
        )
        self.setWidget(self.central_widget)

        self.central_widget.SendOnDrawCheckbox.setCheckState(
            2 if Settings.getSetting("listenCanvas") else 0
        )
        self.central_widget.SendOnDrawCheckbox.stateChanged.connect(
            self.on_listen_change
        )

        def on_uv_show(state):
            print("uvshow changed", state)
            Settings.setSetting("showUVs", state == 2)
            for uo in UvOverlay.INSTANCES_SET:
                if not sip.isdeleted(uo):
                    uo.update()

        self.central_widget.ShowUVCheckbox.setCheckState(
            2 if Settings.getSetting("showUVs") else 0
        )
        self.central_widget.ShowUVCheckbox.stateChanged.connect(on_uv_show)

        def open_color_dialog():
            color = QColorDialog.getColor(
                initial=QColor(Settings.getSetting("uvColor")),
                options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
            )
            UvOverlay.COLOR = color
            self.central_widget.UVColorButton.setStyleSheet(
                f"background-color: {color.name(QColor.NameFormat.HexArgb)};border: 2px solid #000000;"
            )
            Settings.setSetting("uvColor", color.name(QColor.NameFormat.HexArgb))

        self.filter = ClickFilter(open_color_dialog)
        c = QColor(Settings.getSetting("uvColor"))
        self.central_widget.UVColorButton.setStyleSheet(
            f"background-color: {c.name(QColor.NameFormat.HexArgb)};border: 2px solid #000000;"
        )

        def on_port_change(text):
            try:
                new_port = int(text)
                print(f"{ConnectionManager.connection} {new_port} {ConnectionManager.port}")
                if new_port != ConnectionManager.port:
                    self.connection.disconnect()
                    print("disconnecting")
                ConnectionManager.port = new_port 
            except Exception:
                ConnectionManager.port = 65431
            if ConnectionManager.port > 65533:
                ConnectionManager.port = 65431
            Settings.setSetting("port",ConnectionManager.port)
            print(f"port changed to: + {ConnectionManager.port}")

        self.central_widget.connection_port.setText(f"{ConnectionManager.port if Settings.getSetting('port') is None else Settings.getSetting('port')}")
        self.central_widget.connection_port.textChanged.connect(on_port_change)
        
        def on_width_change(number):
            Settings.setSetting("uv_width",number)
        
        # QSpinBox().setValue(Settings.setSetting("uv_width"))
        self.central_widget.uv_width.setValue(1 if Settings.getSetting("uv_width") is None else Settings.getSetting("uv_width"))
        self.central_widget.uv_width.valueChanged.connect(on_width_change)

        self.select_uvs_debouncer = Debouncer(self.select_uvs, 0.2)
        self.uv_overlay_debouncer = Debouncer(
            self.get_uv_overlay, 0.2, self.attach_uv_viewer
        )
        self.send_pixels_debouncer = Debouncer(self.send_pixels, 0.2)

        # self.centralWidget.UVColorButton.clicked.connect(openColorDialog)
        self.central_widget.UVColorButton.installEventFilter(self.filter)
        self.central_widget.ConnectButton.clicked.connect(self.connect_blender)
        self.central_widget.DisconnectButton.clicked.connect(self.connection.disconnect)
        self.central_widget.SendDataButton.clicked.connect(
            self.send_pixels_debouncer.cal
        )
        self.central_widget.RefreshImagesButton.clicked.connect(self.get_image_data)
        self.central_widget.ImageTosRGBButton.clicked.connect(self.image_to_srgb)
        self.central_widget.SelectUVIslandsButton.clicked.connect(
            self.select_uvs_debouncer.cal
        )
        self.central_widget.UVOverlayButton.clicked.connect(
            self.uv_overlay_debouncer.cal
        )

        ImageList(parent=self.central_widget.ImagesFrame, con_manager=self.connection)
        self.central_widget.ImagesFrame.layout().addWidget(ImageList.instance)

        app_notifier.viewCreated.connect(self.attach_uv_viewer)
        app_notifier.viewCreated.connect(self.attach_shortcuts_listeners)

        print(self.central_widget, self.central_widget.ConnectButton)
        print(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "BlenderKritaLinkUI.ui"
            )
        )

        def image_search_change(text:str):
            print("search change",text)
            ImageList.instance.update_images_list(ImageList.image_list,text)

        self.central_widget.image_search.textChanged.connect(image_search_change)
        self.last_send_pixels_time = 0
        MessageListener("SELECT_UVS", self.handle_uv_response)
        MessageListener("GET_UV_OVERLAY", self.handle_uv_overlay)

        attach_watch = QTimer(self)
        attach_watch.setInterval(300)
        attach_watch.timeout.connect(self.attach_uv_viewer)
        attach_watch.start()

    def attach_shortcuts_listeners(self):
        print("onviewcreated, attaching shortcuts listeners...")

        def uv_show_toggle(_):
            toggled_state = not Settings.getSetting("showUVs")
            Settings.setSetting("showUVs", toggled_state)
            self.central_widget.ShowUVCheckbox.setCheckState(2 if toggled_state else 0)
            for uo in UvOverlay.INSTANCES_SET:
                if not sip.isdeleted(uo):
                    uo.update()

        Krita.instance().action("UVsToggleOnOff").triggered.connect(uv_show_toggle)
        Krita.instance().action("sendImage").triggered.connect(
            self.send_pixels_debouncer.cal
        )
        Krita.instance().action("refreshUVs").triggered.connect(
            self.uv_overlay_debouncer.cal
        )

    def connect_blender(self):
        self.connection.connect(
            self.on_blender_connected,
            lambda: (
                self.central_widget.ConnectionStatus.setText(
                    "Connection status: blender disconnected",
                ),
                UvOverlay.set_polygons([]),
                ImageList.instance.clear_signal.emit(),
            ),
        )
        win = Krita.instance().activeWindow().qwindow()
        if not self.avc_connected:
            win.activeViewChanged.connect(self.active_view_changed)
            print("connected krita to blender")
        self.avc_connected = True

    def on_blender_connected(self):
        self.central_widget.ConnectionStatus.setText(
            "Connection status: blender connected"
        )
        Thread(target=self.get_image_data).start()

    def get_image_data(self):
        if self.connection is None or self.connection.connection is None:
            return 
        print("get_image_data log:  ",self.connection.linked_document, self.connection.linked_document in Krita.instance().documents())
        if self.connection.linked_document not in Krita.instance().documents():
            self.connection.remove_link()
        images = asyncio.run(self.connection.request({"type": "GET_IMAGES"}))
        ImageList.instance.refresh_signal.emit(images["data"])

    def refresh_document(self, doc):
        root_node = doc.rootNode()
        if root_node and len(root_node.childNodes()) > 0:
            root_node.setBlendingMode(root_node.blendingMode())
            # test_layer = doc.createNode("DELME", "paintLayer")
            # root_node.addChildNode(test_layer, root_node.childNodes()[0])
            # test_layer.remove()

    def send_pixels(self):
        doc = Krita.instance().activeDocument()
        linked_doc = self.connection.linked_document
        print(doc, linked_doc)
        if doc != linked_doc or not linked_doc:
            return

        print(self.connection.get_active_image()["size"], [doc.width(), doc.height()])

        if self.connection.get_active_image()["size"] != [doc.width(), doc.height()]:
            self.connection.remove_link()
            return
        if self.advancedRefresh == 1:
            self.refresh_document(doc)
        elif self.advancedRefresh == 2:
            doc.refreshProjection()

        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())

        def write_mem():
            self.connection.write_memory(pixelBytes)
            depth = Krita.instance().activeDocument().colorDepth()
            self.connection.send_message(
                {"type": "REFRESH", "depth": depth, "requestId": 2137}
            )

        Thread(target=write_mem).start()

    def on_listen_change(self, checked):
        print("draw Listen changed", checked)
        Settings.setSetting("listenCanvas", checked == 2)

    def on_update_image(self, x):
        print(Settings.getSetting("listenCanvas"))
        if not Settings.getSetting("listenCanvas"):
            return
        if x["paint"]:
            self.send_pixels_debouncer.cal()
        else:
            t = Timer(0.25, self.send_pixels_debouncer.cal)
            t.start()

    def canvasChanged(self, canvas):
        print("something Happened")

    def active_view_changed(self):
        print("active view changed")
        self.get_image_data()
        self.attach_uv_viewer()

    def attach_uv_viewer(self):
        active_window = Application.activeWindow()  # noqa: F821
        active_view = active_window.activeView()
        if active_view.window() is None:
            return
        qv = get_q_view(active_view)
        if qv is None:
            return
        overlay = qv.findChild(UvOverlay, "UVOVERLAY")
        # print("attach call!!!!")
         
        if overlay is not None:
            # for ov in UvOverlay.INSTANCES_SET:
            #     if not sip.isdeleted(ov):
            #         ov.update_stuff()
            return

        # print("active window: ", qv)
        # print(qv.findChild(UvOverlay))
        if active_view.document() is None:
            raise RuntimeError("Document of active view is None!")
        my_overlay = UvOverlay(active_view)
        my_overlay.show()

    def image_to_srgb(self):
        Krita.instance().action("image_properties").trigger()

    def select_uvs(self):
        uvs = asyncio.run(self.connection.request({"type": "SELECT_UVS"}))
        print(format_message(uvs))

    def get_uv_overlay(self):
        asyncio.run(self.connection.request({"type": "GET_UV_OVERLAY"}))

    def handle_uv_response(self, message):
        # print("handle uvs triggered", message)
        action = Krita.instance().action("select_shapes")
        width_height = [
            Krita.instance().activeDocument().width(),
            Krita.instance().activeDocument().height(),
        ]
        faces = message["data"]
        # UvOverlay.set_polygons(faces)

        if action is not None:
            print("action exists")
            for g in faces:
                for f in g:
                    f[0] *= width_height[0]
                    f[1] *= width_height[1]
            action.setData(faces)
            action.trigger()
            action.setData([])

    def handle_uv_overlay(self, message):
        print("handle_uv_overlay")
        UvOverlay.set_polygons(message["data"])
        for ov in UvOverlay.INSTANCES_SET:
            if not sip.isdeleted(ov):
                ov.update_stuff()
