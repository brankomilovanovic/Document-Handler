from abc import ABC
from plugin_framework.plugin import Plugin

class Extension(Plugin, ABC):
    def __init__(self, plugin_specification, iface):
        self.plugin_specification = plugin_specification
        self.iface = iface

    