"""
Chat message widget for rendering individual messages in conversation.
Inspired by OpenCode's component-based message rendering pattern.
"""

from textual.widgets import Static, Label
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from datetime import datetime
from typing import Optional


class ChatMessage(Static):
    """Renders a single message from a conversation with role-based styling and metadata."""

    role = reactive("user")  # 'user', 'assistant', 'system'
    message_content = reactive("")  # Renamed from 'content' to avoid conflict with Static
    model = reactive("")
    timestamp = reactive("")

    def __init__(
        self,
        content: str,
        role: str = "user",
        model: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.role = role
        self.message_content = content
        self.model = model or ""
        self.timestamp = (
            timestamp.strftime("%H:%M:%S") if timestamp else ""
        )

    def render(self) -> str:
        """Render message with role-based formatting."""
        # Format role indicator
        role_map = {
            "user": "You",
            "assistant": self.model or "Assistant",
            "system": "System",
        }
        role_label = role_map.get(self.role, self.role)

        # Color by role
        role_colors = {
            "user": "#e6e6e6",
            "assistant": "#7aa2f7",
            "system": "#f2a65a",
        }
        color = role_colors.get(self.role, "#e6e6e6")

        # Build timestamp suffix if present
        timestamp_str = f" ({self.timestamp})" if self.timestamp else ""

        # Format: [Role] | timestamp | content
        content_preview = self.message_content
        if isinstance(content_preview, str) and len(content_preview) > 100:
            content_preview = content_preview[:97] + "..."
        
        return f"[{color}]{role_label}[/] {content_preview}"

    def compose(self):
        """Compose message subcomponents (optional: for richer rendering)."""
        with Horizontal():
            # Role + timestamp header
            with Vertical():
                role_map = {
                    "user": "You",
                    "assistant": self.model or "Assistant",
                    "system": "System",
                }
                role_label = role_map.get(self.role, self.role)

                header = f"{role_label}"
                if self.timestamp:
                    header += f" - {self.timestamp}"

                yield Label(header, classes=f"msg-header msg-{self.role}")
                # Content (wrapped for long messages)
                yield Label(self.message_content, classes=f"msg-content msg-{self.role}")

