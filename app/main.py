from fastapi import FastAPI
from app.api.v1 import lead, followup
from app.core.database import Base, engine

# Create all database tables
Base.metadata.create_all(bind=engine)

# 1. Create FastAPI app instance
app = FastAPI(
    title="Property Sales Intelligence (Mini)",
    description="MVP for Property Sales Intelligence",
    version="0.1.0"
)

# 2. Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint to verify the API is reachable.
    """
    return {"message": "Welcome to Property Sales Intelligence (Mini)"}

# 3. Health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check for monitoring tools.
    """
    return {"status": "ok"}

# 4. Include routers
app.include_router(lead.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(followup.router, prefix="/api/v1", tags=["Follow-ups"])
