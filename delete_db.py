import os
import sys

db_path = "prosi_mini.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Deleted {db_path}")
    except Exception as e:
        print(f"Error deleting {db_path}: {e}")
else:
    print(f"{db_path} not found")
