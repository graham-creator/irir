"""
ChatArea widget for displaying and managing conversation messages.
Inspired by OpenCode's session/index.tsx route component pattern.
"""

from textual.widgets import Static, Markdown, Label
from textual.containers import Vertical, Horizontal, ScrollableContainer
from typing import Optional, Callable
from datetime import datetime

from .conversation_manager import ConversationManager, Conversation, Message
from .chat_message import ChatMessage


class ChatArea(Static):
    """Main chat display area with message history and scrolling."""

    def __init__(
        self,
        manager: ConversationManager,
        conv_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.manager = manager
        self.conv_id = conv_id
        self.current_conversation: Optional[Conversation] = None

    def on_mount(self):
        """Load initial conversation when mounted."""
        if self.conv_id:
            self.load_conversation(self.conv_id)

    def load_conversation(self, conv_id: str):
        """Load and render a conversation."""
        self.conv_id = conv_id
        self.current_conversation = self.manager.get(conv_id)
        self._render_messages()

    def _render_messages(self):
        """Clear and re-render all messages for current conversation."""
        # Clear existing children
        for child in list(self.children):
            try:
                child.remove()
            except Exception:
                pass

        if not self.current_conversation:
            return

        messages = self.current_conversation.messages
        if not messages:
            # Show placeholder
            try:
                self.mount(Label("No messages yet. Start a conversation!", id="chat-empty"))
            except Exception:
                pass
            return

        # Render each message with proper styling
        for msg in messages:
            self._render_message(msg)

    def _render_message(self, msg: Message):
        """Render a single message."""
        try:
            if msg.role == "assistant":
                # Render assistant response as Markdown for rich formatting
                container = Vertical(classes=f"msg-container msg-{msg.role}")
                
                # Header: model name + timestamp
                header_text = msg.model or "Assistant"
                if msg.timestamp:
                    header_text += f" • {msg.timestamp.strftime('%H:%M')}"
                
                try:
                    container.mount(
                        Label(header_text, classes=f"msg-header msg-{msg.role}")
                    )
                except Exception:
                    pass

                # Content
                try:
                    container.mount(
                        Markdown(msg.content, classes=f"msg-content msg-{msg.role}")
                    )
                except Exception:
                    pass

                self.mount(container)

            elif msg.role == "user":
                # Render user message as simple text
                container = Vertical(classes=f"msg-container msg-{msg.role}")
                
                header = "You"
                if msg.timestamp:
                    header += f" • {msg.timestamp.strftime('%H:%M')}"
                
                try:
                    container.mount(
                        Label(header, classes=f"msg-header msg-{msg.role}")
                    )
                except Exception:
                    pass

                try:
                    container.mount(
                        Label(msg.content, classes=f"msg-content msg-{msg.role}")
                    )
                except Exception:
                    pass

                self.mount(container)

            else:
                # System message
                try:
                    self.mount(
                        Label(
                            f"[System] {msg.content}",
                            classes=f"msg-system msg-{msg.role}",
                        )
                    )
                except Exception:
                    pass

        except Exception as e:
            print(f"Error rendering message: {e}")

    def add_message(
        self,
        content: str,
        role: str = "user",
        model: Optional[str] = None,
    ) -> Optional[Message]:
        """Add a message to current conversation and render it."""
        if not self.conv_id:
            return None

        msg = self.manager.add_message(
            self.conv_id, content=content, role=role, model=model
        )
        if msg:
            # Reload to show new message
            self.load_conversation(self.conv_id)
        return msg

    def clear_messages(self):
        """Clear all messages from display (without deleting from storage)."""
        for child in list(self.children):
            try:
                child.remove()
            except Exception:
                pass

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat area."""
        try:
            # Find parent ScrollableContainer and scroll
            parent = self.parent
            while parent:
                if isinstance(parent, ScrollableContainer):
                    parent.scroll_end(animate=True)
                    break
                parent = parent.parent
        except Exception:
            pass


class ChatHeader(Static):
    """Header showing conversation title, model, message count."""

    def __init__(
        self,
        conversation: Optional[Conversation] = None,
        on_rename: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.conversation = conversation
        self.on_rename = on_rename
        self.classes = "chat-header"

    def render(self) -> str:
        """Render header info."""
        if not self.conversation:
            return "No conversation selected"

        title = self.conversation.title
        msg_count = len(self.conversation.messages)
        model = self.conversation.model

        created = ""
        if self.conversation.created_at:
            created = self.conversation.created_at.strftime("%Y-%m-%d %H:%M")
        
        return f"[bold]{title}[/] ({model}) • {msg_count} messages • {created}"

    def on_click(self):
        """Allow clicking header to rename (optional)."""
        if self.on_rename:
            self.on_rename()
