"""
=========================================================
NEXUS
Core Kernel

Module ID : KERNEL-001
Version   : 0.0.3
=========================================================
"""

from datetime import datetime
from core.logger import Logger
from core.config import Config
from core.plugin_manager import PluginManager
from core.ai_registry import AIRegistry
from core.shared_memory import SharedMemory

class Kernel:

    VERSION = "0.0.3"

    def __init__(self):
        self.start_time = datetime.now()
        self.running = False
        self.logger = Logger()
        self.plugin_manager = PluginManager(Config.PLUGIN_FOLDER)
        self.ai_registry = AIRegistry()
        self.shared_memory = SharedMemory()

    def boot(self):

        print("=" * 60)
        print("NEXUS")
        print(f"Kernel Version : {self.VERSION}")
        print("=" * 60)

        self.logger.info("Kernel Boot Started")

        self.running = True

        self.logger.info("Logger Initialized")

        self.plugin_manager.discover()

        plugins = self.plugin_manager.list_plugins()

        for plugin in plugins:
            self.ai_registry.register(plugin)

        self.logger.info(f"Plugins Loaded : {len(plugins)}")

        for plugin in plugins:
            self.logger.info(f"Plugin: {plugin}")

        self.logger.info("AI Registry Initialized")

        self.ai_registry.print_registry()

        self.logger.info("System Ready")

        self.shared_memory.write("system", "ONLINE")

        self.logger.info("Shared Memory Initialized")

        self.shared_memory.print_memory()

        print("=" * 60)
