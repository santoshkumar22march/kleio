from functools import partial
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from agent.tools.inventory_tools import add_items_wrapper, query_inventory_wrapper
from agent.tools.recipe_tools import check_recipe_feasibility
from agent.tools.shopping_tools import get_shopping_wrapper

logger = logging.getLogger(__name__)


def create_agent(firebase_uid: str, db_session: Session):
    """
    Create LangChain agent for a user with conversation memory.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )
    
    # Bind the firebase_uid and db_session to the tool functions
    add_items_tool = partial(add_items_wrapper, firebase_uid=firebase_uid, db_session=db_session)
    query_inventory_tool = partial(query_inventory_wrapper, firebase_uid=firebase_uid, db_session=db_session)
    get_shopping_tool = partial(get_shopping_wrapper, firebase_uid=firebase_uid, db_session=db_session)
    check_recipe_tool = partial(check_recipe_feasibility, firebase_uid=firebase_uid, db_session=db_session)

    from langchain.tools import StructuredTool
    
    tools = [
        StructuredTool.from_function(
            func=add_items_tool,
            name="add_inventory_items",
            description="Add items to inventory from natural language (e.g., 'bought 2kg tomatoes and milk'). Returns JSON with added items that you MUST format into a natural response."
        ),
        StructuredTool.from_function(
            func=query_inventory_tool,
            name="query_inventory",
            description="Query user's current inventory items. Optional category filter. Returns JSON with items data that you MUST format into a natural response."
        ),
        StructuredTool.from_function(
            func=get_shopping_tool,
            name="get_shopping_list",
            description="Generate smart shopping list based on usage patterns. Returns JSON with urgent/this_week/later items that you MUST format into a natural response."
        ),
        StructuredTool.from_function(
            func=check_recipe_tool,
            name="check_recipe_feasibility",
            description="Check if a recipe is feasible with current inventory. Generates full recipe with ingredients marked as available/missing. Returns JSON that you MUST format into a helpful natural response."
        ),
    ]
    
    system_message = f"""You are Kleio, a friendly household inventory assistant for Indian families.

USER ID: {firebase_uid}

HOW YOU WORK:
1. Tools return JSON data with structured information
2. You MUST call the appropriate tool for every user request
3. You MUST format the JSON data into natural, friendly responses
4. You NEVER make up data - only use what tools return

AVAILABLE TOOLS & WHEN TO USE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 add_inventory_items(items_text)
   When: User says they bought/added items
   Returns: JSON with added items
   You format as: "✅ Added [items] to your inventory!"

📦 query_inventory(category)
   When: User asks what they have
   Returns: JSON with inventory items grouped by category
   You format as: Natural list organized by category with quantities

🛒 get_shopping_list(urgency)
   When: User asks what to buy
   Returns: JSON with urgent/this_week/later items
   You format as: Organized shopping list with urgency levels

🍳 check_recipe_feasibility(preferences)
   When: User wants recipe suggestions
   Returns: JSON with recipe details and ingredient availability
   You format as: Recipe summary with what they have vs need to buy

RESPONSE STYLE:
✅ Friendly and conversational (but not overly chatty)
✅ Use emojis appropriately: ✅ ❌ 🔴 🟡 🟢 📦 🛒 🍳
✅ Indian context: kg, liters, INR, common Indian items
✅ Clear and actionable information
❌ Never say "I'll try" or "let me" - just call the tool and report results
❌ Never apologize for non-existent errors
❌ Never make up data

EXAMPLES:
User: "bought 2kg tomatoes and milk"
You: Call add_inventory_items("bought 2kg tomatoes and milk") → Format JSON as natural response

User: "what vegetables do I have?"
You: Call query_inventory("vegetables") → Format JSON showing vegetables with quantities

User: "what should I buy this week?"
You: Call get_shopping_list("this_week") → Format JSON as organized shopping list

User: "can I make dinner with what I have?"
You: Call check_recipe_feasibility("dinner") → Format JSON showing recipe feasibility
"""
    
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

