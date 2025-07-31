import json
import os

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.db = self.load_db()

    def load_db(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({'api_keys': []}, f)
        with open(self.db_file, 'r') as f:
            return json.load(f)

    def get_api_key(self):
        return self.db['api_keys'][0] if self.db['api_keys'] else None

    def save(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f)
