"""
NEXUS — Owner Manager
Manages the founder/owner profile.
"""

import json, uuid, datetime
from pathlib import Path
from core.auth import Auth

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'


class OwnerManager:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self._auth       = Auth()
        self._owner_file = DATA_DIR / 'owner.json'

    def has_owner(self) -> bool:
        return self._owner_file.exists()

    def create_owner(self, full_name: str, email: str, phone: str,
                     company: str, country: str, timezone: str,
                     password: str) -> dict:
        if self.has_owner():
            return {'success': False, 'error': 'Owner already registered.'}

        if not full_name or not email or not password:
            return {'success': False, 'error': 'Name, email and password are required.'}

        owner = {
            'id'            : str(uuid.uuid4()),
            'full_name'     : full_name,
            'email'         : email.lower(),
            'phone'         : phone,
            'company'       : company or 'NEXUS',
            'country'       : country,
            'timezone'      : timezone or 'UTC',
            'password_hash' : self._auth.hash_password(password),
            'created_at'    : datetime.datetime.now().isoformat(),
            'role'          : 'founder',
        }

        with open(self._owner_file, 'w') as f:
            json.dump(owner, f, indent=2)

        return {
            'success'  : True,
            'owner_id' : owner['id'],
            'name'     : owner['full_name'],
        }

    def get_owner(self) -> dict:
        """Return owner profile without the password hash."""
        if not self._owner_file.exists():
            return {}
        with open(self._owner_file) as f:
            owner = json.load(f)
        owner.pop('password_hash', None)
        return owner

    def update_owner(self, updates: dict) -> dict:
        if not self._owner_file.exists():
            return {'success': False, 'error': 'No owner found.'}
        with open(self._owner_file) as f:
            owner = json.load(f)
        safe_keys = {'full_name', 'phone', 'company', 'country', 'timezone'}
        for k, v in updates.items():
            if k in safe_keys:
                owner[k] = v
        owner['updated_at'] = datetime.datetime.now().isoformat()
        with open(self._owner_file, 'w') as f:
            json.dump(owner, f, indent=2)
        return {'success': True}
