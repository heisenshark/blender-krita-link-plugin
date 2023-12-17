from krita import Krita, DockWidget, QtWidgets, QOpenGLWidget, QtCore
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
from .connection import ConnectionManager
from .ui.ImageList import ImageList
from .settings import Settings

DOCKER_TITLE = "Blender Krita Link"


class BlenderKritaLink(DockWidget):
    listen_to_canvas_change = True
    connection = None
    advancedRefresh = 0  # 0 1 2 0-off 1-on 2-full

    def __init__(self):
        super().__init__()
        print(Settings.getSetting("listenCanvas"))
        self.connection = ConnectionManager()
        appNotifier = Krita.instance().notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(self.listen)
        self.avc_connected = False
        self.setupUi()

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

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(spacerItem)
        self.dockWidgetContents.layout().addWidget(self.verticalFrame)
        self.setWidget(self.dockWidgetContents)

        self.ConnectButton.clicked.connect(self.connect_blender)
        self.DisconnectButton.clicked.connect(self.connection.disconnect)
        self.SendDataButton.clicked.connect(self.send_pixels)
        self.getImageDataButton.clicked.connect(self.get_image_data)

    def connect_blender(self):
        doc = Krita.instance().activeDocument()
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        self.connection.connect(
            len(pixelBytes),
            self.on_blender_connected,
            lambda: self.connectedLabel.setText(
                "Connection status: blender disconnected"
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
        if doc != self.connection.linked_document:
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
        print(checked)
        Settings.setSetting("listenCanvas", checked == 2)

    def on_data_send(self):
        self.send_pixels()

    def onUpdateImage(self):
        if not Settings.getSetting("listenCanvas"):
            return

        t = Timer(0.25, self.on_data_send)
        t.start()

    def listen(self):
        QtWidgets.qApp.installEventFilter(self)

        Krita.instance().action("edit_undo").triggered.connect(
            lambda x: self.onUpdateImage()
        )
        Krita.instance().action("edit_redo").triggered.connect(
            lambda x: self.onUpdateImage()
        )
        Krita.instance().action("image_properties").triggered.connect(
            lambda x: print("properties clicked/changed")
        )
        Krita.instance().action("KritaShape/KisToolBrush").triggered.connect(
            lambda x: print("omg - brush did brushing")
        )

    def canvasChanged(self, canvas):
        print("something Happened")

    def active_view_changed(self):
        print("active view changed")
        self.get_image_data()

    def eventFilter(self, obj, event):
        if isinstance(obj, QOpenGLWidget):
            if event.type() == 3 and event.button() == 1:
                print(obj, type(obj).__bases__)
                self.onUpdateImage()
                print("painted Something on", event.type(), event.button())
        return False
