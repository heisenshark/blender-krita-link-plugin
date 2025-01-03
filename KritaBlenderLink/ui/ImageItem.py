from time import sleep
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QSpacerItem,
    QLabel,
    QMenu,
)
from krita import Krita
from KritaBlenderLink.connection import ConnectionManager, blender_image_as_new_layer, open_as_new_document, link_image, link_layer

class ImageItem(QWidget):
    def __init__(self, image,conn_manager: ConnectionManager, parent=None):
        super().__init__(parent)
        self.image = image
        self.conn_manager = conn_manager
        height = 0
        width = 0
        dir(Krita)
        if (
            hasattr(Krita, "instance")
            and Krita.instance()
            and Krita.instance().activeDocument()
        ):
            document = Krita.instance().activeDocument()
            height = document.height()
            width = document.width()

        self.setObjectName("ListItem")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy1)
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(text=image["name"], parent=self)
        self.label_9.setObjectName("label_9")
        if image["name"] in self.conn_manager.linked_images.keys():
            if self.conn_manager.linked_images[image["name"]]["document"] == Krita.instance().activeDocument(): 
                self.label_9.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.label_9.setStyleSheet("font-weight: bold; color: #003300;")
        self.image_size = image["size"]
        if not (self.image_size[0] == width and self.image_size[1] == height):
            self.label_9.setStyleSheet("color: red;")

        self.horizontalLayout_2.addWidget(self.label_9)
        size_label = str(image["size"][0]) + "x" + str(image["size"][1])
        self.label_size = QLabel(text=size_label, parent=self)
        self.label_size.setObjectName("label_size")

        self.horizontalSpacer_2 = QSpacerItem(
            40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.addWidget(self.label_size)

        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        self.setLayout(self.horizontalLayout_2)

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        cmenu.addSection(self.image["name"])
        
        openAct = cmenu.addAction("Blender image to new Layer")
        linkImageAct = cmenu.addAction("Link image")
        linkLayer = cmenu.addAction("Link Layer/Group Layer")
        unlinkImageAct = cmenu.addAction("Unlink image")
        openAsNewDocumentLinkAct = cmenu.addAction("Open in new document and link")
        openAsNewDocumentAct = cmenu.addAction("Open in new document")

        
        if unlinkImageAct is None or linkImageAct is None or linkLayer is None:
            return
        unlinkImageAct.setDisabled(self.image["name"] not in self.conn_manager.linked_images.keys())
        linkImageAct.setDisabled(self.image["name"] in self.conn_manager.linked_images.keys())
        linkLayer.setDisabled(self.image["name"] in self.conn_manager.linked_images.keys())

        if (
            hasattr(Krita, "instance")
            and Krita.instance()
            and Krita.instance().activeDocument()
        ):
            document = Krita.instance().activeDocument()
            height = document.height()
            width = document.width()

        if not (self.image_size[0] == width and self.image_size[1] == height):
            unlinkImageAct.setDisabled(True)
            linkImageAct.setDisabled(True)
        
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        print(action)
        if action == linkImageAct:
            print("link selected")
            link_image(self.image,self.conn_manager) 
        elif action == linkLayer:
            print("linking layer")
            link_layer(self.image,self.conn_manager)
        elif action == unlinkImageAct:
            print("unlinking image")
            self.conn_manager.remove_link(self.image["name"])
        elif action == openAct:
            print("from blender to krita selected")
            blender_image_as_new_layer(self.image,self.conn_manager)
        elif action == openAsNewDocumentAct:
            open_as_new_document(self.image,self.conn_manager)
            print("dupa") 
        elif action == openAsNewDocumentLinkAct:
            open_as_new_document(self.image,self.conn_manager,True)
            print("dupa") 

    def mouseDoubleClickEvent(self, a0 )-> None: 
        if (
            hasattr(Krita, "instance")
            and Krita.instance()
            and Krita.instance().activeDocument()
        ):
            document = Krita.instance().activeDocument()
            height = document.height()
            width = document.width()
        else:
            return super().mouseDoubleClickEvent(a0)
        if self.image["name"] in  self.conn_manager.linked_images:
            self.conn_manager.remove_link(self.image["name"])
        elif not (self.image_size[0] == width and self.image_size[1] == height):
            sleep(0.1)
            open_as_new_document(self.image,self.conn_manager,True)
        else:
            link_image(self.image,self.conn_manager) 
        # return super().mouseDoubleClickEvent(a0)

