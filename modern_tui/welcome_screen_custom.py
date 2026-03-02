"""
Customized Welcome Screen for IRIR
===================================

Enhanced with:
- Multiple color themes
- 5+ logo style options
- Custom rotating prompts
- Theme selector
- Animated effects
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Select
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align
import random


class ColorTheme:
    """Color theme configuration."""

    def __init__(self, name: str, logo_color: str, accent: str, secondary: str, bg: str):
        self.name = name
        self.logo_color = logo_color
        self.accent = accent
        self.secondary = secondary
        self.bg = bg


THEMES = {
    "cyan_matrix": ColorTheme(
        name="Cyan Matrix",
        logo_color="cyan",
        accent="bright_cyan",
        secondary="green",
        bg="#0a0a0a",
    ),
    "purple_dream": ColorTheme(
        name="Purple Dream",
        logo_color="magenta",
        accent="bright_magenta",
        secondary="purple",
        bg="#0a0014",
    ),
    "fire": ColorTheme(
        name="Fire",
        logo_color="red",
        accent="bright_red",
        secondary="yellow",
        bg="#140a00",
    ),
    "ocean": ColorTheme(
        name="Ocean",
        logo_color="blue",
        accent="bright_blue",
        secondary="cyan",
        bg="#000a14",
    ),
    "forest": ColorTheme(
        name="Forest",
        logo_color="green",
        accent="bright_green",
        secondary="yellow",
        bg="#0a1400",
    ),
    "sunset": ColorTheme(
        name="Sunset",
        logo_color="yellow",
        accent="gold",
        secondary="orange",
        bg="#140a00",
    ),
    "monochrome": ColorTheme(
        name="Monochrome",
        logo_color="white",
        accent="bright_white",
        secondary="grey70",
        bg="#000000",
    ),
}


CUSTOM_PROMPTS = [
    "What is the tech stack of this project?",
    "Explain the architecture of this codebase",
    "How do I contribute to this project?",
    "Show me recent changes and updates",
    "What are the main components?",
    "Help me understand this code",
    "Generate documentation for this module",
    "Review my code for improvements",
    "Explain this error message",
    "Suggest optimization strategies",
    "What are the best practices here?",
    "Compare different approaches",
    "Generate unit tests for this function",
    "Refactor this code",
    "Debug this issue",
]


class WelcomeScreen(Container):
    """Enhanced welcome screen with themes and custom prompts."""

    current_theme: reactive[str] = reactive("cyan_matrix")

    DEFAULT_CSS = """
    WelcomeScreen {
        width: 100%;
        height: 100%;
        background: $background;
        align: center middle;
    }

    #welcome-container {
        width: auto;
        height: auto;
        align: center middle;
    }

    #logo {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 2 0;
    }

    #input-container {
        width: 80;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 1 2;
        margin: 2 0;
    }

    #welcome-input {
        width: 100%;
        background: $surface;
        border: none;
    }

    #model-info {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1 0;
        color: $primary;
    }

    #tip-section {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 2 0;
        color: $warning;
    }

    #theme-selector {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the welcome screen layout."""
        with Vertical(id="welcome-container"):
            yield EnhancedLogo()
            yield ThemeSelector()
            yield SmartInputSection()
            yield ModelInfo()
            yield TipSection()

    def watch_current_theme(self, theme_name: str) -> None:
        """Update colors when theme changes."""
        logo = self.query_one(EnhancedLogo)
        logo.set_theme(theme_name)


class EnhancedLogo(Static):
    """Enhanced IRIR logo with multiple styles and themes."""

    current_style: str = "ascii"
    current_theme: str = "cyan_matrix"

    LOGO_STYLES = {
        "ascii": """
██╗██████╗ ██╗██████╗ 
██║██╔══██╗██║██╔══██╗
██║██████╔╝██║██████╔╝
██║██╔══██╗██║██╔══██╗
██║██║  ██║██║██║  ██║
╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
""",
        "block": """
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ██ ██▀▄ ██ ██▀▄ ██
█ ▄▄ ██▀▄ ██ ██▀▄ ██
█▄██▄██▄▄██▄▄██▄▄███
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
""",
        "minimal": """

        i r i r

""",
        "3d": """
  _____ _____  _____ _____ 
 |_   _|  __ \\|_   _|  __ \\
   | | | |__) | | | | |__) |
   | | |  _  /  | | |  _  / 
  _| |_| | \\ \\ _| |_| | \\ \\ 
 |_____|_|  \\_\\_____|_|  \\_\\
""",
        "neon": """
╔═╗╦═╗╦═╗
║  ╠╦╝╠╦╝
╚═╝╩╚═╩╚═
""",
    }

    def on_mount(self) -> None:
        """Create the logo when mounted."""
        self.update_logo()

    def update_logo(self) -> None:
        """Update logo with current style and theme."""
        logo_text = self.LOGO_STYLES.get(self.current_style, self.LOGO_STYLES["ascii"])
        theme = THEMES.get(self.current_theme, THEMES["cyan_matrix"])

        text = Text(logo_text, justify="center")
        text.stylize(f"bold {theme.logo_color}")

        self.update(text)

    def set_style(self, style: str) -> None:
        """Change logo style."""
        if style in self.LOGO_STYLES:
            self.current_style = style
            self.update_logo()

    def set_theme(self, theme: str) -> None:
        """Change logo theme."""
        if theme in THEMES:
            self.current_theme = theme
            self.update_logo()


class GradientLogo(Static):
    """IRIR logo with animated gradient effect."""

    def on_mount(self) -> None:
        """Create gradient logo."""
        logo_lines = [
            "██╗██████╗ ██╗██████╗ ",
            "██║██╔══██╗██║██╔══██╗",
            "██║██████╔╝██║██████╔╝",
            "██║██╔══██╗██║██╔══██╗",
            "██║██║  ██║██║██║  ██║",
            "╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝",
        ]

        colors = [
            "bright_red",
            "bright_yellow",
            "bright_green",
            "bright_cyan",
            "bright_blue",
            "bright_magenta",
        ]

        text = Text()
        for line, color in zip(logo_lines, colors):
            text.append(line + "\n", style=f"bold {color}")

        self.update(Align.center(text))


class NeonLogo(Static):
    """Neon-style IRIR logo with glow effect."""

    def on_mount(self) -> None:
        """Create neon logo."""
        logo = """
╔══════════════════════╗
║                      ║
║   ██╗██████╗ ██╗██████╗    ║
║   ██║██╔══██╗██║██╔══██╗   ║
║   ██║██████╔╝██║██████╔╝   ║
║   ██║██╔══██╗██║██╔══██╗   ║
║   ██║██║  ██║██║██║  ██║   ║
║   ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝   ║
║                      ║
╚══════════════════════╝
"""
        text = Text(logo, justify="center")
        text.stylize("bold magenta on #000033")
        self.update(text)


class MinimalistLogo(Static):
    """Clean, minimal IRIR logo."""

    def on_mount(self) -> None:
        """Create minimalist logo."""
        text = Text()
        text.append("\n\n", style="")
        text.append("        ", style="")
        text.append("░", style="dim cyan")
        text.append("▒", style="cyan")
        text.append("▓", style="bright_cyan")
        text.append(" ", style="")
        text.append("irir", style="bold bright_cyan")
        text.append(" ", style="")
        text.append("▓", style="bright_cyan")
        text.append("▒", style="cyan")
        text.append("░", style="dim cyan")
        text.append("\n\n", style="")

        self.update(Align.center(text))


class SmartInputSection(Container):
    """Input section with rotating smart prompts."""

    DEFAULT_CSS = """
    SmartInputSection {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose input section."""
        with Container(id="input-container"):
            yield Input(
                placeholder=self._get_random_prompt(),
                id="welcome-input",
            )

    def _get_random_prompt(self) -> str:
        """Get a random prompt from the list."""
        prompt = random.choice(CUSTOM_PROMPTS)
        return f'Ask anything... "{prompt}"'

    def rotate_prompt(self) -> None:
        """Change to a new random prompt."""
        input_widget = self.query_one("#welcome-input", Input)
        input_widget.placeholder = self._get_random_prompt()


class ThemeSelector(Container):
    """Theme selector dropdown."""

    DEFAULT_CSS = """
    ThemeSelector {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1 0;
    }

    #theme-label {
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose theme selector."""
        with Horizontal():
            yield Static("Theme: ", id="theme-label")
            yield ThemeDisplay()


class ThemeDisplay(Static):
    """Display current theme with color preview."""

    current_theme: reactive[str] = reactive("cyan_matrix")

    def on_mount(self) -> None:
        """Initialize theme display."""
        self.update_display()

    def watch_current_theme(self, theme_name: str) -> None:
        """Update display when theme changes."""
        self.update_display()

    def update_display(self) -> None:
        """Update the theme display."""
        theme = THEMES.get(self.current_theme, THEMES["cyan_matrix"])

        text = Text()
        text.append("● ", style=f"bold {theme.logo_color}")
        text.append(theme.name, style=f"{theme.accent}")
        text.append(" ● ", style=f"{theme.secondary}")

        self.update(text)

    def cycle_theme(self) -> None:
        """Cycle to next theme."""
        themes = list(THEMES.keys())
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.current_theme = themes[next_index]


class ModelInfo(Static):
    """Display current model information with theme colors."""

    current_theme: reactive[str] = reactive("cyan_matrix")

    def on_mount(self) -> None:
        """Set model info when mounted."""
        self.update_display()

    def watch_current_theme(self, theme_name: str) -> None:
        """Update colors when theme changes."""
        self.update_display()

    def update_display(self) -> None:
        """Update model info with theme colors."""
        theme = THEMES.get(self.current_theme, THEMES["cyan_matrix"])

        model_text = Text("Build", style=f"bold {theme.accent}")
        model_text.append("  Llama 3 2 3b ", style="white")
        model_text.append("Ollama (local)", style="dim white")

        self.update(Align.center(model_text))


class TipSection(Static):
    """Display rotating helpful tips."""

    TIPS = [
        "Use irir run for non-interactive scripting",
        "Press Ctrl+P to open command palette",
        "Tab to switch between agents",
        "Ctrl+N to start a new chat",
        "Ctrl+S to save conversation",
        "Press / to search conversations",
        "Use @ to mention files or context",
        "Ctrl+T to change themes",
        "F1 for help and documentation",
        "Ctrl+K for keyboard shortcuts",
    ]

    current_theme: reactive[str] = reactive("cyan_matrix")
    current_tip_index: int = 0

    def on_mount(self) -> None:
        """Set tip when mounted."""
        self.update_tip()
        # Rotate tip every 10 seconds
        self.set_interval(10, self.rotate_tip)

    def watch_current_theme(self, theme_name: str) -> None:
        """Update colors when theme changes."""
        self.update_tip()

    def update_tip(self) -> None:
        """Update tip display."""
        theme = THEMES.get(self.current_theme, THEMES["cyan_matrix"])
        tip = self.TIPS[self.current_tip_index]

        tip_text = Text("● ", style=f"bold {theme.secondary}")
        tip_text.append("Tip", style=f"bold {theme.secondary}")
        tip_text.append(" ", style="")
        tip_text.append(tip, style="dim white")

        self.update(Align.center(tip_text))

    def rotate_tip(self) -> None:
        """Rotate to next tip."""
        self.current_tip_index = (self.current_tip_index + 1) % len(self.TIPS)
        self.update_tip()


class AnimatedLogo(Static):
    """IRIR logo with subtle animation."""

    frame: int = 0

    def on_mount(self) -> None:
        """Start animation."""
        self.set_interval(0.5, self.animate)

    def animate(self) -> None:
        """Animate the logo."""
        self.frame = (self.frame + 1) % 4

        # Pulsing effect with different intensities
        styles = ["cyan", "bright_cyan", "bold bright_cyan", "bright_cyan"]
        current_style = styles[self.frame]

        logo = """
██╗██████╗ ██╗██████╗ 
██║██╔══██╗██║██╔══██╗
██║██████╔╝██║██████╔╝
██║██╔══██╗██║██╔══██╗
██║██║  ██║██║██║  ██║
╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""
        text = Text(logo, justify="center")
        text.stylize(current_style)
        self.update(text)


__all__ = [
    "WelcomeScreen",
    "EnhancedLogo",
    "GradientLogo",
    "NeonLogo",
    "MinimalistLogo",
    "AnimatedLogo",
    "SmartInputSection",
    "ThemeSelector",
    "ModelInfo",
    "TipSection",
    "THEMES",
    "CUSTOM_PROMPTS",
]
