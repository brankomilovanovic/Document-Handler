import os
from pathlib import Path
from PySide2.QtWidgets import QListWidgetItem
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QFileDialog, QMessageBox, QWidget
import xml.etree.ElementTree as ET
from ui.open_xml_file import OpenXMLFile

from plugins.list_view.widget import ListView

class SaveFile(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.dict = {} 
        self.dict_parent_page = {} # Prazan recnik za dodavanje dokumenta i njegovih pageova
        self.dict_page = {} # Prazan recnik za dodavanje id pageova iz izabranog dokumenta i teksta

        self.listViewPlugin = ListView(self.iface) # dodeljujemo list view plugin performance
        self.list_view = self.listViewPlugin.list_view # dodeljujemo napravljenu listu

        self.fileName = self.iface.getFileName()
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        self.currentDirectory = self.iface.getCurrentDirectory()
        self.fileInCurrentDirectory = self.iface.getFileInCurrentDirectory()

        #PRILIKOM POREKTANJA APLIKACIJE NE POSTOJI FAJL KOJI JE POKRENUT U TEXT EDITU
        #NE MOZEMO DA DODELIMO PROMENJIVU, ZATO SE RADI EXCEPT
        if(current_file_open[1] == "singi"):
            try:
                if(self.iface.page_open != "None"):
                    print("Uspesno ste sacuvali page: " + self.iface.page_open)
                    root = ET.fromstring(open(self.iface.file_in_current_directory).read())

                    page_for_change = ".//page[@id=\"" + self.iface.page_open + "\"]"
                    all_name_elements = root.find(page_for_change)

                    select_tab = []
                    for tabs in self.iface.all_open_file_tab_widget.split(","):
                        select_tab.append(tabs)

                    w = self.iface.central_widget.widget(select_tab.index(self.iface.page_open))
                    te = w.findChild(QtWidgets.QTextEdit)

                    if te is not None:
                        all_name_elements.text = te.toPlainText()

                    #Cuvanje XML fajla
                    xmldata = ET.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()

                    self.iface.status_bar_message_save_file(self.fileName) 
                    self.fileForReadPage(self.iface.file_in_current_directory, self.iface.position_for_new_page_in_document) # Cistimo list view listu i ucitavamo ponovo sve, da ne bi pageovi pamtili stari text

                    # Otvaramo ponovo fajl u Qtreewidget
                    fileOpen = open(self.iface.file_in_current_directory, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.file_in_current_directory).fileName())

            except TypeError as not_found_page:
                pass #Kada nije odabran ni jedan page da ne radi nista
        else:
            try:
                file_in_directory = Path(self.fileInCurrentDirectory)
            except TypeError as not_found:
                self.save_file_action()
                
            try:
                try:
                    try:
                        try:
                            print(file_in_directory)
                            if file_in_directory.exists():
                                select_tab = []
                                for tabs in self.iface.all_open_file_tab_widget.split(","):
                                    select_tab.append(QtCore.QFileInfo(tabs).fileName())

                                w = self.iface.central_widget.widget(select_tab.index(self.iface.fileName))
                                te = w.findChild(QtWidgets.QTextEdit)
                                if te is not None:
                                    saveFile = os.path.join(self.currentDirectory + "/" + self.fileName)    
                                    file = open(saveFile, 'w')
                                    file.write(te.toPlainText())
                                    file.close() 
                                    self.iface.status_bar_message_save_file(self.fileName)
                            else:
                                self.save_file_action()     

                        except TypeError as not_found:
                            self.save_file_action()

                    except UnboundLocalError as first_file:
                        pass

                except PermissionError as not_found:
                        self.save_file_action()

            except FileNotFoundError as not_found:
                pass # Kada ne odabere ni jedan fajl za otvaranje, da ne prijavljuje gresku

    def save_file_action(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.iface, "Save a new document", self.currentDirectory , "Singi Files (*.singi);;Text Files (*.txt);;Python Files (*.py)", options=QFileDialog.DontUseNativeDialog)
        if name[0] != "":
            if(name[1] == "Singi Files (*.singi)"):
                if not os.path.exists(name[0] + ".singi"):
                    root = ET.Element("dir")
                    root.set('id', "direktorijum_0")
                    root.set('name', QFileInfo(name[0]).fileName())
                    ddocumentoc = ET.SubElement(root, "document")
                    ddocumentoc.set('id', "dokument_0_1")
                    ddocumentoc.set('name', "README")
                    tree = ET.ElementTree(root)
                    tree.write(QFileInfo(name[0]).fileName() + ".singi")
                    self.iface.status_bar_message_save_file(QFileInfo(name[0]).fileName())
                else:
                    QMessageBox.information(self.iface, "Save a new document", "Greska!\nVec postoji fajl sa tim imenom.")

            elif(name[1] == "Text Files (*.txt)"):
                if not os.path.exists(name[0] + ".txt"):
                    fileName = os.path.join(self.currentDirectory, name[0] + ".txt")    
                    file = open(fileName, 'w')
                    text = self.iface.text_edit.toPlainText()
                    file.write(text)
                    file.close()
                    self.iface.status_bar_message_save_file(fileName) 
                else:
                    QMessageBox.information(self.iface, "Save a new document", "Greska!\nVec postoji fajl sa tim imenom.")

            elif(name[1] == "Python Files (*.py)"):
                if not os.path.exists(name[0] + ".py"):
                    fileName = os.path.join(self.currentDirectory, name[0] + ".py")    
                    file = open(fileName, 'w')
                    text = self.iface.text_edit.toPlainText()
                    file.write(text)
                    file.close()
                    self.iface.status_bar_message_save_file(fileName)
                else:
                    QMessageBox.information(self.iface, "Save a new document", "Greska!\nVec postoji fajl sa tim imenom.")
        else:
            pass

    def fileForReadPage(self, fileOpen, selectDocument):
        treeForRead=ET.parse(fileOpen)
        self.dict_parent_page = {} # Setujemo povo recnik da bude prazan

        for root in treeForRead.getiterator():
            for parent in root.findall('document'):
                for child in parent.findall("page"):
                    self.dict_parent_page.update({child.attrib.get("id") : parent.attrib.get("id")}) # Dodajemo u listu pageove i njegov dokument
                    self.dict_page[child.attrib.get("id")] = child.text  #Dodajemo sve pageove u recnik sa njihovim atributima

        self.rotate_key_and_page(self.dict_parent_page) # Zamena kljuca(child) sa vrednosti(parent)
        
        #Kada odaberemo jedan dokument samo njegove pageove iscitavamo
        if(self.dict.get(selectDocument) != None): # self.dict nece bit None tek kada odaberemo neki dokument koji ima pageove, data se pravi novi dict sa pageovima i dokumentom
            self.dict_parent_page = {}
            self.dict_parent_page.update({selectDocument : self.dict.get(selectDocument)}) # dodajemo self.dict sa zamenjenim vrednostima u self.dict_parent_page (ucitava pageove samo jednog dokumenta)

            # DOBIJANJE IMENA SLOTOVA OD SELEKTOVANOG DOKUMENTA
            remove_characters = ["[", "]", "'", "(", ")", "dict_values", " "] # lista nepotrebnih karaktera iz liste
            vrednosti_recnika = str(self.dict_parent_page.values()) # Dobavljamo vrednosti iz recnika
            for character in remove_characters:
                    vrednosti_recnika = vrednosti_recnika.replace(character, "") # Brisemo nepotrebne karaktere iz recnika
            
            vrednosti_recnika = vrednosti_recnika.split(",") # Delimo pageove u listu

            icon_path = "resources/lists/list"
            self.list_view.clear() # Brisemo svaki put list view widget
            page_counter = 1 # Broji pageove
            for i in vrednosti_recnika:
                item = QListWidgetItem(QtGui.QIcon(icon_path),"Page " + str(page_counter) + " (" + i + ")")
                self.list_view.addItem(item)
                if(item.text() == self.iface.page_open):
                    self.list_view.setCurrentItem(item)
                page_counter += 1

            self.listViewPlugin.dict_page_text(self.dict_page) # Prenosimo listu svih pageova sa id i tekstom u ViewList
            self.iface.add_list_view(self.listViewPlugin) # DODAVANJE NOVE LISTE U DOCK WIDGET SA DESNE STRANE
            self.iface.list_view.show()

    def rotate_key_and_page(self, d):
        self.dict = {}
        for k, v in d.items():
            if v in self.dict:
                self.dict[v].append(k)
            else:
                self.dict[v] = [k]
        return self.dict
