from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    price = Column(Float)
    agent_id = Column(Integer)
