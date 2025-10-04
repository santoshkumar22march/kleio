# Usage examples for LangChain agent

from agent.langchain_agent import process_message, process_message_sync
import asyncio


# Example 1: Basic usage (async)
async def example_basic_async():
    """Basic async usage example."""
    
    firebase_uid = "user123"
    message = "I bought 2kg tomatoes and 1 liter milk"
    thread_id = "conversation-1"
    
    response = await process_message(firebase_uid, message, thread_id)
    print(response)
    # Output: ✅ Added 2 items to inventory: tomatoes (2.0kg), milk (1.0liter)


# Example 2: Basic usage (sync)
def example_basic_sync():
    """Basic sync usage example."""
    
    firebase_uid = "user123"
    message = "What do I have in my inventory?"
    
    response = process_message_sync(firebase_uid, message)
    print(response)


# Example 3: Multi-turn conversation
async def example_conversation():
    """Multi-turn conversation with context."""
    
    firebase_uid = "user123"
    thread_id = "conversation-2"
    
    # Turn 1
    response1 = await process_message(
        firebase_uid,
        "I bought tomatoes and onions",
        thread_id
    )
    print("Turn 1:", response1)
    
    # Turn 2 - agent remembers context
    response2 = await process_message(
        firebase_uid,
        "How many tomatoes do I have now?",
        thread_id
    )
    print("Turn 2:", response2)
    
    # Turn 3 - more context
    response3 = await process_message(
        firebase_uid,
        "Suggest a recipe using them",
        thread_id
    )
    print("Turn 3:", response3)


# Example 4: Shopping list workflow
async def example_shopping_workflow():
    """Complete shopping workflow."""
    
    firebase_uid = "user123"
    thread_id = "shopping-1"
    
    # Check what's needed
    response1 = await process_message(
        firebase_uid,
        "What should I buy this week?",
        thread_id
    )
    print("Shopping List:", response1)
    
    # After shopping
    response2 = await process_message(
        firebase_uid,
        "Bought everything on the list",
        thread_id
    )
    print("After Shopping:", response2)


# Example 5: Recipe generation workflow
async def example_recipe_workflow():
    """Recipe generation workflow."""
    
    firebase_uid = "user123"
    thread_id = "recipe-1"
    
    # Check inventory
    response1 = await process_message(
        firebase_uid,
        "What vegetables do I have?",
        thread_id
    )
    print("Inventory:", response1)
    
    # Generate recipe
    response2 = await process_message(
        firebase_uid,
        "Give me a quick vegetarian dinner recipe under 30 minutes",
        thread_id
    )
    print("Recipe:", response2)


# Example 6: Error handling
async def example_error_handling():
    """Handling errors gracefully."""
    
    firebase_uid = "user123"
    
    try:
        response = await process_message(
            firebase_uid,
            "Show me my inventory",
            "error-test"
        )
        print(response)
    except Exception as e:
        print(f"Error occurred: {e}")
        # Agent returns user-friendly error message


# Example 7: FastAPI integration
def example_fastapi_endpoint():
    """Example FastAPI endpoint using the agent."""
    
    from fastapi import APIRouter, Depends
    from utils.auth import get_current_user
    from pydantic import BaseModel
    
    router = APIRouter()
    
    class ChatMessage(BaseModel):
        message: str
        thread_id: str = "default"
    
    @router.post("/chat")
    async def chat_endpoint(
        request: ChatMessage,
        firebase_uid: str = Depends(get_current_user)
    ):
        response = process_message_sync(
            firebase_uid,
            request.message,
            request.thread_id
        )
        return {"response": response}


# Example 8: Telegram bot handler
async def example_telegram_handler(update):
    """Example Telegram bot message handler."""
    
    # Extract message data
    telegram_user_id = update.message.from_user.id
    message_text = update.message.text
    
    # Map Telegram user to Firebase UID (implement your mapping)
    firebase_uid = get_firebase_uid_from_telegram(telegram_user_id)
    
    # Process message
    thread_id = f"telegram-{telegram_user_id}"
    response = await process_message(firebase_uid, message_text, thread_id)
    
    # Send response back to Telegram
    await update.message.reply_text(response)


# Example 9: Batch processing
async def example_batch_processing():
    """Process multiple messages in batch."""
    
    firebase_uid = "user123"
    messages = [
        "bought tomatoes",
        "bought onions",
        "bought rice"
    ]
    
    # Process all messages
    tasks = [
        process_message(firebase_uid, msg, f"batch-{i}")
        for i, msg in enumerate(messages)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for msg, resp in zip(messages, responses):
        print(f"{msg} → {resp}")


# Example 10: Custom tool usage
async def example_with_intent():
    """Different intents triggering different tools."""
    
    firebase_uid = "user123"
    
    # Intent: Add items
    await process_message(
        firebase_uid,
        "I bought 2kg tomatoes and milk"
    )
    
    # Intent: Query inventory
    await process_message(
        firebase_uid,
        "What do I have?"
    )
    
    # Intent: Shopping list
    await process_message(
        firebase_uid,
        "What should I buy?"
    )
    
    # Intent: Recipe
    await process_message(
        firebase_uid,
        "Suggest a recipe"
    )


# Helper function for Telegram example
def get_firebase_uid_from_telegram(telegram_user_id):
    """Map Telegram user ID to Firebase UID."""
    # Implement your mapping logic
    # Example: query database for mapping
    return f"firebase_user_{telegram_user_id}"


# Run examples
if __name__ == "__main__":
    print("LangChain Agent Examples")
    print("=" * 50)
    
    # Run async examples
    print("\n1. Basic Async Example:")
    asyncio.run(example_basic_async())
    
    print("\n2. Basic Sync Example:")
    example_basic_sync()
    
    print("\n3. Multi-turn Conversation:")
    asyncio.run(example_conversation())
    
    print("\n4. Shopping Workflow:")
    asyncio.run(example_shopping_workflow())
    
    print("\n5. Recipe Workflow:")
    asyncio.run(example_recipe_workflow())

