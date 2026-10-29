"""Rasterize UV faces into Krita's one-byte-per-pixel selection format."""

from .qt_compat import QImage, QPainter, QPolygonF, QPointF, QColor, NoPen


def uv_selection_pixels(faces, width, height):
    if width <= 0 or height <= 0:
        raise ValueError("Selection dimensions must be positive")
    image_format = getattr(QImage, "Format_Grayscale8", None)
    if image_format is None:
        image_format = QImage.Format.Format_Grayscale8
    mask = QImage(width, height, image_format)
    if mask.isNull():
        raise MemoryError("Cannot allocate UV selection mask")
    mask.fill(0)
    painter = QPainter(mask)
    try:
        painter.setPen(NoPen)
        painter.setBrush(QColor(255, 255, 255))
        # Paint each face separately to union overlaps. Hard edges avoid faint
        # unselected seams between adjacent faces. Qt clips to the canvas.
        for face in faces:
            if len(face) >= 3:
                painter.drawPolygon(QPolygonF([
                    QPointF(x * width, y * height) for x, y in face
                ]))
    finally:
        painter.end()
    # Blender already flips V into Krita's top-down coordinate system.
    size = mask.sizeInBytes() if hasattr(mask, "sizeInBytes") else mask.byteCount()
    pointer = mask.constBits()
    pointer.setsize(size)
    raw = bytes(pointer)
    stride = mask.bytesPerLine()
    # QImage pads scanlines; Selection.setPixelData expects tightly packed rows.
    return b"".join(raw[y * stride:y * stride + width] for y in range(height))
