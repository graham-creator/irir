"""
Command Palette for IRIR (Ctrl+P)
=================================

OpenCode-style command palette with:
- Fuzzy search
- Command categories
- Keyboard navigation
- Quick actions
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Input, Static


@dataclass
class Command:
    """Represents a command in the palette."""

    id: str
    name: str
    description: str
    category: str
    shortcut: Optional[str] = None
    action: Optional[Callable] = None
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

    def matches(self, query: str) -> bool:
        """Check if command matches search query."""
        if not query:
            return True

        query_lower = query.lower()

        if query_lower in self.name.lower():
            return True
        if query_lower in self.description.lower():
            return True
        if query_lower in self.category.lower():
            return True

        for keyword in self.keywords:
            if query_lower in keyword.lower():
                return True

        return self._fuzzy_match(query_lower, self.name.lower())

    def _fuzzy_match(self, query: str, target: str) -> bool:
        """Simple fuzzy matching."""
        query_idx = 0
        for char in target:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)


DEFAULT_COMMANDS = [
    Command(
        id="file.new",
        name="New Conversation",
        description="Start a new conversation",
        category="File",
        shortcut="Ctrl+N",
        keywords=["new", "create", "start"],
    ),
    Command(
        id="file.save",
        name="Save Conversation",
        description="Save current conversation",
        category="File",
        shortcut="Ctrl+S",
        keywords=["save", "export"],
    ),
    Command(
        id="file.delete",
        name="Delete Conversation",
        description="Delete current conversation",
        category="File",
        keywords=["delete", "remove"],
    ),
    Command(
        id="file.rename",
        name="Rename Conversation",
        description="Rename current conversation",
        category="File",
        keywords=["rename", "title"],
    ),
    Command(
        id="file.export",
        name="Export to Markdown",
        description="Export conversation as markdown",
        category="File",
        keywords=["export", "md", "markdown"],
    ),
    Command(
        id="file.import",
        name="Import Conversation",
        description="Import conversation from JSON file",
        category="File",
        keywords=["import", "json", "conversation"],
    ),
    Command(
        id="view.home",
        name="Go to Home",
        description="Switch to home tab",
        category="View",
        keywords=["home", "tab"],
    ),
    Command(
        id="view.chat",
        name="Go to Chat",
        description="Switch to chat tab",
        category="View",
        keywords=["chat", "tab"],
    ),
    Command(
        id="view.toggle_sidebar",
        name="Toggle Sidebar",
        description="Show/hide context sidebar",
        category="View",
        shortcut="Ctrl+B",
        keywords=["sidebar", "toggle", "hide"],
    ),
    Command(
        id="view.focus_input",
        name="Focus Input",
        description="Focus the message input field",
        category="View",
        shortcut="/",
        keywords=["input", "focus", "type"],
    ),
    Command(
        id="view.toggle_agents",
        name="Toggle Agents",
        description="Show or hide agents/models panel",
        category="View",
        shortcut="Tab",
        keywords=["agents", "models", "panel"],
    ),
    Command(
        id="model.refresh",
        name="Refresh Models",
        description="Reload available local models",
        category="Model",
        keywords=["model", "refresh", "reload"],
    ),
    Command(
        id="model.use_selected",
        name="Use Selected Model",
        description="Set conversation model from selector",
        category="Model",
        keywords=["model", "selected", "set"],
    ),
    Command(
        id="yt.pull",
        name="Pull YouTube Transcript",
        description="Fetch/process transcript from input URL",
        category="YouTube",
        keywords=["youtube", "transcript", "pull"],
    ),
    Command(
        id="edit.open_external_editor",
        name="Open External Editor",
        description="Open $EDITOR for the message input",
        category="Edit",
        shortcut="Ctrl+X E",
        keywords=["editor", "external", "edit"],
    ),
    Command(
        id="tools.run_smoke_test",
        name="Run Smoke Test",
        description="Run built-in smoke test workflow",
        category="Tools",
        keywords=["smoke", "test", "tools"],
    ),
    Command(
        id="quick.interrupt",
        name="Interrupt",
        description="Stop current operation",
        category="Quick",
        shortcut="Esc",
        keywords=["stop", "cancel", "interrupt"],
    ),
    Command(
        id="quick.quit",
        name="Quit",
        description="Exit application",
        category="Quick",
        shortcut="Ctrl+Q",
        keywords=["quit", "exit", "close"],
    ),
]


class CommandPalette(ModalScreen):
    """Command palette modal screen."""

    DEFAULT_CSS = """
    CommandPalette {
        align: center top;
        background: rgba(0, 0, 0, 0.85);
    }

    #palette-container {
        width: 80;
        height: auto;
        max-height: 30;
        margin: 4 0;
        background: #1a1a1a;
        border: thick #00ffff;
    }

    #palette-header {
        width: 100%;
        height: auto;
        background: #003333;
        padding: 1 2;
        color: #00ffff;
        text-style: bold;
    }

    #palette-search {
        width: 100%;
        padding: 0 2;
        margin: 1 0;
    }

    #search-input {
        width: 100%;
        border: solid #00ffff;
    }

    #results-container {
        width: 100%;
        height: auto;
        max-height: 20;
        padding: 0 2 1 2;
    }

    #command-list {
        width: 100%;
        height: auto;
        max-height: 18;
        border: none;
        background: #1a1a1a;
    }

    #no-results {
        width: 100%;
        height: 3;
        content-align: center middle;
        color: #666666;
    }

    #footer-hint {
        width: 100%;
        height: auto;
        padding: 1 2;
        background: #111111;
        color: #666666;
        text-align: center;
    }

    .command-item {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    .command-item:hover,
    .command-item.selected {
        background: #003333;
    }

    .command-category {
        color: #00ffff;
        text-style: bold;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=False),
        Binding("ctrl+p", "dismiss", "Close", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
    ]

    selected_index: reactive[int] = reactive(0)

    def __init__(self, commands: List[Command] = None):
        super().__init__()
        self.commands = commands or DEFAULT_COMMANDS
        self.filtered_commands = self.commands.copy()

    def compose(self) -> ComposeResult:
        with Container(id="palette-container"):
            yield Static("Command Palette", id="palette-header")
            with Container(id="palette-search"):
                yield Input(
                    placeholder="Type a command or search...",
                    id="search-input",
                )
            with Container(id="results-container"):
                yield CommandList(id="command-list")
                yield Static("No commands found", id="no-results", classes="hidden")
            yield Static(
                "↑↓ Navigate  •  Enter Execute  •  Esc Close",
                id="footer-hint",
            )

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()
        self.update_results("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.update_results(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.execute_selected_command()

    def action_cursor_down(self) -> None:
        if not self.filtered_commands:
            return
        self.selected_index = (self.selected_index + 1) % len(self.filtered_commands)
        self.highlight_selected()

    def action_cursor_up(self) -> None:
        if not self.filtered_commands:
            return
        self.selected_index = (self.selected_index - 1) % len(self.filtered_commands)
        self.highlight_selected()

    def update_results(self, query: str) -> None:
        if query:
            self.filtered_commands = [cmd for cmd in self.commands if cmd.matches(query)]
        else:
            self.filtered_commands = self.commands.copy()

        self.filtered_commands.sort(key=lambda c: c.category)

        command_list = self.query_one("#command-list", CommandList)
        command_list.clear()

        if self.filtered_commands:
            self.query_one("#no-results").add_class("hidden")
            current_category = None
            for cmd in self.filtered_commands:
                if cmd.category != current_category:
                    command_list.add_category(cmd.category)
                    current_category = cmd.category
                command_list.add_command(cmd)
        else:
            self.query_one("#no-results").remove_class("hidden")

        self.selected_index = 0
        self.highlight_selected()

    def highlight_selected(self) -> None:
        command_list = self.query_one("#command-list", CommandList)
        command_list.highlight(self.selected_index)

    def execute_selected_command(self) -> None:
        if self.filtered_commands:
            command = self.filtered_commands[self.selected_index]
            self.dismiss(command.id)


class CommandList(VerticalScroll):
    """Scrollable list of commands."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_items: List[CommandItem] = []

    def clear(self) -> None:
        self.remove_children()
        self.command_items = []

    def add_category(self, category: str) -> None:
        header = Static(f"─── {category} ───", classes="command-category")
        self.mount(header)

    def add_command(self, command: Command) -> None:
        item = CommandItem(command)
        self.mount(item)
        self.command_items.append(item)

    def highlight(self, index: int) -> None:
        for idx, item in enumerate(self.command_items):
            if idx == index:
                item.add_class("selected")
            else:
                item.remove_class("selected")


class CommandItem(Container):
    """Individual command item."""

    def __init__(self, command: Command):
        super().__init__(classes="command-item")
        self.command = command

    def compose(self) -> ComposeResult:
        yield CommandItemContent(self.command)


class CommandItemContent(Static):
    """Content of a command item."""

    def __init__(self, command: Command):
        super().__init__()
        self.command = command

    def on_mount(self) -> None:
        text = Text()
        text.append(self.command.name, style="bold white")
        if self.command.shortcut:
            text.append("  ", style="")
            text.append(f"({self.command.shortcut})", style="dim cyan")
        text.append("\n", style="")
        text.append(self.command.description, style="dim white")
        self.update(text)


__all__ = [
    "CommandPalette",
    "Command",
    "DEFAULT_COMMANDS",
]
