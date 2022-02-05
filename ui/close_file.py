from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QFileInfo, QUrl
from PySide2.QtWidgets import QWidget

class CloseFile(QWidget):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface #MainWindow

        self.fileName = self.iface.fileName
        current_file_open = self.fileName
        current_file_open = str(current_file_open).split(".")

        if(current_file_open[1] == "singi"):
            self.iface.text_edit.setText("")
            self.iface.text_edit.hide()
            #Kada korisnik zatvori dokument tada se zatvori i text view
            self.iface.list_view.hide()
            self.iface.list_view.setWidget(QtWidgets.QListWidget())
            self.iface.close_file_in_status_bar()
            self.iface.position_for_new_page_in_document = str(None)
            self.iface.position_for_new_element_in_xml = "direktorijum_0"
            self.iface.last_selected_item = str(None)
            self.iface.page_open = str(None)
        
        else:
            self.iface.list_view.hide()
            self.iface.close_file_in_status_bar()
            select_tab = []
            for tabs in self.iface.all_open_file_tab_widget.split(","):
                select_tab.append(QtCore.QFileInfo(tabs).fileName())
            self.iface.delete_tab(select_tab.index(self.iface.fileName))