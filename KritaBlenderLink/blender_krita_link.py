import time
import typing
from krita import *
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import (
    QPushButton,
    QStatusBar,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QWidget,
    QSpinBox,
    QFrame,
    QScrollArea,
    QMessageBox,
    QMainWindow,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QListWidget,
    QListView,
    QLayout
)
from threading import Timer, Thread
import json
from .connection import ConnectionManager, MessageListener
from .ui.ImageList import ImageList
import asyncio

DOCKER_TITLE = 'Blender Krita Link'


class BlenderKritaLink(DockWidget):
    settings = {}
    listen_to_canvas_change = True
    connection = None

    def __init__(self):
        super().__init__()
        self.init_settings()
        self.connection = ConnectionManager()
        appNotifier = Krita.instance().notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(self.listen)
        self.setupUi()
        asyncio.run(self.connection.request({type: "GET_IMAGES  "}))

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
            self.dockWidgetContents.sizePolicy().hasHeightForWidth())
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
            self.verticalFrame.sizePolicy().hasHeightForWidth())
        self.verticalFrame.setSizePolicy(sizePolicy)
        self.verticalFrame.setFrameShape(QFrame.NoFrame)
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.connectedLabel = QLabel(
            "Connection status: innactive", self.verticalFrame)
        self.connectedLabel.setObjectName("connected Label")
        self.verticalLayout.addWidget(self.connectedLabel)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ConnectButton = QPushButton("Connect", self.verticalFrame,)
        self.ConnectButton.setObjectName("ConnectButton")
        self.horizontalLayout_2.addWidget(self.ConnectButton)
        self.DisconnectButton = QPushButton("Disconnect", self.verticalFrame)
        self.DisconnectButton.setObjectName("DisconnectButton")
        self.horizontalLayout_2.addWidget(self.DisconnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.RefreshButton = QPushButton("Refresh", self.verticalFrame)
        self.RefreshButton.setObjectName("RefreshButton")
        self.verticalLayout.addWidget(self.RefreshButton)
        self.SendDataButton = QPushButton("Send data", self.verticalFrame)
        self.SendDataButton.setObjectName("SendDataButton")
        self.verticalLayout.addWidget(self.SendDataButton)
        self.canvasListenCheckbox = QCheckBox(text="Update on drawing?")
        self.canvasListenCheckbox.setCheckState(self.settings['listenCanvas'])
        self.canvasListenCheckbox.setTristate(False)
        self.canvasListenCheckbox.stateChanged.connect(self.on_listen_change)
        self.verticalLayout.addWidget(self.canvasListenCheckbox)

        # self.imagesFrame = QWidget(self.dockWidgetContents)
        # self.imagesFrame.setEnabled(True)
        # self.imagesFrame.setSizePolicy(sizePolicy)
        # # self.imagesFrame.setFrameShape(QFrame.NoFrame)
        # self.imagesFrame.setObjectName("imagesFrame")
        # self.imagesFrame.layout = QVBoxLayout()
        self.list = ImageList(parent=self.verticalFrame)
        self.verticalLayout.addWidget(self.list)
        self.getImageDataButton = QPushButton(
            "Refresh Images", self.verticalFrame)
        self.getImageDataButton.setObjectName("getImageDataButton")

        self.verticalLayout.addWidget(self.getImageDataButton)

        spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(spacerItem)
        self.dockWidgetContents.layout().addWidget(self.verticalFrame)
        self.setWidget(self.dockWidgetContents)

        self.ConnectButton.clicked.connect(self.connect_blender)
        self.DisconnectButton.clicked.connect(self.connection.disconnect)
        self.RefreshButton.clicked.connect(self.listen)
        self.SendDataButton.clicked.connect(self.send_pixels)
        self.getImageDataButton.clicked.connect(self.get_image_data)

    def connect_blender(self):
        doc = Krita.instance().activeDocument()
        doc.refreshProjection()  # update canvas on screen
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        self.connection.connect(len(pixelBytes), lambda: self.connectedLabel.setText(
            "Connection status: blender connected"), lambda: self.connectedLabel.setText("Connection status: blender disconnected"))
        print("bytes count: ", len(pixelBytes))

    def get_image_data(self):
        dupa = asyncio.run(self.connection.request({"type": "GET_IMAGES"}))
        self.list.refresh_signal.emit(dupa['data'])
        # self.connection.send_message({"type": "GET_IMAGES"})

    def refresh_document(self, doc):
        root_node = doc.rootNode()
        if root_node and len(root_node.childNodes()) > 0:
            test_layer = doc.createNode("DELME", "paintLayer")
            root_node.addChildNode(test_layer, root_node.childNodes()[0])
            # QtCore.QTimer.singleShot(200, lambda: test_layer.remove() )
            test_layer.remove()

    def send_pixels(self):
        t = time.time()
        doc = Krita.instance().activeDocument()
        print("get doc time: ", time.time() - t)
        # self.refresh_document(doc)
        # doc.refreshProjection()
        print("refresh time: ", time.time() - t)
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        # self.connection.send_message(bytes(pixelBytes.data())[:])
        print("pixelbytes time: ", time.time() - t)

        def write_mem():
            self.connection.write_memory(pixelBytes)
            print("write memory time: ", time.time() - t)
            self.connection.send_message("refresh")
            print("send message time: ", time.time() - t)
        t1 = Thread(target=write_mem)
        t1.start()

    def init_settings(self):
        x = Krita.instance().readSetting("", "blenderKritaSettings", "")
        print(x)
        if not x:
            self.settings = {"listenCanvas": True}
            Krita.instance().writeSetting("", "blenderKritaSettings", json.dumps(self.settings))
        else:
            self.settings = json.loads(x)

    def save_settings(self):
        print(self.settings)
        if not self.settings:
            self.settings = {"listenCanvas": True}
        Krita.instance().writeSetting("", "blenderKritaSettings", json.dumps(self.settings))

    def on_listen_change(self, checked):
        print(checked)
        self.settings['listenCanvas'] = checked == 2
        self.save_settings()

    def listen(self):
        QtWidgets.qApp.installEventFilter(self)
        Krita.instance().action('edit_undo').triggered.connect(
            lambda x: self.onUpdateImage())
        Krita.instance().action('edit_redo').triggered.connect(
            lambda x: self.onUpdateImage())

    def on_data_send(self):
        self.send_pixels()

    def onUpdateImage(self):
        if not self.settings['listenCanvas']:
            return
        t = Timer(0.25, self.on_data_send)
        # t = Timer(0,self.chuj)
        t.start()

    def canvasChanged(self, canvas):
        print("something Happened")
        pass

    def eventFilter(self, obj, event):
        if isinstance(obj, QOpenGLWidget):
            if event.type() == 3 and event.button() == 1:
                print(obj, type(obj).__bases__)
                self.onUpdateImage()
                print("painted Something on", event.type(), event.button())
        return False
