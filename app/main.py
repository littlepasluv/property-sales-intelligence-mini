from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.api.v1 import lead, followup, listing, analytics, governance, ingestion, system, health, alerts
from app.core.database import engine, Base, get_db
from app.services.audit_log_service import create_audit_log
from app.schemas.audit_log import AuditLogCreate

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProSi-mini API",
    description="A mini Property Sales Intelligence system.",
    version="0.3.0"
)

# --- Exception Handler ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        # Use a separate DB session for logging
        db: Session = next(get_db())
        role = request.headers.get("X-User-Role", "unknown")
        log_entry = AuditLogCreate(
            event_type="access_denied",
            details=f"Role '{role}' denied access to {request.method} {request.url.path}",
            persona=role
        )
        create_audit_log(db, log_entry)
        db.close()

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # For now, we just return a generic 500 error
    # In production, you'd want to log this exception to a file or monitoring service
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# Include API routers
app.include_router(lead.router, prefix="/api/v1")
app.include_router(followup.router, prefix="/api/v1")
app.include_router(listing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ProSi-mini API"}
