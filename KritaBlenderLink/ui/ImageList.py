from PyQt5.QtWidgets import QListWidget, QWidget, QSizePolicy, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QSize
from .ImageItem import ImageItem
from KritaBlenderLink.connection import (
    ConnectionManager,
    MessageListener,
)


class ImageList(QListWidget):
    image_list = []
    refresh_signal = pyqtSignal(object)
    clear_signal = pyqtSignal()

    def __init__(
        self, con_manager: ConnectionManager, parent: QWidget
    ) -> None:
        ImageList.instance = self
        self.conn_manager = con_manager
        super().__init__(parent)
        self.setObjectName("ImageList")
        self.setObjectName("scrollArea")
        self.setMinimumSize(QSize(0, 100))
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )

        self.refresh_signal.connect(self.update_images_list)
        self.clear_signal.connect(self.clear_images_list)

        MessageListener(
            "GET_IMAGES",
            lambda message: ImageList.instance.refresh_signal.emit(message["data"]),
        )
    
    def update_images_list(self, images_list):
        print("update time")
        self.clear_images_list()
        print("items to be removed", len(images_list))
        for image in images_list:
            listItem = QListWidgetItem(self)
            item = ImageItem(
                image=image,
                parent=self.scrollAreaWidgetContents,
                conn_manager=self.conn_manager
            )
            listItem.setSizeHint(item.sizeHint())
            self.addItem(listItem)
            self.setItemWidget(listItem, item)

    def clear_images_list(self):
        self.clear()
