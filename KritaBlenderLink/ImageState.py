from krita import Krita, Notifier, QOpenGLWidget, QtWidgets
from PyQt5.QtCore import pyqtSignal, QSize, QObject

class ImageState(QObject):
    data = {
        "colorProfile" : None,
        "colorModel" : None,
        "colorDepth" : None,
        "size" : [0,0]
    }

    onPixelsChange = pyqtSignal(object)
    onImageDataChange = pyqtSignal(object)
    onSRGBColorSpace = pyqtSignal(bool)
    instance = None

    def __init__(self) -> None:
        print("init state....")
        super().__init__()
        ImageState.instance = self
        appNotifier:Notifier = Krita.instance().notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(self.setup_listening)
        appNotifier.viewCreated.connect(lambda x: self.check_color_profile())
        appNotifier.imageCreated.connect(lambda x: self.set_data(self.get_data()))
        self.onPixelsChange.connect(lambda x:print("pixels changed"))
        self.onImageDataChange.connect(lambda x:print("imagedata changed"))

    def get_data(self):
        data = {}
        data["colorProfile"] = Krita.instance().activeDocument().colorProfile()
        data["colorModel"] = Krita.instance().activeDocument().colorModel()
        data["colorDepth"] = Krita.instance().activeDocument().colorDepth()
        data["size"] = [Krita.instance().activeDocument().width(),Krita.instance().activeDocument().height()]
        return data
    
    def set_data(self,data):
        self.data = data

    def check_color_profile(self):
        if not Krita.instance().activeDocument():
            return 
        d = self.get_data()
        self.instance.onSRGBColorSpace.emit(d['colorProfile'] == "sRGB")

    def compare_data(self,data1,data2):
        print(data1 , data2)
        self.check_color_profile()
        for key,value in data1.items():

            if key == "size":
                if value == data2['size']:
                    continue
                else:
                    return False
            if key not in data2 or data2[key] != value:
                return False
        return len(dir(data1)) == len(dir(data2))
    
    def on_properties_change(self):
        print("improp change")
        is_eq = self.compare_data(self.get_data(),self.data)
        if not is_eq:
            self.onImageDataChange.emit(self.get_data())
        self.data = self.get_data()
    

    def setup_listening(self):
        QtWidgets.qApp.installEventFilter(self)

        Krita.instance().action("edit_undo").triggered.connect(
            lambda x: self.onPixelsChange.emit(self.data)
        )

        Krita.instance().action("edit_redo").triggered.connect(
            lambda x: self.onPixelsChange.emit(self.data)
        )
        Krita.instance().action("file_open").triggered.connect(
            lambda x: self.check_color_profile()
        )
        
        Krita.instance().action("file_open_recent").triggered.connect(
            lambda x: self.check_color_profile()
        )

        Krita.instance().action("image_properties").triggered.connect(self.on_properties_change)

    def eventFilter(self, obj, event):
        if isinstance(obj, QOpenGLWidget):
            if event.type() == 3 and event.button() == 1:
                print(obj, type(obj).__bases__)
                self.onPixelsChange.emit(self.data)
                print("painted Something on", event.type(), event.button())
        return False

ImageState()