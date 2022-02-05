import os, sys
from PySide2 import QtGui, QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import QFileInfo

from plugin_framework.plugin_registry import PluginRegistry
from ui.open_xml_file import OpenXMLFile

class ActivateDeactivatePlugin(QtWidgets.QDialog):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface
        self.plugin_registry = PluginRegistry("plugins", self.iface)

        self.plugins = [
        'Plugin - Document Viewer | Core version: v1.0.0',
        'Plugin - List Viewer | Core version: v1.0.0',
        'Plugin - Image View | Core version: v1.0.0',
        ]

        self.name = "Activate/Deactivate Plugin"
        self.icon = QtGui.QIcon('resources/icons/applicationImage.png')
        self.model = QtGui.QStandardItemModel()
        self.listView = QtWidgets.QListView()

        for string in self.plugins:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            
            if(string == self.plugins[0]):
                if(self.iface.dock_widget.isVisible() == True):
                    item.setCheckState(QtCore.Qt.Checked)                    
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)

            if(string == self.plugins[1]):
                if(self.iface.list_view.isVisible() == True):
                    item.setCheckState(QtCore.Qt.Checked)                    
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)

            if(string == self.plugins[2]):
                if(self.iface.image_view_activate == True):
                    item.setCheckState(QtCore.Qt.Checked)                    
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)

            self.model.appendRow(item)

        self.listView.setModel(self.model)

        self.okButton = QtWidgets.QPushButton('OK')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.selectButton = QtWidgets.QPushButton('Select All')
        self.unselectButton = QtWidgets.QPushButton('Unselect All')

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.selectButton)
        hbox.addWidget(self.unselectButton)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.listView)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setWindowTitle(self.name)
        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

        self.fileName = self.iface.fileName
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")
        try:
            try:
                if(current_file_open[1] == "singi"):
                    fileOpen = open(self.iface.file_in_current_directory, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.fileName).fileName())
            except IndexError:
                pass
        except TypeError:
            pass

    def onAccepted(self):
        self.choices = [self.model.item(i).text() for i in range(self.model.rowCount()) if self.model.item(i).checkState() == QtCore.Qt.Checked]
        self.accept()

        if self.choices == []:
            self.plugin_registry.deactivate(0)
            self.plugin_registry.deactivate(1)
            self.plugin_registry.deactivate(2)
        
        else:
            if self.plugins[0] in self.choices:
                self.iface.add_dock_widget_after_disable() # PRIVREMENO
                #self.plugin_registry.activate(0)
                self.iface.dock_widget_plugin == "True"
            else:
                self.plugin_registry.deactivate(0)

            if self.plugins[1] in self.choices:
                self.iface.add_list_view_after_disable() # PRIVREMENO
                self.iface.list_view_plugin == "True"
                #self.plugin_registry.activate(1)
            else:
                self.plugin_registry.deactivate(1)

            if self.plugins[2] in self.choices:
                self.plugin_registry.activate(2)
                from ui.open_xml_file import OpenXMLFile
                OpenXMLFile(self.iface).update_document_viewer_and_list_view()
            else:
                self.plugin_registry.deactivate(2)
                from ui.open_xml_file import OpenXMLFile
                OpenXMLFile(self.iface).update_document_viewer_and_list_view()

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
