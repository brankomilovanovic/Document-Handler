import os
import sys
from PySide2 import QtWidgets, QtGui
from ui.main_window import MainWindow

if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow("Rukovalac dokumentima - by Singidunum - v1.0 (2021)", QtGui.QIcon("resources/icons/applicationImage.png"))   
    main_window.show()
    sys.exit(application.exec_())