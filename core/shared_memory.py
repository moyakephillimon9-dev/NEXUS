"""
NEXUS
Shared Memory

Module ID : MEMORY-001
Version   : 0.0.7
"""


class SharedMemory:

    def __init__(self):
        self.memory = {}

    def write(self, key, value):
        self.memory[key] = value

    def read(self, key):
        return self.memory.get(key)

    def exists(self, key):
        return key in self.memory

    def delete(self, key):
        if key in self.memory:
            del self.memory[key]

    def clear(self):
        self.memory.clear()

    def print_memory(self):
        print("\nShared Memory")

        if not self.memory:
            print("Memory is empty.")
            return

        for key, value in self.memory.items():
            print(f"{key} : {value}")
