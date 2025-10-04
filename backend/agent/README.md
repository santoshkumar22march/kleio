# LangChain Agent for Kleio.ai

## Overview

The LangChain agent provides a conversational AI interface for Kleio.ai, allowing users to interact with the inventory management system using natural language. It wraps existing backend functions as tools and uses Google Gemini 2.0 Flash for intelligent processing.

## Architecture

```
User (Telegram/Chat)
    ↓
"bought tomatoes and milk"
    ↓
FastAPI: /api/chat/message
    ↓
LangChain Agent (gemini-2.0-flash-exp)
    ├─ Understands natural language
    ├─ Remembers conversation context
    ├─ Decides which tool to use
    ├─ Extracts entities (2kg, tomatoes, milk)
    └─ Calls appropriate backend function
    ↓
Your existing backend functions
    ↓
Database
    ↓
Response back to user (natural language)
```

## Features

### 1. Natural Language Processing
- Understands casual conversation
- Extracts structured data from text
- Maintains conversation context

### 2. Tool Integration
The agent has access to 4 main tools:

#### `add_inventory_items`
Adds items to user's inventory from natural language.

**Example inputs:**
- "I bought 2kg tomatoes and 1 liter milk"
- "Just purchased onions, potatoes and dal"
- "Got some vegetables today"

#### `get_shopping_list_tool`
Generates smart shopping list based on usage patterns.

**Example inputs:**
- "What should I buy?"
- "Show me my shopping list"
- "What items are urgent?"

#### `generate_recipe_tool`
Suggests recipes from available inventory.

**Example inputs:**
- "Suggest a quick dinner recipe"
- "What can I cook with what I have?"
- "Give me a vegetarian recipe"

#### `query_inventory_tool`
Checks current inventory status.

**Example inputs:**
- "What do I have?"
- "Check my vegetables"
- "Show my inventory"

### 3. Conversation Memory
- Uses LangGraph's MemorySaver for persistent conversations
- Each user has separate thread_id for isolated conversations
- Context maintained across multiple messages

## Installation

### 1. Install Dependencies

```bash
cd backend
uv pip install -r requirements.txt
```

This installs:
- `langchain==0.3.13`
- `langchain-google-genai==2.0.8`
- `langgraph==0.2.59`
- `langgraph-checkpoint==2.0.10`

### 2. Environment Setup

Ensure your `.env` file has:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### REST API

#### Send Chat Message

```http
POST /api/chat/message
Authorization: Bearer {firebase_token}
Content-Type: application/json

{
  "message": "I bought 2kg tomatoes and 1 liter milk",
  "thread_id": "user-123"
}
```

**Response:**
```json
{
  "response": "✅ Added 2 items to inventory: tomatoes (2.0kg), milk (1.0liter)",
  "thread_id": "user-123"
}
```

### Async API (Recommended for FastAPI)

```python
from agent.langchain_agent import process_message

# In async context (FastAPI endpoints, async functions)
response = await process_message(
    firebase_uid="user123",
    message="I bought 2kg tomatoes",
    thread_id="chat-1"
)

print(response)
# Output: "✅ Added 2 items to inventory: tomatoes (2.0kg), milk (1.0liter)"
```

### Sync API (For Scripts/CLI Only)

```python
from agent.langchain_agent import process_message_sync

# ONLY use in non-async contexts (scripts, CLI, sync code)
# DO NOT use in FastAPI async endpoints - will cause event loop conflicts
response = process_message_sync(
    firebase_uid="user123",
    message="What should I buy?",
    thread_id="chat-1"
)
```

**⚠️ Important:** 
- Use `process_message()` (async) in FastAPI endpoints
- Use `process_message_sync()` only in scripts/CLI (non-async contexts)
- Never use `process_message_sync()` in code that already has an event loop running

## Telegram Integration

### Webhook Setup

```python
# In your Telegram bot setup
import requests

TELEGRAM_BOT_TOKEN = "your_bot_token"
WEBHOOK_URL = "https://your-domain.com/api/chat/webhook/telegram"

# Set webhook
requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)
```

### Webhook Endpoint

The agent includes a Telegram webhook endpoint at `/api/chat/webhook/telegram`.

**Flow:**
1. User sends message to Telegram bot
2. Telegram forwards to webhook
3. Agent processes with LangChain
4. Response sent back to user

**Note:** You'll need to:
1. Map Telegram user IDs to Firebase UIDs
2. Implement response sending via Telegram Bot API

## Examples

### Example 1: Adding Items

**User:** "bought 2kg tomatoes, 1kg onions and milk"

**Agent:** 
```
✅ Added 3 items to inventory: tomatoes (2.0kg), onions (1.0kg), milk (1.0liter)
```

### Example 2: Shopping List

**User:** "what should I buy?"

**Agent:**
```
🔴 URGENT (Buy today/tomorrow):
  • rice - 5.0kg (Running low - last purchased 28 days ago)
  • milk - 2.0liter (Consumed within 3 days typically)

🟡 THIS WEEK:
  • onions - 2.0kg (Stock depleting - buy within 5 days)
```

### Example 3: Recipe Generation

**User:** "suggest a quick vegetarian dinner"

**Agent:**
```
🍳 **Vegetable Pulao**
A simple and flavorful one-pot rice dish

⏱️ Time: 30 mins | 🍽️ Serves: 4 | 📊 Difficulty: easy

**Ingredients:**
✅ rice - 2 cups
✅ mixed vegetables - 1 cup
✅ onions - 1 pieces
🛒 oil - 2 tablespoons
🛒 spices - 1 teaspoon

**Instructions:**
1. Wash and soak rice for 15 minutes
2. Heat oil and sauté onions until golden
3. Add vegetables and spices, cook for 5 minutes
4. Add rice and water (1:2 ratio)
5. Cover and cook on low heat for 15 minutes

💡 **Tips:**
  • Add ghee on top for extra flavor
  • Serve with raita or pickle
```

### Example 4: Inventory Query

**User:** "what vegetables do I have?"

**Agent:**
```
📦 **Your Inventory** (8 items):

**Vegetables:**
  • tomatoes: 1.5kg ⏰ Expires in 5 days
  • onions: 2.0kg
  • potatoes: 3.0kg
  • carrots: 0.5kg ⚠️ Expires in 2 days
```

## Conversation Context

The agent maintains conversation context using thread IDs:

```python
# First message
response1 = await process_message(
    firebase_uid="user123",
    message="What do I have?",
    thread_id="chat-1"
)

# Follow-up in same conversation
response2 = await process_message(
    firebase_uid="user123",
    message="Add tomatoes to that",
    thread_id="chat-1"
)
# Agent remembers previous context
```

## Customization

### Adding New Tools

1. Create tool function in `langchain_agent.py`:

```python
@tool
def my_new_tool(firebase_uid: str, param: str, db_session: Any) -> str:
    """
    Tool description for the agent.
    
    Args:
        firebase_uid: User's Firebase UID
        param: Tool parameter
        db_session: Database session
        
    Returns:
        Result message
    """
    # Your logic here
    return "Tool result"
```

2. Add to tools list in `create_agent()`:

```python
tools = [
    add_inventory_items,
    get_shopping_list_tool,
    generate_recipe_tool,
    query_inventory_tool,
    my_new_tool,  # Add your tool
]
```

### Modifying System Prompt

Edit the `system_message` in `create_agent()` function to change agent behavior:

```python
system_message = f"""You are Kleio, a helpful assistant...

Your custom instructions here...
"""
```

### Changing Model

Replace model in `create_agent()`:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Change model here
    google_api_key=settings.gemini_api_key,
    temperature=0.7,  # Adjust creativity
)
```

## Error Handling

The agent includes comprehensive error handling:

1. **Tool Errors**: Each tool catches and returns user-friendly error messages
2. **Agent Errors**: Top-level exception handler for unexpected errors
3. **Input Validation**: Pydantic models validate all inputs

## Performance Considerations

1. **Model Choice**: Uses `gemini-2.0-flash-exp` for balance of speed and quality
2. **Streaming**: Can be enabled for real-time responses
3. **Caching**: Consider caching frequent queries
4. **Rate Limiting**: Implement rate limiting in production

## Testing

Test the agent using the API:

```bash
# Test with curl
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I bought tomatoes",
    "thread_id": "test-1"
  }'
```

## Production Deployment

### Security Checklist

- ✅ Always verify Firebase tokens
- ✅ Implement rate limiting per user
- ✅ Sanitize user inputs
- ✅ Monitor API usage and costs
- ✅ Set up error alerts

### Monitoring

Monitor these metrics:
- Response times
- Tool usage frequency
- Error rates
- API costs (Gemini)
- User engagement

## Troubleshooting

### Agent not responding
- Check Gemini API key in `.env`
- Verify database connection
- Check logs for errors

### Tools not working
- Ensure Firebase UID is valid
- Check database session is passed correctly
- Verify tool function signatures

### Memory issues
- Clean up old thread data periodically
- Use separate thread IDs per conversation
- Monitor memory usage

## Future Enhancements

- [ ] Add voice input/output support
- [ ] Implement multi-language support (Tamil, Hindi)
- [ ] Add festival-based suggestions
- [ ] Integrate with more messaging platforms (WhatsApp)
- [ ] Add image analysis directly in chat
- [ ] Implement smart notifications
- [ ] Add budget tracking conversations

## Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review FastAPI docs at `/docs`
3. See main project documentation

## License

Part of Kleio.ai project - refer to main project license.

