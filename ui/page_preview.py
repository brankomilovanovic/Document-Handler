from typing import List
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtWidgets import QGraphicsView
import xml.etree.ElementTree as et
import os

from ui.q_graphics_view import QGraphicsViewClass

class PagePreview(QGraphicsView):

    def __init__(self, iface, page_id):
        super().__init__()
        self.iface = iface
        self.page_id = page_id
        self.dict = {}
        self.graphicsScene = QtWidgets.QGraphicsScene()
        self.setFixedHeight(120)

        self.read_all_slots_from_page()

    def read_all_slots_from_page(self):  
        treeForRead = et.parse(self.iface.file_in_current_directory)
        self.dict_slots = {}
        self.dict_parent_slot = {} # Setujemo povo recnik da bude prazan
        for root in treeForRead.getiterator():
            for parent in root.findall('document'):
                for child in parent.findall("page"):
                    for slot in child.findall("slot"):
                        self.dict_parent_slot.update({slot.attrib.get("id") : child.attrib.get("id")}) # Dodajemo u listu pageove i njegov dokument
                        self.dict_slots[slot.attrib.get("id")] = slot.attrib.get("id"), slot.attrib.get("positionX"), slot.attrib.get("positionY"), slot.attrib.get("slot_width"), slot.attrib.get("slot_height"), slot.attrib.get("type"), slot.text  #Dodajemo sve pageove u recnik sa njihovim atributima
        
        self.rotate_key_and_page(self.dict_parent_slot) # Zamena kljuca(child) sa vrednosti(parent)

        if(self.dict.get(self.page_id) != None): # self.dict nece bit None tek kada odaberemo neki dokument koji ima pageove, data se pravi novi dict sa pageovima i dokumentom
            self.dict_parent_slot = {}
            self.dict_parent_slot.update({self.page_id : self.dict.get(self.page_id)}) # dodajemo self.dict sa zamenjenim vrednostima u self.dict_parent_page (ucitava pageove samo jednog dokumenta

        remove_characters = ["[", "]", "'", "(", ")", "dict_values", " "] # lista nepotrebnih karaktera iz liste
        vrednosti_recnika = str(self.dict_parent_slot.values()) # Dobavljamo vrednosti iz recnika

        for character in remove_characters:
                vrednosti_recnika = vrednosti_recnika.replace(character, "") # Brisemo nepotrebne karaktere iz recnika
          
        vrednosti_recnika = vrednosti_recnika.split(",") # Delimo pageove u listu

        self.graphicsScene.clear()

        for slots in vrednosti_recnika:
            if(len(slots.split("_")) == 5):
                try:
                    if(self.dict_slots.get(slots)[5] == "image"):
                        file_exist = os.path.exists(self.dict_slots.get(slots)[6])
                        if(self.iface.image_view_activate == False or file_exist == False):
                            pixmapFile = QtGui.QPixmap('resources/icons/image_not_availble.jpg')
                            pixmapFile = pixmapFile.scaled(float(self.dict_slots.get(slots)[3])/10, float(self.dict_slots.get(slots)[4])/10, aspectMode=QtGui.Qt.IgnoreAspectRatio)
                            pixmap = QtWidgets.QGraphicsPixmapItem()
                            pixmap.setPos(float(self.dict_slots.get(slots)[1])/10, float(self.dict_slots.get(slots)[2])/10)
                            pixmap.setPixmap(pixmapFile)
                            self.graphicsScene.addItem(pixmap)
                        else:
                            pixmapFile = QtGui.QPixmap(self.dict_slots.get(slots)[6])
                            pixmapFile = pixmapFile.scaled(float(self.dict_slots.get(slots)[3])/10, float(self.dict_slots.get(slots)[4])/10, aspectMode=QtGui.Qt.IgnoreAspectRatio)
                            pixmap = QtWidgets.QGraphicsPixmapItem()
                            pixmap.setPos(float(self.dict_slots.get(slots)[1])/10, float(self.dict_slots.get(slots)[2])/10)
                            pixmap.setPixmap(pixmapFile)
                            self.graphicsScene.addItem(pixmap)
                    elif(self.dict_slots.get(slots)[5] == "txt"):
                        text = QtWidgets.QGraphicsTextItem()
                        text.setPos(float(self.dict_slots.get(slots)[1])/10, float(self.dict_slots.get(slots)[2])/10)
                        text.document().setPageSize(QtCore.QSizeF(float(self.dict_slots.get(slots)[3])/5, float(self.dict_slots.get(slots)[4])/6))
                        text.document().setDocumentMargin(2)
                        font = QtGui.QFont()
                        font.setPixelSize(1)
                        text.setFont(font)

                        cursor = text.textCursor()
                        format = cursor.charFormat()
                        format.setLayoutDirection(QtCore.Qt.RightToLeft)
                        cursor.setCharFormat(format)
                        text.setTextCursor(cursor)
                        text.setPlainText(self.dict_slots.get(slots)[6])
                        self.graphicsScene.addItem(text)
                    else:
                        rectangle = QtWidgets.QGraphicsRectItem()
                        rectangle.setPos(float(self.dict_slots.get(slots)[1])/10, float(self.dict_slots.get(slots)[2])/10)
                        rectangle.setRect(0, 0, float(self.dict_slots.get(slots)[3])/10, float(self.dict_slots.get(slots)[4])/10)
                        self.graphicsScene.addItem(rectangle)
                except TypeError as page_is_empty:
                    print("Stranica je prazna! Page Preview error!")

        self.setScene(self.graphicsScene)

    def rotate_key_and_page(self, d):
        self.dict = {}
        for k, v in d.items():
            if v in self.dict:
                self.dict[v].append(k)
            else:
                self.dict[v] = [k]
        return self.dict

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        delete_action = QtWidgets.QAction("Remove Slot")
        delete_action.triggered.connect(lambda: self.delete_action())
        delete_action.setIcon(QtGui.QIcon("resources/icons/delete_icon.png"))

        add_slot_up = QtWidgets.QAction("Add new slot up")
        add_slot_up.triggered.connect(lambda: self.add_slot_up())
        add_slot_up.setIcon(QtGui.QIcon("resources/icons/add_slot.png"))

        add_slot_down = QtWidgets.QAction("Add new slot down")
        add_slot_down.triggered.connect(lambda: self.add_slot_down())
        add_slot_down.setIcon(QtGui.QIcon("resources/icons/add_slot.png"))
        
        menu = QtWidgets.QMenu()
        menu.addAction(add_slot_up)
        menu.addAction(add_slot_down)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec_(event.globalPos())

    def add_slot_down(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()

        dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"

        list_all_page = []
        list_all_id = []

        for element in tree.iter():
            for i in tree.findall('.//page'):
                if(i.attrib.get("id") not in list_all_page):
                    list_all_page.append(i.attrib.get("id"))

        for item in list_all_page:
            item = str(item).replace("page_", "") # BRISEMO PAGE_ OSTAVLJAMO SAMO NJIGOVE ID
            list_all_id.append(item)

        list_all_id = [word for line in list_all_id for word in line.split("_")] # SPLITUJEMO LISTU SVE BROJEVE OD PAGE_1_1_1 DELIMO U POSEBAN INDEKS
        list_all_id = list_all_id[2::3] # PRESKACEMO SVAKI TECI ELEMENT DA BI DOBILI SAMO IDEVE PAGEOVA, ID JE JEDINSTVEN ZA CEO FAJL
            
        #PRETVARAMO STRING LISTU U INTIGER
        for i in range(0, len(list_all_id)):
            list_all_id[i] = int(list_all_id[i])

        najveci_id = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
        for number in list_all_id:
            if number > najveci_id:
                najveci_id = number

        dokument = str(self.iface.position_for_new_page_in_document).replace("dokument", "page")
        pages_id_for_delete = []
        current_element_id = ""
        new_element_for_insert = ""

        for element in tree.find(dir_select):
            if(element.attrib.get("id") == self.page_id):
                new_element_for_insert = et.Element('page',{'name':f'{najveci_id + 1}','id':f'{dokument}_{najveci_id + 1}'})
                current_element_id = element.attrib.get("id")

            pages_id_for_delete.append(element.attrib.get("id"))

        string = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"

        element_add_exist = False
        for element in root.iter():
            for child in list(element):
                for i in pages_id_for_delete:
                    if(child.attrib.get("id") == current_element_id):
                        if(element_add_exist == False):
                            element.insert(self.iface.list_widget_id_for_add_new_page.get(current_element_id) + 1, new_element_for_insert)
                            element_add_exist = True

        xmldata = et.tostring(root, encoding="unicode")
        myfile = open(self.iface.file_in_current_directory, "w")
        myfile.write(xmldata)
        myfile.close()
        self.iface.read_all_slots_from_page()

    def add_slot_up(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()

        dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"

        list_all_page = []
        list_all_id = []

        for element in tree.iter():
            for i in tree.findall('.//page'):
                if(i.attrib.get("id") not in list_all_page):
                    list_all_page.append(i.attrib.get("id"))

        for item in list_all_page:
            item = str(item).replace("page_", "") # BRISEMO PAGE_ OSTAVLJAMO SAMO NJIGOVE ID
            list_all_id.append(item)

        list_all_id = [word for line in list_all_id for word in line.split("_")] # SPLITUJEMO LISTU SVE BROJEVE OD PAGE_1_1_1 DELIMO U POSEBAN INDEKS
        list_all_id = list_all_id[2::3] # PRESKACEMO SVAKI TECI ELEMENT DA BI DOBILI SAMO IDEVE PAGEOVA, ID JE JEDINSTVEN ZA CEO FAJL
            
        #PRETVARAMO STRING LISTU U INTIGER
        for i in range(0, len(list_all_id)):
            list_all_id[i] = int(list_all_id[i])

        najveci_id = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
        for number in list_all_id:
            if number > najveci_id:
                najveci_id = number

        dokument = str(self.iface.position_for_new_page_in_document).replace("dokument", "page")
        pages_id_for_delete = []
        current_element_id = ""
        new_element_for_insert = ""

        for element in tree.find(dir_select):
            if(element.attrib.get("id") == self.page_id):
                new_element_for_insert = et.Element('page',{'name':f'{najveci_id + 1}','id':f'{dokument}_{najveci_id + 1}'})
                current_element_id = element.attrib.get("id")

            pages_id_for_delete.append(element.attrib.get("id"))

        string = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"

        element_add_exist = False
        for element in root.iter():
            for child in list(element):
                for i in pages_id_for_delete:
                    if(child.attrib.get("id") == current_element_id):
                        if(element_add_exist == False):
                            element.insert(self.iface.list_widget_id_for_add_new_page.get(current_element_id), new_element_for_insert)
                            element_add_exist = True

        xmldata = et.tostring(root, encoding="unicode")
        myfile = open(self.iface.file_in_current_directory, "w")
        myfile.write(xmldata)
        myfile.close()
        self.iface.read_all_slots_from_page()
    
    def delete_action(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()

        dir_select = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"

        if(len(tree.find(dir_select)) != 1):
            for element in root.iter():
                for child in list(element):
                    if child.attrib.get("id") == self.page_id:
                        element.remove(child)
                        print("Uspesno ste obrisali slot PAGE ID: " + self.page_id)

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
            QtWidgets.QMessageBox.information(self.iface, "Delete page", "Greska!\nNe mozete obrisati zadnju stranicu." )

    def mousePressEvent(self, event):
        self.iface.page_open = self.page_id # Setujemo trenutno otvoreni page da bi mogli kasnije da cuvamo nakon edita (item[1] = page_1_1_1)

        all_tabs_list = self.iface.all_open_file_tab_widget.split(",")
        check_tabs_if_exist = True
        if self.iface.page_open not in all_tabs_list:
            check_tabs_if_exist = False
        else:
            select_tab = []
            for tabs in self.iface.all_open_file_tab_widget.split(","):
                select_tab.append(tabs)

            self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.page_open))
        
        if check_tabs_if_exist == False: 
            new_tab = QtWidgets.QWidget()
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

            self.iface.central_widget.setCurrentIndex(select_tab.index(self.iface.page_open))
            self.iface.read_all_slots_from_page()