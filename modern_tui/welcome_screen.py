"""
Welcome Screen Component for IRIR
==================================

Beautiful OpenCode-style welcome screen that appears when user clicks Chat tab.
Features:
- Large IRIR logo
- Prompt input with placeholder
- Model selector
- Tips section
- Smooth animations
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Input
from rich.text import Text
from rich.align import Align


class WelcomeScreen(Container):
    """OpenCode-style welcome screen with logo and input."""

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
    """

    def compose(self) -> ComposeResult:
        """Compose the welcome screen layout."""
        with Vertical(id="welcome-container"):
            yield Logo(id="logo")
            yield InputSection()
            yield ModelInfo(id="model-info")
            yield TipSection(id="tip-section")


class Logo(Static):
    """Large IRIR logo in ASCII art style."""

    def on_mount(self) -> None:
        """Create the logo when mounted."""
        logo_text = self._create_logo()
        self.update(logo_text)

    def _create_logo(self) -> Text:
        """Create the IRIR logo with styling."""
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
        return text


class InputSection(Container):
    """Input section with placeholder."""

    DEFAULT_CSS = """
    InputSection {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose input section."""
        with Container(id="input-container"):
            yield Input(
                placeholder='Ask anything... "What is the tech stack of this project?"',
                id="welcome-input",
            )


class ModelInfo(Static):
    """Display current model information."""

    def on_mount(self) -> None:
        """Set model info when mounted."""
        model_text = Text("Build", style="bold blue")
        model_text.append("  Llama 3 2 3b ", style="white")
        model_text.append("Ollama (local)", style="dim white")

        self.update(Align.center(model_text))


class TipSection(Static):
    """Display helpful tips."""

    def on_mount(self) -> None:
        """Set tip when mounted."""
        tip_text = Text("● ", style="bold yellow")
        tip_text.append("Tip", style="bold yellow")
        tip_text.append(" Use ", style="dim white")
        tip_text.append("irir run", style="bold white")
        tip_text.append(" for non-interactive scripting", style="dim white")

        self.update(Align.center(tip_text))


class MinimalistLogo(Static):
    """Minimalist IRIR logo with large text."""

    DEFAULT_CSS = """
    MinimalistLogo {
        width: 100%;
        height: 5;
        content-align: center middle;
        margin: 3 0;
    }
    """

    def on_mount(self) -> None:
        """Create minimalist logo."""
        logo = "░▒▓ irir ▓▒░"
        text = Text(logo, style="bold cyan", justify="center")
        text.stylize("bold", 4, 8)
        self.update(text)


class GradientLogo(Static):
    """IRIR logo with gradient effect."""

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

        colors = ["cyan", "bright_cyan", "blue", "bright_blue", "blue", "cyan"]

        text = Text()
        for line, color in zip(logo_lines, colors):
            text.append(line + "\n", style=f"bold {color}")

        self.update(Align.center(text))


__all__ = [
    "WelcomeScreen",
    "Logo",
    "MinimalistLogo",
    "GradientLogo",
    "InputSection",
    "ModelInfo",
    "TipSection",
]
