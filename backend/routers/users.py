# User profile management endpoints


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from utils.auth import get_current_user
from schemas.user import UserCreate, UserResponse, UserUpdate
from schemas.telegram import VerificationCode
from crud.user import create_or_update_user, get_user, update_user
from crud.telegram import get_verification_code, delete_verification_code

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update user profile",
    description="Create a new user profile or update existing one. Called during onboarding."
)
async def create_or_update_profile(
    user_data: UserCreate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create or update user profile

    """    
    - **household_size**: Number of people in household (1-20)
    - **language_preference**: Preferred language (en, hi, ta)
    - **dietary_preferences**: Dict of dietary restrictions
    - **region**: Region for festival filtering (north, south, east, west, all)
    """    
    user = create_or_update_user(db, firebase_uid, user_data)
    return user


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get the current user's profile information"
)
async def get_profile(
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get current user's profile

    user = get_user(db, firebase_uid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete onboarding first."
        )
    
    return user


@router.patch(
    "/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Partially update user profile (only provided fields)"
)
async def update_profile(
    user_data: UserUpdate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user profile (partial update)

    user = update_user(db, firebase_uid, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return user


@router.post("/verify-telegram", summary="Verify Telegram bot", description="Verify the one-time code from the Telegram bot and link accounts")
async def verify_telegram(
    verification_data: VerificationCode,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    code = verification_data.verification_code
    
    # 1. Look up verification code
    verification_code = get_verification_code(db, code)
    
    if not verification_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid verification code.")

    # 2. Check if code is expired
    if verification_code.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired.")

    # 3. Get user profile
    user = get_user(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")

    # 4. Link accounts
    user.telegram_id = verification_code.telegram_id
    db.commit()

    # 5. Delete the verification code
    delete_verification_code(db, code)

    return {"success": True, "message": "Telegram account linked successfully."}


@router.get(
    "/me",
    summary="Get current user info",
    description="Get basic info about the authenticated user"
)
async def get_me(firebase_uid: str = Depends(get_current_user)):
    # Get current authenticated user's Firebase UID

    return {
        "firebase_uid": firebase_uid,
        "authenticated": True
    }
