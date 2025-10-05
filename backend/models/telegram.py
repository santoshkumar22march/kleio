
from sqlalchemy import Column, String, Integer, TIMESTAMP, BigInteger
from sqlalchemy.sql import func
from database import Base

class TelegramVerificationCode(Base):
    __tablename__ = "telegram_verification_codes"
    
    code = Column(String(10), primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
