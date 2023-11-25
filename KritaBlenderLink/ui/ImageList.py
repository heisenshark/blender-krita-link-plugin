from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QSize
from .ImageItem import ImageItem


class ImageList(QScrollArea):
    refresh_signal = pyqtSignal(object)
    l = []

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.image_list = ["Item 1", "Item 2", "Item 3",
                           "Item 3", "Item 3", "Item 3", "Item 3"]
        self.setObjectName(u"ImageList")
        self.setObjectName("scrollArea")
        self.setMinimumSize(QSize(0, 100))
        self.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.setWidget(self.scrollAreaWidgetContents)

        for item_text in self.image_list:
            item = ImageItem(item_text,"0x0",self.scrollAreaWidgetContents)
            # custom_item = QPushButton(item_text, self.scrollAreaWidgetContents)
            self.verticalLayout_2.addWidget(item)
            # self.verticalLayout.addWidget(custom_item)
        # Usuń wszystkie dzieci z głównego widżetu

        self.refresh_signal.connect(self.update_images_list)

    def update_images_list(self, images_list):
        print("update time")
        for i in reversed(range(self.verticalLayout_2.count())):
            widget_to_remove = self.verticalLayout_2.itemAt(i).widget()
            widget_to_remove.moveToThread(self.thread())
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()
        print("items removed", len(images_list))
        self.l.clear()
        for image in images_list:
            item = ImageItem(image['name'], str(
                image['size'][0]) + "x" + str(image['size'][1]), self.scrollAreaWidgetContents)
            self.l.append(item)
            print("item created")
            self.verticalLayout_2.moveToThread(self.thread())
            self.verticalLayout_2.addWidget(item)
            print("item added")

            # custom_item = QPushButton(item_text, self.scrollAreaWidgetContents)
