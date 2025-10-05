"""
CRUD operations for Telegram Verification Codes
"""

from sqlalchemy.orm import Session
from models.telegram import TelegramVerificationCode
from datetime import datetime, timedelta
import secrets

def create_verification_code(db: Session, telegram_id: int) -> str:
    """
    Create a new verification code for a given Telegram ID.

    Args:
        db (Session): The database session.
        telegram_id (int): The user's Telegram ID.

    Returns:
        str: The generated verification code.
    """
    # Generate a random 6-character code
    code = secrets.token_hex(3).upper()

    # Set expiration time to 10 minutes from now
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Create a new verification code entry
    db_code = TelegramVerificationCode(
        code=code,
        telegram_id=telegram_id,
        expires_at=expires_at
    )

    db.add(db_code)
    db.commit()
    db.refresh(db_code)

    return code

def get_verification_code(db: Session, code: str) -> TelegramVerificationCode:
    """
    Get a verification code from the database.

    Args:
        db (Session): The database session.
        code (str): The verification code.

    Returns:
        TelegramVerificationCode: The verification code object, or None if not found.
    """
    return db.query(TelegramVerificationCode).filter(TelegramVerificationCode.code == code).first()

def delete_verification_code(db: Session, code: str):
    """
    Delete a verification code from the database.

    Args:
        db (Session): The database session.
        code (str): The verification code.
    """
    db.query(TelegramVerificationCode).filter(TelegramVerificationCode.code == code).delete()
    db.commit()
