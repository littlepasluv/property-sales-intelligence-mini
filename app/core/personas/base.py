from pydantic import BaseModel
from typing import List, Optional

class PersonaBase(BaseModel):
    name: str
    role: str
    permissions: List[str]
    description: Optional[str] = None
