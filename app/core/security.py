from enum import Enum
from typing import List
from fastapi import Request, HTTPException, Depends

class UserRole(str, Enum):
    """
    Defines the user roles in the system.
    """
    FOUNDER = "founder"
    SALES_MANAGER = "sales_manager"
    OPS_CRM = "ops_crm"

def get_current_role(request: Request) -> UserRole:
    """
    Temporary role resolver for development.
    Resolves the user's role from the 'X-User-Role' header.
    Defaults to 'founder' if the header is not present.
    """
    role_str = request.headers.get("X-User-Role", "founder")
    try:
        return UserRole(role_str)
    except ValueError:
        # If an invalid role is provided, default to founder for dev.
        return UserRole.FOUNDER

def require_roles(allowed_roles: List[UserRole]):
    """
    Factory for creating a dependency that checks for required user roles.
    Raises an HTTPException (403 Forbidden) if the current user's role
    is not in the list of allowed roles.
    """
    def guard(role: UserRole = Depends(get_current_role)):
        if role not in allowed_roles:
            # TODO: Integrate with governance logging
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. User with role '{role.value}' does not have permission for this resource."
            )
    return guard
