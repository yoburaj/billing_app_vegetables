from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from app.database.database import get_db
from app.models.user import User
from app.core.auth import (
    create_access_token,
    hash_password,
    decrypt_phone,
    verify_password,
)
from jose import JWTError, jwt
from app.core import config

router = APIRouter()

RESET_TOKEN_EXPIRE_MINUTES = 15
ALGORITHM = "HS256"


# ── Schemas ────────────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    username: str
    mobile_number: str   # plain text sent by client; we'll compare after decrypt


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str


# ── Helper ─────────────────────────────────────────────────────────────────────

async def _match_mobile(plain_phone: str, encrypted_phone: str) -> bool:
    """Decrypt the stored phone and compare to the plain input."""
    try:
        decrypted = await decrypt_phone(encrypted_phone)
        # Normalise: strip spaces / dashes for a loose match
        return plain_phone.strip() == decrypted.strip()
    except Exception:
        return False


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Step 1 – Verify identity.
    Accepts username + registered mobile number.
    Returns a short-lived reset token if verification succeeds.
    """
    user = db.query(User).filter(User.username == request.username).first()

    # Generic error to avoid user-enumeration attacks
    generic_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username or mobile number is incorrect",
    )

    if not user:
        raise generic_error

    if not user.mobile_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mobile number is registered for this account. "
                   "Please contact the administrator.",
        )

    phone_match = await _match_mobile(request.mobile_number, user.mobile_number)
    if not phone_match:
        raise generic_error

    # Issue a short-lived password-reset JWT
    reset_token = create_access_token(
        data={"sub": user.username, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    )

    return ForgotPasswordResponse(
        message="Identity verified. Use the reset token to set a new password.",
        reset_token=reset_token,
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2 – Reset password.
    Accepts the reset token (from Step 1) + new password.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )

    try:
        payload = jwt.decode(
            request.reset_token, config.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        purpose: str = payload.get("purpose")
        if not username or purpose != "password_reset":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception

    # Hash and persist the new password
    new_hashed = await hash_password(request.new_password)
    user.hashed_password = new_hashed
    db.commit()

    return ResetPasswordResponse(message="Password has been reset successfully.")
