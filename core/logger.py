"""
NEXUS
Core Logger

Module ID : LOGGER-001
Version   : 0.0.3
"""

from datetime import datetime


class Logger:
    def info(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [INFO] {message}")

    def warning(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [WARNING] {message}")

    def error(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [ERROR] {message}")
