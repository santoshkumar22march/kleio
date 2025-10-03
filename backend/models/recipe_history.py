# Recipe History model for storing user's generated/saved recipes

from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base


class RecipeHistory(Base):
    __tablename__ = "recipe_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users
    firebase_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True)
    
    # Recipe details
    recipe_name = Column(String(200), nullable=False)
    description = Column(String(500))
    cooking_time_minutes = Column(Integer)
    difficulty = Column(String(20))
    cuisine = Column(String(50))
    servings = Column(Integer)
    
    # Store full recipe as JSON
    recipe_data = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_cooked = Column(TIMESTAMP(timezone=True), nullable=True)
    times_cooked = Column(Integer, default=0)
    is_favorite = Column(Integer, default=0)  # Using Integer for SQLite compatibility
    
    def __repr__(self):
        return f"<RecipeHistory(id={self.id}, recipe={self.recipe_name})>"
