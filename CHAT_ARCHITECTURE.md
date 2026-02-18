# irir Chat Architecture Improvements

## Overview
This document describes the architectural enhancements made to irir's chat system, inspired by OpenCode's proven patterns for building scalable TUI applications.

## Key Improvements

### 1. **Centralized Conversation State Management** (`conversation_manager.py`)
**Borrowed from OpenCode's `useSync()`, `useSDK()` pattern**

- **ConversationManager**: Central state manager for all conversations
- **Benefits**:
  - Single source of truth for conversation data
  - Typed `Conversation` and `Message` dataclasses for type safety
  - Automatic persistence to disk (JSON)
  - Easy filtering/searching
  - No prop-drilling (unlike OpenCode's context API, this is direct access - more Pythonic)

- **Usage**:
```python
manager = ConversationManager(storage_path=Path("conversations.json"))
conv = manager.create(title="My Chat")
manager.add_message(conv.id, "Hello!", role="user", model="llama3")
conversations = manager.get_all()  # Sorted by recency
```

### 2. **Message History Widget** (`message_history.py`)
**Inspired by OpenCode's session/index.tsx scrollable message rendering**

- **MessageHistory**: ScrollableContainer that renders conversation messages with proper formatting
- **Features**:
  - Role-based styling (user, assistant, system messages have different colors/borders)
  - Auto-scrolling to bottom on new messages
  - Timestamp display
  - Model attribution for assistant responses
  - Markdown support for rich formatting

- **Usage**:
```python
history = MessageHistory(manager, conv_id="abc123", id="chat-history")
history.append_message("Hello there!", role="user")
history.append_message("Hi! How can I help?", role="assistant", model="llama3")
history.reload()  # Re-render all messages
```

### 3. **Typed Message & Conversation Objects**
**Inspired by OpenCode's TypeScript interfaces (AssistantMessage, UserMessage, etc.)**

- **Message**: 
  - `id`, `role`, `content`, `model`, `timestamp`, `turn_id`
  - Serializable to/from JSON
  - Datetime handling with ISO format

- **Conversation**:
  - `id`, `title`, `messages`, `model`, `created_at`, `last_updated`
  - Automatic timestamp management
  - Backwards compatible with legacy format

### 4. **Component-Based Chat Messages** (`chat_message.py`)
**Similar to OpenCode's dedicated message components**

- **ChatMessage**: Static widget for rendering individual messages
- Features role-aware styling and metadata display

### 5. **Chat Area Organization** (`chat_area.py`)
**Pattern from OpenCode's session/routes structure**

- **ChatArea**: Main conversation display widget
- **ChatHeader**: Shows conversation title, message count, model, timestamps
- Separates concerns: header/content/footer components

### 6. **Improved CSS Styling**
Added comprehensive message styling in app.py CSS:
- `.message-user`, `.message-assistant`, `.message-system` classes
- Left border colors for visual role indication
- Proper padding and spacing
- Header styling with timestamps

## Architecture Comparison

| Aspect | OpenCode | irir (New) |
|--------|----------|-----------|
| State Management | React Context API | ConversationManager class |
| Message Rendering | Dedicated components | MessageHistory widget + CSS |
| Typing | TypeScript interfaces | Python dataclasses |
| Persistence | Server-side | JSON file (local) |
| Scrolling | Custom scroll handling | Textual ScrollableContainer |

## Migration Path

The new components are **fully backwards compatible**. The app continues to use the legacy `_conversations` list internally.

### Gradual Migration Strategy:
1. ✅ **Phase 1** (Done): Add ConversationManager alongside legacy code
2. ✅ **Phase 2** (Done): Add MessageHistory component with fallback
3. **Phase 3** (Optional): Replace all select_conversation calls to use MessageHistory
4. **Phase 4** (Optional): Remove legacy _conversations list entirely

Currently at **Phase 2**: Both systems coexist, with preference given to new MessageHistory if available.

## Future Enhancements

Patterns to apply from OpenCode's architecture:

### 1. **Dialog System** (OpenCode has DialogProvider, DialogMessage, etc.)
```python
# Future: Add dialog system for confirmations, settings, etc.
dialog = DialogProvider()
dialog.show("Are you sure?", on_confirm=delete_conv)
```

### 2. **Event Bus** (OpenCode has TuiEvent system)
```python
# Future: Decouple components via events instead of direct calls
event_bus.emit("message_created", message)
event_bus.on("message_created", handle_new_message)
```

### 3. **Worker Management** (OpenCode has dedicated workers)
```python
# Already present via @work decorator, but could expand
@work(thread=True)
def fetch_response(self, prompt: str):
    ...
```

### 4. **Theme Context** (OpenCode's useTheme pattern)
```python
# Future: Centralized theme management
theme = Theme.from_json("themes/dracula.json")
current_color = theme.get("message.assistant.fg")
```

## File Structure

```
modern_tui/
├── app.py                      # Main app (updated with new imports & CSS)
├── conversation_manager.py     # State management (NEW)
├── message_history.py          # Message display widget (NEW)
├── chat_area.py               # Chat display organization (NEW)
├── chat_message.py            # Individual message widget (NEW)
├── welcome_screen.py          # Welcome splash
├── command_palette.py         # Ctrl+P palette
├── slash_commands.py          # Slash command definitions
├── slash_command_menu.py      # Slash command autocomplete
├── sidebar.py                 # Assistant sidebar
├── workers.py                 # Background tasks
└── utils.py                   # Helper functions
```

## Key Design Principles

1. **Separation of Concerns**: ConversationManager handles data, MessageHistory handles presentation
2. **Type Safety**: Dataclasses provide structure and IDE support
3. **Composability**: Components are independent and reusable
4. **Backwards Compatibility**: Legacy code continues to work
5. **Pythonic**: Takes inspiration from TypeScript patterns but adapts idiomatically to Python

## Example: Using the New System

```python
# Initialize
manager = ConversationManager()
history = MessageHistory(manager, id="chat-history")

# Create conversation
conv = manager.create("Chat with Claude")
manager.select(conv.id)

# Add messages
history.append_message("What is Python?", role="user")
history.append_message("Python is a high-level programming language...", 
                      role="assistant", model="claude-3")

# Render when conversation changes
history.render_conversation(conv.id)

# Later: Load and display
all_convs = manager.get_all()
selected_conv = manager.get_current()
```

## Testing

The new components are pure Python classes that don't depend on Textual layout. Testing is straightforward:

```python
def test_message_add():
    manager = ConversationManager()
    conv = manager.create("Test")
    msg = manager.add_message(conv.id, "Hello", role="user")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert len(manager.get_messages(conv.id)) == 1
```

## Notes

- The ConversationManager automatically handles datetime serialization to ISO format
- Legacy format (using timestamps as floats) is automatically converted on load
- MessageHistory can be used outside of the main app for testing
- All components use proper typing for IDE autocomplete support
