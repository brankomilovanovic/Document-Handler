import os
from typing import Text
from PySide2 import QtWidgets
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QMessageBox, QWidget

import xml.etree.ElementTree as ET
from lxml import etree

from ui.open_xml_file import OpenXMLFile

class NewDirectory(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.currentDirectory = self.iface.getCurrentDirectory()

        self.fileName = self.iface.fileName
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        try:
            if(current_file_open[1] == "singi"):
                self.new_directory_in_xml()
            else:
                self.new_directory_standard()
        except IndexError:
            self.new_directory_standard()
            
    def new_directory_standard(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.iface, "Create a new collection", self.currentDirectory , "All Files (*)", options=QFileDialog.DontUseNativeDialog)
        try:
            if not os.path.exists(name[0]):
                os.makedirs(name[0])
            else:
                QMessageBox.information(self.iface, "Create a new collection", "Greska!\nVec postoji direktorijum sa tim imenom.") 

        except FileNotFoundError as no_input_name:
            pass # Ako ne unese ime direktorijuma da ne ispisuje gresku

    
    def new_directory_in_xml(self):     
        #Provera da li je lista splitovana ima 3 elementa, ako ima 3 elmenta znaci odabrali smo dokument, 
        #Da bi dobili direktorijum tog dokumenta uzimamo prvi od dokument_1_1 (prvi id predstavlja broj direktorijuma, drugi broj dokumenta)
        #Nakon toga ime dokument_pretvaramo u direktorijum_
        if(len(str(self.iface.position_for_new_element_in_xml).split("_")) == 3):
            self.iface.position_for_new_element_in_xml = str(self.iface.position_for_new_element_in_xml).split("_")[0].replace("dokument", "direktorijum") + "_" + str(self.iface.position_for_new_element_in_xml).split("_")[1]
        tree = ET.parse(self.iface.file_in_current_directory)
        list_all_directory = []
        list_all_id = []

        #DODAJEMO IMENA DIREKTORIJUMA IZ ODABRANOG DIREKTORIJUMA, DA BI ZABRANILI DUPLIRANJE IMENA
        dir_select = ".//dir[@id=\"" + self.iface.position_for_new_element_in_xml + "\"]"
        list_dir_name = []
        try:
            for element in tree.find(dir_select):
                for i in element.iter('dir'):
                    list_dir_name.append(i.attrib.get("name"))
        except TypeError:
            for child in tree.getroot():
                for i in tree.getroot().findall('dir'):
                    if i.attrib.get("name") not in list_dir_name:
                        list_dir_name.append(i.attrib.get("name"))
        #######
        for element in tree.iter():
            for i in tree.findall('.//dir'):
                if(i.attrib.get("id") not in list_all_directory):
                    list_all_directory.append(i.attrib.get("id"))

        for item in list_all_directory:
            item = str(item).replace("direktorijum_", "") # BRISEMO DIREKTORIJU_ OSTAVLJAMO SAMO NJIGOVE ID
            list_all_id.append(item)

        #PRETVARAMO STRING LISTU U INTIGER
        for i in range(0, len(list_all_id)):
            list_all_id[i] = int(list_all_id[i])

        najveci_id = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
        for number in list_all_id:
            if number > najveci_id:
                najveci_id = number

        inputDialog =  QInputDialog(self)
        text, save = inputDialog.getText(self.iface, "Create a new collection", "Unesite ime novog direktorijuma:                                ", QLineEdit.Normal, "")
        
        if save:
            if text != "":
                if text not in list_dir_name:
                    root = ET.fromstring(open(self.iface.file_in_current_directory).read())
                    string = ".//dir[@id=\"" + self.iface.position_for_new_element_in_xml + "\"]"
                    folder = root.find(string)
                    try:
                        ET.SubElement(folder, 'dir',{'name':f'{text}','id':f'direktorijum_{najveci_id + 1}', 'expanded': 'False'})
                    except TypeError:
                        #Ako je root direktorijum on nema elemnt tree pa zbog toga samo dodajemo element u root.append (dodaje se uvek na kraj)
                        root.append(ET.Element('dir',{'name':f'{text}','id':f'direktorijum_{najveci_id + 1}', 'expanded': 'False'}))

                    print("Uspesno ste dodali novi direktorijum u direktorijumu: " + self.iface.position_for_new_element_in_xml)

                    #Cuvanje XML fajla
                    xmldata = ET.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()

                    # Otvaramo ponovo fajl u Qtreewidget
                    fileOpen = open(self.iface.file_in_current_directory, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.file_in_current_directory).fileName())

                else:
                    QMessageBox.information(self.iface, "Create a new collection", "Greska!\nVec postoji direktorijum sa tim imenom.") 
            else:
                QMessageBox.information(self.iface, "Create a new collection", "Greska!\nNiste uneli ime direktorijuma." )