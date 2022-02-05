from os import name
import xml.etree.ElementTree as et
from xmlrpc.client import boolean
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import QFileInfo
from PySide2.QtWidgets import QAbstractItemView, QAction, QInputDialog, QLineEdit, QListWidgetItem, QMessageBox, QTreeWidget, QTreeWidgetItem, QWidget

from ui.page_preview import PagePreview

class OpenXMLFile(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.treeWidget = QTreeWidget()
        self.treeWidget.setMaximumWidth(450)
        self.treeWidget.setColumnCount(2) 
        self.treeWidget.setHeaderLabels(['Name ','ID'])
        self.treeWidget.setColumnWidth(0,220) # Setuje velicinu prve kolone, da se vidi sve iz stabla
        self.treeWidget.setStyleSheet("QTreeWidget::item:selected {background-color : #cde8ff; color: black;}");

        self.currentOpenFile = ""
        self.dict = {} 
        self.dict_parent_page = {} # Prazan recnik za dodavanje dokumenta i njegovih pageova
        self.dict_page = {} # Prazan recnik za dodavanje id pageova iz izabranog dokumenta i teksta
        self.before_last_position = "" # Treba nam za rename direktorijuma
        self.current_open_document = ""

        self.count = 1
        
        self.iface.dock_widget.setWidget(self.treeWidget)

        self.treeWidget.itemClicked.connect(self.onItemClicked)

        # Connect the contextmenu
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextTree)

    def XMLinTreeView(self, file, fileName):

        self.currentOpenFile = fileName # Setujemo ime trenutno otvorenog fajla da bi mogli iscitati pageove iz dokumenta

        fileOpen = et.fromstring(file)
        tree = QTreeWidgetItem()
        tree.setText(0, fileOpen.attrib.get("name"))
        tree.setToolTip(0, fileOpen.attrib.get("name"))
        tree.setText(1, fileOpen.attrib.get("id"))
        tree.setToolTip(1, fileOpen.attrib.get("id"))
        self.treeWidget.addTopLevelItem(tree)

        tree.setIcon(0, QtGui.QIcon("resources/icons/folder.png"))

        if(fileOpen.attrib.get("id") == self.iface.last_selected_item):
            tree.setSelected(True)
            
        if(fileOpen.attrib.get("expanded") == "True"):
            tree.setExpanded(True) # Izlistavamo odmah stablo  

        def displayTree(tree,childs):
            for child in childs:
                branch = QTreeWidgetItem()
                branch.setText(0, child.attrib.get("name"))
                branch.setToolTip(0, child.attrib.get("name"))
                branch.setText(1, child.attrib.get("id"))
                branch.setToolTip(1, child.attrib.get("id"))
                tree.addChild(branch)
                if child.findall("page"):
                    branch.setIcon(0, QtGui.QIcon("resources/icons/document.png"))
                else:
                    branch.setIcon(0, QtGui.QIcon("resources/icons/folder.png"))
                    displayTree(branch, child)

                if(child.attrib.get("expanded") == "True"):
                    branch.setExpanded(True) # Izlistavamo svu decu iz direktorijuma (izlistavamo dokumente)
                    
            self.iface.open_file_in_status_bar(self.currentOpenFile) # <----- OVO NE DIRATI AKO SE OBRISE NE UCITAVA FAJL

        displayTree(tree, fileOpen)

    def XMLinTreeViewUpdate(self, file, fileName):
        self.currentOpenFile = fileName # Setujemo ime trenutno otvorenog fajla da bi mogli iscitati pageove iz dokumenta

        fileOpen = et.fromstring(file)
        tree = QTreeWidgetItem()
        tree.setText(0, fileOpen.attrib.get("name"))
        tree.setToolTip(0, fileOpen.attrib.get("name"))
        tree.setText(1, fileOpen.attrib.get("id"))
        tree.setToolTip(1, fileOpen.attrib.get("id"))

        self.treeWidget.addTopLevelItem(tree)

        tree.setIcon(0, QtGui.QIcon("resources/icons/folder.png"))

        if(fileOpen.attrib.get("id") == self.iface.last_selected_item):
            tree.setSelected(True)

        if(fileOpen.attrib.get("expanded") == "True"):
            tree.setExpanded(True) # Izlistavamo odmah stablo   

        def displayTree(tree,childs):
            for child in childs:
                branch = QTreeWidgetItem()
                branch.setText(0, child.attrib.get("name"))
                branch.setToolTip(0, child.attrib.get("name"))
                branch.setText(1, child.attrib.get("id"))
                branch.setToolTip(1, child.attrib.get("id"))
                tree.addChild(branch)

                if(child.attrib.get("id") == self.iface.last_selected_item):
                    branch.setSelected(True)
                    
                if child.findall("page"):
                    branch.setIcon(0, QtGui.QIcon("resources/icons/document.png"))
                else:
                    branch.setIcon(0, QtGui.QIcon("resources/icons/folder.png"))
                    displayTree(branch, child)

                if(child.attrib.get("expanded") == "True"):
                    branch.setExpanded(True) # Izlistavamo svu decu iz direktorijuma (izlistavamo dokumente)

            self.iface.open_file_in_status_bar(self.currentOpenFile) # <----- OVO NE DIRATI AKO SE OBRISE NE UCITAVA FAJL

        displayTree(tree, fileOpen)

    def onItemClicked(self):
        item = self.treeWidget.currentItem().text(1)
        item_is_expanded = self.treeWidget.currentItem()

        #print(self.getParentPath(item), self.count)
        #self.before_last_position = self.getParentPath(item)
        #print(self.get_all_items(self.treeWidget))
        #print(list(set(self.get_all_items(self.treeWidget)) - set(lista_direktorijuma)))

        print(item)

        #Setujemo samo ID trenutno otvorenog direktorijuma
        self.iface.last_selected_item = item

        if(len(item.split("_")) == 2):
            self.iface.position_for_new_element_in_xml = item # SAMO AKO JE DIREKTORIJUM ONDA SETUJEMO

            item_for_expandee = item_is_expanded.isExpanded()

            if(item_is_expanded.isExpanded() == False):
                item_for_expandee = True
            else:
                item_for_expandee = False

            root = et.fromstring(open(self.iface.file_in_current_directory).read())
            string = ".//dir[@id=\"" + item_is_expanded.text(1) + "\"]"
            folder = root.find(string)

            if(item == "direktorijum_0"):
                if(item_for_expandee == True):
                    root.attrib["expanded"] = "True"
                elif(item_for_expandee == False):
                    root.attrib["expanded"] = "False"
            elif(item_for_expandee == True):
                folder.attrib["expanded"] = "True"
            elif(item_for_expandee == False):
                folder.attrib["expanded"] = "False"

            #Cuvanje XML fajla
            xmldata = et.tostring(root, encoding="unicode")
            myfile = open(self.iface.file_in_current_directory, "w")
            myfile.write(xmldata)
            myfile.close()

        elif(len(item.split("_")) == 3):
            self.iface.position_for_new_element_in_xml = item.split("_")[0].replace("dokument", "direktorijum") + "_" + item.split("_")[1]
            self.iface.position_for_new_page_in_document = item # Dodajemo samo selektovan dokument za novu stranicu
            self.fileForReadPage(self.iface.file_in_current_directory, item)

        #if(len(item.split("_")) == 3):
            #self.fileForReadPage(self.iface.file_in_current_directory, item)
            #self.iface.position_for_new_page_in_document = item # Dodajemo samo selektovan dokument za novu stranicu

        self.update_document_viewer_and_list_view()
        
    def get_all_items(self, tree_widget):
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
        all_items = []
        for i in range(tree_widget.topLevelItemCount()):
            top_item = tree_widget.topLevelItem(i)
            all_items.extend(self.get_subtree_nodes(top_item))
        return all_items

    def get_subtree_nodes(self, tree_widget_item):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
        nodes = []
        nodes.append({tree_widget_item.text(1): tree_widget_item.isExpanded()})
        for i in range(tree_widget_item.childCount()):
            nodes.extend(self.get_subtree_nodes(tree_widget_item.child(i)))
        return nodes

    def fileForReadPage(self, fileOpen, selectDocument):
        from plugins.list_view.widget import ListView
        self.listViewPlugin = ListView(self.iface) # dodeljujemo list view plugin performance
        #view = self.listViewPlugin.list_view # dodeljujemo napravljenu listu

        treeForRead=et.parse(fileOpen)
        self.dict_parent_page = {} # Setujemo povo recnik da bude prazan
        self.current_open_document = selectDocument

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

            # DOBIJANJE IMENA PAGEOVA OD SELEKTOVANOG DOKUMENTA
            remove_characters = ["[", "]", "'", "(", ")", "dict_values", " "] # lista nepotrebnih karaktera iz liste
            vrednosti_recnika = str(self.dict_parent_page.values()) # Dobavljamo vrednosti iz recnika
            for character in remove_characters:
                    vrednosti_recnika = vrednosti_recnika.replace(character, "") # Brisemo nepotrebne karaktere iz recnika
            
            vrednosti_recnika = vrednosti_recnika.split(",") # Delimo pageove u listu

            index = 0
            for i in vrednosti_recnika:
                page_preview = PagePreview(self.iface, i)
                if(i == self.iface.page_open):
                    page_preview.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#E7E7E7")))

                item = QListWidgetItem(i)
                item.setSizeHint(QtCore.QSize(1,125))
                self.listViewPlugin.list_view.insertItem(index, item)
                self.listViewPlugin.list_view.setItemWidget(item, page_preview)
                if(item.text() == self.iface.page_open):
                    item.setSelected(True) 
                self.iface.list_widget_id_for_add_new_page[item.text()] = index # ovo nam treba zbog dodavanja page up i page down
                index += 1

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

    def menuContextTree(self, point):
        index = self.treeWidget.indexAt(point)

        if not index.isValid():
            return

        item = self.treeWidget.itemAt(point).text(1)

        delete_action = QAction("Delete Selected")
        delete_action.triggered.connect(lambda: self.delete_action(item))
        delete_action.setIcon(QtGui.QIcon("resources/icons/delete_icon.png"));

        rename_action = QAction("Rename Selected")
        rename_action.triggered.connect(lambda: self.rename_action(item))
        rename_action.setIcon(QtGui.QIcon("resources/icons/rename_icon.png"));

        copy_action = QAction("Copy")
        #copy_action.triggered.connect(lambda: self.copy_action)
        copy_action.setIcon(QtGui.QIcon("resources/icons/copy.png"));
        copy_action.setEnabled(False)

        cut_action = QAction("Cut")
        #cut_action.triggered.connect(lambda: self.cut_action)
        cut_action.setIcon(QtGui.QIcon("resources/icons/cut.png"));
        cut_action.setEnabled(False)

        paste_action = QAction("Paste")
        #paste_action.triggered.connect(lambda: self.paste_action)
        paste_action.setIcon(QtGui.QIcon("resources/icons/paste.png"));
        paste_action.setEnabled(False)
        
        menu = QtWidgets.QMenu()
        menu.addAction(copy_action)
        menu.addAction(cut_action)
        menu.addAction(paste_action)
        menu.addSeparator()
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        menu.exec_(self.treeWidget.mapToGlobal(point))

    def delete_action(self, item_select):
        from plugins.list_view.widget import ListView
        self.listViewPlugin = ListView(self.iface) # dodeljujemo list view plugin performance
        #self.list_view = self.listViewPlugin.list_view # dodeljujemo napravljenu listu
        
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()

        for element in root.iter():
            for child in list(element):
                if child.attrib.get("id") == item_select:
                    element.remove(child)
                    if self.iface.position_for_new_page_in_document == item_select:
                        self.iface.central_widget.clear()
                        #self.list_view.clear() # Brisemo svaki put list view widget
                        self.iface.list_view.hide()
                        self.iface.page_open = str(None)
                        self.iface.last_selected_item = str(None)
                        self.iface.position_for_new_page_in_document = str(None)

                    if self.iface.position_for_new_element_in_xml == item_select:
                        self.iface.position_for_new_element_in_xml = "direktorijum_0"

                    if item_select == self.iface.last_selected_item:
                        self.iface.last_selected_item = str(None)

        list_all_document = [] 
        for element in tree.iter():
            for i in tree.findall('.//document'):
                if(i.attrib.get("id") not in list_all_document):
                    list_all_document.append(i.attrib.get("id"))
                            
        if (self.iface.position_for_new_page_in_document not in list_all_document):
            self.iface.position_for_new_page_in_document = str(None)
            self.iface.last_selected_item = str(None)
            self.iface.page_open = str(None)
            self.iface.central_widget.clear()
            self.iface.list_view.hide()
            self.iface.list_view.setWidget(QtWidgets.QListWidget())

        xmldata = et.tostring(root, encoding="unicode")
        myfile = open(self.iface.file_in_current_directory, "w")
        myfile.write(xmldata)
        myfile.close()

        # Otvaramo ponovo fajl u Qtreewidget
        fileOpen = open(self.iface.file_in_current_directory, 'r').read()
        OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.file_in_current_directory).fileName())

    def rename_action(self, item_select):
        tree = et.parse(self.iface.file_in_current_directory)
        list_exist_name = []

        '''self.before_last_position = str(self.before_last_position).split("/")
        self.before_last_position = self.before_last_position[len(self.before_last_position)-2]
        
        if(len(str(item_select).split("_")) == 2): # directory
            #DODAJEMO IMENA DIREKTORIJUMA IZ ODABRANOG DIREKTORIJUMA, DA BI ZABRANILI DUPLIRANJE IMENA
            dir_select = ".//dir[@id=\"" + self.before_last_position + "\"]"
            try:
                for element in tree.find(dir_select):
                    for i in element.iter('dir'):
                        list_exist_name.append(i.attrib.get("name"))
            except TypeError:
                for child in tree.getroot():
                    for i in tree.getroot().findall('dir'):
                        if i.attrib.get("name") not in list_exist_name:
                            list_exist_name.append(i.attrib.get("name"))
        elif(len(str(item_select).split("_")) == 3): # document
            #DODAJEMO IMENA DIREKTORIJUMA IZ ODABRANOG DIREKTORIJUMA, DA BI ZABRANILI DUPLIRANJE IMENA
            dir_select = ".//dir[@id=\"" + self.before_last_position + "\"]"
            try:
                for element in tree.find(dir_select):
                    for i in element.iter('document'):
                        list_exist_name.append(i.attrib.get("name"))
            except TypeError:
                for child in tree.getroot():
                    for i in tree.getroot().findall('document'):
                        if i.attrib.get("name") not in list_exist_name:
                            list_exist_name.append(i.attrib.get("name"))'''
       
        inputDialog =  QInputDialog()
        text, save = inputDialog.getText(self.iface, "Rename", "Unesite novo ime fajla:          ", QLineEdit.Normal, "")

        if save:
            if text != "":
                if text not in list_exist_name:
                    tree = et.parse(self.iface.file_in_current_directory)
                    root = tree.getroot()

                    for element in root.iter():
                        for child in list(element):
                            if child.attrib.get("id") == item_select:
                                child.set("name",text)

                    xmldata = et.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()

                    # Otvaramo ponovo fajl u Qtreewidget
                    fileOpen = open(self.iface.file_in_current_directory, 'r').read()
                    OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QFileInfo(self.iface.file_in_current_directory).fileName())
                else:
                    QMessageBox.information(self.iface, "Rename", "Greska!\nVec postoji to ime.")

    def getParentPath(self, item):
        def getParent(item, outstring):
            if item.parent() is None:
                return outstring
            outstring = item.parent().text(0) + "/" + outstring
            return getParent(item.parent(), outstring)

        output = getParent(item, item.text(1))
        return output

    def update_document_viewer_and_list_view(self):
        #if(self.iface.list_view_plugin == "True"):
        OpenXMLFile(self.iface).fileForReadPage(self.iface.file_in_current_directory, self.iface.position_for_new_page_in_document)
        fileOpen = open(self.iface.file_in_current_directory, 'r').read()
        #if(self.iface.dock_widget_plugin == "True"):
        OpenXMLFile(self.iface).XMLinTreeViewUpdate(fileOpen, QtCore.QFileInfo(self.iface.file_in_current_directory).fileName())