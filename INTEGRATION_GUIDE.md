# Integration Guide: Using the New Chat Components

## Quick Start

The new chat system is already integrated! Here's what you can do now:

### 1. Replace Chat History Widget

In your `compose()` method, you can now use `MessageHistory` instead of plain `ScrollableContainer`:

**Before:**
```python
yield ScrollableContainer(id="chat-history")
```

**After:**
```python
from .message_history import MessageHistory
yield MessageHistory(manager=self._manager, id="chat-history")
```

### 2. Add Messages with Role-Based Styling

**Before (plain Label/Markdown):**
```python
chat_box.mount(Label(f"You: {content}", classes='user-msg'))
chat_box.mount(Markdown(model_response))
```

**After (with timestamps and model info):**
```python
history = self.query_one("#chat-history", MessageHistory)
history.append_message(content, role="user")
history.append_message(response, role="assistant", model="llama3")
```

### 3. Use ConversationManager for State

**Before (manual list management):**
```python
self._conversations = []
self._current_conv_id = None
conv = {'id': uuid4(), 'title': 'Chat', 'messages': []}
self._conversations.append(conv)
```

**After (structured state management):**
```python
self._manager = ConversationManager()
conv = self._manager.create("Chat")
msg = self._manager.add_message(conv.id, "Hello!", role="user")
self._manager.save()  # Auto-saved, but explicit save is available
```

## Current Integration Status

✅ **Already done:**
- ConversationManager initialized in on_mount()
- New imports added to app.py
- CSS styling for message components added
- select_conversation() updated to support MessageHistory

⚠️ **Next steps (optional):**
- Update get_ai_response() to use manager.add_message() instead of direct chat_box.mount()
- Update create_conversation() to use manager.create()
- Update delete_conversation() to use manager.delete()
- Replace all message rendering with MessageHistory.append_message()

## Example: Updating get_ai_response()

**Current code:**
```python
@work
async def get_ai_response(self, user_text, model_name):
    chat_box = self.query_one("#chat-history")
    await chat_box.mount(Label(f"{model_name}:", classes="system-msg"))
    
    # ... streaming logic ...
    await chat_box.mount(Markdown(chunked_text))
    
    # Save to conversation
    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
    if conv is not None:
        conv['messages'].append({'role': 'assistant', 'content': chunked_text, 'model': model_name})
```

**Updated code:**
```python
@work
async def get_ai_response(self, user_text, model_name):
    history = self.query_one("#chat-history", MessageHistory)
    
    # ... streaming logic ...
    
    # Add to manager and history (automatic styling!)
    history.append_message(chunked_text, role="assistant", model=model_name)
```

## Pattern: Message Streaming

For streaming responses, collect the full message before adding:

```python
@work
async def stream_response(self, prompt: str, model: str):
    history = self.query_one("#chat-history", MessageHistory)
    
    full_response = ""
    stream = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}], stream=True)
    
    for chunk in stream:
        full_response += chunk.get('message', {}).get('content', '')
        # Optional: Update live display for long responses
    
    # Add complete message to history
    history.append_message(full_response, role="assistant", model=model)
```

## Testing New Components

```python
# Test ConversationManager independently
def test_manager():
    manager = ConversationManager()
    conv = manager.create("Test")
    msg = manager.add_message(conv.id, "Hello", role="user")
    
    assert msg.role == "user"
    assert len(manager.get_messages(conv.id)) == 1
    assert manager.get(conv.id).title == "Test"
    
    # Verify persistence
    manager2 = ConversationManager(manager.storage_path)
    assert len(manager2.get_all()) == 1

# Test in TUI context
async def test_history_widget():
    manager = ConversationManager()
    conv = manager.create("Widget Test")
    
    history = MessageHistory(manager, conv_id=conv.id)
    # Would need full app context to mount
```

## Migration Checklist

- [ ] Review CHAT_ARCHITECTURE.md for design overview
- [ ] Check that app starts without errors: `python modern_tui/app.py`
- [ ] Create a test conversation and verify message display
- [ ] Update get_ai_response() to use manager
- [ ] Update on_input_submitted() to use manager.add_message()
- [ ] Update select_conversation() to use MessageHistory (already partial support)
- [ ] Remove legacy _conversations list (after full migration)

## Troubleshooting

### MessageHistory not rendering
- Ensure it's mounted in compose() with `id="chat-history"`
- Check that ConversationManager is initialized in on_mount()
- Verify the conv_id is valid: `manager.get(conv_id) is not None`

### Messages not appearing
- Check that append_message() is called on the correct MessageHistory instance
- Verify the message is being added to the manager: `len(manager.get_messages(conv_id)) > 0`
- Ensure MessageHistory has the conversation loaded: `history.conv_id == conv_id`

### Timestamps not showing
- Timestamps are auto-generated when messages are created
- Check Message.timestamp is not None: `msg.timestamp is not None`
- Verify strftime format in message_history.py is correct

## Next Steps to Improve Further

Patterns from OpenCode that could be added:

1. **Event System**: Emit "message_added" events when history changes
2. **Caching**: Store rendered messages to avoid re-rendering on scroll
3. **Virtual Scrolling**: For 1000+ message conversations
4. **Search**: Full-text search across all messages (already in manager!)
5. **Export**: Convert conversation to Markdown/PDF
6. **Threading**: Show message threads and replies (like Discord)

## References

- [CHAT_ARCHITECTURE.md](./CHAT_ARCHITECTURE.md) - Detailed architecture overview
- [conversation_manager.py](./modern_tui/conversation_manager.py) - State management implementation
- [message_history.py](./modern_tui/message_history.py) - Widget implementation
- [app.py](./modern_tui/app.py) - Integration point (search for "ConversationManager")
