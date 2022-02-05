from PySide2 import QtGui
from plugin_framework.extension import Extension
from .widget import DocumentViewer

class Plugin(Extension):
    def __init__(self, specification, iface):
        """
        :param iface: main_window aplikacije
        """
        super().__init__(specification, iface)    
        self.widget = DocumentViewer(iface)
        print("DOCUMENT VIEWER")

    # FIXME: implementacija apstraktnih metoda
    def activate(self):
        print("Activated - Document viewer")
        self.iface.add_dock_widget(self.widget)

    def deactivate(self):
        print("Deactivated - Document viewer")
        self.iface.remove_dock_widget()