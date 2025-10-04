# Test script for LangChain agent

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.langchain_agent import process_message


async def test_agent():
    """Test the LangChain agent with sample messages."""
    
    # Use a test firebase_uid
    test_uid = "test_user_123"
    thread_id = "test_thread"
    
    print("🤖 Kleio.ai LangChain Agent Test")
    print("=" * 50)
    print()
    
    # Test 1: Add items
    print("Test 1: Adding items to inventory")
    print("-" * 50)
    message1 = "I bought 2kg tomatoes, 1 liter milk and some onions"
    print(f"User: {message1}")
    response1 = await process_message(test_uid, message1, thread_id)
    print(f"Agent: {response1}")
    print()
    
    # Test 2: Query inventory
    print("Test 2: Querying inventory")
    print("-" * 50)
    message2 = "What do I have in my inventory?"
    print(f"User: {message2}")
    response2 = await process_message(test_uid, message2, thread_id)
    print(f"Agent: {response2}")
    print()
    
    # Test 3: Shopping list
    print("Test 3: Getting shopping list")
    print("-" * 50)
    message3 = "What should I buy?"
    print(f"User: {message3}")
    response3 = await process_message(test_uid, message3, thread_id)
    print(f"Agent: {response3}")
    print()
    
    # Test 4: Recipe generation
    print("Test 4: Generating recipe")
    print("-" * 50)
    message4 = "Suggest a quick vegetarian recipe"
    print(f"User: {message4}")
    response4 = await process_message(test_uid, message4, thread_id)
    print(f"Agent: {response4}")
    print()
    
    print("=" * 50)
    print("✅ Tests completed!")


def test_agent_sync():
    """Run synchronous test."""
    from agent.langchain_agent import process_message_sync
    
    test_uid = "test_user_sync"
    
    print("🤖 Kleio.ai LangChain Agent Sync Test")
    print("=" * 50)
    
    message = "bought 1kg rice and dal"
    print(f"User: {message}")
    response = process_message_sync(test_uid, message)
    print(f"Agent: {response}")
    print()


if __name__ == "__main__":
    # Run async test
    print("Running async test...")
    print()
    asyncio.run(test_agent())
    
    print()
    print()
    
    # Run sync test
    print("Running sync test...")
    print()
    test_agent_sync()

