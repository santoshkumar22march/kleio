# Recipe History API endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from utils.auth import get_current_user
from schemas.recipe import RecipeSave, RecipeHistoryResponse
from crud.recipe_history import (
    save_recipe,
    get_user_recipes,
    get_recipe_by_id,
    mark_recipe_cooked,
    toggle_favorite,
    delete_recipe
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recipes", tags=["Recipe History"])


@router.post(
    "/save",
    response_model=RecipeHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save recipe",
    description="Save a generated recipe to user's collection"
)
async def save_user_recipe(
    recipe_save: RecipeSave,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a recipe to user's history
    
    User can save AI-generated recipes for later reference.
    Saved recipes can be viewed with current ingredient availability.
    """
    recipe = save_recipe(db, firebase_uid, recipe_save)
    return recipe


@router.get(
    "/list",
    response_model=List[RecipeHistoryResponse],
    summary="List saved recipes",
    description="Get all saved recipes for the user"
)
async def list_user_recipes(
    limit: int = 50,
    offset: int = 0,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's saved recipes
    
    Returns recipes ordered by creation date (newest first).
    """
    recipes = get_user_recipes(db, firebase_uid, limit, offset)
    return recipes


@router.get(
    "/{recipe_id}",
    response_model=RecipeHistoryResponse,
    summary="Get recipe",
    description="Get a specific saved recipe"
)
async def get_recipe(
    recipe_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific saved recipe by ID"""
    recipe = get_recipe_by_id(db, recipe_id, firebase_uid)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe


@router.post(
    "/{recipe_id}/mark-cooked",
    response_model=RecipeHistoryResponse,
    summary="Mark recipe as cooked",
    description="Increment cook counter and update last cooked date"
)
async def mark_as_cooked(
    recipe_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark recipe as cooked
    
    Increments times_cooked counter and updates last_cooked timestamp.
    """
    recipe = mark_recipe_cooked(db, recipe_id, firebase_uid)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe


@router.post(
    "/{recipe_id}/toggle-favorite",
    response_model=RecipeHistoryResponse,
    summary="Toggle favorite",
    description="Add/remove recipe from favorites"
)
async def toggle_recipe_favorite(
    recipe_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle recipe favorite status"""
    recipe = toggle_favorite(db, recipe_id, firebase_uid)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="Delete a saved recipe"
)
async def delete_user_recipe(
    recipe_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved recipe"""
    success = delete_recipe(db, recipe_id, firebase_uid)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return None
