# User model for storing user profiles and preferences
"""
Architecture Note:
- firebase_uid is the PRIMARY KEY (from Firebase Auth)
- NO passwords stored (Firebase handles authentication)
- This table only stores application-specific profile data
- Firebase manages: passwords, email verification, OAuth, sessions
- We manage: household preferences, dietary restrictions, inventory data
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, BigInteger
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    
    # Primary key - Firebase UID
    firebase_uid = Column(String(128), primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    
    # Profile information
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    household_size = Column(Integer, default=1)
    location_city = Column(String(100), nullable=True)
    language_preference = Column(String(10), default="en")  # en, hi, ta
    
    # Dietary preferences stored as JSON
    # Example: {"vegetarian": true, "vegan": false, "diabetic": false, "gluten_free": false}
    dietary_preferences = Column(JSON, default=dict)
    
    # Region for festival filtering
    region = Column(String(50), default="all")  # north, south, east, west, all
    
    # FCM token for push notifications (future feature)
    fcm_token = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(firebase_uid={self.firebase_uid}, household_size={self.household_size})>"

