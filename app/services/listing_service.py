# In-memory "database" for now
fake_listings_db = [
    {"id": 1, "address": "123 Main St", "price": 500000, "agent_id": 1},
    {"id": 2, "address": "456 Oak Ave", "price": 750000, "agent_id": 1},
    {"id": 3, "address": "789 Pine Ln", "price": 620000, "agent_id": 2},
]

def get_all_listings():
    """
    Business logic to retrieve all listings.
    For now, it just returns the fake database.
    """
    return fake_listings_db
