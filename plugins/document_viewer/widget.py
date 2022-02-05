import os
from posixpath import abspath, dirname
from tabnanny import check
from xmlrpc.client import boolean

from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QAbstractItemView, QAction, QHeaderView, QInputDialog, QLineEdit, QMenu, QMessageBox, QTreeView, QTreeWidget, QWidget, QLabel
from plugins.image_view.widget import ImageView

from ui.open_xml_file import OpenXMLFile

class DocumentViewer(QWidget):
    widget_for = 0

    def __init__(self, iface):
        super().__init__(iface)

        self.iface = iface #MainWindow
        
        work_space_last_open = self.iface.current_open_work_space

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(work_space_last_open)
        self.model.setReadOnly(False)

        self.iface.currentDirectoryName(self.model.rootPath())

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(work_space_last_open))

        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)

        #----------add context menu--------------------------------------
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        #---------------------------------------------------------------------

        self.tree.hideColumn(1) # Sakriva kolonu byte
        self.tree.hideColumn(3)
        self.tree.setColumnWidth(0,200) # Setuje velicinu prve kolone, da se vidi sve iz stabla
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

        self.tree.clicked.connect(self.select_file)

    def select_file(self, index):
        imageExt = ['.png', '.gif', ".jpeg", ".jpg"]
        fileExt = ['.txt', '.py', '.singi']

        indexItem = self.model.index(index.row(), 0, index.parent())

        file = self.model.filePath(indexItem)

        print(file)

        self.model.setRootPath(file)
        self.iface.currentDirectoryName(self.model.rootPath())
        self.iface.currentFileInDirectory(file)  

        all_tabs_list = self.iface.all_open_file_tab_widget.split(",")
        check_tabs_if_exist = True
        if file not in all_tabs_list:
            check_tabs_if_exist = False
        else:
            select_tab = []
            for tabs in self.iface.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            self.iface.central_widget.setCurrentIndex(select_tab.index(QtCore.QFileInfo(file).fileName()))
        
        if check_tabs_if_exist == False:       
            if file.endswith(tuple(imageExt)):
                if(self.iface.image_view_activate == True):

                    ImageView(self.iface).setImage(file)

                    if(self.iface.all_open_file_tab_widget == "None"):
                        self.iface.all_open_file_tab_widget = file
                    else:
                        self.iface.all_open_file_tab_widget += "," + file

                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(QtCore.QFileInfo(tabs).fileName())

                    self.iface.fileName = QtCore.QFileInfo(file).fileName()
                    self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.fileName))

                elif(self.iface.image_view_activate == False):
                    QMessageBox.information(self, "Open a new file", "Image view plugin je deaktiviran.")

            elif file.endswith(tuple(fileExt)):
                if(QtCore.QFileInfo(file).fileName().split(".")[1] == "singi"):
                    fileOpen = open(file, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeView(fileOpen, QtCore.QFileInfo(file).fileName())
                    self.iface.central_widget.clear()
                    self.iface.all_open_file_tab_widget = str(None)
                    self.iface.set_singi_tool_bar() # set tool bar menu actions for work with singi document

                else:
                    try:
                        with open(file ,'r') as f:
                            tekst = f.read()

                        new_tab = QWidget()
                        text = QtWidgets.QTextEdit(lineWrapMode=QtWidgets.QTextEdit.NoWrap)
                        text.setText(tekst)
                        text.setUndoRedoEnabled(True)
                        TextBoxlayout = QtWidgets.QVBoxLayout(new_tab)
                        TextBoxlayout.addWidget(text)
                        self.iface.central_widget.addTab(new_tab, QIcon("resources/icons/document.png"), QtCore.QFileInfo(file).fileName())

                        if(self.iface.all_open_file_tab_widget == "None"):
                            self.iface.all_open_file_tab_widget = file
                        else:
                            self.iface.all_open_file_tab_widget += "," + file
                                  
                        select_tab = []
                        for tabs in self.iface.all_open_file_tab_widget.split(","):
                            select_tab.append(QtCore.QFileInfo(tabs).fileName())
                        
                        self.iface.fileName = QtCore.QFileInfo(file).fileName()
                        self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.fileName))

                    except UnicodeDecodeError as type_error:
                        QMessageBox.information(self, "Open a new file", "Greska!\nFormat nije podrzan")
            else:
                QMessageBox.information(self, "Open a new file", "Greska!\nFormat nije podrzan")

    def _show_context_menu(self, position):
        indexes = self.tree.selectedIndexes()

        items = []
        for index in indexes:
            item = self.model.filePath(index)
            if(item not in items): #Provera ako je item vec dodat da ga ne dodaje opet u listu
                items.append(item)
            else:
                pass

        delete_action = QAction("Delete Selected");
        delete_action.triggered.connect(lambda: self.delete_action(items))
        delete_action.setIcon(QIcon("resources/icons/delete_icon.png"));

        rename_action = QAction("Rename Selected")
        rename_action.triggered.connect(lambda: self.rename_action(items))
        rename_action.setIcon(QIcon("resources/icons/rename_icon.png"));

        copy_action = QAction("Copy")
        #copy_action.triggered.connect(lambda: self.copy_action)
        copy_action.setIcon(QIcon("resources/icons/copy.png"));
        copy_action.setEnabled(False)

        cut_action = QAction("Cut")
        #cut_action.triggered.connect(lambda: self.cut_action)
        cut_action.setIcon(QIcon("resources/icons/cut.png"));
        cut_action.setEnabled(False)

        paste_action = QAction("Paste")
        #paste_action.triggered.connect(lambda: self.paste_action)
        paste_action.setIcon(QIcon("resources/icons/paste.png"));
        paste_action.setEnabled(False)
        
        menu = QMenu(self.tree)
        menu.addAction(copy_action)
        menu.addAction(cut_action)
        menu.addAction(paste_action)
        menu.addSeparator()
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        menu.exec_(self.tree.mapToGlobal(position))

    def delete_action(self, item):
        item_selected = ""
        for items in item:
            item_selected = items
        
        try:
            os.remove(item_selected)
        except (PermissionError): # Ako je direktorijum brisemo reko remove dir
            os.rmdir(item_selected)

    def rename_action(self, item):
        item_selected = ""
        for items in item:
            item_selected = items
        
        try:
            fileFormat = QtCore.QFileInfo(item_selected).fileName().split(".")[1]
        except (IndexError):
            fileFormat = None

        inputDialog =  QInputDialog(self)
        text, save = inputDialog.getText(self.iface, "Rename", "Unesite novo ime fajla:          ", QLineEdit.Normal, "")

        if save:
            if text != "":
                # Provera da li je fajl ako je fajl ima ekstenziju ako je dokument onda je None
                if(fileFormat != None):
                    if not os.path.exists(text + "." + fileFormat):
                        old_name = item_selected
                        new_name = os.path.dirname(item_selected) + "/" + text + "." + fileFormat
                        os.rename(old_name, new_name)
                    else:
                        QMessageBox.information(self.iface, "Rename", "Greska!\nVec postoji dokument sa tim imenom.")
                else:
                    if not os.path.exists(text):
                        old_name = item_selected
                        new_name = os.path.dirname(item_selected) + "/" + text
                        os.rename(old_name, new_name)
                    else:
                        QMessageBox.information(self.iface, "Rename", "Greska!\nVec postoji direktorijum sa tim imenom.")
            else:
                QMessageBox.information(self.iface, "Rename", "Greska!\nNiste uneli ime dokument." )