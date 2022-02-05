import os
from PySide2 import QtGui, QtWidgets
from PySide2.QtWidgets import QFileDialog, QWidget

from plugins.document_viewer.widget import DocumentViewer
from plugins.list_view.widget import ListView

class OpenDirectory(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        documentViewer = DocumentViewer(self.iface)

        self.fileName = self.iface.getFileName()
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        self.model = documentViewer.model
        self.layout = documentViewer.layout
        
        self.tree = documentViewer.tree
        self.tree.setModel(self.model)
        self.tree.hideColumn(3)
        self.tree.setMinimumWidth(300)

        self.layout.addWidget(self.tree)

        self.currentDirectory = self.iface.current_open_work_space

        if(self.currentDirectory == "None"):
            self.currentDirectory = os.path.expanduser("~/Desktop")

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        directory = QFileDialog.getExistingDirectory(self.iface, "Select directory", self.currentDirectory, QFileDialog.ShowDirsOnly)

        if not directory:
            return
        elif directory != "":
            try:
                if(current_file_open[1] == "singi"):
                    #Kada korisnik zatvori dokument tada se zatvori i text view
                    self.iface.list_view.hide()
                    self.iface.list_view.setWidget(QtWidgets.QListWidget())
                    self.iface.close_file_in_status_bar()
                    self.iface.position_for_new_element_in_xml = "direktorijum_0"
                    self.iface.position_for_new_page_in_document = str(None) # dokument_1_1
                    self.iface.last_selected_item = str(None) # dokument_1_1
                    self.iface.page_open = str(None) # page_1_1_1
                    self.iface.fileName = str(None) #openfilename
                    self.iface.file_in_current_directory = str(None)
                    self.iface.all_open_file_tab_widget = str(None)
                    self.iface.central_widget.clear()
                    self.iface.remove_singi_tool_bar()

            except IndexError:
                self.iface.list_view.hide()
                self.iface.list_view.setWidget(QtWidgets.QListWidget())
                self.iface.position_for_new_element_in_xml = "direktorijum_0"
                self.iface.position_for_new_page_in_document = str(None) # dokument_1_1
                self.iface.last_selected_item = str(None) # dokument_1_1
                self.iface.page_open = str(None) # page_1_1_1
                self.iface.fileName = str(None) #openfilename
                self.iface.file_in_current_directory = str(None)
                self.iface.all_open_file_tab_widget = str(None)
                self.iface.central_widget.clear()
                self.iface.remove_singi_tool_bar()
                self.iface.current_open_work_space = directory
                self.iface.currentdirectory = directory
                self.model.setRootPath(directory)
                self.tree.setRootIndex(self.model.index(directory))
                self.iface.dock_widget.setWidget(self.tree)
                self.iface.dock_widget.setMinimumWidth(300)
                self.iface.currentDirectoryName(self.model.rootPath())
                self.iface.add_dock_widget_after_disable()

            self.model.setRootPath(directory)
            self.tree.setRootIndex(self.model.index(directory))
            self.iface.current_open_work_space = directory
            self.iface.currentdirectory = directory
            self.iface.dock_widget.setWidget(self.tree)
            self.iface.dock_widget.setMinimumWidth(300)
            self.iface.currentDirectoryName(self.model.rootPath())
            self.iface.add_dock_widget_after_disable()

        else:
            try:
                if(current_file_open[1] == "singi"):
                    #Kada korisnik zatvori dokument tada se zatvori i text view
                    self.iface.list_view.hide()
                    self.iface.list_view.setWidget(QtWidgets.QListWidget())
                    self.iface.close_file_in_status_bar()
                    self.iface.position_for_new_element_in_xml = "direktorijum_0"
                    self.iface.position_for_new_page_in_document = str(None) # dokument_1_1
                    self.iface.last_selected_item = str(None) # dokument_1_1
                    self.iface.page_open = str(None) # page_1_1_1
                    self.iface.fileName = str(None) #openfilename
                    self.iface.file_in_current_directory = str(None)
                    self.iface.all_open_file_tab_widget = str(None)
                    self.iface.central_widget.clear()
                    self.iface.remove_singi_tool_bar()
            except IndexError:
                pass