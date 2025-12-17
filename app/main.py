from fastapi import FastAPI
from app.api.v1 import lead, followup, listing, analytics, governance
from app.core.database import engine, Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProSi-mini API",
    description="A mini Property Sales Intelligence system.",
    version="0.1.0"
)

# Include API routers
app.include_router(lead.router, prefix="/api/v1")
app.include_router(followup.router, prefix="/api/v1")
app.include_router(listing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ProSi-mini API"}
