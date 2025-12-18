from enum import Enum
from typing import List, Optional
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

class UserRole(str, Enum):
    FOUNDER = "founder"
    SALES_MANAGER = "sales_manager"
    OPS_CRM = "ops_crm"

class UserContext(BaseModel):
    """
    Represents the context of the current user, derived from either
    a JWT or a fallback header.
    """
    user_id: str
    role: UserRole
    source: str # 'jwt' or 'header'

# This dependency looks for a token in the Authorization header but doesn't enforce it.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UserContext]:
    """
    Parses a JWT from the Authorization header if present.
    Does not raise an error if the token is missing or invalid,
    allowing for fallback authentication methods.
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check expiration
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            # In a real app, you might log this token expiration event.
            return None

        return UserContext(
            user_id=payload.get("sub"),
            role=UserRole(payload.get("role")),
            source='jwt'
        )
    except (JWTError, ValueError):
        # Log token validation failure
        return None

def get_current_user_role(request: Request, user_context: Optional[UserContext] = Depends(get_current_user)) -> UserRole:
    """
    Determines the user's role, prioritizing JWT context and falling back
    to the X-User-Role header for development or legacy access.
    """
    if user_context and user_context.source == 'jwt':
        return user_context.role

    # Fallback to header for backward compatibility/development
    role_str = request.headers.get("X-User-Role")
    if role_str:
        try:
            return UserRole(role_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role in X-User-Role header")
    
    # If no JWT and no header, access is denied unless the endpoint is public.
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

def require_roles(allowed_roles: List[UserRole]):
    """

    Factory for a dependency that checks if the user's role is allowed.
    The user's role is determined by get_current_user_role.
    """
    def guard(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User with role '{role.value}' does not have permission."
            )
    return guard
