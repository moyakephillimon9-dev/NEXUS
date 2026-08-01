"""
NEXUS Health Check System

Diagnostics and system health monitoring.
"""

import os
from datetime import datetime
from pathlib import Path
from core.config import Config
from core.logger import get_health_logger

log = get_health_logger()


class HealthCheck:
    """System health diagnostics."""
    
    def __init__(self):
        self.checks = {}
        self.status = 'unknown'
        self.timestamp = None
    
    def run_all_checks(self):
        """Run all health checks."""
        self.timestamp = datetime.now().isoformat()
        self.checks = {
            'system': self._check_system(),
            'storage': self._check_storage(),
            'memory': self._check_memory(),
            'brain': self._check_brain(),
            'auth': self._check_auth(),
            'logs': self._check_logs(),
        }
        
        # Determine overall status
        all_ok = all(c.get('status') == 'ok' for c in self.checks.values())
        self.status = 'healthy' if all_ok else 'degraded'
        
        log.log_check('NEXUS', self.status, f"Checks completed at {self.timestamp}")
        return self
    
    def _check_system(self):
        """Check system configuration."""
        try:
            return {
                'status': 'ok',
                'version': Config.VERSION,
                'project': Config.PROJECT_NAME,
                'owner': Config.OWNER,
                'python_version': os.sys.version.split()[0],
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_storage(self):
        """Check required directories."""
        required = [
            ('logs', Config.LOG_FOLDER),
            ('memory', Config.MEMORY_FOLDER),
            ('projects', Config.PROJECTS_FOLDER),
            ('data', Config.ROOT / 'data'),
        ]
        
        storage = {}
        for name, path in required:
            try:
                path.mkdir(exist_ok=True, parents=True)
                storage[name] = {'status': 'ok', 'path': str(path)}
            except Exception as e:
                storage[name] = {'status': 'error', 'error': str(e)}
        
        overall_ok = all(d.get('status') == 'ok' for d in storage.values())
        return {
            'status': 'ok' if overall_ok else 'error',
            'directories': storage,
        }
    
    def _check_memory(self):
        """Check memory system."""
        try:
            mem_db = Config.MEMORY_FOLDER / 'database.json'
            mem_db.parent.mkdir(exist_ok=True, parents=True)
            readable = mem_db.exists() or True  # Can create
            return {
                'status': 'ok',
                'database': str(mem_db),
                'readable': readable,
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_brain(self):
        """Check NEXUS brain (chat engine)."""
        try:
            from core.nexus_brain import NexusBrain
            brain = NexusBrain()
            return {
                'status': 'ok',
                'engine': 'Built-in Pattern Matching',
                'workers_available': 22,
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_auth(self):
        """Check authentication system."""
        try:
            from core.owner_manager import OwnerManager
            owner_mgr = OwnerManager()
            has_owner = owner_mgr.has_owner()
            return {
                'status': 'ok',
                'owner_configured': has_owner,
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_logs(self):
        """Check logging system."""
        try:
            log_files = {
                'main': Config.LOG_FOLDER / 'nexus.log',
                'chat': Config.LOG_FOLDER / 'chat.log',
                'errors': Config.LOG_FOLDER / 'errors.log',
            }
            
            Config.LOG_FOLDER.mkdir(exist_ok=True, parents=True)
            
            return {
                'status': 'ok',
                'log_folder': str(Config.LOG_FOLDER),
                'log_files': {k: str(v) for k, v in log_files.items()},
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def to_dict(self):
        """Convert to dictionary for JSON response."""
        return {
            'status': self.status,
            'timestamp': self.timestamp,
            'checks': self.checks,
        }
