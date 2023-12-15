import asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from krita import *


class ImageItem(QWidget):
    def __init__(self, image, on_open, on_override, parent=None):
        super().__init__(parent)
        self.image = image
        height = 0
        width = 0
        dir(Krita)
        if (
            hasattr(Krita, "instance")
            and Krita.instance()
            and Krita.instance().activeDocument()
        ):
            print("dupa")
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
        self.label_9 = QLabel(text=image["name"], parent=self)
        self.label_9.setObjectName("label_9")
        if "isActive" in image and image["isActive"]:
            self.label_9.setStyleSheet("font-weight: bold")

        self.horizontalLayout_2.addWidget(self.label_9)
        size_label = str(image["size"][0]) + "x" + str(image["size"][1])
        self.label_size = QLabel(text=size_label, parent=self)
        self.label_size.setObjectName("label_size")

        self.horizontalLayout_2.addWidget(self.label_size)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_4 = QPushButton("Override", self)
        if not (image["size"][0] == width and image["size"][1] == height):
            print(image["size"], width, height)
            self.pushButton_4.setStyleSheet("color: red;")
            self.pushButton_4.setDisabled(True)
        self.pushButton_4.setObjectName("Override")
        self.pushButton_4.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        self.pushButton_4.clicked.connect(lambda: on_override(self.image))

        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.setLayout(self.horizontalLayout_2)
