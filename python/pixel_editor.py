#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QWidget, QPushButton,\
    QLabel, QSpinBox, QGridLayout, QVBoxLayout, QSplitter, QTableView, QFileDialog, QScrollArea, QAbstractScrollArea
from PyQt5.QtGui import QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import QDir, Qt, QAbstractTableModel, QVariant
from functools import partial


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = PictureModel(self)
        self.current_path = QDir.homePath()

        new_action = QAction('&New', self, shortcut=QKeySequence.New, statusTip='Create new picture',
                             triggered=self.new_file)
        open_action = QAction('&Open', self, shortcut=QKeySequence.Open, statusTip='Open picture',
                              triggered=self.open_file)
        self.save_action = QAction('&Save', self, shortcut=QKeySequence.Save, statusTip='Save picture',
                                   triggered=self.save_file)
        self.save_action.setEnabled(False)
        self.save_as_action = QAction('&Save as...', self, shortcut=QKeySequence.SaveAs, statusTip='Save picture as...',
                                      triggered=self.save_file_as)
        self.save_as_action.setEnabled(False)
        exit_action = QAction('&Exit', self, shortcut=QKeySequence.Quit, statusTip='Exit application',
                              triggered=qApp.quit)

        self.statusBar()

        # Menu Bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Setup main window
        splitter = QSplitter(self)
        left = QWidget(splitter)
        # Size widget
        size = QWidget(left)
        size_layout = QGridLayout()
        size.setLayout(size_layout)
        label_x = QLabel(size)
        label_x.setText('x Size')
        self.spinbox_x = QSpinBox(size)
        self.spinbox_x.setMaximum(1000000)
        self.spinbox_x.setValue(100)
        label_y = QLabel(size)
        label_y.setText('y Size')
        self.spinbox_y = QSpinBox(size)
        self.spinbox_y.setMaximum(1000000)
        self.spinbox_y.setValue(100)
        apply_button = QPushButton("Apply", size)
        size_layout.addWidget(label_x, 0, 0)
        size_layout.addWidget(self.spinbox_x, 0, 1)
        size_layout.addWidget(label_y, 1, 0)
        size_layout.addWidget(self.spinbox_y, 1, 1)
        size_layout.addWidget(apply_button, 2, 1)
        # Buttons
        left_layout = QVBoxLayout()
        left.setLayout(left_layout)
        empty_button = QPushButton("Set to emtpy", left)
        fluid_button = QPushButton("Set to fluid", left)
        obstacle_button = QPushButton("Set to obstacle", left)
        # Picutre
        self.picture_label = QLabel(self)
        self.picture_label.setPixmap(QPixmap.fromImage(self.model.image))
        self.picture_label.setAlignment(Qt.AlignCenter)
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.picture_label)
        scroll_area.setAlignment(Qt.AlignCenter)
        scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Layout
        left_layout.addWidget(size)
        left_layout.addWidget(empty_button)
        left_layout.addWidget(fluid_button)
        left_layout.addWidget(obstacle_button)
        left_layout.addWidget(scroll_area)

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setDefaultSectionSize(25)
        self.table_view.verticalHeader().setDefaultSectionSize(25)
        self.table_view.setModel(self.model)

        splitter.addWidget(left)
        splitter.addWidget(self.table_view)

        # Connect signals
        empty_button.clicked.connect(partial(self.colorize_image, QColor(Qt.white)))
        empty_button.clicked.connect(self.show_image)
        fluid_button.clicked.connect(partial(self.colorize_image, QColor(Qt.blue)))
        fluid_button.clicked.connect(self.show_image)
        obstacle_button.clicked.connect(partial(self.colorize_image, QColor(Qt.black)))
        obstacle_button.clicked.connect(self.show_image)
        apply_button.clicked.connect(self.resize)
        apply_button.clicked.connect(self.show_image)

        # Set window
        self.setCentralWidget(splitter)
        # self.setGeometry(500, 500, 300, 200)
        self.setWindowTitle('Pixel editor')

    def new_file(self):
        self.model.image = QImage(self.spinbox_x.value(), self.spinbox_y.value(), QImage.Format_RGB32)
        self.model.image.fill(Qt.blue)
        self.show_image()
        self.save_as_action.setEnabled(True)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open picture', self.current_path, "Images (*.png)")
        if file_name[0]:
            if self.model.open_image(file_name[0]):
                self.spinbox_x.setValue(self.model.image.width())
                self.spinbox_y.setValue(self.model.image.height())
                self.current_path = file_name[0].rpartition('/')[0]
                self.save_action.setEnabled(True)
                self.save_as_action.setEnabled(True)
                self.show_image()

    def save_file(self):
        if self.model.file:
            self.model.save_image(self.model.file)

    def save_file_as(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save picture', self.current_path, "Images (*.png)")
        if file_name[0]:
            self.model.save_image(file_name[0])
            self.current_path = file_name[0].rpartition('/')[0]
            self.save_action.setEnabled(True)

    def colorize_image(self, color):
        selected = self.table_view.selectionModel().selectedIndexes()
        for index in selected:
            self.model.image.setPixel(index.column(), index.row(), color.rgb())
            self.model.dataChanged.emit(index, index)

    def resize(self):
        if self.model.image.isNull():
            self.new_file()
        self.model.image = self.model.image.scaled(self.spinbox_x.value(), self.spinbox_y.value())

    def show_image(self):
        self.picture_label.setPixmap(QPixmap.fromImage(self.model.image))
        self.picture_label.resize(self.picture_label.pixmap().size())


class PictureModel(QAbstractTableModel):
    def __init__(self, parent, file=""):
        super().__init__(parent)
        if not file:
            self._image = QImage()
        else:
            self._image = QImage(file)
        self.file = file

    def rowCount(self, parent):
        if self.image.isNull():
            return 0
        return self.image.height()

    def columnCount(self, parent):
        if self.image.isNull():
            return 0
        return self.image.width()

    def data(self, index, role):
        if role == Qt.BackgroundRole:
            rgb = self.image.pixel(index.column(), index.row())
            return QColor(rgb)
        return QVariant()

    def open_image(self, file_name):
        self.image.load(file_name)
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


if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
