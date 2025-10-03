# CRUD operations for Recipe History

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from models.recipe_history import RecipeHistory
from schemas.recipe import RecipeSave, RecipeData

logger = logging.getLogger(__name__)


def save_recipe(db: Session, firebase_uid: str, recipe_save: RecipeSave) -> RecipeHistory:
    """
    Save a recipe to user's history
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        recipe_save: Recipe data to save
        
    Returns:
        RecipeHistory: Saved recipe
    """
    recipe_data = recipe_save.recipe_data
    
    new_recipe = RecipeHistory(
        firebase_uid=firebase_uid,
        recipe_name=recipe_data.recipe_name,
        description=recipe_data.description,
        cooking_time_minutes=recipe_data.cooking_time_minutes,
        difficulty=recipe_data.difficulty,
        cuisine=recipe_data.cuisine,
        servings=recipe_data.servings,
        recipe_data=recipe_data.model_dump(),
        times_cooked=0,
        is_favorite=0
    )
    
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    logger.info(f"Saved recipe: {new_recipe.recipe_name} for user {firebase_uid}")
    return new_recipe


def get_user_recipes(
    db: Session,
    firebase_uid: str,
    limit: int = 50,
    offset: int = 0
) -> List[RecipeHistory]:
    """
    Get user's saved recipes
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        limit: Maximum recipes to return
        offset: Number of recipes to skip
        
    Returns:
        List[RecipeHistory]: List of saved recipes
    """
    recipes = db.query(RecipeHistory).filter(
        RecipeHistory.firebase_uid == firebase_uid
    ).order_by(RecipeHistory.created_at.desc()).limit(limit).offset(offset).all()
    
    return recipes


def get_recipe_by_id(db: Session, recipe_id: int, firebase_uid: str) -> Optional[RecipeHistory]:
    """
    Get a specific recipe by ID
    
    Args:
        db: Database session
        recipe_id: Recipe ID
        firebase_uid: User's Firebase UID
        
    Returns:
        RecipeHistory | None: Recipe if found
    """
    recipe = db.query(RecipeHistory).filter(
        RecipeHistory.id == recipe_id,
        RecipeHistory.firebase_uid == firebase_uid
    ).first()
    
    return recipe


def mark_recipe_cooked(db: Session, recipe_id: int, firebase_uid: str) -> Optional[RecipeHistory]:
    """
    Mark recipe as cooked (increment counter, update last_cooked)
    
    Args:
        db: Database session
        recipe_id: Recipe ID
        firebase_uid: User's Firebase UID
        
    Returns:
        RecipeHistory | None: Updated recipe if found
    """
    recipe = get_recipe_by_id(db, recipe_id, firebase_uid)
    
    if not recipe:
        return None
    
    from sqlalchemy.sql import func
    recipe.times_cooked += 1
    recipe.last_cooked = func.now()
    
    db.commit()
    db.refresh(recipe)
    logger.info(f"Marked recipe {recipe_id} as cooked for user {firebase_uid}")
    return recipe


def toggle_favorite(db: Session, recipe_id: int, firebase_uid: str) -> Optional[RecipeHistory]:
    """
    Toggle recipe favorite status
    
    Args:
        db: Database session
        recipe_id: Recipe ID
        firebase_uid: User's Firebase UID
        
    Returns:
        RecipeHistory | None: Updated recipe if found
    """
    recipe = get_recipe_by_id(db, recipe_id, firebase_uid)
    
    if not recipe:
        return None
    
    recipe.is_favorite = 1 if recipe.is_favorite == 0 else 0
    
    db.commit()
    db.refresh(recipe)
    logger.info(f"Toggled favorite for recipe {recipe_id} (now: {recipe.is_favorite})")
    return recipe


def delete_recipe(db: Session, recipe_id: int, firebase_uid: str) -> bool:
    """
    Delete a saved recipe
    
    Args:
        db: Database session
        recipe_id: Recipe ID
        firebase_uid: User's Firebase UID
        
    Returns:
        bool: True if deleted, False if not found
    """
    recipe = get_recipe_by_id(db, recipe_id, firebase_uid)
    
    if not recipe:
        return False
    
    db.delete(recipe)
    db.commit()
    logger.info(f"Deleted recipe {recipe_id} for user {firebase_uid}")
    return True
