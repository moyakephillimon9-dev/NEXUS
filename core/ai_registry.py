"""
NEXUS
AI Registry

Module ID : REGISTRY-001
Version   : 0.0.6
"""


class AIRegistry:

    def __init__(self):
        self.registry = {}

    def register(self, name):
        self.registry[name] = "LOADED"

    def unregister(self, name):
        if name in self.registry:
            del self.registry[name]

    def list_all(self):
        return self.registry

    def print_registry(self):
        print("\nAI Registry")

        if not self.registry:
            print("No AI modules registered.")
            return

        for name, status in self.registry.items():
            print(f"{name} : {status}")

