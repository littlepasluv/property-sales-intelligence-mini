from datetime import datetime
from typing import List, Dict, Any
from app.schemas.lead import Lead, LeadCreate

# In-memory storage (simulating a database table)
# This list will reset every time the server restarts
leads_db: List[Dict[str, Any]] = []
next_lead_id = 1

def create_lead(lead_create: LeadCreate) -> Lead:
    """
    Creates a new lead and stores it in the in-memory database.
    
    Args:
        lead_create: The data to create the lead with.
        
    Returns:
        The created Lead object with its generated ID and timestamp.
    """
    global next_lead_id
    
    # Convert Pydantic model to a dictionary
    new_lead_data = lead_create.model_dump()
    
    # Create the full Lead object (simulating DB insertion)
    new_lead = Lead(
        id=next_lead_id,
        created_at=datetime.utcnow(),
        **new_lead_data
    )
    
    # Store the raw data (simulating DB storage)
    leads_db.append(new_lead.model_dump())
    
    # Increment the ID counter
    next_lead_id += 1
    
    return new_lead

def get_all_leads() -> List[Lead]:
    """
    Retrieves all leads from the in-memory database.
    
    Returns:
        A list of Lead objects.
    """
    # Convert the raw dictionaries back into Pydantic models
    return [Lead(**lead_data) for lead_data in leads_db]
