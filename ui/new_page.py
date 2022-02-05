from typing import Text
from PySide2 import QtGui
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QListWidgetItem
from PySide2.QtWidgets import QListWidgetItem, QMessageBox, QWidget
import xml.etree.ElementTree as ET

class NewPage(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow
        
        self.dict = {} 
        self.dict_parent_page = {} # Prazan recnik za dodavanje dokumenta i njegovih pageova
        self.dict_page = {} # Prazan recnik za dodavanje id pageova iz izabranog dokumenta i teksta

        self.fileName = self.iface.fileName
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        if(current_file_open[1] == "singi"):
            self.new_page_sent()
        else:
            QMessageBox.information(self.iface, "Create a new page", "Greska!\nNiste otvorili ni jedan Singi dokument.")

    def new_page_sent(self):
        #Provera da li je lista splitovana ima 3 elementa, ako ima 3 elmenta znaci odabrali smo dokument, 
        if(len(str(self.iface.position_for_new_page_in_document).split("_")) != 3):
            QMessageBox.information(self.iface, "Create a new page", "Greska!\nNiste otvorili ni jedan dokument." )
        else:
            tree = ET.parse(self.iface.file_in_current_directory)
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
                    
            text = najveci_id + 1 # Setujemo ime pagea sa njegovim ID-om
            root = ET.fromstring(open(self.iface.file_in_current_directory).read())
            string = ".//document[@id=\"" + self.iface.position_for_new_page_in_document + "\"]"
            folder = root.find(string)

            #menjamo direktorijum u dokument, da ne bi dovlacili id direktorijuma u koji pravimo dokument
            dokument = str(self.iface.position_for_new_page_in_document).replace("dokument", "page")
            ET.SubElement(folder, 'page',{'name':f'{text}','id':f'{dokument}_{najveci_id + 1}'})

            #Cuvanje XML fajla
            xmldata = ET.tostring(root, encoding="unicode")
            myfile = open(self.iface.file_in_current_directory, "w")
            myfile.write(xmldata)
            myfile.close()

            from ui.open_xml_file import OpenXMLFile
            OpenXMLFile(self.iface).update_document_viewer_and_list_view()
            print("Uspesno ste dodali novi page u dokumentu: " + self.iface.position_for_new_page_in_document)