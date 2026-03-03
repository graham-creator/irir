"""
ConversationManager for centralized conversation state management.
Inspired by OpenCode's context-based state pattern (useSync, useSDK, etc.).
"""

import json
import uuid
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import os
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in a conversation."""

    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    model: Optional[str] = None
    timestamp: Optional[datetime] = None
    turn_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "turn_id": self.turn_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Message":
        """Create Message from dict."""
        ts = d.get("timestamp")
        if ts and isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        return Message(
            id=d.get("id", str(uuid.uuid4())[:8]),
            role=d.get("role", "user"),
            content=d.get("content", ""),
            model=d.get("model"),
            timestamp=ts,
            turn_id=d.get("turn_id"),
        )


@dataclass
class Conversation:
    """Represents a full conversation."""

    id: str
    title: str
    messages: List[Message]
    model: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        # Ensure a sensible default model (can be overridden via env var)
        if not self.model:
            self.model = os.environ.get("MODERN_TUI_DEFAULT_MODEL", "llama3")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "model": self.model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Conversation":
        """Create Conversation from dict (handles legacy format)."""
        # Handle legacy format where messages are plain dicts
        messages = []
        for msg_data in d.get("messages", []):
            if isinstance(msg_data, dict):
                messages.append(Message.from_dict(msg_data))
            else:
                messages.append(msg_data)

        created_at = d.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        last_updated = d.get("last_updated")
        if last_updated and isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated)

        return Conversation(
            id=d.get("id", str(uuid.uuid4())[:8]),
            title=d.get("title", "Untitled"),
            messages=messages,
            model=d.get("model", "llama3"),
            created_at=created_at,
            last_updated=last_updated,
        )



class ConversationManager:
    """
    Central state manager for conversations.
    Provides persistent storage and in-memory access patterns.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = (
            storage_path or Path(__file__).resolve().parent / "conversations.json"
        )
        self._conversations: Dict[str, Conversation] = {}
        self._current_id: Optional[str] = None
        self._load()

    def _load(self):
        """Load conversations from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._conversations = {
                cid: Conversation.from_dict(cdata)
                for cid, cdata in data.get("conversations", {}).items()
            }
            self._current_id = data.get("current")
        except Exception as e:
            print(f"Error loading conversations: {e}")

    def save(self):
        """Save all conversations to disk."""
        try:
            data = {
                "conversations": {
                    cid: conv.to_dict() for cid, conv in self._conversations.items()
                },
                "current": self._current_id,
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving conversations: {e}")

    # Query methods (read-only)
    def get_all(self) -> List[Conversation]:
        """Get all conversations, sorted by last_updated descending."""
        def sort_key(c: Conversation) -> float:
            return c.last_updated.timestamp() if c.last_updated else 0
        
        return sorted(
            self._conversations.values(),
            key=sort_key,
            reverse=True,
        )

    def get(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self._conversations.get(conv_id)

    def get_current(self) -> Optional[Conversation]:
        """Get currently selected conversation."""
        if self._current_id:
            return self.get(self._current_id)
        return None

    def get_current_id(self) -> Optional[str]:
        """Get current conversation ID."""
        return self._current_id

    # Mutation methods (write)
    def create(self, title: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        conv_id = str(uuid.uuid4())[:8]
        conv = Conversation(
            id=conv_id,
            title=title or f"Conversation {len(self._conversations) + 1}",
            messages=[],
        )
        self._conversations[conv_id] = conv
        self._current_id = conv_id
        self.save()
        return conv

    def delete(self, conv_id: str):
        """Delete a conversation."""
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            if self._current_id == conv_id:
                # Select first remaining conversation
                remaining = list(self._conversations.keys())
                self._current_id = remaining[0] if remaining else None
            self.save()

    def select(self, conv_id: str):
        """Select a conversation as current."""
        if conv_id in self._conversations:
            self._current_id = conv_id
            self.save()

    def rename(self, conv_id: str, new_title: str):
        """Rename a conversation."""
        conv = self.get(conv_id)
        if conv:
            conv.title = new_title
            conv.last_updated = datetime.now()
            self.save()

    def add_message(
        self,
        conv_id: str,
        content: str,
        role: str = "user",
        model: Optional[str] = None,
    ) -> Optional[Message]:
        """Add a message to a conversation."""
        conv = self.get(conv_id)
        if not conv:
            return None

        msg = Message(
            id=str(uuid.uuid4())[:8],
            role=role,
            content=content,
            model=model,
            timestamp=datetime.now(),
        )
        conv.messages.append(msg)
        conv.last_updated = datetime.now()
        self.save()
        return msg

    def get_messages(self, conv_id: str) -> List[Message]:
        """Get all messages from a conversation."""
        conv = self.get(conv_id)
        return conv.messages if conv else []

    # Search/filter
    def search(self, query: str) -> List[Conversation]:
        """Search conversations by title."""
        q_lower = query.lower()
        return [
            c
            for c in self.get_all()
            if q_lower in c.title.lower()
        ]
