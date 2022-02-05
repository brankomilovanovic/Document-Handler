from plugin_framework.extension import Extension
from .widget import ListView

class Plugin(Extension):
    def __init__(self, specification, iface):
        """
        :param iface: main_window aplikacije
        """
        super().__init__(specification, iface)    
        self.widget = ListView(iface)
        print("LIST VIEW")

    # FIXME: implementacija apstraktnih metoda
    def activate(self):
        print("Activated - View list")
        self.iface.add_list_view(self.widget)

    def deactivate(self):
        print("Deactivated - View list")
        self.iface.remove_list_view()