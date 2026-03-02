# Architecture Diagram: Enhanced Chat System

## Component Hierarchy

```
AIClient (app.py)
│
├── ConversationManager
│   ├── _conversations: Dict[str, Conversation]
│   └── _current_id: str
│
├── MessageHistory Widget
│   ├── manager: ConversationManager
│   ├── conv_id: str
│   └── rendered widgets: List[Vertical]
│       ├── Message 1 (user)
│       ├── Message 2 (assistant)
│       └── Message N (any role)
│
├── Command Palette
├── Slash Commands
├── Welcome Screen
└── Sidebar
```

## Data Flow: Adding a Message

```
User Input (chat-history)
    ↓
on_input_submitted()
    ↓
MessageHistory.append_message()
    ↓
ConversationManager.add_message()
    ↓
Add to Conversation.messages[]
    ↓
ConversationManager.save() [JSON]
    ↓
Render in MessageHistory widget
    ↓
Auto-scroll to bottom
```

## State Management Layers

```
Layer 1: Persistence (JSON File)
    ↓ ConversationManager.load()
Layer 2: In-Memory State (ConversationManager._conversations)
    ↓ Typed objects (Conversation, Message)
Layer 3: UI Display (MessageHistory widget)
    ↓ Reactive rendering based on role/metadata
Layer 4: Terminal (Textual framework)
    ↓ Colored text, boxes, borders
```

## Message Rendering Pipeline

```
Raw Message Data (dict)
    ↓
Message.from_dict()  [validation]
    ↓
Typed Message object
    ↓
MessageHistory._render_message_widget()
    ↓
Create Vertical container
    ├── Label (header: role + timestamp)
    └── Markdown/Label (content)
    ↓
Mount to MessageHistory
    ↓
Apply CSS classes (.message-{role})
    ↓
Display with colors/borders
```

## Comparison: Before vs After

### Before
```
User input → on_input_submitted()
             ↓
          chat_box.mount(Label(..., classes='user-msg'))
             ↓
          conv['messages'].append({'role': 'user', 'content': '...'})
             ↓
          Direct dictionary manipulation
```

### After
```
User input → on_input_submitted()
             ↓
          history.append_message(content, role="user")
             ↓
          manager.add_message(conv_id, content, role="user")
             ↓
          Typed Message object created + saved + rendered
             ↓
          Automatic timestamps, validation, styling
```

## Interaction Flow

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ↓
    ┌────────────────────┐
    │  MessageHistory    │
    │ append_message()   │
    └────────┬───────────┘
             │
             ↓
    ┌──────────────────────┐
    │ ConversationManager  │
    │ add_message()        │
    └────────┬─────────────┘
             │
        ┌────┴────┐
        ↓         ↓
    ┌────────┐  ┌──────┐
    │ Manager│ │ JSON  │
    │memory  │→ │persist│
    └────────┘  └──────┘
        │
        ↓
    ┌──────────────────┐
    │ Update UI render │
    │ (auto-scroll)    │
    └──────────────────┘
```

## Class Relationships

```
ConversationManager
├── stores List[Conversation]
│
└── Conversation
    ├── id: str
    ├── title: str
    ├── messages: List[Message]
    │   │
    │   └── Message
    │       ├── id: str
    │       ├── role: "user" | "assistant" | "system"
    │       ├── content: str
    │       ├── model: Optional[str]
    │       ├── timestamp: Optional[datetime]
    │       └── turn_id: Optional[str]
    │
    ├── model: str
    ├── created_at: datetime
    └── last_updated: datetime


MessageHistory (Textual Widget)
├── manages (ConversationManager)
├── conv_id: Optional[str]
└── renders List[Vertical] with Message components


ChatArea (Textual Widget)
├── manager: ConversationManager
├── conv_id: Optional[str]
└── mounts ChatHeader + Messages


ChatHeader (Textual Static)
├── conversation: Optional[Conversation]
└── renders metadata


ChatMessage (Textual Static)
├── role: str
├── message_content: str
└── renders role-specific formatting
```

## CSS Styling Structure

```
.message-user
├── background: #0f0f0f
├── border-left: #0b7377 (cyan-ish)
└── .message-header-user
    └── color: #e6e6e6
    
.message-assistant
├── background: #0f0f0f
├── border-left: #7aa2f7 (blue)
└── .message-header-assistant
    └── color: #7aa2f7
    
.message-system
├── background: #0f0f0f
├── border-left: #f2a65a (orange)
└── .message-header-system
    └── color: #f2a65a

.message-content-{role}
└── width: 1fr (full width)

.message-separator
└── border-bottom: #1e1e1e (visual divider)
```

## File Dependencies

```
app.py
├── imports: ConversationManager
│   └── conversation_manager.py (Message, Conversation dataclasses)
│
├── imports: MessageHistory
│   ├── message_history.py
│   └── depends on: ConversationManager
│
├── imports: ChatArea, ChatHeader
│   ├── chat_area.py
│   └── depends on: ConversationManager
│
├── imports: ChatMessage
│   └── chat_message.py (standalone)
│
└── CSS styles
    └── applies to: all widgets above
```

## Async Flow

```
get_ai_response() [@work decorator]
    ├── streams response from Ollama
    │   └── updates UI incrementally (via loop)
    │
    └── calls history.append_message()
        └── manager.add_message()
            └── saves to JSON (blocking but fast)
            
on_input_submitted() [sync]
    └── history.append_message()
        └── immediately visible in UI
```

## Type Safety Flow

```
Raw Data (JSON)
    ↓
json.load() → Dict[str, Any]
    ↓
Conversation.from_dict() → Type validation
    ↓
Typed Conversation object
    ├── id: str ✓
    ├── title: str ✓
    ├── messages: List[Message] ✓
    │   └── Each Message is typed
    └── model: str ✓
    ↓
IDE autocomplete available
    ↓
Type checker (mypy) validates calls
```

## Search Pipeline Example

```
manager.search("python")
    ↓
iterate Conversation objects
    ↓
filter by conv.title.lower() contains query
    ↓
return List[Conversation]
    ↓
user can render any result
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Create conversation | < 1ms | dataclass instantiation |
| Add message | 1-5ms | JSON write (depends on disk) |
| Load from disk | 10-100ms | JSON parse (linear with size) |
| Search 1000 convs | < 5ms | in-memory string comparison |
| Render 100 messages | 100-200ms | widget creation (can be optimized) |

## Scalability Notes

```
For 100 conversations, 10k messages: ✅ Works fine
For 1000 conversations, 100k messages: ⚠️ JSON may be slow
For 10k conversations: ❌ Consider database (SQLite)

Optimization paths:
1. Virtual scrolling (render visible messages only)
2. Message compression (summarize old messages)
3. Database instead of JSON
4. Pagination (load N messages at a time)
```

---

**Visual Guide**: This diagram shows how all the new components fit together and interact.
