import typing
import asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QSize
from .ImageItem import ImageItem
from KritaBlenderLink.connection import ConnectionManager, MessageListener, override_image
# from connection import ConnectionManager


class ImageList(QScrollArea):
    image_list = []
    refresh_signal = pyqtSignal(object)
    clear_signal = pyqtSignal()
    instance = None

    def __init__(self, con_manager: ConnectionManager, parent: QWidget | None = ...) -> None:
        ImageList.instance = self
        self.conn_manager = con_manager
        super().__init__(parent)
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
        self.refresh_signal.connect(self.update_images_list)
        self.clear_signal.connect(self.clear_images_list)
        MessageListener(
            "GET_IMAGES", lambda message: ImageList.instance.refresh_signal.emit(message['data']))

    def update_images_list(self, images_list):
        print("update time")
        self.clear_images_list()
        print("items to be removed", len(images_list))
        for image in images_list:
            item = ImageItem(image=image, on_open=lambda: asyncio.run(self.conn_manager.request(
                {"data": "", "type": "OPEN"})), on_override=lambda image: override_image(image, self.conn_manager), parent=self.scrollAreaWidgetContents)
            self.image_list.append(item)
            print("item created")
            self.verticalLayout_2.moveToThread(self.thread())
            self.verticalLayout_2.addWidget(item)
            print("item added")

    def clear_images_list(self):
        for i in reversed(range(self.verticalLayout_2.count())):
            widget_to_remove = self.verticalLayout_2.itemAt(i).widget()
            widget_to_remove.moveToThread(self.thread())
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()
        self.image_list.clear()