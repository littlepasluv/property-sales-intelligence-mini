from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.api.v1 import lead, followup, listing, analytics, governance, ingestion, system, health, alerts, auth
from app.core.database import engine, Base, get_db
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.security import get_current_user, UserContext
from app.services.decision_sla_service import evaluate_decision_sla

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    try:
        evaluate_decision_sla(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="ProSi-mini API",
    description="A mini Property Sales Intelligence system.",
    version="0.4.0",
    lifespan=lifespan
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        db: Session = next(get_db())
        try:
            user_context: UserContext = await get_current_user(request, request.headers.get("authorization"))
            details = f"User '{user_context.user_id}' with role '{user_context.role.value}' denied access to {request.method} {request.url.path}"
            persona = user_context.role.value
        except HTTPException:
            details = f"Anonymous user denied access to {request.method} {request.url.path}"
            persona = "anonymous"
        
        log_entry = AuditLogCreate(event_type="access_denied", details=details, persona=persona)
        create_audit_log_entry(db, log_entry)
        db.close()
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})

app.include_router(auth.router, prefix="/api/v1")
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
