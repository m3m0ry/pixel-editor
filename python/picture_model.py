from PyQt5.QtCore import QAbstractTableModel, QVariant
from PyQt5.QtGui import QColor, QImage
from PyQt5.QtCore import Qt


class PictureModel(QAbstractTableModel):
    def __init__(self, parent, image=None, file=None):
        super().__init__(parent)
        self._image = image
        self.file = file

    def rowCount(self, parent):
        if self.image is None:
            return 0
        return self.image.height()

    def columnCount(self, parent):
        if self.image is None:
            return 0
        return self.image.width()

    def data(self, index, role):
        if role == Qt.BackgroundRole:
            rgb = self.image.pixel(index.column(), index.row())
            return QColor(rgb)
        return QVariant()

    def open_image(self, file_name):
        self.image = QImage(file_name)
        self.layoutChanged.emit()
        return True

    def save_image(self, file_name):
        if file_name is not None:
            self.file = file_name
        self.image.save(self.file)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.layoutChanged.emit()
