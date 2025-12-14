from datetime import datetime

# In-memory "database" for now
fake_followups_db = [
    {"id": 1, "lead_id": 1, "notes": "Called John, he's interested.", "timestamp": datetime(2024, 1, 16, 10, 30)},
    {"id": 2, "lead_id": 2, "notes": "Emailed Jane with more details.", "timestamp": datetime(2024, 1, 17, 14, 0)},
]

def get_all_followups():
    """
    Business logic to retrieve all followups.
    """
    return fake_followups_db
