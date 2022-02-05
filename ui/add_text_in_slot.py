import os, sys
from PySide2 import QtGui, QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QTextEdit, QPushButton, QHBoxLayout
import xml.etree.ElementTree as et

from plugin_framework.plugin_registry import PluginRegistry
from ui.open_xml_file import OpenXMLFile

class AddTextInSlot(QtWidgets.QDialog):

    def __init__(self, iface, slot_id, text):
        super().__init__()

        self.iface = iface
        self.slot_id = slot_id
        self.slot_text = text
        self.setWindowIcon(QtGui.QIcon('resources/icons/applicationImage.png'))
        self.setWindowTitle("Text slot")
        self.resize(300,270)

        self.textEdit = QTextEdit()
        self.input_text = QPushButton("Input text in slot")
        self.cancel_input = QPushButton("Cancel")

        self.actions_dict = {
            "undo": QtWidgets.QAction(QtGui.QIcon("resources/icons/undo.png"), "&Undo", self),
            "redo": QtWidgets.QAction(QtGui.QIcon("resources/icons/redo.png"), "&Redo", self),
            "cut": QtWidgets.QAction(QtGui.QIcon("resources/icons/cut.png"), "&Cut", self),
            "copy": QtWidgets.QAction(QtGui.QIcon("resources/icons/copy.png"), "&Copy", self),
            "paste": QtWidgets.QAction(QtGui.QIcon("resources/icons/paste.png"), "&Paste", self)
        }

        self.tool_bar = QtWidgets.QToolBar("Toolbar",self)
        self.tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tool_bar.setIconSize(QtCore.QSize(20, 20))
        self.tool_bar.setMovable(False)
        self.tool_bar.setFixedHeight(50)
        
        self._populate_tool_bar()

        hbox = QHBoxLayout()
        hbox.addWidget(self.input_text)
        hbox.addWidget(self.cancel_input)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tool_bar)
        vbox.setAlignment(self.tool_bar, QtCore.Qt.AlignHCenter)
        vbox.addWidget(self.textEdit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        if(self.slot_text != "None"):
            self.textEdit.setPlainText(self.slot_text)

        self.input_text.clicked.connect(self.input_text_clicked)
        self.cancel_input.clicked.connect(self.reject)

    def _populate_tool_bar(self):
        self.actions_dict["undo"].setToolTip("Undo action in file")
        self.actions_dict["undo"].triggered.connect(self.undo)
        self.tool_bar.addAction(self.actions_dict["undo"])

        self.actions_dict["redo"].setToolTip("Redo action in file")
        self.actions_dict["redo"].triggered.connect(self.redo)
        self.tool_bar.addAction(self.actions_dict["redo"])

        self.tool_bar.addSeparator()

        self.actions_dict["cut"].setToolTip("Cut select text")
        self.actions_dict["cut"].triggered.connect(self.cut)
        self.tool_bar.addAction(self.actions_dict["cut"])

        self.actions_dict["copy"].setToolTip("Copy select text")
        self.actions_dict["copy"].triggered.connect(self.copy)
        self.tool_bar.addAction(self.actions_dict["copy"])

        self.actions_dict["paste"].setToolTip("Paste the copied text")
        self.actions_dict["paste"].triggered.connect(self.paste)
        self.tool_bar.addAction(self.actions_dict["paste"])

    def undo(self):
        QtWidgets.QTextEdit.undo(self.textEdit)

    def redo(self):
        QtWidgets.QTextEdit.redo(self.textEdit)

    def cut(self):
        print("cut")
        QtWidgets.QTextEdit.cut(self.textEdit)

    def copy(self):
        QtWidgets.QTextEdit.copy(self.textEdit)

    def paste(self):
        QtWidgets.QTextEdit.paste(self.textEdit)

    def input_text_clicked(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()
        for element in root.iter():
            for child in list(element):
                if child.attrib.get("id") == self.slot_id:
                    child.set("type", "txt")
                    child.text = self.textEdit.toPlainText()

        xmldata = et.tostring(root, encoding="unicode")
        myfile = open(self.iface.file_in_current_directory, "w")
        myfile.write(xmldata)
        myfile.close()

        self.iface.read_all_slots_from_page()

        self.accept()


    def cancel_input_clciked(self):
        pass