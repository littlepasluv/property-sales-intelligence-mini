from pydantic import BaseModel

class Listing(BaseModel):
    id: int
    address: str
    price: float
    agent_id: int
