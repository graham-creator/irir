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
    # FILE OPERATIONS
    Command(
        id="file.new",
        name="New Conversation",
        description="Start a new conversation",
        category="File Operations",
        shortcut="Ctrl+N",
        keywords=["new", "create", "start"],
    ),
    Command(
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
    ),
    Command(
        id="file.delete",
        name="Delete Conversation",
        description="Delete current conversation",
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
        keywords=["home", "tab"],
    ),
    Command(
        id="view.chat",
        name="Go to Chat",
        description="Switch to chat tab",
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
    Command(
        id="quick.interrupt",
        name="Interrupt",
        description="Stop current operation",
        category="Quick Actions",
        shortcut="Esc",
        keywords=["stop", "cancel", "interrupt"],
    ),
    Command(
        id="quick.quit",
        name="Quit",
        description="Exit application",
        category="Quick Actions",
        shortcut="Ctrl+Q",
        keywords=["quit", "exit", "close"],
    ),
]


class CommandPalette(ModalScreen):
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
    }

    #palette-search {
        width: 100%;
        padding: 1 2 0 2;
        margin: 0;
    }

    #search-input {
        width: 100%;
        border: none;
        background: #080808;
        color: #eef3f6;
        padding: 0 1;
    }

    #results-container {
        width: 100%;
        height: auto;
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
    }
    """

    BINDINGS = [
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
