from KritaBlenderLink.uvs_viewer import UvOverlay, get_q_view
from krita import Krita, DockWidget, QOpenGLWidget, QtCore, Notifier
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFrame,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QLayout,
    QDockWidget,
    QColorDialog
)
from PyQt5.QtCore import (
    QObject,
    QEvent
)
from PyQt5.QtGui import QColor
from threading import Timer, Thread
import asyncio
from .connection import ConnectionManager, MessageListener, change_memory, format_message
from .ui.ImageList import ImageList
from .settings import Settings
from .ImageState import ImageState
from PyQt5 import uic
import os as os
from PyQt5 import sip

DOCKER_TITLE = "Blender Krita Link"


class ClickFilter(QObject):
    def __init__(self, function):
        super().__init__()
        self.function = function

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.function:  # Sprawdź, czy funkcja została przekazana
                self.function()  # Wywołaj funkcję
            return True  # Zatrzymaj propagację zdarzenia
        return super().eventFilter(obj, event)


class BlenderKritaLink(DockWidget):
    listen_to_canvas_change = True
    connection = None
    advancedRefresh = 0  # 0 1 2 0-off 1-on 2-full

    def __init__(self):
        super().__init__()

        print(Settings.getSetting("listenCanvas"))
        self.connection = ConnectionManager()
        self.avc_connected = False
        ImageState.instance.onImageDataChange.connect(
            lambda x: [change_memory(self.connection),
                       print("image file changed")]
        )
        ImageState.instance.onPixelsChange.connect(
            lambda x: self.on_update_image() and print("drawed smh")
        )
        app_notifier: Notifier = Krita.instance().notifier()

        app_notifier.imageClosed.connect(lambda: print("image Closed"))
        app_notifier.imageCreated.connect(lambda: print("image Created"))

        app_notifier.viewCreated.connect(lambda: print("view Created"))
        app_notifier.windowCreated.connect(lambda: print("window Created"))
        app_notifier.applicationClosing.connect(lambda: print("app closing"))

        self.setWindowTitle("Blender Krita Link")
        self.central_widget = uic.loadUi(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "BlenderKritaLinkUI.ui"))
        self.setWidget(self.central_widget)

        self.central_widget.SendOnDrawCheckbox.setCheckState(
            2 if Settings.getSetting("listenCanvas") else 0)
        self.central_widget.SendOnDrawCheckbox.stateChanged.connect(
            self.on_listen_change)

        def on_uv_show(state):
            print("uvshow changed", state)
            Settings.setSetting("showUVs", state == 2)
            for uo in UvOverlay.INSTANCES_SET:
                if not sip.isdeleted(uo):
                    uo.update()

        self.central_widget.ShowUVCheckbox.setCheckState(
            2 if Settings.getSetting("showUVs") else 0)
        self.central_widget.ShowUVCheckbox.stateChanged.connect(on_uv_show)

        def open_color_dialog():
            color = QColorDialog.getColor(initial=QColor(Settings.getSetting(
                "uvColor")), options=QColorDialog.ColorDialogOption.ShowAlphaChannel)
            UvOverlay.COLOR = color
            self.central_widget.UVColorButton.setStyleSheet(
                f"background-color: {color.name(QColor.NameFormat.HexArgb)};border: 2px solid #000000;")
            Settings.setSetting("uvColor", color.name(
                QColor.NameFormat.HexArgb))

        self.filter = ClickFilter(open_color_dialog)
        c = QColor(Settings.getSetting("uvColor"))
        self.central_widget.UVColorButton.setStyleSheet(
            f"background-color: {c.name(QColor.NameFormat.HexArgb)};border: 2px solid #000000;")
        # self.centralWidget.UVColorButton.clicked.connect(openColorDialog)
        self.central_widget.UVColorButton.installEventFilter(self.filter)

        self.central_widget.ConnectButton.clicked.connect(self.connect_blender)
        self.central_widget.DisconnectButton.clicked.connect(
            self.connection.disconnect)
        self.central_widget.SendDataButton.clicked.connect(self.send_pixels)
        self.central_widget.RefreshImagesButton.clicked.connect(
            self.get_image_data)
        self.central_widget.ImageTosRGBButton.clicked.connect(
            self.image_to_srgb)
        self.central_widget.SelectUVIslandsButton.clicked.connect(
            self.select_uvs)
        self.central_widget.UVOverlayButton.clicked.connect(self.get_uv_overlay)

        ImageList(parent=self.central_widget.ImagesFrame,
                  con_manager=self.connection)
        self.central_widget.ImagesFrame.layout().addWidget(ImageList.instance)

        app_notifier.viewCreated.connect(self.attach_uv_viewer)

        print(self.central_widget, self.central_widget.ConnectButton)
        print(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "BlenderKritaLinkUI.ui"))

        MessageListener("SELECT_UVS", self.handle_uv_response)
        MessageListener("GET_UV_OVERLAY", self.handle_uv_overlay)

    def connect_blender(self):
        doc = Krita.instance().activeDocument()
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        self.connection.connect(
            len(pixelBytes),
            self.on_blender_connected,
            lambda: (
                self.central_widget.ConnectionStatus.setText(
                    "Connection status: blender disconnected",
                ),
                ImageList.instance.clear_signal.emit(),
            ),
        )
        print("bytes count: ", len(pixelBytes))
        win = Krita.instance().activeWindow().qwindow()
        if not self.avc_connected:
            win.activeViewChanged.connect(self.active_view_changed)
            print("connected krita to blender")
        self.avc_connected = True

    def on_blender_connected(self):
        self.central_widget.ConnectionStatus.setText(
            "Connection status: blender connected")
        Thread(target=self.get_image_data).start()

    def get_image_data(self):
        if self.connection.connection == None:
            return
        images = asyncio.run(self.connection.request({"type": "GET_IMAGES"}))
        ImageList.instance.refresh_signal.emit(images["data"])

    def refresh_document(self,doc):
        root_node = doc.rootNode()
        if root_node and len(root_node.childNodes()) > 0:
            test_layer = doc.createNode("DELME", "paintLayer")
            root_node.addChildNode(test_layer, root_node.childNodes()[0])
            test_layer.remove()

    def send_pixels(self):
        doc = Krita.instance().activeDocument()
        linked_doc = self.connection.linked_document
        print(doc, linked_doc)
        if doc != linked_doc or not linked_doc:
            return

        print(self.connection.get_active_image()[
              "size"], [doc.width(), doc.height()])

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

    def on_update_image(self):
        print(Settings.getSetting("listenCanvas"))
        if not Settings.getSetting("listenCanvas"):
            return
        t = Timer(0.25, self.send_pixels)
        t.start()

    def canvasChanged(self, canvas):
        print("something Happened")

    def active_view_changed(self):
        print("active view changed")
        self.get_image_data()
        self.attach_uv_viewer()

    def attach_uv_viewer(self):
        active_window = Application.activeWindow()
        active_view = active_window.activeView()
        if active_view.window() is None:
            return
        qv = get_q_view(active_view)
        if qv is None:
            return
        print("active window: ", qv)
        print(qv.findChild(UvOverlay))
        overlay = qv.findChild(UvOverlay, "UVOVERLAY")
        if overlay is not None:
            for ov in UvOverlay.INSTANCES_SET:
                if not sip.isdeleted(ov):
                    ov.update_stuff()
            return
        if active_view.document() is None:
            raise RuntimeError('Document of active view is None!')
        my_overlay = UvOverlay(active_view)
        my_overlay.show()

    def image_to_srgb(self):
        Krita.instance().action("image_properties").trigger()

    def select_uvs(self):
        uvs = asyncio.run(self.connection.request({"type": "SELECT_UVS"}))
        print(format_message(uvs))

    def get_uv_overlay(self):
        self.attach_uv_viewer()
        asyncio.run(self.connection.request({"type": "GET_UV_OVERLAY"}))

    def handle_uv_response(self, message):
        # print("handle uvs triggered", message)
        action = Krita.instance().action("select_shapes")
        width_height = [Krita.instance().activeDocument(
        ).width(), Krita.instance().activeDocument().height()]
        faces = message['data']
        # UvOverlay.set_polygons(faces)

        if action != None:
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
        UvOverlay.set_polygons(message['data'])
