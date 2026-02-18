"""
Slash Command Autocomplete Widget
==================================

Dropdown UI that appears when typing / in the chat input.
"""

from typing import List, Optional
import logging
from textual.containers import Vertical
from textual.widgets import Static, Label
from rich.table import Table
from rich.text import Text

from .slash_commands import SlashCommand, get_commands_for_query


class SlashCommandMenu(Vertical):
    """Dropdown menu for slash commands."""
    
    DEFAULT_CSS = """
    SlashCommandMenu {
        height: auto;
        max-height: 9;
        background: #0a0a0a;
        border: solid #1a5a7f;
        width: 100%;
        padding: 0 0;
    }
    
    .slash-cmd-item {
        padding: 0 1;
        height: 1;
        color: #e0e0e0;
    }
    
    .slash-cmd-item.selected {
        background: #007fbf;
        color: #ffffff;
        text-style: bold;
    }
    
    .slash-cmd-category {
        padding: 0 1;
        color: #7adfff;
        text-style: bold;
        height: 1;
    }
    """
    
    selected_index = -1
    commands: List[SlashCommand] = []
    current_category = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children_by_command = {}
        self.display = False  # Start hidden until slash is typed
        self.selected_index = 0
    
    def render(self) -> str:
        """Keep render minimal."""
        return ""
    
    def update_menu(self, query: str) -> None:
        """Update menu with matching commands."""
        # Debug log for visibility during testing
        logging.getLogger(__name__).debug("SlashCommandMenu.update_menu query=%r", query)
        self.commands = get_commands_for_query(query)
        self.selected_index = 0
        self.current_category = ""
        
        # Show if there are commands, hide if not
        if self.commands:
            logging.getLogger(__name__).debug("SlashCommandMenu found %d commands", len(self.commands))
            self.display = True
            self._render_commands()
        else:
            logging.getLogger(__name__).debug("SlashCommandMenu no commands -> hiding")
            self.display = False
    
    def _render_commands(self) -> None:
        """Render the command list."""
        # Clear existing
        for child in list(self.children):
            child.remove()
        self.children_by_command.clear()
        
        if not self.commands:
            return
        
        for i, cmd in enumerate(self.commands):
            # Add category header if changed
            if cmd.category != self.current_category:
                self.current_category = cmd.category
                category_label = Label(f"╭─ {cmd.category}")
                category_label.add_class("slash-cmd-category")
                self.mount(category_label)
            
            # Add command item
            text = f"/{cmd.name:<14} {cmd.description}"
            cmd_label = Label(text)
            cmd_label.add_class("slash-cmd-item")
            if i == self.selected_index:
                cmd_label.add_class("selected")
            self.mount(cmd_label)
            self.children_by_command[i] = (cmd, cmd_label)
    
    def select_next(self) -> None:
        """Select next command."""
        if self.commands:
            self.selected_index = (self.selected_index + 1) % len(self.commands)
            self._render_commands()
    
    def select_previous(self) -> None:
        """Select previous command."""
        if self.commands:
            self.selected_index = (self.selected_index - 1) % len(self.commands)
            self._render_commands()
    
    def get_selected_command(self) -> SlashCommand | None:
        """Get the currently selected command."""
        if 0 <= self.selected_index < len(self.commands):
            return self.commands[self.selected_index]
        return None
    
    def hide(self) -> None:
        """Hide the menu."""
        self.display = False
