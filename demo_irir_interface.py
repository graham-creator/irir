#!/usr/bin/env python3
"""
IRIR Demo Application
=====================

Standalone demo showing the complete OpenCode-style interface:
- Beautiful IRIR logo welcome screen
- Stunning sidebar with context info
- Chat functionality
- Smooth animations

Run: python demo_irir_interface.py
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static
from textual.binding import Binding
from textual.containers import Container

# Import our custom components
from modern_tui.welcome_screen import WelcomeScreen
from modern_tui.sidebar import Sidebar
from modern_tui.enhanced_chat_view import EnhancedChatView


class HomeTab(Container):
    """Simple home tab."""

    DEFAULT_CSS = """
    HomeTab {
        align: center middle;
    }

    #home-content {
        width: 60;
        height: auto;
        border: thick cyan;
        padding: 2 4;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose home tab."""
        with Container(id="home-content"):
            yield Static(
                "[bold cyan]Welcome to IRIR[/]\n\n"
                "[white]AI Assistant Terminal Interface[/]\n\n"
                "[dim]Features:[/]\n"
                "• OpenCode-style interface\n"
                "• Beautiful welcome screen\n"
                "• Context-aware sidebar\n"
                "• Real-time token tracking\n"
                "• Keyboard shortcuts\n\n"
                "[bold yellow]Click 'Chat' to get started![/]",
                markup=True,
            )


class IRIRApp(App):
    """IRIR Demo Application."""

    TITLE = "IRIR"
    SUB_TITLE = "AI Assistant Terminal Interface"

    CSS = """
    Screen {
        background: #0a0a0a;
    }

    Header {
        background: $primary;
    }

    Footer {
        background: $surface;
    }

    TabbedContent {
        height: 100%;
    }

    TabPane {
        background: $background;
    }

    /* Welcome Screen Styling */
    #logo {
        color: cyan;
    }

    #input-container {
        background: #1a1a1a;
        border: tall cyan;
    }

    #welcome-input {
        background: #1a1a1a;
    }

    #model-info {
        color: cyan;
    }

    #tip-section {
        color: yellow;
    }

    /* Sidebar Styling */
    Sidebar {
        background: #0f0f0f;
        border-left: thick cyan;
    }

    .section-title {
        color: cyan;
        text-style: bold;
    }

    .metric-value {
        color: #00ff00;
    }

    SidebarHeader {
        color: cyan;
    }

    /* Messages */
    .user-message {
        background: #1a2332;
        border-left: thick cyan;
    }

    .assistant-message {
        background: #1a1a1a;
        border-left: thick green;
    }

    /* Hidden class */
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+s", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+t", "switch_tab", "Switch Tab"),
    ]

    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()

        with TabbedContent(initial="home"):
            with TabPane("Home", id="home"):
                yield HomeTab()

            with TabPane("Chat", id="chat"):
                yield EnhancedChatView()

            with TabPane("About", id="about"):
                yield AboutTab()

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize app."""
        # Set up initial context
        chat_view = self.query_one(EnhancedChatView)
        chat_view.update_context(
            tokens_used=0,
            tokens_total=100000,
            cost=0.0,
        )

    async def _demo_conversation(self) -> None:
        """Demo conversation (for testing)."""
        chat_view = self.query_one(EnhancedChatView)

        # User message
        chat_view.add_message("user", "Hello! What can you do?")
        await self.wait_for_animation()

        # AI response
        chat_view.add_message(
            "assistant",
            "Hi! I'm IRIR, an AI assistant. I can help with:\n\n"
            "• Coding and development\n"
            "• Technical explanations\n"
            "• Project documentation\n"
            "• Problem solving\n\n"
            "What would you like to know?",
        )

        # Update context
        chat_view.update_context(1250, 100000, 0.01)
        chat_view.update_lsp_status("● Python LSP active")

    async def wait_for_animation(self) -> None:
        """Wait for animation."""
        import asyncio

        await asyncio.sleep(1)

    def action_new_chat(self) -> None:
        """Start new chat."""
        try:
            chat_view = self.query_one(EnhancedChatView)
            chat_view.action_new_chat()
            self.notify("New chat started")
        except Exception:
            pass

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar."""
        try:
            chat_view = self.query_one(EnhancedChatView)
            chat_view.action_toggle_sidebar()
            status = "shown" if chat_view.show_sidebar else "hidden"
            self.notify(f"Sidebar {status}")
        except Exception:
            pass

    def action_switch_tab(self) -> None:
        """Switch to next tab."""
        tabs = self.query_one(TabbedContent)
        tabs.action_next_tab()


class AboutTab(Container):
    """About tab."""

    DEFAULT_CSS = """
    AboutTab {
        align: center middle;
    }

    #about-content {
        width: 70;
        height: auto;
        border: thick cyan;
        padding: 2 4;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose about tab."""
        with Container(id="about-content"):
            yield Static(
                "[bold cyan]IRIR - AI Assistant[/]\n\n"
                "[white]Version:[/] 1.0.0\n"
                "[white]Interface:[/] OpenCode-inspired\n"
                "[white]Framework:[/] Textual\n\n"
                "[bold]Features:[/]\n\n"
                "[cyan]•[/] Beautiful welcome screen with IRIR logo\n"
                "[cyan]•[/] Context-aware sidebar with metrics\n"
                "[cyan]•[/] Real-time token and cost tracking\n"
                "[cyan]•[/] LSP status integration\n"
                "[cyan]•[/] Keyboard shortcuts for power users\n"
                "[cyan]•[/] Smooth animations and transitions\n\n"
                "[bold yellow]Keyboard Shortcuts:[/]\n\n"
                "[cyan]Tab[/]         - Switch between agents\n"
                "[cyan]Ctrl+P[/]      - Open command palette\n"
                "[cyan]Ctrl+N[/]      - Start new chat\n"
                "[cyan]Ctrl+S[/]      - Toggle sidebar\n"
                "[cyan]Ctrl+T[/]      - Switch tabs\n"
                "[cyan]Q[/]           - Quit application\n"
                "[cyan]Esc[/]         - Interrupt operation\n\n"
                "[dim]Built with ❤️ using Textual[/]",
                markup=True,
            )


def main():
    """Run the demo app."""
    app = IRIRApp()
    app.run()


if __name__ == "__main__":
    main()
