# LangChain agent that wraps Kleio.ai backend functions as tools
# PURE WRAPPER APPROACH: Tools call existing functions, return data, LLM formats response

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
import json
import asyncio

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.orm import Session

from config import settings
from crud.inventory import create_inventory_item, get_user_inventory
from schemas.inventory import InventoryCreate
from utils.pattern_analyzer import generate_shopping_list
from utils.gemini_client import get_gemini_client
from models.inventory import ItemStatus
from database import get_db

logger = logging.getLogger(__name__)


# Agent setup and process_message function

def create_agent(firebase_uid: str, db_session: Session):
    """
    Create LangChain agent for a user with conversation memory.
    
    Args:
        firebase_uid: User's Firebase UID
        db_session: Database session
        
    Returns:
        Configured agent with tools and memory
    """
    
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )
    
    # Create wrapper functions that bind firebase_uid and db_session
    def add_items_wrapper(items_text: str) -> str:
        """Add items to inventory from natural language."""
        logger.info(f"🔧 TOOL CALLED: add_items_wrapper with input: {items_text}")
        try:
            # Use Gemini to parse the natural language into structured items
            gemini = get_gemini_client()
            
            prompt = f"""
Parse this natural language text into structured grocery items:
"{items_text}"

Return ONLY valid JSON array (no markdown):
[
  {{
    "item_name": "tomatoes",
    "quantity": 2.0,
    "unit": "kg",
    "category": "vegetables"
  }},
  {{
    "item_name": "milk",
    "quantity": 1.0,
    "unit": "liter",
    "category": "dairy"
  }}
]

Categories: vegetables, fruits, dairy, staples, pulses, spices, snacks, beverages, meat, seafood, bakery, frozen, oils, condiments, others
"""
            
            response = gemini.client.models.generate_content(
                model=gemini.MODEL_ID,
                contents=prompt,
                config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )
            
            items_data = json.loads(response.text)
            
            if not isinstance(items_data, list) or not items_data:
                return "❌ Could not understand the items. Please be more specific (e.g., '2kg tomatoes, 1 liter milk')"
            
            # Add items to inventory
            added_items = []
            for item_dict in items_data:
                item = InventoryCreate(**item_dict)
                created_item = create_inventory_item(db_session, firebase_uid, item)
                added_items.append(f"{created_item.item_name} ({created_item.quantity}{created_item.unit})")
                logger.info(f"✅ Database updated: {created_item.item_name} added to inventory")
            
            result = f"✅ Added {len(added_items)} items to inventory: {', '.join(added_items)}"
            logger.info(f"🔧 TOOL RESULT: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error adding inventory items: {e}")
            return f"❌ Failed to add items: {str(e)}"
    
    def get_shopping_wrapper(urgency: Optional[str] = None) -> str:
        """Get smart shopping list."""
        logger.info(f"🔧 TOOL CALLED: get_shopping_wrapper with urgency: {urgency}")
        try:
            shopping_list = generate_shopping_list(
                db=db_session,
                firebase_uid=firebase_uid,
                urgency_filter=urgency
            )
            
            result = []
            
            # Format urgent items
            if shopping_list["urgent"]:
                result.append("🔴 URGENT (Buy today/tomorrow):")
                for item in shopping_list["urgent"]:
                    result.append(f"  • {item['item_name']} - {item['suggested_quantity']:.1f}{item['unit']} ({item['reason']})")
            
            # Format this week items
            if shopping_list["this_week"]:
                result.append("\n🟡 THIS WEEK:")
                for item in shopping_list["this_week"]:
                    result.append(f"  • {item['item_name']} - {item['suggested_quantity']:.1f}{item['unit']} ({item['reason']})")
            
            # Format later items
            if shopping_list["later"]:
                result.append("\n🟢 LATER:")
                for item in shopping_list["later"]:
                    result.append(f"  • {item['item_name']} - {item['suggested_quantity']:.1f}{item['unit']} ({item['reason']})")
            
            if not result:
                return "✅ Your inventory looks good! No urgent shopping needed right now."
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error generating shopping list: {e}")
            return f"❌ Failed to generate shopping list: {str(e)}"
    
    def generate_recipe_wrapper(preferences: str = "") -> str:
        """Generate recipe from inventory."""
        logger.info(f"🔧 TOOL CALLED: generate_recipe_wrapper with preferences: {preferences}")
        try:
            # Get user's inventory
            inventory_items = get_user_inventory(
                db_session,
                firebase_uid,
                status=ItemStatus.ACTIVE,
                limit=500
            )
            
            if not inventory_items:
                return "❌ Your inventory is empty. Please add items first before generating recipes."
            
            # Build available items list
            available_items = [f"{item.item_name} ({item.quantity}{item.unit})" for item in inventory_items]
            
            # Parse preferences to extract filters
            gemini = get_gemini_client()
            
            # Generate recipe using existing function
            filters = {
                "cooking_time": 45,
                "meal_type": "any",
                "cuisine": "Indian"
            }
            
            # Extract preferences from natural language
            preferences_lower = preferences.lower()
            if "quick" in preferences_lower or "fast" in preferences_lower or "30" in preferences_lower:
                filters["cooking_time"] = 30
            if "lunch" in preferences_lower:
                filters["meal_type"] = "lunch"
            elif "dinner" in preferences_lower:
                filters["meal_type"] = "dinner"
            elif "breakfast" in preferences_lower:
                filters["meal_type"] = "breakfast"
            
            # For now, return a helpful message with available items
            # Note: Full recipe generation requires async context
            result = [
                f"🍳 **Recipe Suggestions Based on Your Inventory**",
                f"\nYou have {len(available_items)} items available:",
            ]
            
            for item in available_items[:10]:  # Show first 10 items
                result.append(f"  • {item}")
            
            if len(available_items) > 10:
                result.append(f"  ... and {len(available_items) - 10} more items")
            
            result.append(f"\n💡 **Suggestion:** Use the web interface at /api/ai/generate-recipe for full recipe generation with detailed instructions.")
            result.append(f"\nPreferences: {preferences}")
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return f"❌ Failed to generate recipe: {str(e)}"
    
    def query_inventory_wrapper(category: Optional[str] = None) -> str:
        """Query current inventory."""
        logger.info(f"🔧 TOOL CALLED: query_inventory_wrapper with category: {category}")
        try:
            inventory_items = get_user_inventory(
                db_session,
                firebase_uid,
                status=ItemStatus.ACTIVE,
                category=category,
                limit=100
            )
            
            if not inventory_items:
                if category:
                    return f"❌ No {category} items found in your inventory."
                return "❌ Your inventory is empty. Add items to get started!"
            
            # Group by category
            by_category = {}
            for item in inventory_items:
                if item.category not in by_category:
                    by_category[item.category] = []
                by_category[item.category].append(item)
            
            result = [f"📦 **Your Inventory** ({len(inventory_items)} items):"]
            
            for cat, items in sorted(by_category.items()):
                result.append(f"\n**{cat.title()}:**")
                for item in items:
                    expiry_text = ""
                    if item.expiry_date:
                        days_left = (item.expiry_date - date.today()).days
                        if days_left <= 3:
                            expiry_text = f" ⚠️ Expires in {days_left} days"
                        elif days_left <= 7:
                            expiry_text = f" ⏰ Expires in {days_left} days"
                    
                    result.append(f"  • {item.item_name}: {item.quantity}{item.unit}{expiry_text}")
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error querying inventory: {e}")
            return f"❌ Failed to query inventory: {str(e)}"
    
    # Wrap the functions as tools with proper signatures
    from langchain.tools import StructuredTool
    
    tools = [
        StructuredTool.from_function(
            func=add_items_wrapper,
            name="add_inventory_items",
            description="Add items to user's inventory from natural language. Example: 'bought 2kg tomatoes and 1 liter milk'"
        ),
        StructuredTool.from_function(
            func=get_shopping_wrapper,
            name="get_shopping_list",
            description="Generate smart shopping list based on usage patterns. Can filter by urgency: 'urgent', 'this_week', or None for all"
        ),
        StructuredTool.from_function(
            func=generate_recipe_wrapper,
            name="generate_recipe",
            description="Generate recipe from available inventory items. Include preferences like 'quick vegetarian dinner' or 'North Indian lunch'"
        ),
        StructuredTool.from_function(
            func=query_inventory_wrapper,
            name="query_inventory",
            description="Query user's current inventory. Can filter by category like 'vegetables', 'dairy', or None for all items"
        ),
    ]
    
    # System prompt - CRITICAL: Must be emphatic about tool usage
    system_message = f"""You are Kleio, a household inventory management assistant for Indian families.

Current user: {firebase_uid}

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. ALWAYS use tools to perform actions - NEVER just talk about doing them
2. When user wants to add items → MUST call add_inventory_items tool
3. When user wants shopping list → MUST call get_shopping_list tool  
4. When user wants recipe → MUST call generate_recipe tool
5. When user wants inventory → MUST call query_inventory tool

TOOL USAGE EXAMPLES (YOU MUST DO THIS):
- User: "bought tomatoes and milk" → CALL add_inventory_items("bought tomatoes and milk")
- User: "what should I buy?" → CALL get_shopping_list(urgency=None)
- User: "suggest a recipe" → CALL generate_recipe(preferences="")
- User: "what do I have?" → CALL query_inventory(category=None)

DO NOT:
❌ Say "I'll add items" without calling the tool
❌ Say "I tried adding" without showing tool results  
❌ Make up responses - only relay tool results
❌ Apologize for errors that didn't happen

DO:
✅ Call the tool immediately
✅ Return the exact result from the tool
✅ Be friendly but action-oriented

For Indian context: use kg/liters, INR currency, common Indian grocery items.
"""
    
    # Create agent with memory
    memory = MemorySaver()
    agent = create_react_agent(
        llm,
        tools,
        state_modifier=system_message,
        checkpointer=memory
    )
    
    return agent


async def process_message(firebase_uid: str, message: str, thread_id: str = "default") -> str:
    """
    Process user message through LangChain agent.
    
    Args:
        firebase_uid: User's Firebase UID
        message: User's message
        thread_id: Conversation thread ID for memory (default: "default")
        
    Returns:
        Agent's response as string
        
    Example:
        response = await process_message("user123", "I bought 2kg tomatoes and milk", "chat-1")
    """
    try:
        logger.info(f"Processing message for {firebase_uid}: {message}")
        
        # Get database session
        db = next(get_db())
        
        # Create agent with bound context
        agent = create_agent(firebase_uid, db)
        
        # Invoke agent
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        response = agent.invoke(
            {"messages": [("user", message)]},
            config=config
        )
        
        # Extract final response
        messages = response.get("messages", [])
        logger.info(f"📨 Agent returned {len(messages)} messages")
        
        if messages:
            final_message = messages[-1]
            logger.info(f"📨 Final message type: {type(final_message).__name__}")
            if hasattr(final_message, "content"):
                logger.info(f"📨 Final response: {final_message.content[:200]}...")
                return final_message.content
            return str(final_message)
        
        return "I'm sorry, I couldn't process that request. Please try again."
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return f"❌ Sorry, I encountered an error: {str(e)}"


# Synchronous wrapper for non-async contexts
def process_message_sync(firebase_uid: str, message: str, thread_id: str = "default") -> str:
    """
    Synchronous wrapper for process_message.
    
    IMPORTANT: Use this ONLY in non-async contexts (scripts, CLI, sync code).
    For FastAPI async endpoints, use process_message() directly with await.
    
    This function creates its own event loop, which conflicts with existing loops.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(process_message(firebase_uid, message, thread_id))

