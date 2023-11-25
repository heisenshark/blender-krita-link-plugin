from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal


class ImageItem(QWidget):
    def __init__(self, text, size, parent=None):
        super().__init__(parent)
        self.setObjectName(u"ListItem")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy1)
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_9 = QLabel(text=text, parent=self)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_2.addWidget(self.label_9)

        self.label_size = QLabel(text=size, parent=self)
        self.label_size.setObjectName(u"label_size")

        self.horizontalLayout_2.addWidget(self.label_size)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_3 = QPushButton("Open", self)
        self.pushButton_3.setObjectName(u"Open")
        self.pushButton_3.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        sizePolicy2 = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.pushButton_3.sizePolicy().hasHeightForWidth())
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
