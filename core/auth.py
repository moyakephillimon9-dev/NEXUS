"""
NEXUS — Authentication Manager
Handles password hashing and credential verification.
"""

import hashlib, os, json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'


class Auth:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    # ── Password utilities ────────────────────────────────────────────────────
    def hash_password(self, password: str) -> str:
        salt   = os.urandom(32).hex()
        hashed = hashlib.sha256(f"{salt}{password}".encode('utf-8')).hexdigest()
        return f"{salt}:{hashed}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt, hashed = stored_hash.split(':', 1)
            return hashlib.sha256(
                f"{salt}{password}".encode('utf-8')
            ).hexdigest() == hashed
        except Exception:
            return False

    # ── Login verification ────────────────────────────────────────────────────
    def verify(self, email: str, password: str) -> dict:
        owner_file = DATA_DIR / 'owner.json'
        if not owner_file.exists():
            return {'success': False, 'error': 'No owner registered.'}

        with open(owner_file) as f:
            owner = json.load(f)

        if owner.get('email', '').lower() != email.lower():
            return {'success': False, 'error': 'Invalid credentials.'}

        if not self.verify_password(password, owner.get('password_hash', '')):
            return {'success': False, 'error': 'Invalid credentials.'}

        return {
            'success'  : True,
            'owner_id' : owner['id'],
            'name'     : owner['full_name'],
        }
