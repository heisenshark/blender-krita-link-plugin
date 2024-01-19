from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QSpacerItem,
    QLabel,
    QMenu
)
from krita import Krita


class ImageItem(QWidget):
    def __init__(self, image, on_open, on_override, parent=None):
        super().__init__(parent)
        self.image = image
        self.on_open = on_open
        self.on_override = on_override
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
            self.label_9.setStyleSheet("font-weight: bold; color: green;")

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

        sizePolicy2 = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        self.setLayout(self.horizontalLayout_2)

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        cmenu.addSection(self.image["name"])
        openAct = cmenu.addAction("From Blender To new Layer")
        linkImageAct = cmenu.addAction("Link Image")

        if (
            hasattr(Krita, "instance")
            and Krita.instance()
            and Krita.instance().activeDocument()
        ):
            document = Krita.instance().activeDocument()
            height = document.height()
            width = document.width()

        if not (self.image_size[0] == width and self.image_size[1] == height):
            linkImageAct.setDisabled(True)

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        print(action)
        if action == linkImageAct:
            print("link selected")
            self.on_override(self.image)
        elif action == openAct:
            self.on_open(self.image)
            print("from blender to krita selected")
