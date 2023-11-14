import time
import typing
from krita import *
from PyQt5.QtCore import QSize,pyqtSignal
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
from threading import Timer,Thread
import json

from .connection import ConnectionManager

DOCKER_TITLE = 'Blender Krita Link'

class ImageItem(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName(u"ListItem")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy1)
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_9 = QLabel(text=text,parent=self)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_2.addWidget(self.label_9)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_3 = QPushButton("Open",self)
        self.pushButton_3.setObjectName(u"Open")
        self.pushButton_3.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Preferred)
        
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy2)
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.setLayout(self.horizontalLayout_2)

        # layout = QHBoxLayout(self)
        # self.title = QLabel("dupa")
        # self.label = QPushButton(text)
        # self.label.clicked.connect(self.on_button_click)
        # layout.addWidget(self.title)
        # layout.addWidget(self.label)
        # self.setLayout(layout)

    def on_button_click(self):
        print(f"Button clicked: {self.label.text()}")

class ImageList(QScrollArea):
    refresh_signal = pyqtSignal(object)
    l = []
        
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.image_list = ["Item 1", "Item 2", "Item 3", "Item 3", "Item 3", "Item 3", "Item 3"]
        self.setObjectName(u"ImageList")
        self.setObjectName("scrollArea")
        self.setMinimumSize(QSize(0, 100))
        self.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.setWidget(self.scrollAreaWidgetContents)
        
        
        for item_text in self.image_list:
            item = ImageItem(item_text,self.scrollAreaWidgetContents)
            # custom_item = QPushButton(item_text, self.scrollAreaWidgetContents)
            self.verticalLayout_2.addWidget(item)
            # self.verticalLayout.addWidget(custom_item)
        # Usuń wszystkie dzieci z głównego widżetu
                
        self.refresh_signal.connect(self.update_images_list)
        
    def update_images_list(self,images_list):
        print("update time")
        for i in reversed(range(self.verticalLayout_2.count())):
            widget_to_remove = self.verticalLayout_2.itemAt(i).widget()
            widget_to_remove.moveToThread(self.thread());
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()
        print("items removed", len(images_list))
        self.l.clear()
        for image in images_list:
            item = ImageItem(image['name'],self.scrollAreaWidgetContents)
            self.l.append(item)
            print("item created")
            self.verticalLayout_2.moveToThread(self.thread())
            self.verticalLayout_2.addWidget(item)
            print("item added")
        
        
            # custom_item = QPushButton(item_text, self.scrollAreaWidgetContents)



class BlenderKritaLink(DockWidget):
    settings = {}
    listen_to_canvas_change = True
    connection = None
    def __init__(self):
        super().__init__()
        self.init_settings()
        self.connection = ConnectionManager(self.message_callback)
        appNotifier = Krita.instance().notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(self.listen)
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
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        
        self.horizontalLayout = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.verticalFrame = QFrame(self.dockWidgetContents)
        self.verticalFrame.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalFrame.sizePolicy().hasHeightForWidth())
        self.verticalFrame.setSizePolicy(sizePolicy)
        self.verticalFrame.setFrameShape(QFrame.NoFrame)
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.connectedLabel = QLabel("Connection status: innactive",self.verticalFrame)
        self.connectedLabel.setObjectName("connected Label")
        self.verticalLayout.addWidget(self.connectedLabel)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ConnectButton = QPushButton("Connect",self.verticalFrame,)
        self.ConnectButton.setObjectName("ConnectButton")
        self.horizontalLayout_2.addWidget(self.ConnectButton)
        self.DisconnectButton = QPushButton("Disconnect",self.verticalFrame)
        self.DisconnectButton.setObjectName("DisconnectButton")
        self.horizontalLayout_2.addWidget(self.DisconnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.RefreshButton = QPushButton("Refresh",self.verticalFrame)
        self.RefreshButton.setObjectName("RefreshButton")
        self.verticalLayout.addWidget(self.RefreshButton)
        self.SendDataButton = QPushButton("Send data",self.verticalFrame)
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
        self.getImageDataButton = QPushButton("Refresh Images",self.verticalFrame)
        self.getImageDataButton.setObjectName("getImageDataButton")

        self.verticalLayout.addWidget(self.getImageDataButton)

        
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
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
        doc.refreshProjection() #update canvas on screen
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        self.connection.connect(len(pixelBytes), lambda: self.connectedLabel.setText("Connection status: blender connected"),  lambda: self.connectedLabel.setText("Connection status: blender disconnected"))    
        print("bytes count: ",len(pixelBytes))
    
    def get_image_data(self):
        self.connection.send_message({"type":"GET_IMAGES"})
    
    def refresh_document(self, doc):
        root_node = doc.rootNode()
        if root_node and len(root_node.childNodes())>0:
            test_layer = doc.createNode("DELME", "paintLayer")
            root_node.addChildNode(test_layer, root_node.childNodes()[0])
            # QtCore.QTimer.singleShot(200, lambda: test_layer.remove() )
            test_layer.remove()
    
    def send_pixels(self):
        t = time.time()
        doc = Krita.instance().activeDocument()
        print("get doc time: ",time.time() - t)
        # self.refresh_document(doc)
        # doc.refreshProjection()
        print("refresh time: ",time.time() - t)
        pixelBytes = doc.pixelData(0, 0, doc.width(), doc.height())
        # self.connection.send_message(bytes(pixelBytes.data())[:])
        print("pixelbytes time: ",time.time() - t)
        def write_mem():
            self.connection.write_memory(pixelBytes)    
            print("write memory time: ",time.time() - t)
            self.connection.send_message("refresh")
            print("send message time: ",time.time() - t)
        t1 = Thread(target=write_mem)
        t1.start()
        
        
        
    def message_callback(self,message):
        if isinstance(message, object) and "type" in message and 'data' in message:
            print(message)
            match message['type']:
                case "IMAGES_DATA":
                    self.list.refresh_signal.emit(message['data'])
                    # self.list.update_images_list(message['data'])
                case _: 
                    pass
    
    def init_settings(self):
        x= Krita.instance().readSetting("","blenderKritaSettings","")
        print(x)
        if not x:
            self.settings={"listenCanvas":True}
            Krita.instance().writeSetting("","blenderKritaSettings", json.dumps(self.settings))
        else:
            self.settings = json.loads(x)
            
    def save_settings(self):
        print(self.settings)
        if not self.settings:
            self.settings={"listenCanvas":True}
        Krita.instance().writeSetting("","blenderKritaSettings", json.dumps(self.settings))

    def on_listen_change(self,checked):
        print(checked)
        self.settings['listenCanvas'] = checked == 2
        self.save_settings()
    
        
    def popup(self):
        QMessageBox.information(QWidget(),"DockerExample","It Works")
        print("popup")

    def toggleListen(self):
        self.listen_to_canvas_change = not self.listen_to_canvas_change
    
    def listen(self):
        QtWidgets.qApp.installEventFilter(self)
        Krita.instance().action('edit_undo').triggered.connect(lambda x: self.onUpdateImage())
        Krita.instance().action('edit_redo').triggered.connect(lambda x: self.onUpdateImage())

        
    def checkEnter(self, eventType):
        pass

    def chuj(self):
        self.send_pixels()

    def onUpdateImage(self):
        if not self.settings['listenCanvas']:
            return
        t = Timer(0.25,self.chuj)
        #t = Timer(0,self.chuj)
        t.start()
        
    def canvasChanged(self, canvas):
        print("something Happened")
        pass
    
    def eventFilter(self, obj, event):
        if isinstance(obj,QOpenGLWidget):
            if event.type() == 3 and event.button() == 1 :
                print(obj, type(obj).__bases__)
                self.onUpdateImage()
                print("painted Something on", event.type(), event.button())
        # print("asdasdasd")  
        return False  
    # def eventFilter(self, obj, event):
    #     if isinstance(obj,QOpenGLWidget):
    #         if event.type() == 3 and event.button() == Qt.RightButton:
    #             Krita.instance().action('chooseForegroundColor').trigger()




# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

# from krita import DockWidget
# from PyQt5 import QtCore, QtGui, QtWidgets




# class DockerTemplate(DockWidget):
#     def __init__(self):
#         DockWidget.setObjectName("DockWidget")
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(DockWidget.sizePolicy().hasHeightForWidth())
#         DockWidget.setSizePolicy(sizePolicy)
#         DockWidget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
#         self.dockWidgetContents = QtWidgets.QWidget()
#         self.dockWidgetContents.setEnabled(True)
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
#         self.dockWidgetContents.setSizePolicy(sizePolicy)
#         self.dockWidgetContents.setObjectName("dockWidgetContents")
#         self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents)
#         self.horizontalLayout.setObjectName("horizontalLayout")
#         self.verticalFrame = QtWidgets.QFrame(self.dockWidgetContents)
#         self.verticalFrame.setEnabled(True)
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.verticalFrame.sizePolicy().hasHeightForWidth())
#         self.verticalFrame.setSizePolicy(sizePolicy)
#         self.verticalFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
#         self.verticalFrame.setObjectName("verticalFrame")
#         self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalFrame)
#         self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
#         self.verticalLayout.setObjectName("verticalLayout")
#         self.label = QtWidgets.QLabel(self.verticalFrame)
#         self.label.setObjectName("label")
#         self.verticalLayout.addWidget(self.label)
#         self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
#         self.horizontalLayout_2.setObjectName("horizontalLayout_2")
#         self.ConnectButton = QtWidgets.QPushButton(self.verticalFrame)
#         self.ConnectButton.setObjectName("ConnectButton")
#         self.horizontalLayout_2.addWidget(self.ConnectButton)
#         self.DisconnectButton = QtWidgets.QPushButton(self.verticalFrame)
#         self.DisconnectButton.setObjectName("DisconnectButton")
#         self.horizontalLayout_2.addWidget(self.DisconnectButton)
#         self.verticalLayout.addLayout(self.horizontalLayout_2)
#         self.RefreshButton = QtWidgets.QPushButton(self.verticalFrame)
#         self.RefreshButton.setObjectName("RefreshButton")
#         self.verticalLayout.addWidget(self.RefreshButton)
#         self.SendDataButton = QtWidgets.QPushButton(self.verticalFrame)
#         self.SendDataButton.setObjectName("SendDataButton")
#         self.verticalLayout.addWidget(self.SendDataButton)
#         spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
#         self.verticalLayout.addItem(spacerItem)
#         self.horizontalLayout.addWidget(self.verticalFrame)
#         DockWidget.setWidget(self.dockWidgetContents)

#         self.retranslateUi(DockWidget)
#         QtCore.QMetaObject.connectSlotsByName(DockWidget)

#     def retranslateUi(self, DockWidget):
#         _translate = QtCore.QCoreApplication.translate
#         DockWidget.setWindowTitle(_translate("DockWidget", "DockWidget"))
#         self.label.setText(_translate("DockWidget", "isConnected"))
#         self.ConnectButton.setText(_translate("DockWidget", "Connect"))
#         self.DisconnectButton.setText(_translate("DockWidget", "Disconnect"))
#         self.RefreshButton.setText(_translate("DockWidget", "Refresh"))
#         self.SendDataButton.setText(_translate("DockWidget", "Send data manually"))
