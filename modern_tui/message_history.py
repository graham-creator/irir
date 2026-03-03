"""
Improved message history widget with scrolling and message rendering.
Inspired by OpenCode's message history pattern in session/index.tsx.
"""

from textual.widgets import Static, Label, Markdown
from textual.containers import Vertical, ScrollableContainer
from typing import Optional, List
from datetime import datetime

from .conversation_manager import ConversationManager, Message, Conversation


class MessageHistory(ScrollableContainer):
    """
    Scrollable message history container.
    Shows all messages in a conversation with proper formatting and separators.
    """

    def __init__(
        self,
        manager: Optional[ConversationManager] = None,
        conv_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.manager = manager
        self.conv_id = conv_id
        self.classes = "message-history"

    def on_mount(self):
        """Initialize message display on mount."""
        if self.conv_id:
            self.render_conversation(self.conv_id)

    def render_conversation(self, conv_id: Optional[str]):
        """Render all messages from a conversation."""
        if conv_id is None:
            return
        self.conv_id = conv_id
        self._clear()
        self._render_all_messages()

    def _clear(self):
        """Clear all message widgets."""
        for child in list(self.children):
            try:
                child.remove()
            except Exception:
                pass

    def _render_all_messages(self):
        """Render all messages from current conversation."""
        if not self.conv_id:
            return

        conv = self.manager.get(self.conv_id)
        if not conv or not conv.messages:
            return

        for i, msg in enumerate(conv.messages):
            self._render_message_widget(msg, i == 0)  # Add separator after first

    def _render_message_widget(self, msg: Message, is_first: bool = False):
        """Render a single message with role-specific styling."""
        try:
            # Message container
            msg_container = Vertical(classes=f"message-{msg.role}")

            # Header with role and metadata
            header_parts = []
            if msg.role == "user":
                header_parts.append("You")
            elif msg.role == "assistant":
                header_parts.append(msg.model or "Assistant")
            else:
                header_parts.append(msg.role.capitalize())

            if msg.timestamp:
                header_parts.append(msg.timestamp.strftime("%H:%M:%S"))

            header_text = " • ".join(header_parts)
            header_label = Label(header_text, classes=f"message-header message-header-{msg.role}")

            msg_container.mount(header_label)

            # Message content - use Markdown for assistant (supports formatting), Label for user/system
            if msg.role == "assistant":
                content_widget = Markdown(msg.content, classes=f"message-content message-content-{msg.role}")
            else:
                content_widget = Label(msg.content, classes=f"message-content message-content-{msg.role}")

            msg_container.mount(content_widget)

            # Add to container
            self.mount(msg_container)

            # Add separator between messages (except the last)
            if is_first:
                separator = Label("", classes="message-separator")
                self.mount(separator)

        except Exception as e:
            print(f"Error rendering message: {e}")

    def append_message(
        self,
        content: str,
        role: str = "user",
        model: Optional[str] = None,
    ) -> Optional[Message]:
        """Add a message to conversation and display it immediately."""
        if not self.conv_id:
            return None

        msg = self.manager.add_message(
            self.conv_id, content=content, role=role, model=model
        )

        if msg:
            # Render the new message
            self._render_message_widget(msg)
            # Auto-scroll to bottom
            try:
                self.scroll_end()
            except Exception:
                pass

        return msg

    def clear_all(self):
        """Clear all messages from display."""
        self._clear()

    def reload(self):
        """Reload and re-render all messages for current conversation."""
        self.render_conversation(self.conv_id)
