"""
Slash Command System for IRIR Chat
===================================

Provides slash-based quick commands accessible via / in the chat input.
Examples: /help, /export, /models, /agents, etc.
"""

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class SlashCommand:
    """Represents a slash command."""
    
    name: str
    description: str
    category: str
    example: Optional[str] = None
    callback: Optional[Callable] = None
    
    def matches(self, query: str) -> bool:
        """Check if command matches search query."""
        if not query:
            return True
        query_lower = query.lower().lstrip('/')
        return query_lower in self.name.lower() or query_lower in self.description.lower()


# All available slash commands
SLASH_COMMANDS = [
    # SESSION MANAGEMENT
    SlashCommand(
        name="new",
        description="Start a new chat session",
        category="Session Management",
        example="/new",
    ),
    SlashCommand(
        name="sessions",
        description="Switch between sessions",
        category="Session Management",
        example="/sessions",
    ),
    SlashCommand(
        name="rename",
        description="Rename current session",
        category="Session Management",
        example="/rename My Session",
    ),
    SlashCommand(
        name="share",
        description="Share current session link",
        category="Session Management",
        example="/share",
    ),
    SlashCommand(
        name="export",
        description="Export session transcript",
        category="Session Management",
        example="/export",
    ),
    
    # MODEL & PROVIDER CONTROL
    SlashCommand(
        name="models",
        description="Switch AI model",
        category="Model Control",
        example="/models",
    ),
    SlashCommand(
        name="agents",
        description="Switch agent",
        category="Model Control",
        example="/agents",
    ),
    SlashCommand(
        name="connect",
        description="Connect to AI provider",
        category="Model Control",
        example="/connect",
    ),
    
    # CODE & DEVELOPMENT
    SlashCommand(
        name="copy",
        description="Copy session transcript",
        category="Development",
        example="/copy",
    ),
    SlashCommand(
        name="fork",
        description="Fork from this message",
        category="Development",
        example="/fork",
    ),
    SlashCommand(
        name="review",
        description="Review changes [commit|branch|pr]",
        category="Development",
        example="/review commit",
    ),
    SlashCommand(
        name="editor",
        description="Open external editor",
        category="Development",
        example="/editor",
    ),
    
    # SETTINGS & DISPLAY
    SlashCommand(
        name="themes",
        description="Switch theme",
        category="Settings",
        example="/themes",
    ),
    SlashCommand(
        name="compact",
        description="Toggle compact mode",
        category="Settings",
        example="/compact",
    ),
    SlashCommand(
        name="status",
        description="Show system status",
        category="Settings",
        example="/status",
    ),
    SlashCommand(
        name="skills",
        description="Show available skills",
        category="Settings",
        example="/skills",
    ),
    
    # READING & DISPLAY
    SlashCommand(
        name="thinking",
        description="Hide/show thinking process",
        category="Display",
        example="/thinking",
    ),
    SlashCommand(
        name="timestamps",
        description="Show message timestamps",
        category="Display",
        example="/timestamps",
    ),
    SlashCommand(
        name="timeline",
        description="Jump to message",
        category="Display",
        example="/timeline",
    ),
    
    # UTILITY
    SlashCommand(
        name="undo",
        description="Undo previous message",
        category="Utility",
        example="/undo",
    ),
    SlashCommand(
        name="help",
        description="Show command help",
        category="Utility",
        example="/help [command]",
    ),
    SlashCommand(
        name="init",
        description="Initialize/reset session",
        category="Utility",
        example="/init",
    ),
    SlashCommand(
        name="exit",
        description="Exit the application",
        category="Utility",
        example="/exit",
    ),
    SlashCommand(
        name="mcps",
        description="Toggle MCP servers",
        category="Utility",
        example="/mcps",
    ),
]


def get_slash_commands() -> List[SlashCommand]:
    """Get all available slash commands."""
    return SLASH_COMMANDS


def get_commands_for_query(query: str) -> List[SlashCommand]:
    """Get commands matching the given query."""
    query_clean = query.lstrip('/').strip()
    if not query_clean:
        return SLASH_COMMANDS
    return [cmd for cmd in SLASH_COMMANDS if cmd.matches(query_clean)]


def format_command_help(cmd: SlashCommand) -> str:
    """Format command for display."""
    return f"/{cmd.name:<15} {cmd.description:<40} {cmd.example or ''}"
