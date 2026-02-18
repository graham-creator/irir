<<<<<<< HEAD
=======
"""
Stunning Sidebar Component for IRIR
====================================

OpenCode-style sidebar with:
- Context information (tokens, usage, cost)
- LSP status
- Build information
- Keyboard shortcuts
- Beautiful visual design
"""

>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table


class Sidebar(Container):
    """OpenCode-style sidebar with context and status information."""

    # Reactive properties
    tokens_used: reactive[int] = reactive(0)
    tokens_total: reactive[int] = reactive(100000)
    cost_spent: reactive[float] = reactive(0.0)
    lsp_status: reactive[str] = reactive("LSPs will activate as files are read")
    current_model: reactive[str] = reactive("Llama 3 2 3b")

    DEFAULT_CSS = """
    Sidebar {
        width: 30%;
        height: 100%;
        background: #111;
<<<<<<< HEAD
=======
        border-left: solid #1e1e1e;
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        padding: 1 2;
    }

    #sidebar-container {
        width: 100%;
        height: 100%;
    }

    .sidebar-section {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        padding: 1 0;
    }

    .section-title {
        width: 100%;
        height: 1;
        color: #e6e6e6;
        text-style: bold;
        margin: 0 0 1 0;
    }

    .section-content {
        width: 100%;
        height: auto;
        color: #9a9a9a;
    }

    .metric-label {
        color: #9a9a9a;
    }

    .metric-value {
        color: #7aa2f7;
        text-style: bold;
    }

    #context-section {
        border-bottom: solid #1e1e1e;
    }

    #lsp-section {
        border-bottom: solid #1e1e1e;
    }

    #shortcuts-section {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose sidebar layout."""
        with VerticalScroll(id="sidebar-container"):
            yield SidebarHeader()
            yield ContextSection()
            yield LSPSection()
            yield ShortcutsSection()


class SidebarHeader(Static):
    """Sidebar header with title."""

    DEFAULT_CSS = """
    SidebarHeader {
        width: 100%;
        height: auto;
        margin: 0 0 2 0;
        content-align: center top;
    }
    """

    def on_mount(self) -> None:
        """Set header text."""
<<<<<<< HEAD
        text = Text("irir layout and theme", style="bold white", justify="center")
=======
        text = Text("OpenCode layout and theme", style="bold white", justify="center")
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        text.append("\n", style="")
        text.append("explanation", style="dim white")
        self.update(text)


class ContextSection(Container):
    """Context information section."""

    DEFAULT_CSS = """
    ContextSection {
        width: 100%;
        height: auto;
        border-bottom: solid $primary-darken-2;
        padding: 0 0 2 0;
        margin: 0 0 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose context section."""
        yield Static("Context", classes="section-title")
        yield ContextMetrics()


class ContextMetrics(Static):
    """Display context metrics."""

    tokens_used: reactive[int] = reactive(0)
    tokens_total: reactive[int] = reactive(100000)
    cost_spent: reactive[float] = reactive(0.0)

    def on_mount(self) -> None:
        """Initialize metrics display."""
        self.update_metrics()

    def watch_tokens_used(self, new_value: int) -> None:
        """Update display when tokens change."""
        self.update_metrics()

    def watch_tokens_total(self, new_value: int) -> None:
        """Update display when total changes."""
        self.update_metrics()

    def watch_cost_spent(self, new_value: float) -> None:
        """Update display when cost changes."""
        self.update_metrics()

    def update_metrics(self) -> None:
        """Update the metrics display."""
        percentage = (self.tokens_used / self.tokens_total * 100) if self.tokens_total > 0 else 0

        text = Text()

        # Tokens
        text.append(f"{self.tokens_used:,}", style="bold white")
        text.append(" tokens\n", style="dim white")

        # Percentage
        text.append(f"{percentage:.0f}%", style="bold white")
        text.append(" used\n", style="dim white")

        # Cost
        text.append(f"${self.cost_spent:.2f}", style="bold white")
        text.append(" spent", style="dim white")

        self.update(text)


class LSPSection(Container):
    """LSP status section."""

    DEFAULT_CSS = """
    LSPSection {
        width: 100%;
        height: auto;
        border-bottom: solid $primary-darken-2;
        padding: 0 0 2 0;
        margin: 0 0 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose LSP section."""
        yield Static("LSP", classes="section-title")
        yield LSPStatus()


class LSPStatus(Static):
    """Display LSP status."""

    status: reactive[str] = reactive("LSPs will activate as files are read")

    def on_mount(self) -> None:
        """Initialize status display."""
        self.update_status()

    def watch_status(self, new_value: str) -> None:
        """Update display when status changes."""
        self.update_status()

    def update_status(self) -> None:
        """Update the status display."""
        text = Text(self.status, style="dim white")
        self.update(text)


class ShortcutsSection(Container):
    """Keyboard shortcuts section."""

    DEFAULT_CSS = """
    ShortcutsSection {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose shortcuts section."""
        yield Static("Keyboard Shortcuts", classes="section-title")
        yield ShortcutsTable()


class ShortcutsTable(Static):
    """Display keyboard shortcuts."""

    def on_mount(self) -> None:
        """Create shortcuts display."""
        shortcuts = [
            ("Tab", "agents"),
            ("Ctrl+P", "commands"),
            ("Ctrl+T", "variants"),
            ("Ctrl+N", "new chat"),
            ("Ctrl+S", "save"),
            ("Esc", "interrupt"),
        ]

        text = Text()
        for key, action in shortcuts:
            text.append("  ", style="")
            text.append(key, style="bold cyan")
            text.append("  ", style="")
            text.append(action, style="dim white")
            text.append("\n", style="")

        self.update(text)


# Alternative: More detailed sidebar with panels
class DetailedSidebar(Container):
    """More detailed sidebar with panels."""

    DEFAULT_CSS = """
    DetailedSidebar {
        width: 45;
        height: 100%;
        background: $surface;
        border-left: thick $primary;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose detailed sidebar."""
        with VerticalScroll():
            yield DetailedContextPanel()
            yield DetailedLSPPanel()
            yield DetailedModelPanel()
            yield DetailedShortcutsPanel()


class DetailedContextPanel(Static):
    """Detailed context panel with progress bar."""

    def on_mount(self) -> None:
        """Create detailed context display."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Label", style="dim white")
        table.add_column("Value", style="bold cyan")

        table.add_row("Tokens", "20,517 / 100,000")
        table.add_row("Usage", "20%")
        table.add_row("Cost", "$0.00")

        panel = Panel(
            table,
            title="[bold cyan]Context[/]",
            border_style="cyan",
            padding=(1, 2),
        )

        self.update(panel)


class DetailedLSPPanel(Static):
    """Detailed LSP panel."""

    def on_mount(self) -> None:
        """Create LSP display."""
        panel = Panel(
            "[dim white]LSPs will activate as files are read[/]",
            title="[bold cyan]LSP[/]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.update(panel)


class DetailedModelPanel(Static):
    """Detailed model information panel."""

    def on_mount(self) -> None:
        """Create model display."""
        text = Text()
        text.append("Llama 3 2 3b\n", style="bold white")
        text.append("Ollama (local)\n", style="dim white")
        text.append("\nStatus: ", style="dim white")
        text.append("● Ready", style="bold green")

        panel = Panel(
            text,
            title="[bold cyan]Model[/]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.update(panel)


class DetailedShortcutsPanel(Static):
    """Detailed shortcuts panel."""

    def on_mount(self) -> None:
        """Create shortcuts display."""
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Action", style="dim white")

        table.add_row("Tab", "agents")
        table.add_row("Ctrl+P", "commands")
        table.add_row("Ctrl+T", "variants")
        table.add_row("Ctrl+N", "new chat")
        table.add_row("Ctrl+S", "save")
        table.add_row("Esc", "interrupt")

        panel = Panel(
            table,
            title="[bold cyan]Shortcuts[/]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.update(panel)


__all__ = [
    "Sidebar",
    "SidebarHeader",
    "ContextSection",
    "ContextMetrics",
    "LSPSection",
    "LSPStatus",
    "ShortcutsSection",
    "ShortcutsTable",
    "DetailedSidebar",
]
