from asyncio.windows_events import NULL
import datetime
from fileinput import filename
from lib2to3.pgen2.token import OP
from operator import pos
import os
from tkinter import E
import xml.etree.ElementTree as et
from typing import List
from xmlrpc.client import boolean

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSettings, QSize, Qt
from PySide2.QtGui import QBrush, QPen, QPainter
from PyQt5.QtCore import (Qt, pyqtSignal)
from PySide2.QtWidgets import QDockWidget, QLabel, QMainWindow, QMessageBox, QStatusBar, QTextEdit, QGraphicsScene, QGraphicsView, QGraphicsItem, QTabWidget, QGraphicsSceneMouseEvent
import csv
from plugin_framework.plugin_registry import PluginRegistry
from plugins.list_view.widget import ListView

from ui.q_graphics_view import QGraphicsViewClass

from ui.slot_text import SlotText
from ui.slot_image import SlotImage
from ui.slot import Slot
from ui.activate_deactivate_plugin import ActivateDeactivatePlugin
from ui.close_file import CloseFile
from ui.new_directory import NewDirectory
from ui.new_document import NewDocument
from ui.new_page import NewPage
from ui.open_directory import OpenDirectory
from ui.open_file import OpenFile
from ui.save_file import SaveFile
from ui.new_slot import NewSlot

# FIXME: GRESKA SA PRIKAZOM TRENUTNO OTVORENOG FAJLA U STATUS BARU SVAKI PUT SE DODAJE NOVI FAJL, NE STOJI SA O JEDAN
# FIXME: KREIRATI DINAMICKI KREIRANU LISTU SA PLUGINIMA
# FIXME: KADA DEAKTIVIRAM PLUGIN I OPET AKTIVIRAM VRATI ME SVE NA POCETAK, A NE VRATI KAKO TREBA GDE SAM OSTAVIO SREDITI TO
# FIXME: GET PATH DIR U OPEN XML PRAVI VELIKI RPBOLEM POSLE NEKOG VREMENA SAMO PRESTANE DA RADI DOCK WIEVER
# TODO: NAPRAVITI DA KADA OBRISEN NEKI DOKUMENT URADI SE PROVERA JESU LI NJEGOVE STRANICE OTVORENE I OBRISATI STRANICE AKO POSTOJE

# FIXME: NESTO BAGUJE LIST VIEW KADA SE DAKTIVIRA POKRENE APLIKACIJA ON BUDE DEAKTIVIRAN I PONOVO GA AKTIVIRAMO
# TODO: KADA DODAJEM NOVI SLOT PREKO KOORDINATA URADITI PROVERU DA LI SE PODUDARA SA NEKIM DRUGIM

class MainWindow(QMainWindow):

    settings_ui_name = 'defaultUiwidget'
    settings_ui_user_name = 'user'
    _names_to_avoid = {}

    def __init__(self, title, icon, parent=None):
        super().__init__(parent)

        self.settings = QSettings( 'Singidunum', 'Rukovalac dokumentima' )
        # Initial window size/pos last saved. Use default values for first time
        windowScreenGeometry = self.settings.value("windowScreenGeometry")
        windowScreenState = self.settings.value("windowScreenState")
        if windowScreenGeometry:
            self.restoreGeometry(windowScreenGeometry)
        else:
            self.resize(1200, 800)

        if windowScreenState:
            self.restoreState(windowScreenState)

        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        self.dict_for_read_save_data = {}
        try:
            reader = csv.reader(open('appData.csv', 'r'))
            for row in reader:
                k, v = row
                self.dict_for_read_save_data[k] = v
    
            #Kada otvorimo xml fajl setujemo mu pocetnu poziciju koja ce biti ako nije promenjena
            #Uvek je pocetna pozicija (direktorijum_0)
            self.current_open_work_space = self.dict_for_read_save_data["current_open_work_space"]
            self.position_for_new_element_in_xml = self.dict_for_read_save_data["position_for_new_element_in_xml"]
            self.position_for_new_page_in_document = self.dict_for_read_save_data["position_for_new_page_in_document"] # dokument_1_1
            self.last_selected_item = self.dict_for_read_save_data["last_selected_item"] # dokument_1_1
            self.page_open = self.dict_for_read_save_data["page_open"] # page_1_1_1
            self.fileName = self.dict_for_read_save_data["fileName"] #openfilename
            self.currentdirectory = self.dict_for_read_save_data["currentdirectory"] #currentdirectory
            self.file_in_current_directory = self.dict_for_read_save_data["file_in_current_directory"] #fileincurrentdirectory
            self.all_open_file_tab_widget = self.dict_for_read_save_data["all_open_file_tab_widget"] #dobijamo listu svih fajlova otvorenih u central widgetu

            self.dock_widget_plugin = self.dict_for_read_save_data["dock_widget_plugin"] #dobijamo listu svih fajlova otvorenih u central widgetu
            self.list_view_plugin = self.dict_for_read_save_data["list_view_plugin"] #dobijamo listu svih fajlova otvorenih u central widgetu
            self.image_view_plugin = self.dict_for_read_save_data["image_view_plugin"] #dobijamo listu svih fajlova otvorenih u central widgetu

        except FileNotFoundError:
            self.current_open_work_space = str(None)
            self.position_for_new_element_in_xml = "direktorijum_0"
            self.position_for_new_page_in_document = str(None) # dokument_1_1
            self.last_selected_item = str(None) # dokument_1_1
            self.page_open = str(None) # page_1_1_1
            self.fileName = str(None) #openfilename
            self.currentdirectory = str(None) #currentdirectory
            self.file_in_current_directory = str(None) #fileincurrentdirectory
            self.all_open_file_tab_widget = str(None) #lista svih fajlova otvorenih u central widgetu
            self.dock_widget_plugin = False
            self.list_view_plugin = False
            self.image_view_plugin = False

        #meni
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        #toolbar
        self.tool_bar = QtWidgets.QToolBar("Toolbar",self)
        self.tool_bar.setObjectName("Toolbar")
        self.tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tool_bar.setIconSize(QSize(20, 20))
        self.tool_bar.setMovable(False)
        self.tool_bar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        #statusbar
        self.status_bar = QStatusBar(self)
        self.update_time()
        #timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)  # 1000ms = 1s
        self.timer.start()
        #centralwidget
        #dockwidget
        self.dock_widget = QtWidgets.QDockWidget(self)
        self.dock_widget.setObjectName("DocumentViewer")
        #dockwidget for list view
        self.list_view = QtWidgets.QDockWidget(self)
        self.list_view.setObjectName("ListView")
        self.central_widget = QtWidgets.QTabWidget(self)
        self.central_widget.setTabsClosable(True)
        self.central_widget.tabCloseRequested.connect(self.delete_tab)
        self.central_widget.currentChanged.connect(self.change_tab)
        #widgets in stacked widget
        self.widgets = {}
        #Uzimamo klasu list vieuw plugina
        self.list_view_class = ListView(self) # dodeljujemo napravljenu listu
        self.list_view_class.hide()
        self.list_widget_id_for_add_new_page = {}
        #qgraphisscenes
        self.scene = QGraphicsScene()
        self.selected_slot = str(None)

        self.document = None # otvoreni dokument (trenutno aktivni dokument)

        self.actions_dict = {
            "newDirectory": QtWidgets.QAction(QtGui.QIcon("resources/icons/newDirectory.png"), "&New collection", self),
            "openDirectory": QtWidgets.QAction(QtGui.QIcon("resources/icons/openDirectory.png"), "&Open Workspace", self),
            "closeDirectory": QtWidgets.QAction(QtGui.QIcon("resources/icons/closeWorkspace.png"), "&Close Workspace", self),
            "newDocument": QtWidgets.QAction(QtGui.QIcon("resources/icons/newFile.png"), "&New Document", self),
            "openFile": QtWidgets.QAction(QtGui.QIcon("resources/icons/openFile.png"), "&Open Document", self),
            "saveFile": QtWidgets.QAction(QtGui.QIcon("resources/icons/saveFile.png"), "&Save Document", self),
            "closeFile": QtWidgets.QAction(QtGui.QIcon("resources/icons/closeFile.png"), "&Close Document", self),
            "quit": QtWidgets.QAction(QtGui.QIcon("resources/icons/quit.png"), "&Quit", self),

            ###################################################################################################

            "undo": QtWidgets.QAction(QtGui.QIcon("resources/icons/undo.png"), "&Undo", self),
            "redo": QtWidgets.QAction(QtGui.QIcon("resources/icons/redo.png"), "&Redo", self),
            "cut": QtWidgets.QAction(QtGui.QIcon("resources/icons/cut.png"), "&Cut", self),
            "copy": QtWidgets.QAction(QtGui.QIcon("resources/icons/copy.png"), "&Copy", self),
            "paste": QtWidgets.QAction(QtGui.QIcon("resources/icons/paste.png"), "&Paste", self),

            ###################################################################################################

            "addSlot": QtWidgets.QAction(QtGui.QIcon("resources/icons/add_slot.png"), "&Add new slot", self),
            "removeSlot": QtWidgets.QAction(QtGui.QIcon("resources/icons/delete_icon.png"), "&Remove slot", self),

            ###################################################################################################

            "activate_deactivate": QtWidgets.QAction(QtGui.QIcon("resources/icons/activate.png"), "&Activate/&Deactivate", self),

            ###################################################################################################

            "about": QtWidgets.QAction(QtGui.QIcon("resources/icons/about.png"), "&About", self)
        }

        self._bind_actions()

        self._populate_tool_bar()
        self._populate_menu_bar()

        self.setMenuBar(self.menu_bar)
        self.addToolBar(self.tool_bar)
        self.setStatusBar(self.status_bar)
        self.setCentralWidget(self.central_widget)

        #########################################################################################################################################

        plugin_registry = PluginRegistry("plugins", self)
        #Dobijanje broja direktorijuma u plugins fajlu
        for i in range(len([name for name in os.listdir("plugins") if os.path.isfile(os.path.join("plugins", name)) + 1])):
            if (plugin_registry.aktiviranje() == True):
                
                if(plugin_registry._get_plugin_name(i) == "Document viewer"):
                    #if(self.dock_widget_plugin == "True"):
                    if(self.current_open_work_space != "None"):
                        plugin_registry.activate(i)
                    else:
                        plugin_registry.activate(i)
                        plugin_registry.deactivate(i)

                elif(plugin_registry._get_plugin_name(i) == "List view"):
                    #if(self.list_view_plugin == "True"):
                    if(self.page_open != "None"):
                        plugin_registry.activate(i)
                    else:
                        plugin_registry.activate(i)
                        plugin_registry.deactivate(i)

                elif(plugin_registry._get_plugin_name(i) == "Image view"):
                    if(self.image_view_plugin == "True"):
                        plugin_registry.activate(i)
                    else:
                        plugin_registry.activate(i)
                        plugin_registry.deactivate(i)

                '''else:
                    plugin_registry.activate(i)
            else:
                plugin_registry.deactivate(i)  '''

#########################################################################################################################################
        
        self.check_singi_file_open_in_list_view()
        self.check_singi_file_open_in_document_viewer()

################################################# OPEN FILE IN TEXT EDIT IF OPEN BEFORE CLOSE APP #####################################
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")
        if(self.all_open_file_tab_widget != "None"):
            if(self.fileName.split(".")[1] == "singi"):
                self.list_view_class.read_slot_data()
                self.set_singi_tool_bar() 
                self.read_all_slots_from_page()
            else:
                imageExt = ['.png', '.gif', ".jpeg", ".jpg"]
                fileExt = ['.txt', '.py', '.singi']

                filename = self.fileName
                file_in_current_directory = self.file_in_current_directory

                all_tabs_list = self.all_open_file_tab_widget.split(",")
                for tab in all_tabs_list:
                    if tab.endswith(tuple(imageExt)):
                        if(self.image_view_activate == True):
                            label = QLabel(self)
                            label.setPixmap(QtGui.QPixmap(tab))
                            label.setAlignment(QtCore.Qt.AlignCenter)
                            self.central_widget.addTab(label, QtGui.QIcon("resources/icons/image.png"), QtCore.QFileInfo(tab).fileName())

                        elif(self.image_view_activate == False):
                            QMessageBox.information(self, "Open image", "Image view plugin je deaktiviran.")

                    elif tab.endswith(tuple(fileExt)):
                        try:
                            with open(self.file_in_current_directory ,'r') as f:
                                tekst = f.read()
                                                
                            fileName = QtCore.QFileInfo(tab).fileName()
                            new_tab = QtWidgets.QWidget()
                            text = QtWidgets.QTextEdit(lineWrapMode=QtWidgets.QTextEdit.NoWrap)
                            text.setText(tekst)
                            TextBoxlayout = QtWidgets.QVBoxLayout(new_tab)
                            TextBoxlayout.addWidget(text)
                            self.central_widget.addTab(new_tab, QtGui.QIcon("resources/icons/document.png"), fileName)

                        except UnicodeDecodeError as type_error:
                            QMessageBox.information(self, "Open a new document", "Greska!\nFormat nije podrzan")
                    else:
                        QMessageBox.information(self, "Open a new document", "Greska!\nFormat nije podrzan")

                self.fileName = filename
                self.file_in_current_directory = file_in_current_directory

                select_tab = []
                for tabs in all_tabs_list:
                    select_tab.append(QtCore.QFileInfo(tabs).fileName())

                self.central_widget.setCurrentIndex(select_tab.index(self.fileName))

#########################################################################################################################################
    
    def _populate_tool_bar(self):
        self.tool_bar.addAction(self.actions_dict["openDirectory"])

        self.actions_dict["newDirectory"].setToolTip("Create a new collection")
        self.tool_bar.addAction(self.actions_dict["newDirectory"])   

        self.actions_dict["newDocument"].setToolTip("Create a new document")
        self.tool_bar.addAction(self.actions_dict["newDocument"])

        self.actions_dict["openFile"].setToolTip("Open a file")
        self.tool_bar.addAction(self.actions_dict["openFile"])

        self.actions_dict["saveFile"].setToolTip("Save a file")
        self.tool_bar.addAction(self.actions_dict["saveFile"])

        self.tool_bar.addSeparator()
        ##################################################################
        self.actions_dict["undo"].setToolTip("Undo action in file")
        self.tool_bar.addAction(self.actions_dict["undo"])

        self.actions_dict["redo"].setToolTip("Redo action in file")
        self.tool_bar.addAction(self.actions_dict["redo"])

        self.tool_bar.addSeparator()

        self.actions_dict["cut"].setToolTip("Cut select text")
        self.tool_bar.addAction(self.actions_dict["cut"])

        self.actions_dict["copy"].setToolTip("Copy select text")
        self.tool_bar.addAction(self.actions_dict["copy"])

        self.actions_dict["paste"].setToolTip("Paste the copied text")
        self.tool_bar.addAction(self.actions_dict["paste"])
        self.tool_bar.addSeparator()

        ##################################################################

        self.actions_dict["quit"].setToolTip("Exit of application")
        self.tool_bar.addAction(self.actions_dict["quit"])

    def _populate_menu_bar(self):
        file_menu = QtWidgets.QMenu("&File")
        edit_menu = QtWidgets.QMenu("&Edit")
        plugin_menu = QtWidgets.QMenu("&Plugin")
        help_menu = QtWidgets.QMenu("&Help")
        
        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(plugin_menu)
        self.menu_bar.addMenu(help_menu)

        file_menu.addAction(self.actions_dict["openDirectory"])
        file_menu.addAction(self.actions_dict["newDirectory"])
        file_menu.addAction(self.actions_dict["closeDirectory"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions_dict["openFile"])
        file_menu.addAction(self.actions_dict["newDocument"])
        file_menu.addAction(self.actions_dict["saveFile"])
        file_menu.addAction(self.actions_dict["closeFile"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions_dict["quit"])
        ##################################################################
        edit_menu.addAction(self.actions_dict["undo"])
        edit_menu.addAction(self.actions_dict["redo"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions_dict["cut"])
        edit_menu.addAction(self.actions_dict["copy"])
        edit_menu.addAction(self.actions_dict["paste"])
        ##################################################################
        plugin_menu.addAction(self.actions_dict["activate_deactivate"])
        ##################################################################
        help_menu.addAction(self.actions_dict["about"])

    def _bind_actions(self):
        self.actions_dict["newDirectory"].setShortcut("Ctrl+D")
        self.actions_dict["newDirectory"].triggered.connect(self.new_directory)

        self.actions_dict["openDirectory"].setShortcut("Ctrl+O")
        self.actions_dict["openDirectory"].triggered.connect(self.open_directory)

        self.actions_dict["closeDirectory"].setShortcut("Ctrl+Shift+Q")
        self.actions_dict["closeDirectory"].triggered.connect(self.close_directory)

        self.actions_dict["newDocument"].setShortcut("Ctrl+N")
        self.actions_dict["newDocument"].triggered.connect(self.new_document)

        self.actions_dict["saveFile"].setShortcut("Ctrl+S")
        self.actions_dict["saveFile"].triggered.connect(self.save_file)
        
        self.actions_dict["openFile"].setShortcut("Ctrl+Shift+O")
        self.actions_dict["openFile"].triggered.connect(self.open_file)

        self.actions_dict["closeFile"].setShortcut("Ctrl+Shift+C")
        self.actions_dict["closeFile"].triggered.connect(self.close_file)

        self.actions_dict["quit"].setShortcut("Ctrl+Q")
        self.actions_dict["quit"].triggered.connect(self.close_application)

    ###########################################################################################

        self.actions_dict["undo"].setShortcut("Ctrl+Z")
        self.actions_dict["undo"].triggered.connect(self.undo)

        self.actions_dict["redo"].setShortcut("Ctrl+Y")
        self.actions_dict["redo"].triggered.connect(self.redo)

        self.actions_dict["cut"].setShortcut("Ctrl+X")
        self.actions_dict["cut"].triggered.connect(self.cut)

        self.actions_dict["copy"].setShortcut("Ctrl+C")
        self.actions_dict["copy"].triggered.connect(self.copy)

        self.actions_dict["paste"].setShortcut("Ctrl+V")
        self.actions_dict["paste"].triggered.connect(self.paste)

    ###########################################################################################

        self.actions_dict["addSlot"].triggered.connect(self.addSlot)
        self.actions_dict["removeSlot"].triggered.connect(self.removeSlot)

    ###########################################################################################

        self.actions_dict["activate_deactivate"].triggered.connect(self.activate_deactivate)
        
    ###########################################################################################

        self.actions_dict["about"].triggered.connect(self.about)
    
    def new_directory(self):
        if(self.current_open_work_space == "None"):
            QMessageBox.information(self, "New collection", "Greska! Niste otvorili ni jedan work space!")
        else:
            NewDirectory(self)

    def open_directory(self):
        OpenDirectory(self)
    
    def close_directory(self):
        self.current_open_work_space = str(None)
        self.position_for_new_element_in_xml = "direktorijum_0"
        self.position_for_new_page_in_document = str(None) # dokument_1_1
        self.last_selected_item = str(None) # dokument_1_1
        self.page_open = str(None) # page_1_1_1
        self.fileName = str(None) #openfilename
        self.currentdirectory = str(None) #currentdirectory
        self.file_in_current_directory = str(None) #fileincurrentdirectory
        self.all_open_file_tab_widget = str(None)
        self.dock_widget.hide()
        self.list_view.hide()
        self.dock_widget.setWidget(QtWidgets.QTreeView())
        self.list_view.setWidget(QtWidgets.QListWidget())

    def new_document(self):
        if(self.current_open_work_space == "None"):
            QMessageBox.information(self, "New Document", "Greska! Niste otvorili ni jedan work space!")
        else:
            NewDocument(self)

    def new_page(self):
        NewPage(self)
    
    def open_file(self):
        if(self.current_open_work_space == "None"):
            QMessageBox.information(self, "Open Document", "Greska! Niste otvorili ni jedan work space!")
        else:
            OpenFile(self)
        
    def save_file(self):
        if(self.fileName == "None"):
            QMessageBox.information(self, "Save Document", "Greska! Niste otvorili ni jedan dokument!")
        else:
            SaveFile(self)

    def close_file(self):
        CloseFile(self)

    #################################################################################################################################

    def undo(self):
        try:
            select_tab = []
            for tabs in self.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            w = self.central_widget.widget(select_tab.index(self.fileName))   
            text_edit = w.findChild(QtWidgets.QTextEdit)

            QtWidgets.QTextEdit.undo(text_edit)

        except ValueError as open_xml_file:
            pass

    def redo(self):
        try:
            select_tab = []
            for tabs in self.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            w = self.central_widget.widget(select_tab.index(self.fileName))   
            text_edit = w.findChild(QtWidgets.QTextEdit)

            QtWidgets.QTextEdit.redo(text_edit)
            
        except ValueError as open_xml_file:
            pass

    def cut(self):
        try:
            select_tab = []
            for tabs in self.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            w = self.central_widget.widget(select_tab.index(self.fileName))   
            text_edit = w.findChild(QtWidgets.QTextEdit)

            QtWidgets.QTextEdit.cut(text_edit)
            
        except ValueError as open_xml_file:
            pass

    def copy(self):
        try:
            select_tab = []
            for tabs in self.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            w = self.central_widget.widget(select_tab.index(self.fileName))   
            text_edit = w.findChild(QtWidgets.QTextEdit)

            QtWidgets.QTextEdit.copy(text_edit)
            
        except ValueError as open_xml_file:
            pass

    def paste(self):
        try:
            select_tab = []
            for tabs in self.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())

            w = self.central_widget.widget(select_tab.index(self.fileName))   
            text_edit = w.findChild(QtWidgets.QTextEdit)

            QtWidgets.QTextEdit.paste(text_edit)
            
        except ValueError as open_xml_file:
            pass

    #################################################################################################################################

    def change_tab(self,index):
        try:
            if(self.fileName.split(".")[1] == "singi"):
                if(self.central_widget.count() == 0):
                    self.all_open_file_tab_widget = str(None)
                    self.page_open = str(None)
                else:
                    self.page_open = self.central_widget.tabText(index)
                    self.read_all_slots_from_page()

                self.selected_slot = str(None)

            else:
                if(self.central_widget.count() == 0):
                    self.fileName = str(None)
                    self.file_in_current_directory = str(None)
                else:
                    self.fileName = self.central_widget.tabText(index)
                    all_tabs_list = self.all_open_file_tab_widget.split(",")
                    self.file_in_current_directory = all_tabs_list[index]
        except IndexError as file_not_singi:
            pass

    def delete_tab(self, index):
        all_tabs_list = self.all_open_file_tab_widget.split(",")
        all_tabs_list.pop(index)

        if(self.fileName.split(".")[1] == "singi"):
            if(len(all_tabs_list) == 0):
                self.all_open_file_tab_widget = str(None)
                self.page_open = str(None)
            else:
                element_number = 1
                self.all_open_file_tab_widget = ""
                for tabs in all_tabs_list:
                    if(element_number == 1):
                        self.all_open_file_tab_widget = tabs
                    else:
                        self.all_open_file_tab_widget += "," + tabs
                    element_number += 1

            self.central_widget.removeTab(index)
            from ui.open_xml_file import OpenXMLFile
            OpenXMLFile(self).update_document_viewer_and_list_view()

        else:
            if(len(all_tabs_list) == 0):
                self.all_open_file_tab_widget = str(None)
                self.file_in_current_directory = str(None)
                self.fileName = str(None)
            else:
                element_number = 1
                self.all_open_file_tab_widget = ""
                for tabs in all_tabs_list:
                    if(element_number == 1):
                        self.all_open_file_tab_widget = tabs
                    else:
                        self.all_open_file_tab_widget += "," + tabs
                    element_number += 1

            self.central_widget.removeTab(index)      

    #################################################################################################################################

    def update_time(self):
        current_time = datetime.datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
        self.status_bar.showMessage(current_time)

    #################################################################################################################################

    def status_bar_message_save_file(self, fileName):
        self.status_bar.showMessage("Sacuvali ste fajl: " + fileName, 3000)

    #################################################################################################################################

    def close_file_in_status_bar(self):
        self.status_bar.insertPermanentWidget(0, QLabel(""), 0)
        
    def open_file_in_status_bar(self, fileName):
        self.fileName = fileName
        self.labelFileName = QLabel(f"{self.getFileName()}")
        #self.status_bar.addPermanentWidget(self.labelFileName)

    #################################################################################################################################

    #Vraca ime trenutno otvorenog fajla
    def getFileName(self):
        return self.fileName

    #################################################################################################################################

    def currentDirectoryName(self, directory):
        self.currentdirectory = directory

    def getCurrentDirectory(self):
        return self.currentdirectory

    def currentFileInDirectory(self, file):
        self.file_in_current_directory = file

    def getFileInCurrentDirectory(self):
        return self.file_in_current_directory

    #################################################################################################################################
    
    def activate_deactivate(self):
        form = ActivateDeactivatePlugin(self)
        form.exec_()

    #################################################################################################################################

    def about(self):
        QMessageBox.information(self, "About", "Naziv: Rukovalac dokumentima\nVerzija: 1.0\nNapravio: Branko Milovanović")

    #################################################################################################################################
    
    # Pop up poruka za proveru izlaska iz aplikacije
    def close_application(self):
        reply = QMessageBox.question(self, "Izaberite opciju", "Da li ste sigurni da zelite zatvoriti aplikaciju?", QMessageBox.Yes | QMessageBox.No)
        if (reply == QMessageBox.Yes):
            self.actions_dict["quit"].triggered.connect(self.close)

    #################################################################################################################################

    def add_dock_widget(self, widget):
        """
        Adds widget to dock widget
        """
        self.widgets[widget.widget_for] = self.dock_widget.widget()
        self.dock_widget.setWidget(widget)
        self.dock_widget.setWindowTitle("Document viewer")
        self.dock_widget.setMinimumWidth(300)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock_widget.setVisible(True)
    
    def add_dock_widget_after_disable(self):
        print("Activated - Document viewer")
        if( self.current_open_work_space == "None"):
            self.dock_widget.setWidget(QtWidgets.QTreeView())

        self.dock_widget.setVisible(True)

    def remove_dock_widget(self):
        self.dock_widget.setVisible(False)

    def add_list_view(self, widget):
        """
        Adds widget to dock widget
        """
        self.widgets[widget.widget_for] = self.list_view.widget()
        self.list_view.setWidget(widget)
        self.list_view.setWindowTitle("Page viewer")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.list_view)
        self.list_view.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.list_view.setVisible(True)

    def add_list_view_after_disable(self):
        print("Activated - View list")
        self.list_view.setVisible(True)

    def remove_list_view(self):
        self.list_view.setVisible(False)

    def activate_image_view(self):
        self.image_view_activate = True

    def deactivate_image_view(self):
        self.image_view_activate = False

#################################################################################################################################

    def read_all_slots_from_page(self): 
        treeForRead = et.parse(self.file_in_current_directory)
        self.dict_slots = {}
        self.dict_parent_slot = {} # Setujemo povo recnik da bude prazan
        for root in treeForRead.getiterator():
            for parent in root.findall('document'):
                for child in parent.findall("page"):
                    for slot in child.findall("slot"):
                        self.dict_parent_slot.update({slot.attrib.get("id") : child.attrib.get("id")}) # Dodajemo u listu pageove i njegov dokument
                        self.dict_slots[slot.attrib.get("id")] = slot.attrib.get("id"), slot.attrib.get("positionX"), slot.attrib.get("positionY"), slot.attrib.get("slot_width"), slot.attrib.get("slot_height"), slot.attrib.get("type"), slot.text  #Dodajemo sve pageove u recnik sa njihovim atributima
        
        self.rotate_key_and_page(self.dict_parent_slot) # Zamena kljuca(child) sa vrednosti(parent)
        if(self.dict.get(self.page_open) != None): # self.dict nece bit None tek kada odaberemo neki dokument koji ima pageove, data se pravi novi dict sa pageovima i dokumentom
            self.dict_parent_slot = {}
            self.dict_parent_slot.update({self.page_open : self.dict.get(self.page_open)}) # dodajemo self.dict sa zamenjenim vrednostima u self.dict_parent_page (ucitava pageove samo jednog dokumenta)

        remove_characters = ["[", "]", "'", "(", ")", "dict_values", " "] # lista nepotrebnih karaktera iz liste
        vrednosti_recnika = str(self.dict_parent_slot.values()) # Dobavljamo vrednosti iz recnika
        for character in remove_characters:
                vrednosti_recnika = vrednosti_recnika.replace(character, "") # Brisemo nepotrebne karaktere iz recnika
          
        vrednosti_recnika = vrednosti_recnika.split(",") # Delimo pageove u listu
        select_tab = []
        for tabs in self.all_open_file_tab_widget.split(","):
            select_tab.append(tabs)

        self.scene.clear()
        return_error_just_one_time = True
        
        if("None" not in select_tab):
            try:
                for slots in vrednosti_recnika:
                    if(self.dict_slots.get(slots)[5] == "image"):
                        image = SlotImage(self, self.dict_slots.get(slots)[0], float(self.dict_slots.get(slots)[1]), float(self.dict_slots.get(slots)[2]), float(self.dict_slots.get(slots)[3]), float(self.dict_slots.get(slots)[4]), self.dict_slots.get(slots)[6])
                        self.scene.addItem(image)
                    elif(self.dict_slots.get(slots)[5] == "txt"):
                        text = SlotText(self, self.dict_slots.get(slots)[0], float(self.dict_slots.get(slots)[1]), float(self.dict_slots.get(slots)[2]), float(self.dict_slots.get(slots)[3]), float(self.dict_slots.get(slots)[4]), self.dict_slots.get(slots)[6])
                        self.scene.addItem(text)
                    else:
                        rectangle = Slot(self, self.dict_slots.get(slots)[0], float(self.dict_slots.get(slots)[1]), float(self.dict_slots.get(slots)[2]), float(self.dict_slots.get(slots)[3]), float(self.dict_slots.get(slots)[4]))
                        self.scene.addItem(rectangle)

                    current_tab_widget = self.central_widget.widget(select_tab.index(self.page_open))
                    graphicsView = current_tab_widget.findChild(QtWidgets.QGraphicsView)
                    graphicsView.setScene(self.scene)
                    graphicsView.setParent(self.central_widget.widget(select_tab.index(self.page_open)))
            except TypeError as page_is_empty:
                if(return_error_just_one_time == True):
                    print("Stranica je prazna! Main Window error!")
                    return_error_just_one_time = False
                else:
                    pass

        from ui.open_xml_file import OpenXMLFile
        OpenXMLFile(self).update_document_viewer_and_list_view()

    def addSlot(self):  
        position_x = 0
        position_y = 0
        slot_width = 200
        slot_height = 100

        select_tab = []
        for tabs in self.all_open_file_tab_widget.split(","):
            select_tab.append(tabs)

        self.scene.clear()
        try:
            id = NewSlot(self, position_x, position_y, slot_width, slot_height).slot_new_id
            rectangle = Slot(self, id, position_x, position_y, slot_width, slot_height)
            self.scene.addItem(rectangle)
            current_tab_widget = self.central_widget.widget(select_tab.index(self.page_open))
            graphicsView = current_tab_widget.findChild(QtWidgets.QGraphicsView)
            graphicsView.setScene(self.scene)
            graphicsView.setParent(self.central_widget.widget(select_tab.index(self.page_open)))
            self.read_all_slots_from_page()

        except AttributeError as page_not_open:
            QMessageBox.information(self, "Create a new slot", "Greska!\nNiste otvorili ni jednu stranicu." )

    def rotate_key_and_page(self, d):
        self.dict = {}
        for k, v in d.items():
            if v in self.dict:
                self.dict[v].append(k)
            else:
                self.dict[v] = [k]
        return self.dict

#################################################################################################################################

    def closeEvent(self, e):
        # Write window size and position to config file
        self.settings.setValue( "windowScreenGeometry", self.saveGeometry())
        self.settings.setValue( "windowScreenState", self.saveState())
        e.accept()
        self.data = [
            ['current_open_work_space', self.current_open_work_space],
            ['position_for_new_element_in_xml', self.position_for_new_element_in_xml],
            ['position_for_new_page_in_document', self.position_for_new_page_in_document],
            ['last_selected_item', self.last_selected_item],
            ['page_open', self.page_open],
            ['fileName', self.fileName],
            ['currentdirectory', self.currentdirectory],
            ['file_in_current_directory', self.file_in_current_directory],
            ['all_open_file_tab_widget', self.all_open_file_tab_widget],
            ['dock_widget_plugin', self.dock_widget.isVisible()],
            ['list_view_plugin', self.list_view.isVisible()],
            ['image_view_plugin', self.image_view_activate]
        ]
        with open('appData.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.data)
        
    # OPEN SINGI WORKSPACE IN DOCKUMENT VIEWER
    def check_singi_file_open_in_document_viewer(self):
        from ui.open_xml_file import OpenXMLFile
        try:
            fileName = str(self.fileName).split(".")
            try:
                if(self.dock_widget_plugin == "True"):
                    if(fileName[1] == "singi"):
                        fileOpen = open(self.file_in_current_directory, 'r').read()
                        OpenXMLFile(self).XMLinTreeViewUpdate(fileOpen, QtCore.QFileInfo(self.file_in_current_directory).fileName())
                        self.open_file_in_status_bar(QtCore.QFileInfo(self.file_in_current_directory).fileName())
                        self.set_singi_tool_bar()

            except IndexError:
                pass

        except FileNotFoundError:
            QMessageBox.information(self, "Open WorkSpace", "Greska!\nWorkspace u kojem ste radili je obrisan.")
            self.current_open_work_space = str(None)
            self.position_for_new_element_in_xml = "direktorijum_0"
            self.position_for_new_page_in_document = str(None) # dokument_1_1
            self.last_selected_item = str(None) # dokument_1_1
            self.page_open = str(None) # page_1_1_1
            self.fileName = str(None) #openfilename
            self.currentdirectory = str(None) #currentdirectory
            self.file_in_current_directory = str(None) #fileincurrentdirectory
            self.all_open_file_tab_widget = str(None)
            self.dock_widget_plugin = False
            self.list_view_plugin = False
            self.image_view_plugin = False
            self.dock_widget.hide()
            self.list_view.hide()
            self.dock_widget.setWidget(QtWidgets.QTreeView())
            self.list_view.setWidget(QtWidgets.QListWidget())

     # OPEN SINGI DOCUMENT IN LIST VIEW
    def check_singi_file_open_in_list_view(self):
        try:
            if(self.position_for_new_page_in_document != "None"):
                from ui.open_xml_file import OpenXMLFile
                OpenXMLFile(self).update_document_viewer_and_list_view()
        except IndexError:
            pass

    def set_singi_tool_bar(self):
        self.tool_bar.removeAction(self.actions_dict["quit"])

        self.actions_dict["addSlot"].setToolTip("Add new slot")
        self.tool_bar.addAction(self.actions_dict["addSlot"])

        self.actions_dict["removeSlot"].setToolTip("Remove select slot")
        self.tool_bar.addAction(self.actions_dict["removeSlot"])

    def remove_singi_tool_bar(self):
        self.tool_bar.removeAction(self.actions_dict["addSlot"])
        self.tool_bar.removeAction(self.actions_dict["removeSlot"])

        self.tool_bar.addAction(self.actions_dict["quit"])

    def removeSlot(self):
        if(self.selected_slot != "None"):
            tree = et.parse(self.file_in_current_directory)
            root = tree.getroot()

            for element in root.iter():
                for child in list(element):
                    if child.attrib.get("id") == self.selected_slot:
                        element.remove(child)
                        print("Uspesno ste obrisali slot ID: " + self.selected_slot)

                        xmldata = et.tostring(root, encoding="unicode")
                        myfile = open(self.file_in_current_directory, "w")
                        myfile.write(xmldata)
                        myfile.close()
                        self.read_all_slots_from_page()
                        self.selected_slot = str("None")
        else:
            QMessageBox.information(self, "Delete slot", "Greska!\nNiste odabrali ni jedan slot." )