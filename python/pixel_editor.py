#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QWidget, QPushButton,\
    QLabel, QSpinBox, QGridLayout, QVBoxLayout, QSplitter, QTableView, QFileDialog
from PyQt5.QtGui import QKeySequence, QColor, QImage
from PyQt5.QtCore import QDir, Qt
from functools import partial


from picture_model import PictureModel


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
        label_y = QLabel(size)
        label_y.setText('y Size')
        self.spinbox_y = QSpinBox(size)
        self.spinbox_y.setMaximum(1000000)
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
        left_layout.addWidget(size)
        left_layout.addWidget(empty_button)
        left_layout.addWidget(fluid_button)
        left_layout.addWidget(obstacle_button)
        left_layout.addStretch()

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setDefaultSectionSize(25)
        self.table_view.verticalHeader().setDefaultSectionSize(25)
        self.table_view.setModel(self.model)

        splitter.addWidget(left)
        splitter.addWidget(self.table_view)

        # Connect signals
        empty_button.clicked.connect(partial(self.colorize_image, QColor(Qt.white)))
        fluid_button.clicked.connect(partial(self.colorize_image, QColor(Qt.blue)))
        obstacle_button.clicked.connect(partial(self.colorize_image, QColor(Qt.black)))
        apply_button.clicked.connect(self.resize)

        # Set window
        self.setCentralWidget(splitter)
        # self.setGeometry(500, 500, 300, 200)
        self.setWindowTitle('Pixel editor')

    def new_file(self):
        self.model.image = QImage(self.spinbox_x.value(), self.spinbox_y.value(), QImage.Format_RGB32)
        self.model.image.fill(Qt.blue)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open picture', self.current_path, "Images (*.png)")
        if file_name[0]:
            if self.model.open_image(file_name[0]):
                self.spinbox_x.setValue(self.model.image.width())
                self.spinbox_y.setValue(self.model.image.height())
                self.current_path = file_name[0].rpartition('/')[0]
                self.save_action.setEnabled(True)
                self.save_as_action.setEnabled(True)

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
        if self.model.image is None:
            self.new_file()
        self.model.image = self.model.image.scaled(self.spinbox_x.value(), self.spinbox_y.value())

if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
