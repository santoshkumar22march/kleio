"""
Pydantic schemas for User model validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating/updating user profile"""
    household_size: int = Field(default=1, ge=1, le=20, description="Number of people in household")
    location_city: Optional[str] = Field(default=None, max_length=100)
    language_preference: str = Field(default="en", pattern="^(en|hi|ta)$")
    dietary_preferences: Optional[Dict[str, bool]] = Field(
        default_factory=dict,
        description="Dietary restrictions: vegetarian, vegan, diabetic, gluten_free, etc."
    )
    region: Optional[str] = Field(
        default="all",
        pattern="^(north|south|east|west|all)$",
        description="Region for festival filtering"
    )
    phone_number: Optional[str] = Field(default=None, max_length=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "household_size": 4,
                "location_city": "Chennai",
                "language_preference": "ta",
                "dietary_preferences": {
                    "vegetarian": True,
                    "vegan": False,
                    "diabetic": False,
                    "gluten_free": False
                },
                "region": "south",
                "phone_number": "+919876543210"
            }
        }


class UserUpdate(BaseModel):
    """Schema for partial user profile updates"""
    household_size: Optional[int] = Field(default=None, ge=1, le=20)
    location_city: Optional[str] = Field(default=None, max_length=100)
    language_preference: Optional[str] = Field(default=None, pattern="^(en|hi|ta)$")
    dietary_preferences: Optional[Dict[str, bool]] = None
    region: Optional[str] = Field(default=None, pattern="^(north|south|east|west|all)$")
    phone_number: Optional[str] = Field(default=None, max_length=20)
    fcm_token: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user profile response"""
    firebase_uid: str
    household_size: int
    location_city: Optional[str]
    language_preference: str
    dietary_preferences: Dict[str, bool]
    region: str
    phone_number: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "firebase_uid": "abc123xyz",
                "household_size": 4,
                "location_city": "Chennai",
                "language_preference": "ta",
                "dietary_preferences": {
                    "vegetarian": True,
                    "vegan": False
                },
                "region": "south",
                "phone_number": "+919876543210",
                "created_at": "2025-10-03T10:00:00",
                "updated_at": "2025-10-03T10:00:00"
            }
        }

