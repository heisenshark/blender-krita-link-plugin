import time
from krita import *
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
)
from threading import Timer
import json

DOCKER_TITLE = 'Blender Krita Link'

class BlenderKritaLink(DockWidget):
    cursor_in_view = False
    cursor_last = time.time_ns()
    canvas_update_last = time.time_ns()
    
    settings = {}
    listen_to_canvas_change = True
    
    def __init__(self):
        super().__init__()
        self.init_settings()
        self.setupUi()
        appNotifier = Krita.instance().notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(self.listen)
                
    def setupUi(self):
        self.setObjectName(DOCKER_TITLE)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.dockWidgetContents = QWidget()
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
        self.label = QLabel("Connection status: innactive",self.verticalFrame)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
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
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.canvasListenCheckbox = QCheckBox(text="Update on drawing?")
        self.canvasListenCheckbox.setCheckState(self.settings['listenCanvas'])
        self.canvasListenCheckbox.setTristate(False)
        self.canvasListenCheckbox.stateChanged.connect(self.on_listen_change)
        self.verticalLayout.addWidget(self.canvasListenCheckbox)

        self.verticalLayout.addItem(spacerItem)
        self.dockWidgetContents.layout().addWidget(self.verticalFrame)
        self.setWidget(self.dockWidgetContents)
        
        
        self.ConnectButton.clicked.connect(self.listen)
        self.DisconnectButton.clicked.connect(self.popup)
        self.RefreshButton.clicked.connect(self.listen)
        self.SendDataButton.clicked.connect(self.onUpdateImage)
        
    def setup_ui(self):
        self.setWindowTitle(DOCKER_TITLE)
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)
        connection_wrapper = QHBoxLayout()
        connectButton = QPushButton("Connect",mainWidget)
        connectButton.clicked.connect(self.popup)
        disconnectButton = QPushButton("Disconnect",mainWidget)
        disconnectButton.clicked.connect(self.popup)
        startButton = QPushButton("StartExtension",mainWidget)
        startButton.clicked.connect(self.listen)
        
        connection_wrapper.addWidget(connectButton)
        connection_wrapper.addWidget(disconnectButton)

        print(self.settings)
        
        checkbox = QCheckBox(text="Update on drawing?")
        checkbox.setCheckState(self.settings['listenCanvas'])
        checkbox.setTristate(False)
        checkbox.stateChanged.connect(self.on_listen_change)
        
        mainWidget.setLayout(QVBoxLayout())
        mainWidget.layout().addChildLayout(connection_wrapper)
        mainWidget.layout().addWidget(startButton)
        mainWidget.layout().addWidget(checkbox)
        mainWidget.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

    
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
        if eventType in [10,11]:
            self.cursor_last=time.time_ns()
        if eventType == 10:
            self.cursor_in_view = True
        if eventType == 11:
            self.cursor_in_view = False

    def chuj(self):
        if self.canvas_update_last +250000000 < time.time_ns():
            print("Canvas Updated", self.canvas_update_last +250000000, time.time_ns())

    def onUpdateImage(self):
        if not self.settings['listenCanvas']:
            return
        self.canvas_update_last = time.time_ns()
        t = Timer(0.25,self.chuj)
        t.start()
        
    def canvasChanged(self, canvas):
        print("something Happened")
        pass
    
    def eventFilter(self, obj, event):
        if isinstance(obj,QOpenGLWidget):
            etype = event.type()
            self.checkEnter(etype)
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
