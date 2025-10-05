"""
CRUD operations for User model
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import logging

from models.user import User
from schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def create_or_update_user(db: Session, firebase_uid: str, user_data: UserCreate) -> User:
    """
    Create a new user or update existing user profile
    
    Args:
        db: Database session
        firebase_uid: Firebase user ID
        user_data: User profile data
        
    Returns:
        User: Created or updated user object
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if existing_user:
        # Update existing user
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(existing_user, key, value)
        
        db.commit()
        db.refresh(existing_user)
        logger.info(f"Updated user profile: {firebase_uid}")
        return existing_user
    
    else:
        # Create new user
        new_user = User(
            firebase_uid=firebase_uid,
            **user_data.model_dump()
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Created new user: {firebase_uid}")
            return new_user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise


def get_user(db: Session, firebase_uid: str) -> Optional[User]:
    """
    Get user by Firebase UID
    
    Args:
        db: Database session
        firebase_uid: Firebase user ID
        
    Returns:
        User | None: User object if found, None otherwise
    """
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()


def update_user(db: Session, firebase_uid: str, user_data: UserUpdate) -> Optional[User]:
    """
    Update user profile (partial update)
    
    Args:
        db: Database session
        firebase_uid: Firebase user ID
        user_data: Updated user data (only provided fields)
        
    Returns:
        User | None: Updated user object if found, None otherwise
    """
    user = get_user(db, firebase_uid)
    
    if not user:
        return None
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    logger.info(f"Updated user: {firebase_uid}")
    return user


def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """
    Get user by Telegram ID
    
    Args:
        db: Database session
        telegram_id: Telegram user ID
        
    Returns:
        User | None: User object if found, None otherwise
    """
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """
    Get user by phone number (for WhatsApp integration)
    
    Args:
        db: Database session
        phone_number: Phone number
        
    Returns:
        User | None: User object if found, None otherwise
    """
    return db.query(User).filter(User.phone_number == phone_number).first()

