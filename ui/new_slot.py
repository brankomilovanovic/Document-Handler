from typing import Text
from PySide2 import QtGui
from PySide2.QtGui import QBrush, QPen, Qt
from PySide2.QtCore import QFileInfo, Qt 
from PySide2.QtWidgets import QListWidgetItem, QMessageBox, QWidget, QGraphicsRectItem, QGraphicsView, QGraphicsScene, QGraphicsItem
import xml.etree.ElementTree as ET

from plugins.list_view.widget import ListView
from ui.open_xml_file import OpenXMLFile

class NewSlot(QGraphicsRectItem):

    def __init__(self, iface, positionX, positionY, width, height):
        super().__init__()

        self.iface = iface #MainWindow
        self.positionX = positionX
        self.positionY = positionY
        self.slot_width = width
        self.slot_height = height
        self.slot_new_id = 0

        self.dict = {} 
        self.dict_parent_page = {} # Prazan recnik za dodavanje dokumenta i njegovih pageova
        self.dict_page = {} # Prazan recnik za dodavanje id pageova iz izabranog dokumenta i teksta

        self.new_page_sent()

    def new_page_sent(self):
        if(len(str(self.iface.page_open).split("_")) != 4):
            QMessageBox.information(self.iface, "Create a new slot", "Greska!\nNiste otvorili ni jednu stranicu." )
        else:
            tree = ET.parse(self.iface.file_in_current_directory)
            list_all_page = []
            list_all_id = []

            for element in tree.iter():
                for i in tree.findall('.//slot'):
                    if(i.attrib.get("id") not in list_all_page):
                        list_all_page.append(i.attrib.get("id"))

            for item in list_all_page:
                item = str(item).replace("slot_", "") # BRISEMO PAGE_ OSTAVLJAMO SAMO NJIGOVE ID
                list_all_id.append(item)


            list_all_id = [word for line in list_all_id for word in line.split("_")] # SPLITUJEMO LISTU SVE BROJEVE OD PAGE_1_1_1 DELIMO U POSEBAN INDEKS
            list_all_id = list_all_id[3::4] # PRESKACEMO SVAKI TECI ELEMENT DA BI DOBILI SAMO IDEVE PAGEOVA, ID JE JEDINSTVEN ZA CEO FAJL

            #PRETVARAMO STRING LISTU U INTIGER
            for i in range(0, len(list_all_id)):
                list_all_id[i] = int(list_all_id[i])

            najveci_id = 0 # PRVI SLOBODAN ID NIKAD KORISCEN (UZIMAMO NAJVECI BROJ IZ LISTE I NJEMU DODAJEMO + 1)
            for number in list_all_id:
                if number > najveci_id:
                    najveci_id = number

            text = najveci_id + 1 # Setujemo ime pagea sa njegovim ID-om
            root = ET.fromstring(open(self.iface.file_in_current_directory).read())
            string = ".//page[@id=\"" + self.iface.page_open + "\"]"
            folder = root.find(string)

            #menjamo direktorijum u dokument, da ne bi dovlacili id direktorijuma u koji pravimo dokument
            dokument = str(self.iface.page_open).replace("page", "slot")
            ET.SubElement(folder, 'slot',{'id':f'{dokument}_{najveci_id + 1}','positionX':f'{self.positionX}','positionY':f'{self.positionY}','slot_width':f'{self.slot_width}','slot_height':f'{self.slot_height}','type':'empty'})

            self.slot_new_id = f'{dokument}_{najveci_id + 1}'
            #Cuvanje XML fajla
            xmldata = ET.tostring(root, encoding="unicode")
            myfile = open(self.iface.file_in_current_directory, "w")
            myfile.write(xmldata)
            myfile.close()

            print("Uspesno ste dodali novi slot u page: " + self.iface.page_open)