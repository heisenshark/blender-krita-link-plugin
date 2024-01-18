#code heavily inspired from https://krita-artists.org/t/canvas-render-how-to/31540

from krita import *
from PyQt5.QtCore import (
        Qt,
        QEvent,
        QPointF,
        QRect)

from PyQt5.QtGui import *

from PyQt5.QtWidgets import (
        QWidget,
        QMdiArea,
        QAbstractScrollArea)

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from .settings import Settings
from threading import Timer
from PyQt5 import sip

def ruler_correction():
    qwin = Krita.instance().activeWindow().qwindow()
    pobj = qwin.findChild(QMdiSubWindow)

    view = None 
    for c in pobj.children():
        if c.metaObject().className() == "KisView":
            view = c
            print(c)

    x = 0
    y = 0

    for c in view.children():
        if c.metaObject().className() == "KoRuler" and c.isVisible():
            h = c.size().height()
            w = c.size().width()
            if h >= w : x = w
            if w >= h : y = h
    print(x,y)
    return [x,y]


def get_q_view(view):
    window = view.window()
    q_window = window.qwindow()
    q_stacked_widget = q_window.centralWidget()
    q_mdi_area = q_stacked_widget.findChild(QMdiArea)
    for v, q_mdi_view in zip(window.views(), q_mdi_area.subWindowList()):
        if v == view:
            return q_mdi_view.widget()


def get_transform(view):
    def _offset(scroller):
        mid = (scroller.minimum() + scroller.maximum()) / 2.0
        return -(scroller.value() - mid)

    canvas = view.canvas()
    document = view.document()
    q_view = get_q_view(view)
    if q_view is None:
        print("view is none")
        return QTransform()
    area = q_view.findChild(QAbstractScrollArea)
    zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
    transform = QTransform()
    transform.translate(
            _offset(area.horizontalScrollBar()),
            _offset(area.verticalScrollBar()))
    transform.rotate(canvas.rotation())
    transform.scale(zoom, zoom)
    return transform
        
class VieportResizeListener(QtCore.QObject):
    def __init__(self, function):
        super().__init__()
        self.function = function

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            print("resize handle from canvas")
            self.function()
            # q_canvas = self.parent().findChild(QAbstractScrollArea).viewport()
            # size = q_canvas.size()
            # x, y = ruler_correction()
            # self.setGeometry(x,y,q_canvas.geometry().width(),q_canvas.geometry().height())
        return super().eventFilter(obj, e)

class UvOverlay(QWidget):
    INSTANCES_SET = []

    _tris = []
    __tris = []
    ACTIVE_VIEW = None
    INSTANCE = None
    COLOR = QColor(0,0,0,255)
    destroyAll = pyqtSignal()

    def __init__(self, view):
        parent = get_q_view(view)
        self.view = view
        # self.moveToThread(parent.thread())
        super().__init__(parent)
        
        
        UvOverlay.COLOR = QColor(Settings.getSetting("uvColor") or "#000000FF")
        UvOverlay.INSTANCES_SET.append(self)
        # self.destroyAll.emit()
        self.setObjectName("UVOVERLAY")
        # if UvOverlay.INSTANCE != None and not UvOverlay.INSTANCE.destroyed:
        #     UvOverlay.INSTANCE.deleteLater()
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.NoFocus)
        # UvOverlay.ACTIVE_VIEW = view
        q_canvas = parent.findChild(QAbstractScrollArea).viewport()
        # size = q_canvas.size()
        
        # x, y = ruler_correction()
        # self.setGeometry(x,y,q_canvas.geometry().width(),q_canvas.geometry().height())

        self.ls = VieportResizeListener(self.resize_handle)
        q_canvas.installEventFilter(self.ls)
        
        parent.installEventFilter(self)
        self.update_stuff()
        def saydupa():
            print("dupa")
        self.destroyed.connect(saydupa)
        self._tris = []

    def update_stuff(self):
        print("update stuff")
        active_window = Application.activeWindow()
        active_view = active_window.activeView()
        if active_view != self.view:
            return
        document = self.view.document()
        width = float(document.width())
        height = float(document.height())
        print("doc", width, height)
        self._tris = []

        for p in UvOverlay._tris:
            polygon = QPolygonF()
            for v in p:
                polygon.append(QPointF((v[0]-0.5)*width,(v[1]-0.5)*height))
            self._tris.append(polygon)
            
        Krita.instance().action("view_ruler").triggered.connect(self.resize_handle)
        self.resize_handle()


    def updatePolygons(self, polygons):
        self._tris = polygons
        self.update()

    def paintEvent(self, e):
        document = self.view.document()
        view = self.view
        canvas = view.canvas()
        painter = QPainter(self)
        show_uv= Settings.getSetting("showUVs")
        if not show_uv:
            return
        try:
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.translate(self.rect().center())
            painter.setTransform(get_transform(self.view), combine=True)
            painter.setPen(Qt.NoPen)

            document = view.document()
            zoom = (canvas.zoomLevel() * 72.0) / document.resolution()

            painter.setPen(QPen(UvOverlay.COLOR, 0.5/zoom, Qt.SolidLine))
            for p in self._tris:
                painter.drawPolygon(p)

        finally:
            painter.end()
    
    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            self.resize_handle()
            # q_canvas = self.parent().findChild(QAbstractScrollArea).viewport()
            # size = q_canvas.size()
            # x, y = ruler_correction()
            # self.setGeometry(x,y,q_canvas.geometry().width(),q_canvas.geometry().height())
        return super().eventFilter(obj, e)
    
    def resize_handle(self):
        print("resize !!!! ")
        q_canvas = self.parent().findChild(QAbstractScrollArea).viewport()
        size = q_canvas.size()
        x, y = ruler_correction()
        print(q_canvas.x(),q_canvas.y(),q_canvas.geometry().width(),q_canvas.geometry().height())
        self.setGeometry(x,y,q_canvas.geometry().width(),q_canvas.geometry().height())
        
    def set_polygons(polygons):
        # if UvOverlay.ACTIVE_VIEW is None or UvOverlay.ACTIVE_VIEW.document() is None:
        #     return
        active_window = Application.activeWindow()
        active_view = active_window.activeView()

        document = active_view.document()

        width = float(document.width())
        height = float(document.height())
        # instance = UvOverlay.INSTANCE
        # if instance == None:
        #     return

        UvOverlay._tris = []
        for f in polygons:
            pp = []
            for v in f:
                pp.append([v[0],v[1]])
            UvOverlay._tris.append(pp)

        __tris = []
        for p in polygons:
            polygon = QPolygonF()
            for v in p:
                polygon.append(QPointF((v[0]-0.5)*width,(v[1]-0.5)*height))
            __tris.append(polygon)
        print(__tris[:5])
        UvOverlay.__tris = __tris
        print(UvOverlay.INSTANCES_SET)
        for ov in UvOverlay.INSTANCES_SET:
            if not sip.isdeleted(ov):
                # UvOverlay.INSTANCE = overlay
                # if ov.view == active_view: 
                ov.update_stuff()
                ov.update()
        print("UVs updated, len:",len(__tris))
