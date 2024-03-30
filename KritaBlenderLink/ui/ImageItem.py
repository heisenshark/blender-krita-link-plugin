from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QSpacerItem,
    QLabel,
    QMenu,
)
from krita import Krita
from KritaBlenderLink.connection import ConnectionManager, blender_image_as_new_layer, open_as_new_document, override_image

class ImageItem(QWidget):
    def __init__(self, image,conn_manager: ConnectionManager, parent=None):
        super().__init__(parent)
        # self.setVisible(False)
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

        if "isActive" in image and image["isActive"]:
            if conn_manager.linked_document == Krita.instance().activeDocument(): 
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
        
        openAct = cmenu.addAction("From Blender To new Layer")
        linkImageAct = cmenu.addAction("Link Image")
        unlinkImageAct = cmenu.addAction("Unlink Image")
        openAsNewDocumentLinkAct = cmenu.addAction("Open in new Document and link")
        openAsNewDocumentAct = cmenu.addAction("Open in new document")
        
        if unlinkImageAct is None or linkImageAct is None:
            return
        unlinkImageAct.setDisabled(not self.image["isActive"])
        linkImageAct.setDisabled(self.image["isActive"])

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
            override_image(self.image,self.conn_manager) 
        elif action == unlinkImageAct:
            print("unlinking image")
            self.conn_manager.remove_link()
        elif action == openAct:
            print("from blender to krita selected")
            blender_image_as_new_layer(self.image,self.conn_manager)
        elif action == openAsNewDocumentAct:
            open_as_new_document(self.image,self.conn_manager)
            print("dupa") 
        elif action == openAsNewDocumentLinkAct:
            open_as_new_document(self.image,self.conn_manager,True)
            print("dupa") 
            pass
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

        if self.image["isActive"]:
            self.conn_manager.remove_link()
        elif not (self.image_size[0] == width and self.image_size[1] == height):
            open_as_new_document(self.image,self.conn_manager,True)
        else:
            override_image(self.image,self.conn_manager) 
        return super().mouseDoubleClickEvent(a0)

