<<<<<<< HEAD
=======
"""
Complete Chat View for Your AIClient App
=========================================

This replaces your current chat tab with:
- Welcome screen when no messages
- Message view when chatting
- Your existing sidebar (IRIR with Context)
- Your existing conversations panel
- Your existing YT Action controls

Drop this into your modern_tui folder and import it!
"""

>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog, Button, Select
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

from .welcome_screen import WelcomeScreen
from .sidebar import ContextMetrics


class ChatTabContent(Container):
    """Complete chat tab matching your current layout."""

    DEFAULT_CSS = """
    ChatTabContent {
        width: 100%;
        height: 100%;
    }

    #chat-controls {
        width: 100%;
        height: auto;
        background: $surface;
        padding: 1 2;
        border-bottom: solid $primary;
    }

    #chat-main {
        width: 100%;
        height: 1fr;
    }

    #chat-input-container {
        width: 100%;
        height: auto;
        background: $surface;
        border-top: solid $primary;
        padding: 1 2;
    }

    .hidden {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the complete chat tab."""
        with Vertical():
            # Top controls
            yield ChatControls()

            # Main area
            with Horizontal(id="chat-main"):
                yield ConversationsPanel()
                yield ChatArea()
                yield IRIRSidebar()

            # Input
            yield ChatInput()


class ChatControls(Container):
    """Top controls: YT Action dropdown and Pull Transcript button."""

    DEFAULT_CSS = """
    ChatControls {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    #yt-action-select {
        width: 30;
        margin-right: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose controls."""
        with Horizontal(id="chat-controls"):
            yield Select(
                options=[("YT Action", "yt_action")],
                value="yt_action",
                id="yt-action-select",
            )
            yield Button("Pull Transcript", id="pull-transcript-btn")


class ConversationsPanel(Container):
    """Left sidebar with conversations list."""

    DEFAULT_CSS = """
    ConversationsPanel {
        width: 30;
        height: 100%;
        background: $surface-darken-1;
        border-right: solid $primary-darken-2;
        padding: 1 2;
    }

    #conversations-header {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        text-style: bold;
    }

    #conversations-search {
        width: 100%;
        margin: 0 0 1 0;
    }

    #conversations-buttons {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
    }

    #conversations-list {
        width: 100%;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose conversations panel."""
        yield Static("Conversations", id="conversations-header")
        yield Input(placeholder="Search...", id="conversations-search")

        with Horizontal(id="conversations-buttons"):
            yield Button("New", id="conv-new-btn", variant="primary")
            yield Button("Rename", id="conv-rename-btn")
            yield Button("Delete", id="conv-delete-btn", variant="error")

        yield RichLog(id="conversations-list")


class ChatArea(Container):
    """Center area: Shows welcome screen or messages."""

    has_messages = reactive(False)

    DEFAULT_CSS = """
    ChatArea {
        width: 1fr;
        height: 100%;
        background: $background;
    }

    .hidden {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose chat area."""
        yield WelcomeScreenSimple()
        yield RichLog(id="chat-messages", classes="hidden")

    def watch_has_messages(self, has_messages: bool) -> None:
        """Toggle views."""
        welcome = self.query_one(WelcomeScreenSimple)
        messages = self.query_one("#chat-messages", RichLog)

        if has_messages:
            welcome.add_class("hidden")
            messages.remove_class("hidden")
        else:
            welcome.remove_class("hidden")
            messages.add_class("hidden")

    def add_message(self, role: str, content: str) -> None:
        """Add message and switch to message view."""
        self.has_messages = True
        messages = self.query_one("#chat-messages", RichLog)

        if role == "user":
            messages.write(f"[bold cyan]You:[/] {content}")
        else:
            messages.write(f"[bold green]IRIR:[/] {content}")


class WelcomeScreenSimple(Container):
<<<<<<< HEAD
=======
    """Simple welcome screen matching OpenCode style."""
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72

    DEFAULT_CSS = """
    WelcomeScreenSimple {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #welcome-content {
        width: auto;
        height: auto;
        align: center middle;
    }

    #welcome-logo {
        content-align: center middle;
        margin: 2 0;
    }

    #welcome-model-info {
        content-align: center middle;
        margin: 1 0;
    }

    #welcome-tip {
        content-align: center middle;
        margin: 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose welcome screen."""
        with Vertical(id="welcome-content"):
            yield LogoDisplay()
            yield ModelInfoDisplay()
            yield TipDisplay()


class LogoDisplay(Static):
    """IRIR logo."""

    def on_mount(self) -> None:
        """Create logo."""
        logo = """
██╗██████╗ ██╗██████╗ 
██║██╔══██╗██║██╔══██╗
██║██████╔╝██║██████╔╝
██║██╔══██╗██║██╔══██╗
██║██║  ██║██║██║  ██║
╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""
        text = Text(logo, justify="center")
        text.stylize("bold cyan")
        self.update(text)


class ModelInfoDisplay(Static):
    """Model information."""

    def on_mount(self) -> None:
        """Set model info."""
        text = Text("Build", style="bold blue")
        text.append("  Llama 3 2 3b ", style="white")
        text.append("Ollama (local)", style="dim white")
        self.update(Align.center(text))


class TipDisplay(Static):
    """Helpful tip."""

    def on_mount(self) -> None:
        """Set tip."""
        text = Text("● ", style="bold yellow")
        text.append("Tip", style="bold yellow")
        text.append(" Use ", style="dim white")
        text.append("irir run", style="bold white")
        text.append(" for non-interactive scripting", style="dim white")
        self.update(Align.center(text))


class IRIRSidebar(Container):
    """Right sidebar - matches your current IRIR sidebar."""

    DEFAULT_CSS = """
    IRIRSidebar {
        width: 35;
        height: 100%;
        background: $surface;
        border-left: solid $primary;
        padding: 1 2;
    }

    #sidebar-header {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 0 0 2 0;
    }

    #context-section {
        width: 100%;
        height: auto;
        margin: 0 0 2 0;
        border-bottom: solid $primary-darken-2;
        padding: 0 0 1 0;
    }

    .section-title {
        text-style: bold;
        color: $text;
        margin: 0 0 1 0;
    }
    """

    tokens_used = reactive(0)
    tokens_total = reactive(100000)
    cost_spent = reactive(0.0)

    def compose(self) -> ComposeResult:
        """Compose sidebar."""
        yield SidebarHeader()
        yield ContextDisplay()


class SidebarHeader(Static):
    """Sidebar header."""

    def on_mount(self) -> None:
        """Set header."""
        text = Text("IRIR", style="bold cyan", justify="center")
        text.append("\n", style="")
        text.append("AI Assistant", style="dim white")
        self.update(text)


class ContextDisplay(Container):
    """Context metrics display."""

    DEFAULT_CSS = """
    ContextDisplay {
        width: 100%;
        height: auto;
    }

    #context-metrics {
        width: 100%;
        height: auto;
    }
    """

    tokens_used = reactive(0)
    tokens_total = reactive(100000)
    cost_spent = reactive(0.0)

    def compose(self) -> ComposeResult:
        """Compose context display."""
        yield Static("Context", classes="section-title")
        yield ContextMetrics()


class ChatInput(Container):
    """Bottom input field."""

    DEFAULT_CSS = """
    ChatInput {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    #message-input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose input."""
        yield Input(
            placeholder="Type a message (or YouTube URL)...",
            id="message-input",
        )


__all__ = [
    "ChatTabContent",
    "ChatArea",
    "IRIRSidebar",
    "ConversationsPanel",
]
