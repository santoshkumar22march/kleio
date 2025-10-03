# CRUD operations package

from crud.user import create_or_update_user, get_user, update_user
from crud.inventory import (
    create_inventory_item,
    get_user_inventory,
    get_inventory_item,
    update_inventory_item,
    delete_inventory_item,
    mark_item_as_used,
    get_common_items
)
from crud.recipe_history import (
    save_recipe,
    get_user_recipes,
    get_recipe_by_id,
    mark_recipe_cooked,
    toggle_favorite,
    delete_recipe
)

__all__ = [
    "create_or_update_user",
    "get_user",
    "update_user",
    "create_inventory_item",
    "get_user_inventory",
    "get_inventory_item",
    "update_inventory_item",
    "delete_inventory_item",
    "mark_item_as_used",
    "get_common_items",
    "save_recipe",
    "get_user_recipes",
    "get_recipe_by_id",
    "mark_recipe_cooked",
    "toggle_favorite",
    "delete_recipe",
]

