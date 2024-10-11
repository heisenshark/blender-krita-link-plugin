# code heavily inspired from https://krita-artists.org/t/canvas-render-how-to/31540
from __future__ import annotations

from .settings import Settings
from krita import Krita
from PyQt5 import sip
from PyQt5.QtCore import (
    QEvent,
    QObject,
    QPointF,
    Qt,
    QRect
)
from PyQt5.QtGui import QColor, QPainter, QPen, QPolygonF, QTransform, QImage
from PyQt5.QtWidgets import (
    QAbstractScrollArea,
    QMdiArea,
    QMdiSubWindow,
    QWidget,
    QOpenGLWidget,
)



def ruler_correction():
    qwin = Krita.instance().activeWindow().qwindow()
    pobj = qwin.findChild(QMdiSubWindow)

    view = None
    for c in pobj.children():
        if c.metaObject().className() == "KisView":
            view = c
            # print(c)
    x = 0
    y = 0
    for c in view.children():
        if c.metaObject().className() == "KoRuler" and c.isVisible():
            h = c.size().height()
            w = c.size().width()
            if h >= w:
                x = w
            if w >= h:
                y = h
    # print(x, y)
    return [x, y]


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
        _offset(area.horizontalScrollBar()), _offset(area.verticalScrollBar())
    )
    transform.rotate(canvas.rotation())
    transform.scale(zoom, zoom)
    return transform


class VieportResizeListener(QObject):
    def __init__(self, function):
        super().__init__()
        self.function = function

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            print("resize handle from canvas")
            self.function()
        return super().eventFilter(obj, e)


class UvOverlay(QWidget):
    INSTANCES_SET: list[UvOverlay] = []

    POLYGONS = []
    ACTIVE_VIEW = None
    INSTANCE = None
    COLOR = QColor(0, 0, 0, 255)

    def __init__(self, view):
        parent = get_q_view(view)
        self.view = view
        self.openGL = parent.findChild(QOpenGLWidget)
        super().__init__(parent)
        n = Settings.getSetting("uvColor")
        UvOverlay.COLOR = QColor(n if n is not None else "#000000FF")
        UvOverlay.INSTANCES_SET.append(self)
        self.setObjectName("UVOVERLAY")

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.NoFocus)
        q_canvas = parent.findChild(QAbstractScrollArea).viewport()

        self.ls = VieportResizeListener(self.resize_handle)
        q_canvas.installEventFilter(self.ls)

        parent.installEventFilter(self)
        self.update_stuff()
        self._polygons = []

    def update_stuff(self):
        active_window = Krita.instance().activeWindow()
        if sip.isdeleted(active_window):
            return
        active_view = active_window.activeView()
        if sip.isdeleted(self.view)  or sip.isdeleted(active_view) or active_view != self.view:
            return
        document = self.view.document()
        if sip.isdeleted(document):
            return
        width = float(document.width())
        height = float(document.height())
        # print("doc", width, height)
        self._polygons = []

        for p in UvOverlay.POLYGONS:
            polygon = QPolygonF()
            for v in p:
                polygon.append(QPointF((v[0] - 0.5) * width, (v[1] - 0.5) * height))
            self._polygons.append(polygon)

        Krita.instance().action("view_ruler").triggered.connect(self.resize_handle)
        self.resize_handle()

    def update_polygons(self, polygons):
        self._polygons = polygons
        self.update()

    def paintEvent(self, e):
        document = self.view.document()
        view = self.view

        if self.openGL is not None:
            for (
                c
            ) in self.openGL.children():  # hide uvs so they dont cover palette popup
                if c.isVisible() and c.metaObject().className() == "KisPopupPalette":
                    return

        canvas = view.canvas()
        painter = QPainter(self)
        show_uv = Settings.getSetting("showUVs")

        if not show_uv:
            return
        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.translate(self.rect().center())
            painter.setTransform(get_transform(self.view), combine=True)
            painter.setPen(Qt.NoPen)

            document = view.document()
            zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
            pen_weight = Settings.getSetting("uv_width") if Settings.getSetting("uv_width") is not None else 1
            painter.setPen(QPen(UvOverlay.COLOR, 0.5 * pen_weight / zoom, Qt.SolidLine))
            for p in self._polygons:
                painter.drawPolygon(p)

        finally:
            painter.end()

    @staticmethod
    def exportImage(layer): 
        krita_instance = Krita.instance()
        document = krita_instance.activeDocument()
        if document:
            image_data = layer.projectionPixelData(0, 0, document.width(), document.height())

# Konwertuj dane do obrazu QImage
            image = QImage(image_data, document.width(), document.height(), QImage.Format_ARGB32)
            print(image)

            painter = QPainter(image)
            painter.translate(document.width()/2,document.height()/2)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen_weight = Settings.getSetting("uv_width") if Settings.getSetting("uv_width") is not None else 1
            painter.setPen(QPen(UvOverlay.COLOR, pen_weight, Qt.SolidLine))

            for p in UvOverlay.INSTANCES_SET[0]._polygons:
                painter.drawPolygon(p)            
            painter.end()
            return image

        else:
            return None

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            self.resize_handle()
        return super().eventFilter(obj, e)

    def resize_handle(self):
        # print("resize !!!! ")
        q_canvas = self.parent().findChild(QAbstractScrollArea).viewport()
        x, y = ruler_correction()
        # print(
        #     q_canvas.x(),
        #     q_canvas.y(),
        #     q_canvas.geometry().width(),
        #     q_canvas.geometry().height(),
        # )
        self.setGeometry(
            x, y, q_canvas.geometry().width(), q_canvas.geometry().height()
        )

    @staticmethod
    def set_polygons(polygons):
        UvOverlay.POLYGONS = []
        for f in polygons:
            pp = []
            for v in f:
                pp.append([v[0], v[1]])
            UvOverlay.POLYGONS.append(pp)

        # print(UvOverlay.INSTANCES_SET)
        for ov in UvOverlay.INSTANCES_SET:
            if not sip.isdeleted(ov):
                ov.update_stuff()
                ov.update()
