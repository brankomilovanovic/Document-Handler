import os
import inspect
import importlib
import json
from plugin_framework.plugin_specification import PluginSpecification

class PluginRegistry:
    def __init__(self, path, iface, plugins=[]):
        self.path = path # folder
        self.iface = iface # interface (main_window)
        self._plugins = plugins
        self.init_plugins()

    def install(self, plugin):
        exsists = self._check_existing_plugin(plugin.plugin_specification.id)
        if not exsists:
            # FIXME: nisu proverene zavisnosti
            self._plugins.append(plugin)

    def uninstall(self, plugin):
        # FIXME: sta se radi sa zavisnostima
        self.deactivate(plugin.plugin_specification.id)
        self._plugins.remove(plugin)

    def activate(self, _id):
        for plugin in self._plugins: # plugin # naslednica od extension
            if _id == plugin.plugin_specification.id:
                plugin.activate()

    def deactivate(self, _id):
        for plugin in self._plugins: # plugin # naslednica od extension
            if _id == plugin.plugin_specification.id:
                plugin.deactivate()

    def init_plugins(self):
        """
        Loads all plugins from path.
        """
        plugins_packages = os.listdir(self.path)
        for package in plugins_packages:
            package_path = os.path.join(self.path, package)
            plugin_path = os.path.join(package_path, "plugin.py") # Po dogovoru glavni deo plugin-a cuvamo u plugin.py
            spec_path = os.path.join(package_path, "specification.json") # specifikacija svakog plugina ce se nalaziti
            # u ovoj dateoteci

            data = {}
            with open(spec_path) as fp:
                data = json.load(fp)
            specification = PluginSpecification.from_dict(data)
            print(data, specification)
            # dinamicko ucitavanje modula
            plugin = importlib.import_module(plugin_path.replace(os.path.sep, ".").rstrip(".py"))
            clsmembers = inspect.getmembers(plugin_path, inspect.isclass)
            print(clsmembers)
            if len(clsmembers) == 1:
                plugin = plugin.Plugin(specification, self.iface) # unutar modula ce postojati tacno jedna klasa koju cemo
                # zvati Plugin
                # instalacija plugin-a
                self.install(plugin)
            else:
                raise IndexError("The plugin.py module must contain just one class!")

    def _check_existing_plugin(self, _id):
        """
        Checks if plugin with _id is already in plugin list.
        """
        for plugin in self._plugins:
            if plugin.plugin_specification.id == _id:
                return True

    def _get_plugin_name(self, _id):
        """
        Checks if plugin with _id is already in plugin list.
        """
        for plugin in self._plugins:
            if plugin.plugin_specification.id == _id:
                return plugin.plugin_specification.name
        return False

    def aktiviranje(self):
        plugins_packages = os.listdir(self.path)
        for package in plugins_packages:
            return True
        return False