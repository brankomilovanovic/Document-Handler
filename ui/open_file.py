import os
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtCore import QFileInfo, QUrl
from PySide2.QtWidgets import QWidget
from plugins.list_view.widget import ListView

from ui.open_xml_file import OpenXMLFile

class OpenFile(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.listViewPlugin = ListView(self.iface) # dodeljujemo list view plugin performance
        self.list_view = self.listViewPlugin.list_view # dodeljujemo napravljenu listu

        self.fileName = self.iface.getFileName()
        current_file_open = self.fileName + ".file"
        current_file_open = str(current_file_open).split(".")

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        self.currentDirectory = self.iface.getCurrentDirectory()

        file = QtWidgets.QFileDialog.getOpenFileName(self,"Select file", self.currentDirectory, "Singi Files (*.singi);;Text Files (*.txt *.py)", "", options=options)

        if file[1] == "Singi Files (*.singi)":
            fileOpen = open(file[0], 'r').read()
            OpenXMLFile(self.iface).XMLinTreeView(fileOpen, QFileInfo(file[0]).fileName())
            self.iface.open_file_in_status_bar(QFileInfo(file[0]).fileName())
            self.iface.list_view.hide()
            self.iface.list_view.setWidget(QtWidgets.QListWidget())

            self.iface.position_for_new_page_in_document = str(None)
            self.iface.position_for_new_element_in_xml = str("direktorijum_0")
            self.iface.last_selected_item = str(None)
            self.iface.page_open = str(None)

            self.iface.current_open_work_space = os.path.dirname(file[0])
            self.iface.currentdirectory = os.path.dirname(file[0])
            self.iface.file_in_current_directory = file[0]

        else:
            try:
                if(current_file_open[1] == "singi"):
                    #Kada korisnik zatvori dokument tada se zatvori i text view
                    self.iface.close_file_in_status_bar()
                    self.iface.list_view.hide()
                    self.iface.list_view.setWidget(QtWidgets.QListWidget())
                    self.iface.position_for_new_page_in_document = str(None)
                    self.iface.position_for_new_element_in_xml = str("direktorijum_0")
                    self.iface.last_selected_item = str(None)
                    self.iface.page_open = str(None)

                path = file[0]
                self.iface.current_open_work_space = os.path.dirname(path)
                self.iface.currentdirectory = os.path.dirname(path)
                self.iface.file_in_current_directory = path

                with open(path ,'r') as f:
                    tekst = f.read()

                    new_tab = QWidget()
                    text = QtWidgets.QTextEdit(lineWrapMode=QtWidgets.QTextEdit.NoWrap)
                    text.setText(tekst)
                    text.setUndoRedoEnabled(True)
                    TextBoxlayout = QtWidgets.QVBoxLayout(new_tab)
                    TextBoxlayout.addWidget(text)
                    self.iface.central_widget.addTab(new_tab, QtGui.QIcon("resources/icons/document.png"), QtCore.QFileInfo(file[0]).fileName())

                    if(self.iface.all_open_file_tab_widget == "None"):
                        self.iface.all_open_file_tab_widget = QtCore.QFileInfo(file[0]).fileName()
                    else:
                        self.iface.all_open_file_tab_widget += "," + QtCore.QFileInfo(file[0]).fileName()
                                  
                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(QtCore.QFileInfo(tabs).fileName())
                        
                    self.iface.fileName = QtCore.QFileInfo(file[0]).fileName()
                    self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.fileName))

            except FileNotFoundError as not_found:
                pass # Kada ne odabere ni jedan fajl za otvaranje, da ne prijavljuje gresku