"""Admin authentication (HTTP Basic).

If ``ADMIN_USERNAME`` and ``ADMIN_PASSWORD`` are both configured, the admin
panel and other protected routes require those credentials. If they are not
configured, access is allowed but a warning is logged at startup.
"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import config

_basic = HTTPBasic(auto_error=False)


def require_admin(
    credentials: HTTPBasicCredentials = Depends(_basic),
) -> None:
    """FastAPI dependency guarding admin-only routes."""
    if not config.ADMIN_AUTH_ENABLED:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Basic"},
        )

    valid_user = secrets.compare_digest(
        credentials.username, config.ADMIN_USERNAME
    )
    valid_pass = secrets.compare_digest(
        credentials.password, config.ADMIN_PASSWORD
    )
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
