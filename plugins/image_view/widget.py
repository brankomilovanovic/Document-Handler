from posixpath import abspath, dirname
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtWidgets import QWidget, QLabel
from pkg_resources import PEP440Warning

class ImageView(QWidget):
    widget_for = 1

    def __init__(self, iface):
        super().__init__(iface)

        self.iface = iface #MainWindow

    def setImage(self, imageUrl):
        label = QLabel(self)
        label.setPixmap(QtGui.QPixmap(imageUrl))
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.iface.central_widget.addTab(label, QtGui.QIcon("resources/icons/image.png"), QtCore.QFileInfo(imageUrl).fileName())