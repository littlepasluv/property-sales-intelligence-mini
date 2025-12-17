from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.api.v1 import lead, followup, listing, analytics, governance, ingestion
from app.core.database import engine, Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProSi-mini API",
    description="A mini Property Sales Intelligence system.",
    version="0.2.0"
)

# --- Exception Handler ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "context": {"request_url": str(request.url)}
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # In a real production app, you would log this error in detail
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected internal server error occurred.",
            "context": {"error_type": type(exc).__name__}
        },
    )

# Include API routers
app.include_router(lead.router, prefix="/api/v1")
app.include_router(followup.router, prefix="/api/v1")
app.include_router(listing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ProSi-mini API"}
