"""
Enhanced Chat View for IRIR
============================

Complete chat interface integrating:
- Welcome screen (when no messages)
- Chat messages view (during conversation)
- Stunning sidebar with context info
- Smooth transitions

Usage in your AIClient app:
    from modern_tui.enhanced_chat_view import EnhancedChatView

    # In your compose method:
    yield EnhancedChatView()
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text

from .welcome_screen import WelcomeScreen
from .sidebar import Sidebar, ContextMetrics, LSPStatus


class EnhancedChatView(Container):
    """Complete chat view with welcome screen and sidebar."""

    # Reactive state
    has_messages: reactive[bool] = reactive(False)
    show_sidebar: reactive[bool] = reactive(True)

    DEFAULT_CSS = """
    EnhancedChatView {
        width: 100%;
        height: 100%;
    }

    #chat-layout {
        width: 100%;
        height: 100%;
    }

    #main-chat-area {
        width: 1fr;
        height: 100%;
    }

    #chat-messages {
        width: 100%;
        height: 1fr;
        background: $background;
        border: none;
        padding: 1 2;
    }

    #chat-input-container {
        width: 100%;
        height: auto;
        background: $surface;
        border-top: solid $primary;
        padding: 1 2;
    }

    #chat-input {
        width: 100%;
    }

    .user-message {
        background: $primary-darken-2;
        padding: 1 2;
        margin: 0 0 1 0;
        border-left: thick $primary;
    }

    .assistant-message {
        background: $surface;
        padding: 1 2;
        margin: 0 0 1 0;
        border-left: thick cyan;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("escape", "interrupt", "Interrupt"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the chat view."""
        with Horizontal(id="chat-layout"):
            with Vertical(id="main-chat-area"):
                # This will show either welcome screen or messages
                yield WelcomeScreen(id="welcome-screen")
                yield RichLog(id="chat-messages", classes="hidden")
                yield InputArea()

            # Sidebar (can be toggled)
            yield Sidebar(id="chat-sidebar")

    def on_mount(self) -> None:
        """Initialize the view."""
        self._update_view()

    def watch_has_messages(self, has_messages: bool) -> None:
        """Update view when message state changes."""
        self._update_view()

    def watch_show_sidebar(self, show: bool) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#chat-sidebar", Sidebar)
        if show:
            sidebar.remove_class("hidden")
        else:
            sidebar.add_class("hidden")

    def _update_view(self) -> None:
        """Update which view is shown (welcome vs messages)."""
        welcome = self.query_one("#welcome-screen", WelcomeScreen)
        messages = self.query_one("#chat-messages", RichLog)

        if self.has_messages:
            welcome.add_class("hidden")
            messages.remove_class("hidden")
        else:
            welcome.remove_class("hidden")
            messages.add_class("hidden")

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat.

        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        # Show messages view
        self.has_messages = True

        messages = self.query_one("#chat-messages", RichLog)

        if role == "user":
            text = Text("You", style="bold cyan")
            text.append(f"\n{content}", style="white")
        else:
            text = Text("IRIR", style="bold green")
            text.append(f"\n{content}", style="white")

        messages.write(text)
        messages.write("")  # Add spacing

    def update_context(self, tokens_used: int, tokens_total: int, cost: float) -> None:
        """Update context metrics in sidebar.

        Args:
            tokens_used: Number of tokens used
            tokens_total: Total available tokens
            cost: Cost in dollars
        """
        sidebar = self.query_one("#chat-sidebar", Sidebar)
        context = sidebar.query_one(ContextMetrics)

        context.tokens_used = tokens_used
        context.tokens_total = tokens_total
        context.cost_spent = cost

    def update_lsp_status(self, status: str) -> None:
        """Update LSP status in sidebar.

        Args:
            status: LSP status message
        """
        sidebar = self.query_one("#chat-sidebar", Sidebar)
        lsp = sidebar.query_one(LSPStatus)
        lsp.status = status

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self.show_sidebar = not self.show_sidebar

    def action_new_chat(self) -> None:
        """Start a new chat."""
        messages = self.query_one("#chat-messages", RichLog)
        messages.clear()
        self.has_messages = False

    def action_interrupt(self) -> None:
        """Interrupt current operation."""
        try:
            self.app.bell()
        except Exception:
            pass


class InputArea(Container):
    """Input area for user messages."""

    DEFAULT_CSS = """
    InputArea {
        width: 100%;
        height: auto;
        background: $surface;
        border-top: solid $primary;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose input area."""
        yield Input(
            placeholder="Type your message... (Enter to send)",
            id="chat-input",
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission."""
        if event.value.strip():
            # Post message to parent
            chat_view = self.ancestors.filter(EnhancedChatView).first()
            if chat_view:
                chat_view.add_message("user", event.value)

                # Clear input
                event.input.value = ""

                # Trigger AI response (implement in parent if desired)


class CompactChatView(Container):
    """Compact chat view without sidebar."""

    DEFAULT_CSS = """
    CompactChatView {
        width: 100%;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose compact view."""
        with Vertical():
            yield WelcomeScreen()
            yield RichLog(id="messages", classes="hidden")
            yield InputArea()


__all__ = [
    "EnhancedChatView",
    "CompactChatView",
    "InputArea",
]
