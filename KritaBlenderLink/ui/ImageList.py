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
        self.setMinimumSize(QSize(0, 40))
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.setSizePolicy(sizePolicy)
        self.refresh_signal.connect(self.update_images_list)
        self.clear_signal.connect(self.clear_images_list)

        MessageListener(
            "GET_IMAGES",
            lambda message: ImageList.instance.refresh_signal.emit(message["data"]),
        )
    
    def update_images_list(self, images_list: list[object], str_filter:str|None=None):
        str_filter = str_filter if str_filter != "" else None
        print("update time")
        self.clear_images_list()
        print("items to be removed", len(images_list))
        def compute_index(text):
            return text.upper().find(str_filter.upper()) if str_filter is not None else 1 
        if len(images_list) > 10: 
            images_list.sort(key= lambda x:compute_index(x["name"]) - 1000 if x["name"] in self.conn_manager.linked_images.keys() else 0)

        for image in images_list:
            if str_filter is not None and image["name"].upper().find(str_filter.upper()) < 0:
                continue
            if image["size"][0] == 0 or image["size"][1] == 0:
                continue
            listItem = QListWidgetItem(self)
            item = ImageItem(
                image=image,
                parent=self.scrollAreaWidgetContents,
                conn_manager=self.conn_manager
            )
            listItem.setSizeHint(item.sizeHint())
            self.addItem(listItem)
            self.setItemWidget(listItem, item)
        ImageList.image_list = images_list

    def clear_images_list(self):
        self.clear()
