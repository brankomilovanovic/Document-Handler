import os
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QMessageBox, QTreeWidgetItem, QWidget
import xml.etree.ElementTree as ET

from ui.open_xml_file import OpenXMLFile

class NewDocument(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.currentDirectory = self.iface.getCurrentDirectory()

        self.fileName = self.iface.fileName
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        try:
            if(current_file_open[1] == "singi"):
                self.new_document_sent()
            else:
                self.new_document_standard()
        except IndexError:
            self.new_document_standard()
    
    def new_document_standard(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.iface, "Create a new document", self.currentDirectory , "Singi Files (*.singi);;Text Files (*.txt);;Python Files (*.py)", options=QFileDialog.DontUseNativeDialog)
        if name[0] != "":
            if(name[1] == "Singi Files (*.singi)"):
                if not os.path.exists(name[0] + ".singi"):
                    fileName = os.path.join(self.currentDirectory, name[0] + ".singi")
                    file = open(fileName, "w")
                    file.write('<dir expanded="False" id="direktorijum_0" name="' + QtCore.QFileInfo(name[0]).fileName() + '" />')
                    file.close() 
                else:
                    QMessageBox.information(self.iface, "Create a new document", "Greska!\nVec postoji dokument sa tim imenom.")

            elif(name[1] == "Text Files (*.txt)"):
                if not os.path.exists(name[0] + ".txt"):
                    fileName = os.path.join(self.currentDirectory, name[0] + ".txt")    
                    file = open(fileName, "w")
                    file.write("")
                    file.close()
                else:
                    QMessageBox.information(self.iface, "Create a new document", "Greska!\nVec postoji dokument sa tim imenom.")

            elif(name[1] == "Python Files (*.py)"):
                if not os.path.exists(name[0] + ".py"):
                    fileName = os.path.join(self.currentDirectory, name[0] + ".py")    
                    file = open(fileName, "w")
                    file.write("")
                    file.close()
                else:
                    QMessageBox.information(self.iface, "Create a new document", "Greska!\nVec postoji dokument sa tim imenom.")

    def new_document_sent(self):
        #Provera da li je lista splitovana ima 3 elementa, ako ima 3 elmenta znaci odabrali smo dokument, 
        #Da bi dobili direktorijum tog dokumenta uzimamo prvi od dokument_1_1 (prvi id predstavlja broj direktorijuma, drugi broj dokumenta)
        #Nakon toga ime dokument_pretvaramo u direktorijum_
        if(len(str(self.iface.position_for_new_element_in_xml).split("_")) == 3):
            self.iface.position_for_new_element_in_xml = str(self.iface.position_for_new_element_in_xml).split("_")[0].replace("dokument", "direktorijum") + "_" + str(self.iface.position_for_new_element_in_xml).split("_")[1]

        tree = ET.parse(self.iface.file_in_current_directory)
        list_all_directory = []
        list_all_id = []
        list_all_id_page = []
        list_all_page = []

        for element in tree.iter():
            for i in tree.findall('.//page'):
                if(i.attrib.get("id") not in list_all_page):
                    list_all_page.append(i.attrib.get("id"))

        for item in list_all_page:
            item = str(item).replace("page_", "") # BRISEMO Page_ OSTAVLJAMO SAMO NJIGOVE ID
            list_all_id_page.append(item)


        list_all_id_page = [word for line in list_all_id_page for word in line.split("_")] # SPLITUJEMO LISTU SVE BROJEVE OD Page_1_1_1 DELIMO U POSEBAN INDEKS
        list_all_id_page = list_all_id_page[2::3] # PRESKACEMO SVAKI TECI ELEMENT DA BI DOBILI SAMO IDEVE PageOVA, ID JE JEDINSTVEN ZA CEO FAJL
            
        #PRETVARAMO STRING LISTU U INTIGER
        for i in range(0, len(list_all_id_page)):
            list_all_id_page[i] = int(list_all_id_page[i])

        najveci_id_pagea = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
        for number in list_all_id_page:
            if number > najveci_id_pagea:
                najveci_id_pagea = number

        #DODAJEMO IMENA DIREKTORIJUMA IZ ODABRANOG DIREKTORIJUMA, DA BI ZABRANILI DUPLIRANJE IMENA
        dir_select = ".//dir[@id=\"" + self.iface.position_for_new_element_in_xml + "\"]"
        list_document_name = []
        try:
            for element in tree.find(dir_select):
                for i in element.iter('document'):
                    list_document_name.append(i.attrib.get("name"))
        except TypeError:
            for child in tree.getroot():
                for i in tree.getroot().findall('document'):
                    if i.attrib.get("name") not in list_document_name:
                        list_document_name.append(i.attrib.get("name"))
        ##########
        for element in tree.iter():
            for i in tree.findall('.//document'):
                if(i.attrib.get("id") not in list_all_directory):
                    list_all_directory.append(i.attrib.get("id"))

        for item in list_all_directory:
            item = str(item).replace("dokument_", "") # BRISEMO DIREKTORIJU_ OSTAVLJAMO SAMO NJIGOVE ID
            list_all_id.append(item)

        list_all_id = [word for line in list_all_id for word in line.split("_")] # SPLITUJEMO LISTU SVE BROJEVE OD DOKUMENT_1_1 DELIMO U POSEBAN INDEKS
        list_all_id = list_all_id[1::2] # PRESKACEMO SVAKI DRUGI ELEMENT DA BI DOBILI SAMO IDEVE DOKUMENATA, ID JE JEDINSTVEN ZA CEO FAJL

        #PRETVARAMO STRING LISTU U INTIGER
        for i in range(0, len(list_all_id)):
            list_all_id[i] = int(list_all_id[i])

        najveci_id = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
        for number in list_all_id:
            if number > najveci_id:
                najveci_id = number

        inputDialog =  QInputDialog(self)
        text, save = inputDialog.getText(self.iface, "Create a new document", "Unesite ime novog dokumenta:                               ", QLineEdit.Normal, "")
        
        if save:
            if text != "":
                if text not in list_document_name:
                    root = ET.fromstring(open(self.iface.file_in_current_directory).read())
                    string = ".//dir[@id=\"" + self.iface.position_for_new_element_in_xml + "\"]"
                    folder = root.find(string)

                    #menjamo direktorijum u dokument, da ne bi dovlacili id direktorijuma u koji pravimo dokument
                    direktorijum = str(self.iface.position_for_new_element_in_xml).replace("direktorijum", "dokument")
                    page = direktorijum.replace("dokument", "page")

                    try:
                        element = ET.SubElement(folder, 'document',{'name':f'{text}','id':f'{direktorijum}_{najveci_id + 1}'})
                        first_page = ET.Element('page',{'name':f'{text}','id':f'{page}_{najveci_id + 1}_{najveci_id_pagea + 1}'})
                        element.insert(0,first_page)
                    except TypeError:
                        #Ako je root direktorijum on nema elemnt tree pa zbog toga samo dodajemo element u root.append (dodaje se uvek na kraj)
                        element = ET.Element('document',{'name':f'{text}','id':f'{direktorijum}_{najveci_id + 1}'})
                        first_page = ET.Element('page',{'name':f'{text}','id':f'{page}_{najveci_id + 1}_{najveci_id_pagea + 1}'})
                        element.insert(0,first_page)
                        root.append(element)

                    print("Uspesno ste dodali novi dokument u direktorijumu: " + self.iface.position_for_new_element_in_xml)
                        
                    #Cuvanje XML fajla
                    xmldata = ET.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()
                    
                    # Otvaramo ponovo fajl u Qtreewidget
                    fileOpen = open(self.iface.file_in_current_directory, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.file_in_current_directory).fileName())
                    
                else:
                    QMessageBox.information(self.iface, "Create a new document", "Greska!\nVec postoji dokument sa tim imenom.") 
            else:
                QMessageBox.information(self.iface, "Create a new document", "Greska!\nNiste uneli ime dokumenta." )