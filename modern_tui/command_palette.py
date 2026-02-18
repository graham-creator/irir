<<<<<<< HEAD
=======
"""
Command Palette for IRIR (Ctrl+P)
=================================

OpenCode-style command palette with:
- Fuzzy search
- Command categories
- Keyboard navigation
- Quick actions
"""

>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
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
<<<<<<< HEAD
    # FILE OPERATIONS
=======
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    Command(
        id="file.new",
        name="New Conversation",
        description="Start a new conversation",
<<<<<<< HEAD
        category="File Operations",
=======
        category="File",
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        shortcut="Ctrl+N",
        keywords=["new", "create", "start"],
    ),
    Command(
<<<<<<< HEAD
        id="file.search",
        name="Search Conversations",
        description="Find conversations by name or content",
        category="File Operations",
        shortcut="Ctrl+F",
        keywords=["search", "find", "filter"],
    ),
    Command(
        id="file.recent",
        name="Recent Conversations",
        description="Show recently used conversations",
        category="File Operations",
        keywords=["recent", "history", "list"],
    ),
    Command(
        id="file.goto_line",
        name="Go to Line",
        description="Jump to specific message line",
        category="File Operations",
        shortcut="Ctrl+G",
        keywords=["goto", "line", "jump"],
    ),
    Command(
        id="file.import",
        name="Import Conversation",
        description="Import conversation from file",
        category="File Operations",
        keywords=["import", "load"],
    ),
    Command(
        id="file.export",
        name="Export to Markdown",
        description="Export conversation as markdown",
        category="File Operations",
        shortcut="Ctrl+E",
        keywords=["export", "md", "markdown", "save"],
    ),
    Command(
        id="file.rename",
        name="Rename Conversation",
        description="Rename current conversation",
        category="File Operations",
        keywords=["rename", "title"],
=======
        id="file.save",
        name="Save Conversation",
        description="Save current conversation",
        category="File",
        shortcut="Ctrl+S",
        keywords=["save", "export"],
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    ),
    Command(
        id="file.delete",
        name="Delete Conversation",
        description="Delete current conversation",
<<<<<<< HEAD
        category="File Operations",
        keywords=["delete", "remove"],
    ),
    
    # CODE ACTIONS
    Command(
        id="code.format",
        name="Format Message",
        description="Format code blocks in message",
        category="Code Actions",
        shortcut="Ctrl+Shift+F",
        keywords=["format", "code"],
    ),
    Command(
        id="code.refactor",
        name="Suggest Refactoring",
        description="Ask AI for refactoring suggestions",
        category="Code Actions",
        keywords=["refactor", "improve", "optimize"],
    ),
    Command(
        id="code.test",
        name="Generate Tests",
        description="Generate test cases for code",
        category="Code Actions",
        keywords=["test", "unit", "generate"],
    ),
    Command(
        id="code.build",
        name="Run/Build Commands",
        description="Execute build or run commands",
        category="Code Actions",
        keywords=["build", "run", "execute"],
    ),
    
    # WORKSPACE MANAGEMENT
    Command(
        id="workspace.switch",
        name="Switch Workspace/Project",
        description="Switch to different workspace",
        category="Workspace Management",
        keywords=["workspace", "project", "switch"],
    ),
    Command(
        id="workspace.terminal",
        name="Open Terminal",
        description="Open external terminal",
        category="Workspace Management",
        keywords=["terminal", "shell", "bash"],
    ),
    Command(
        id="workspace.toggle_panels",
        name="Toggle Panels",
        description="Show/hide side panels",
        category="Workspace Management",
        shortcut="Ctrl+B",
        keywords=["panel", "toggle", "sidebar"],
    ),
    Command(
        id="workspace.settings",
        name="Settings/Preferences",
        description="Open settings and preferences",
        category="Workspace Management",
        shortcut="Ctrl+,",
        keywords=["settings", "preferences", "config"],
    ),
    
    # GIT INTEGRATION
    Command(
        id="git.commit",
        name="Commit Changes",
        description="Commit conversation to git",
        category="Git Integration",
        keywords=["commit", "git"],
    ),
    Command(
        id="git.push",
        name="Push to Remote",
        description="Push changes to remote repository",
        category="Git Integration",
        keywords=["push", "git"],
    ),
    Command(
        id="git.pull",
        name="Pull from Remote",
        description="Pull latest changes from remote",
        category="Git Integration",
        keywords=["pull", "git"],
    ),
    Command(
        id="git.branch",
        name="Branch Management",
        description="Create, switch, or delete branches",
        category="Git Integration",
        keywords=["branch", "git"],
    ),
    Command(
        id="git.changes",
        name="View Changes",
        description="View pending changes and diffs",
        category="Git Integration",
        keywords=["changes", "diff", "git"],
    ),
    
    # AI-SPECIFIC
    Command(
        id="ai.new_session",
        name="Start New Chat Session",
        description="Create a new AI chat session",
        category="AI-Specific",
        shortcut="Ctrl+Alt+N",
        keywords=["chat", "session", "new"],
    ),
    Command(
        id="ai.switch_model",
        name="Switch AI Model",
        description="Change the active AI model",
        category="AI-Specific",
        keywords=["model", "switch", "provider"],
    ),
    Command(
        id="ai.switch_provider",
        name="Switch Model Provider",
        description="Switch between different AI providers (Ollama, ChatGPT, Copilot)",
        category="AI-Specific",
        keywords=["provider", "switch", "api"],
    ),
    Command(
        id="ai.copilot_account",
        name="Access Copilot/ChatGPT Account",
        description="Sign in or manage AI account credentials",
        category="AI-Specific",
        keywords=["account", "copilot", "chatgpt", "auth"],
    ),
    Command(
        id="ai.share_session",
        name="Share Session Link",
        description="Generate shareable link for current session",
        category="AI-Specific",
        keywords=["share", "link", "session"],
    ),
    Command(
        id="ai.compare_models",
        name="Compare Model Responses",
        description="Send same prompt to multiple models",
        category="AI-Specific",
        keywords=["compare", "models", "multi"],
    ),
    
    # VIEW & NAVIGATION
    Command(
        id="view.home",
        name="Go to Home",
        description="Switch to home tab",
        category="View & Navigation",
=======
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
        id="view.home",
        name="Go to Home",
        description="Switch to home tab",
        category="View",
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        keywords=["home", "tab"],
    ),
    Command(
        id="view.chat",
        name="Go to Chat",
        description="Switch to chat tab",
<<<<<<< HEAD
        category="View & Navigation",
        keywords=["chat", "tab"],
    ),
    Command(
        id="view.focus_input",
        name="Focus Input",
        description="Focus the message input field",
        category="View & Navigation",
        shortcut="/",
        keywords=["input", "focus", "type"],
    ),
    
    # QUICK ACTIONS
=======
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
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    Command(
        id="quick.interrupt",
        name="Interrupt",
        description="Stop current operation",
<<<<<<< HEAD
        category="Quick Actions",
=======
        category="Quick",
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        shortcut="Esc",
        keywords=["stop", "cancel", "interrupt"],
    ),
    Command(
        id="quick.quit",
        name="Quit",
        description="Exit application",
<<<<<<< HEAD
        category="Quick Actions",
=======
        category="Quick",
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
        shortcut="Ctrl+Q",
        keywords=["quit", "exit", "close"],
    ),
]


class CommandPalette(ModalScreen):
<<<<<<< HEAD
    """Command palette - can be inline or modal."""

    DEFAULT_CSS = """
    /* Overlay covers screen; inner dialog is centered and compact */
    CommandPalette {
        align: center middle;
        background: $surface;
    }

    /* Dialog uses solid background and border to feel like a popup */
    #palette-dialog {
        width: 48%;
        max-width: 88;
        background: #0b0b0b;
        border: solid #1a5a7f;
        padding: 0;
        color: #e9eef2;
    }

    /* Class toggled on mount to trigger visibility */
    #palette-dialog.enter {
        opacity: 1;
    }

    /* Header with title and esc hint */
    #palette-header {
        width: 100%;
        height: 1;
        background: #0a0a0a;
        border-bottom: solid #1a5a7f;
        padding: 0 2;
    }

    #palette-title {
        width: 1fr;
        height: 1;
        color: #e9eef2;
        text-style: bold;
        align: left middle;
    }

    #palette-hint {
        width: auto;
        height: 1;
        color: #888888;
        text-align: right;
        align: right middle;
=======
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
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    }

    #palette-search {
        width: 100%;
<<<<<<< HEAD
        padding: 1 2 0 2;
        margin: 0;
=======
        padding: 0 2;
        margin: 1 0;
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    }

    #search-input {
        width: 100%;
<<<<<<< HEAD
        border: none;
        background: #080808;
        color: #eef3f6;
        padding: 0 1;
=======
        border: solid #00ffff;
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    }

    #results-container {
        width: 100%;
        height: auto;
<<<<<<< HEAD
        max-height: 16;
        padding: 0 2;
        overflow: auto;
    }

    .command-result {
        padding: 0 2;
        margin: 0;
        color: #e6e6e6;
    }

    .command-result.selected {
        background: #007fbf;
        color: #ffffff;
    }

    .command-category {
        padding: 0 2;
        color: #7adfff;
        text-style: bold;
    }

    .command-shortcut {
        text-align: right;
        color: #cfcfcf;
=======
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
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
    }
    """

    BINDINGS = [
<<<<<<< HEAD
        Binding("escape", "quit", "Cancel", show=False),
        Binding("enter", "submit", "Submit", show=False),
        Binding("up", "select_previous", "Previous", show=False),
        Binding("down", "select_next", "Next", show=False),
    ]

    def __init__(self, commands: List[Command]):
        super().__init__()
        self.commands = commands
        self.filtered_commands: List[Command] = commands.copy()
        self.selected_index: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the command palette UI."""
        # Inner dialog container mirrors the centered modal in OpenCode
        with Container(id="palette-dialog"):
            # Header with title and esc hint
            yield Container(
                Static("Commands", id="palette-title"),
                Static("esc", id="palette-hint"),
                id="palette-header",
            )
            yield Container(
                Input(
                    id="search-input",
                    placeholder="Type a command name, description, or category...",
                ),
                id="palette-search",
            )
            yield VerticalScroll(id="results-container")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        query = event.value
        self.filter_commands(query)
        self.selected_index = 0
        self.render_results()

    def on_mount(self) -> None:
        """Focus search input when the modal mounts."""
        try:
            # focus search field
            self.query_one("#search-input", Input).focus()
        except Exception:
            pass

        # trigger enter state on dialog
        try:
            dlg = self.query_one("#palette-dialog")
            dlg.add_class("enter")
        except Exception:
            pass

        # Render initial results so the palette shows suggestions immediately
        try:
            self.filter_commands("")
            self.selected_index = 0
            self.render_results()
        except Exception:
            pass

    def filter_commands(self, query: str) -> None:
        """Filter commands based on search query."""
        if not query:
            self.filtered_commands = self.commands.copy()
        else:
            self.filtered_commands = [
                cmd for cmd in self.commands if cmd.matches(query)
            ]

    def render_results(self) -> None:
        """Render the filtered commands."""
        container = self.query_one("#results-container", VerticalScroll)
        # Clear existing children
        for child in list(container.children):
            child.remove()

        if not self.filtered_commands:
            container.mount(
                Static("No commands found.", classes="")
            )
            return

        current_category = None
        for i, cmd in enumerate(self.filtered_commands):
            if cmd.category != current_category:
                current_category = cmd.category
                container.mount(
                    Static(f"╭─ {current_category}", classes="command-category")
                )

            cls = "command-result" + (
                " selected" if i == self.selected_index else ""
            )
            text = f"{cmd.name:<38} {cmd.shortcut or '':<14}"
            container.mount(Static(text, classes=cls))

    def action_select_next(self) -> None:
        """Select next command."""
        if self.filtered_commands:
            self.selected_index = min(
                self.selected_index + 1,
                len(self.filtered_commands) - 1,
            )
            self.render_results()

    def action_select_previous(self) -> None:
        """Select previous command."""
        if self.filtered_commands:
            self.selected_index = max(self.selected_index - 1, 0)
            self.render_results()

    def action_submit(self) -> None:
        """Submit the selected command."""
        if self.filtered_commands and self.selected_index < len(self.filtered_commands):
            cmd = self.filtered_commands[self.selected_index]
            try:
                # Notify the app about the selected command before dismissing.
                if hasattr(self.app, "handle_palette_result"):
                    self.app.handle_palette_result(cmd.id)
            except Exception:
                pass
            self.dismiss(cmd.id)
        else:
            self.dismiss(None)

    def action_quit(self) -> None:
        """Close the command palette."""
        try:
            if hasattr(self.app, "handle_palette_result"):
                self.app.handle_palette_result(None)
        except Exception:
            pass
        self.dismiss(None)

    def on_unmount(self) -> None:
        """Ensure app is notified when the palette unmounts."""
        try:
            if hasattr(self.app, "handle_palette_result"):
                self.app.handle_palette_result(None)
        except Exception:
            pass
=======
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
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
