from krita import Krita, DockWidget, QOpenGLWidget, QtCore
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
)
from threading import Timer, Thread
import asyncio
from .connection import ConnectionManager, MessageListener, change_memory
from .ui.ImageList import ImageList
from .settings import Settings
from .ImageState import ImageState

DOCKER_TITLE = "Blender Krita Link"


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
            lambda x: change_memory(self.connection) and print("image file changed")
        )
        ImageState.instance.onPixelsChange.connect(
            lambda x: self.on_update_image() and print("drawed smh")
        )
        self.setupUi()
        MessageListener("SELECT_UVS",lambda m: self.handle_uv_response(m))

    def setupUi(self):
        self.setWindowTitle(DOCKER_TITLE)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(DOCKER_TITLE)
        self.dockWidgetContents.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dockWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName("dockWidgetContents")

        self.horizontalLayout = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalFrame = QFrame(self.dockWidgetContents)
        self.verticalFrame.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.verticalFrame.sizePolicy().hasHeightForWidth()
        )
        self.verticalFrame.setSizePolicy(sizePolicy)
        self.verticalFrame.setFrameShape(QFrame.NoFrame)
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.connectedLabel = QLabel("Connection status: innactive", self.verticalFrame)
        self.connectedLabel.setObjectName("connected Label")
        self.verticalLayout.addWidget(self.connectedLabel)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ConnectButton = QPushButton(
            "Connect",
            self.verticalFrame,
        )
        self.ConnectButton.setObjectName("ConnectButton")
        self.horizontalLayout_2.addWidget(self.ConnectButton)
        self.DisconnectButton = QPushButton("Disconnect", self.verticalFrame)
        self.DisconnectButton.setObjectName("DisconnectButton")
        self.horizontalLayout_2.addWidget(self.DisconnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.SendDataButton = QPushButton("Send data", self.verticalFrame)
        self.SendDataButton.setObjectName("SendDataButton")
        self.verticalLayout.addWidget(self.SendDataButton)
        self.canvasListenCheckbox = QCheckBox(text="Update on drawing?")
        self.canvasListenCheckbox.setCheckState(Settings.getSetting("listenCanvas"))
        self.canvasListenCheckbox.setTristate(False)
        self.canvasListenCheckbox.stateChanged.connect(self.on_listen_change)
        self.verticalLayout.addWidget(self.canvasListenCheckbox)
        ImageList(parent=self.verticalFrame, con_manager=self.connection)
        self.verticalLayout.addWidget(ImageList.instance)
        self.getImageDataButton = QPushButton("Refresh Images", self.verticalFrame)
        self.getImageDataButton.setObjectName("getImageDataButton")

        self.verticalLayout.addWidget(self.getImageDataButton)

        self.colorSpaceLabel = QLabel("Please Use sRGB Color Space")
        self.colorSpaceLabel.setHidden(True)
        self.verticalLayout.addWidget(self.colorSpaceLabel)

        self.imageToSrgbButton = QPushButton("Current Image to sRGB", self.verticalFrame)
        self.verticalLayout.addWidget(self.imageToSrgbButton)

        self.selectUVs = QPushButton("Select Selected Uvs", self.verticalFrame)
        self.verticalLayout.addWidget(self.selectUVs)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(spacerItem)
        self.dockWidgetContents.layout().addWidget(self.verticalFrame)
        self.setWidget(self.dockWidgetContents)

        self.ConnectButton.clicked.connect(self.connect_blender)
        self.DisconnectButton.clicked.connect(self.connection.disconnect)
        self.SendDataButton.clicked.connect(self.send_pixels)
        self.getImageDataButton.clicked.connect(self.get_image_data)
        self.imageToSrgbButton.clicked.connect(self.image_to_srgb)
        self.selectUVs.clicked.connect(self.select_uvs)

        ImageState.instance.onSRGBColorSpace.connect(
            lambda matching: (
                self.colorSpaceLabel.setHidden(matching),
                print("kurwa kuwatwe: ", matching),
            )
        )

    def connect_blender(self):
        doc = Krita.instance().activeDocument()
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        self.connection.connect(
            len(pixelBytes),
            self.on_blender_connected,
            lambda: (
                self.connectedLabel.setText(
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
        self.connectedLabel.setText("Connection status: blender connected")
        Thread(target=self.get_image_data).start()

    def get_image_data(self):
        images = asyncio.run(self.connection.request({"type": "GET_IMAGES"}))
        ImageList.instance.refresh_signal.emit(images["data"])

    def refresh_document(doc):
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

    def on_update_image(self):
        if not Settings.getSetting("listenCanvas"):
            return

        t = Timer(0.25, self.send_pixels)
        t.start()

    def canvasChanged(self, canvas):
        print("something Happened")

    def active_view_changed(self):
        print("active view changed")
        self.get_image_data()

    def image_to_srgb(self):
        Krita.instance().action("image_properties").trigger()

    def select_uvs(self):
        uvs = asyncio.run(self.connection.request({"type": "SELECT_UVS"}))
        print(uvs)

    def handle_uv_response(self, message):
        print("handle uvs triggered", message)
        action = Krita.instance().action("select_shapes")
        width_height = [Krita.instance().activeDocument().width(),Krita.instance().activeDocument().height()]
        groups = message['data']
        if action != None:
            print("action exists")
            for g in groups:
                for f in g:
                    f[0] *= width_height[0]
                    f[1] *= width_height[1]
            action.setData(groups)
            action.trigger()
            action.setData([])
