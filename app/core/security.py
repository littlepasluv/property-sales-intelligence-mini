from enum import Enum
from typing import List, Optional
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

DEV_MODE_BYPASS_AUTH = False

class UserRole(str, Enum):
    FOUNDER = "founder"
    SALES_MANAGER = "sales_manager"
    OPS_CRM = "ops_crm"
    VIEWER = "viewer"

class UserContext(BaseModel):
    user_id: str
    role: UserRole
    source: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> UserContext:
    if DEV_MODE_BYPASS_AUTH:
        # This path is disabled for production lock.
        # In a real dev environment, this might return a mock user.
        # For finalization, we ensure it's off.
        pass

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        user_id: Optional[str] = payload.get("sub")
        role_str: Optional[str] = payload.get("role")
        
        if user_id is None or role_str is None:
            raise credentials_exception
            
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise HTTPException(status_code=401, detail="Token has expired")

        return UserContext(
            user_id=user_id,
            role=UserRole(role_str),
            source='jwt'
        )
    except (JWTError, ValueError):
        raise credentials_exception

def get_current_user_role(user_context: UserContext = Depends(get_current_user)) -> UserRole:
    return user_context.role

def require_roles(allowed_roles: List[UserRole]):
    def guard(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User with role '{role.value}' does not have permission."
            )
    return guard
