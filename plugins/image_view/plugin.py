from plugin_framework.extension import Extension
from plugins.image_view.widget import ImageView

class Plugin(Extension):
    def __init__(self, specification, iface):
        """
        :param iface: main_window aplikacije
        """
        super().__init__(specification, iface)    
        print("IMAGE VIEW")

    # FIXME: implementacija apstraktnih metoda
    def activate(self):
        print("Activated - Image view")
        self.iface.activate_image_view()

    def deactivate(self):
        print("Deactivated - Image view")
        self.iface.deactivate_image_view()