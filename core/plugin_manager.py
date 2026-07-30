"""
NEXUS
Plugin Manager

Module ID : PLUGIN-001
Version   : 0.0.5
"""

from pathlib import Path


class PluginManager:

    def __init__(self, plugin_folder):
        self.plugin_folder = Path(plugin_folder)
        self.plugins = []

    def discover(self):
        self.plugins.clear()

        if not self.plugin_folder.exists():
            return

        for item in self.plugin_folder.iterdir():
            if item.is_dir():
                self.plugins.append(item.name)

    def list_plugins(self):
        return self.plugins

    def print_plugins(self):
        print("\nDetected Plugins")

        if not self.plugins:
            print("No plugins found.")
            return

        for plugin in self.plugins:
            print(f"✓ {plugin}")

        print(f"\nTotal Plugins : {len(self.plugins)}")
