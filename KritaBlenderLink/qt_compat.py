"""
Qt Compatibility layer for Krita 5.x (PyQt5) and Krita 6.x (PyQt6).
Provides a unified interface for imports and Qt enums across both Qt versions.
"""
from __future__ import annotations

try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    try:
        from PyQt5 import sip
    except ImportError:
        import sip
    from PyQt5.QtCore import (
        QByteArray,
        QEvent,
        QObject,
        QPointF,
        QRect,
        QSize,
        Qt,
        QTimer,
        pyqtSignal,
    )
    from PyQt5.QtGui import (
        QColor,
        QImage,
        QPainter,
        QPen,
        QPolygonF,
        QTransform,
    )
    from PyQt5.QtWidgets import (
        QAbstractScrollArea,
        QColorDialog,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMdiArea,
        QMdiSubWindow,
        QMenu,
        QPushButton,
        QSizePolicy,
        QSpacerItem,
        QWidget,
    )
    try:
        from PyQt5.QtOpenGL import QOpenGLWidget
    except (ImportError, ModuleNotFoundError):
        from PyQt5.QtWidgets import QOpenGLWidget

    QT_VERSION = 5

    # Enums for Qt5
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    ShowAlphaChannel = QColorDialog.ShowAlphaChannel
    HexArgb = QColor.HexArgb
    SizePreferred = QSizePolicy.Preferred
    SizeExpanding = QSizePolicy.Expanding
    SizeMinimum = QSizePolicy.Minimum
    SizeMinimumExpanding = QSizePolicy.MinimumExpanding
    SizeFixed = QSizePolicy.Fixed
    EvMouseButtonPress = QEvent.MouseButtonPress
    EvWheel = QEvent.Wheel
    EvResize = QEvent.Resize
    LeftButton = Qt.LeftButton
    WA_TransparentForMouseEvents = Qt.WA_TransparentForMouseEvents
    NoFocus = Qt.NoFocus
    Antialiasing = QPainter.Antialiasing
    NoPen = Qt.NoPen
    SolidLine = Qt.SolidLine
    Format_ARGB32 = QImage.Format_ARGB32

except (ImportError, ModuleNotFoundError):
    from PyQt6 import QtCore, QtGui, QtWidgets, uic
    try:
        from PyQt6 import sip
    except ImportError:
        import sip
    from PyQt6.QtCore import (
        QByteArray,
        QEvent,
        QObject,
        QPointF,
        QRect,
        QSize,
        Qt,
        QTimer,
        pyqtSignal,
    )
    from PyQt6.QtGui import (
        QColor,
        QImage,
        QPainter,
        QPen,
        QPolygonF,
        QTransform,
    )
    from PyQt6.QtWidgets import (
        QAbstractScrollArea,
        QColorDialog,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMdiArea,
        QMdiSubWindow,
        QMenu,
        QPushButton,
        QSizePolicy,
        QSpacerItem,
        QWidget,
    )
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget

    QT_VERSION = 6

    # Scoped enums for Qt6
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    ShowAlphaChannel = QColorDialog.ColorDialogOption.ShowAlphaChannel
    HexArgb = QColor.NameFormat.HexArgb
    SizePreferred = QSizePolicy.Policy.Preferred
    SizeExpanding = QSizePolicy.Policy.Expanding
    SizeMinimum = QSizePolicy.Policy.Minimum
    SizeMinimumExpanding = QSizePolicy.Policy.MinimumExpanding
    SizeFixed = QSizePolicy.Policy.Fixed
    EvMouseButtonPress = QEvent.Type.MouseButtonPress
    EvWheel = QEvent.Type.Wheel
    EvResize = QEvent.Type.Resize
    LeftButton = Qt.MouseButton.LeftButton
    WA_TransparentForMouseEvents = Qt.WidgetAttribute.WA_TransparentForMouseEvents
    NoFocus = Qt.FocusPolicy.NoFocus
    Antialiasing = QPainter.RenderHint.Antialiasing
    NoPen = Qt.PenStyle.NoPen
    SolidLine = Qt.PenStyle.SolidLine
    Format_ARGB32 = QImage.Format.Format_ARGB32
