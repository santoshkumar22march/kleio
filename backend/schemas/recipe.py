# Pydantic schemas for Recipe History

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RecipeIngredient(BaseModel):
    item: str
    quantity: float
    unit: str
    available: bool
    note: Optional[str] = None


class RecipeNutrition(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int
    fiber: int


class RecipeData(BaseModel):
    recipe_name: str
    description: str
    cooking_time_minutes: int
    difficulty: str
    cuisine: str
    servings: int
    ingredients: List[RecipeIngredient]
    instructions: List[str]
    tips: List[str]
    nutrition: RecipeNutrition


class RecipeSave(BaseModel):
    """Schema for saving a recipe"""
    recipe_data: RecipeData


class RecipeHistoryResponse(BaseModel):
    """Schema for recipe history response"""
    id: int
    firebase_uid: str
    recipe_name: str
    description: str
    cooking_time_minutes: int
    difficulty: str
    cuisine: str
    servings: int
    recipe_data: RecipeData
    created_at: datetime
    last_cooked: Optional[datetime]
    times_cooked: int
    is_favorite: bool
    
    class Config:
        from_attributes = True
