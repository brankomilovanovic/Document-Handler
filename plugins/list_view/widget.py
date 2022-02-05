from lib2to3.pgen2.token import OP
from posixpath import abspath, dirname
from PySide2 import QtCore, QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox, QVBoxLayout, QWidget, QGraphicsView, QListView
import xml.etree.ElementTree as et

from ui.q_graphics_view import QGraphicsViewClass

class ListView(QWidget):
    widget_for = 1

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.actions_dict = {
            "newPage": QtWidgets.QAction(QtGui.QIcon("resources/icons/newFile.png"), "", self),
            "removePage": QtWidgets.QAction(QtGui.QIcon("resources/icons/remove_page.png"), "", self),
            "pageNext": QtWidgets.QAction(QtGui.QIcon("resources/icons/page_next.png"), "", self),
            "pageBack": QtWidgets.QAction(QtGui.QIcon("resources/icons/page_back.png"), "", self)
        }

        #listwidget
        self.list_view = QtWidgets.QListWidget()
        self.list_view.setMinimumWidth(180)

        #QListWidget::item:selected { background: rgb(255,255,255); }
        #QListWidget::item { margin: 4px; background: rgb(255,255,255);  }

        self.list_view.setStyleSheet("""
        QListView::item:selected:active:hover{
            background: rgb(255,255,255);
        }
        QListView::item:selected:active:!hover{
            background: rgb(255,255,255);
        }
        QListView::item:selected:!active{
            background: rgb(255,255,255);
        }
        QListView::item:!selected:hover{
            background-color:gray;
        }
        QScrollBar:vertical {              
            border: none;
            background:white;
            width:3px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0 rgb(151, 148, 148), stop: 0.5 rgb(151, 148, 148), stop:1 rgb(151, 148, 148));
            min-height: 0px;
        }
        QScrollBar::add-line:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0 rgb(151, 148, 148), stop: 0.5 rgb(151, 148, 148),  stop:1 rgb(151, 148, 148));
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0  rgb(151, 148, 148), stop: 0.5 rgb(151, 148, 148),  stop:1 rgb(151, 148, 148));
            height: 0 px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
    """)

        #toolbar
        self.tool_bar = QtWidgets.QToolBar("Toolbar",self)
        self.tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tool_bar.setIconSize(QtCore.QSize(30, 30))
        self.tool_bar.setMovable(False)
        self.tool_bar.setFixedHeight(30)
        self._populate_tool_bar()

        #layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tool_bar)
        self.layout.addWidget(self.list_view)
        self.layout.setAlignment(self.tool_bar, QtCore.Qt.AlignHCenter)
        self.setLayout(self.layout)

    def _populate_tool_bar(self):
        self.actions_dict["newPage"].setToolTip("Create a new page")
        self.actions_dict["newPage"].setShortcut("Ctrl+Shift+S")
        self.actions_dict["newPage"].triggered.connect(self.new_page)
        self.tool_bar.addAction(self.actions_dict["newPage"])

        self.actions_dict["removePage"].setToolTip("Remove a select page")
        self.actions_dict["removePage"].setShortcut("Ctrl+Shift+X")
        self.actions_dict["removePage"].triggered.connect(self.remove_page)
        self.tool_bar.addAction(self.actions_dict["removePage"])

        self.actions_dict["pageNext"].setToolTip("Next Page")
        self.actions_dict["pageNext"].setShortcut("Ctrl+N")
        self.actions_dict["pageNext"].triggered.connect(self.next_page)
        self.tool_bar.addAction(self.actions_dict["pageNext"])

        self.actions_dict["pageBack"].setToolTip("Back Page")
        self.actions_dict["pageBack"].setShortcut("Ctrl+Shift+S")
        self.actions_dict["pageBack"].triggered.connect(self.back_page)
        self.tool_bar.addAction(self.actions_dict["pageBack"])
    
    def new_page(self):
        self.iface.new_page()

    def next_page(self):
        page_lists = []
        tree = et.parse(self.iface.file_in_current_directory)
        if(self.iface.position_for_new_page_in_document != "None"):
            dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"
            for element in tree.find(dir_select):
                page_lists.append(element.attrib.get("id"))

            try:
                try:
                    index = page_lists.index(self.iface.page_open)
                except ValueError as page_exist_but_not_in_this_list:
                    index = -1
                self.iface.page_open = page_lists[index + 1]
                all_tabs_list = self.iface.all_open_file_tab_widget.split(",")
                
                check_tabs_if_exist = True
                if self.iface.page_open not in all_tabs_list:
                    check_tabs_if_exist = False
                else:
                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(tabs)
                
                if check_tabs_if_exist == False: 

                    new_tab = QWidget()
                    #graphicsView = QGraphicsView()
                    graphicsView = QGraphicsViewClass(self.iface)
                    layout = QtWidgets.QVBoxLayout(new_tab)
                    layout.addWidget(graphicsView)
                    self.iface.central_widget.addTab(new_tab, QtGui.QIcon("resources/icons/page.png"), self.iface.page_open)

                    if(self.iface.all_open_file_tab_widget == "None"):
                        self.iface.all_open_file_tab_widget = self.iface.page_open
                    else:
                        self.iface.all_open_file_tab_widget += "," + self.iface.page_open

                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(tabs)

                #####
                self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.page_open))
                self.iface.read_all_slots_from_page()
                from ui.open_xml_file import OpenXMLFile
                OpenXMLFile(self.iface).update_document_viewer_and_list_view()

            except IndexError as no_more_pages:
                print("Nema vise stranica. error: list_view.widget")

    def back_page(self):
        page_lists = []
        tree = et.parse(self.iface.file_in_current_directory)
        if(self.iface.position_for_new_page_in_document != "None"):
            dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"
            for element in tree.find(dir_select):
                page_lists.append(element.attrib.get("id"))

            try:
                try:
                    index = page_lists.index(self.iface.page_open)
                except ValueError as page_exist_but_not_in_this_list:
                    index = 1
                self.iface.page_open = page_lists[index - 1]
                all_tabs_list = self.iface.all_open_file_tab_widget.split(",")
                
                check_tabs_if_exist = True
                if self.iface.page_open not in all_tabs_list:
                    check_tabs_if_exist = False
                else:
                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(tabs)
                
                if check_tabs_if_exist == False: 

                    new_tab = QWidget()
                    #graphicsView = QGraphicsView()
                    graphicsView = QGraphicsViewClass(self.iface)
                    layout = QtWidgets.QVBoxLayout(new_tab)
                    layout.addWidget(graphicsView)
                    self.iface.central_widget.addTab(new_tab, QtGui.QIcon("resources/icons/page.png"), self.iface.page_open)

                    if(self.iface.all_open_file_tab_widget == "None"):
                        self.iface.all_open_file_tab_widget = self.iface.page_open
                    else:
                        self.iface.all_open_file_tab_widget += "," + self.iface.page_open

                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(tabs)

                #####
                self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.page_open))
                self.iface.read_all_slots_from_page()
                from ui.open_xml_file import OpenXMLFile
                OpenXMLFile(self.iface).update_document_viewer_and_list_view()

            except IndexError as no_more_pages:
                print("Nema vise stranica. error: list_view.widget")

    def remove_page(self):
        currentItemName = self.iface.page_open
        # Delimo ime pagea i id (da ostane samo id)
        if(currentItemName != "None"):
            tree = et.parse(self.iface.file_in_current_directory)
            root = tree.getroot()

            dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"
            try:
                if(len(tree.find(dir_select)) != 1):
                    for element in root.iter():
                        for child in list(element):
                            if child.attrib.get("id") == currentItemName:
                                element.remove(child)
                                print("Uspesno ste obrisali page: " + currentItemName)

                                select_tab = []
                                for tabs in self.iface.all_open_file_tab_widget.split(","):
                                    select_tab.append(tabs)
                                self.iface.delete_tab(select_tab.index(self.iface.page_open))
                                
                                xmldata = et.tostring(root, encoding="unicode")
                                myfile = open(self.iface.file_in_current_directory, "w")
                                myfile.write(xmldata)
                                myfile.close()
                                self.iface.read_all_slots_from_page()

                else:
                    QMessageBox.information(self.iface, "Delete page", "Greska!\nNe mozete obrisati zadnju stranicu." )
            except ValueError as not_select_page:
                QMessageBox.information(self.iface, "Delete page", "Greska!\nNiste odabrali ni jednu stranicu." )
        else:
            QMessageBox.information(self.iface, "Delete page", "Greska!\nNiste odabrali ni jednu stranicu." )

    def read_slot_data(self):
        all_tabs_list = self.iface.all_open_file_tab_widget.split(",")
        tabs_id = []
        for tab in self.iface.all_open_file_tab_widget.split(","):
            tabs_id.append(tab)

        page_open = self.iface.page_open

        number = 0
        for tab_id in tabs_id:
            new_tab = QWidget()
            #graphicsView = QGraphicsView()
            graphicsView = QGraphicsViewClass(self.iface)
            layout = QtWidgets.QVBoxLayout(new_tab)
            layout.addWidget(graphicsView)
            self.iface.central_widget.addTab(new_tab, QtGui.QIcon("resources/icons/page.png"), tab_id)
            number += 1

        self.iface.page_open = page_open
        select_tab = []
        for tabs in all_tabs_list:
            select_tab.append(tabs)

        self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.page_open))
