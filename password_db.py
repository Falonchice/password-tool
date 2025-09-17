import json
from Crypto.Cipher import AES
import base64
import os
import hashlib

class PasswordDB:
    def __init__(self, db_file, master_password):
        self.db_file = db_file
        self.key = hashlib.sha256(master_password.encode()).digest()
        self.data = []
        if os.path.exists(db_file):
            self.load()

    def pad(self, s):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = os.urandom(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode()

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[AES.block_size:]).decode())

    def load(self):
        with open(self.db_file, 'r') as f:
            enc_data = f.read()
        try:
            raw = self.decrypt(enc_data)
            self.data = json.loads(raw)
        except Exception:
            raise Exception("Invalid master password or corrupted database.")

    def save(self):
        raw = json.dumps(self.data)
        enc_data = self.encrypt(raw)
        with open(self.db_file, 'w') as f:
            f.write(enc_data)

    def add_entry(self, name, username, password, remark=''):
        self.data.append({'name': name, 'username': username, 'password': password, 'remark': remark})

    def update_entry(self, idx, name, username, password, remark=''):
        self.data[idx] = {'name': name, 'username': username, 'password': password, 'remark': remark}

    def delete_entry(self, idx):
        del self.data[idx]

    def search(self, keyword):
        return [
            (i, item)
            for i, item in enumerate(self.data)
            if keyword.lower() in item['name'].lower()
            or keyword.lower() in item['username'].lower()
            or keyword.lower() in item['remark'].lower()
        ]

    def export_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            imported = json.load(f)
            if isinstance(imported, list):
                self.data.extend(imported)