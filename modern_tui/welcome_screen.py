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
        background: #0b0b0b;
        align: center middle;
    }

    #welcome-container {
        width: 60;
        height: auto;
        align: center middle;
    }

    #logo {
        width: 60;
        height: auto;
        content-align: center middle;
        margin: 1 0 2 0;
    }

    #input-container {
        width: 60;
        height: auto;
        background: #151515;
        border: solid #1e1e1e;
        padding: 1 2;
        margin: 2 0 2 0;
    }

    #welcome-input {
        width: 100%;
        background: transparent;
        border: none;
        color: #e6e6e6;
    }

    #model-info {
        width: 60;
        height: auto;
        content-align: center middle;
        margin: 2 0 1 0;
    }

    #tip-section {
        width: 60;
        height: auto;
        content-align: center middle;
        margin: 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the welcome screen layout."""
        with Vertical(id="welcome-container"):
            # Logo
            yield Static(self._render_logo(), id="logo")
            # Input section
            with Container(id="input-container"):
                yield Input(
                    placeholder='Ask anything... "Fix broken tests"',
                    id="welcome-input",
                )
            # Model info
            yield Static(self._render_model_info(), id="model-info")
            # Tip section
            yield Static(self._render_tip(), id="tip-section")

    def _render_logo(self) -> Text:
        """Render the logo."""
        logo_lines = [
            "",
            "  ██╗██╗██╗██╗██╗",
            "  ██║██║██║██║██║",
            "  ██║██║██║██║██║",
            "  ██║██║██║██║██║",
            "  ╚═╝╚═╝╚═╝╚═╝╚═╝",
            "",
        ]
        text = Text()
        for line in logo_lines:
            text.append(line + "\n", style="bold #00d7ff")
        return text

    def _render_model_info(self) -> Text:
        """Render model info."""
        text = Text()
        text.append("Build", style="bold #7aa2f7")
        text.append("  Llama 3 2 3b  ", style="#ffffff")
        text.append("Ollama (local)", style="dim #cccccc")
        text.justify = "center"
        return text

    def _render_tip(self) -> Text:
        """Render tip section."""
        text = Text()
        text.append("● ", style="bold #f2a65a")
        text.append("Tip", style="bold #f2a65a")
        text.append(" Use ", style="dim #cccccc")
        text.append("irir run", style="bold #ffffff")
        text.append(" for non-interactive scripting", style="dim #cccccc")
        text.justify = "center"
        return text


class Logo(Static):
    """Large IRIR logo in ASCII art style."""

    DEFAULT_CSS = """
    Logo {
        width: 100%;
        height: 8;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        """Create the logo when mounted."""
        logo_text = self._create_logo()
        self.update(logo_text)

    def _create_logo(self) -> Text:
        """Create a large, prominent IRIR logo."""
        # Large blocky ASCII art logo
        logo_lines = [
            "",
            "  ██╗██╗██╗██╗██╗",
            "  ██║██║██║██║██║",
            "  ██║██║██║██║██║",
            "  ██║██║██║██║██║",
            "  ╚═╝╚═╝╚═╝╚═╝╚═╝",
            "",
        ]
        text = Text()
        for line in logo_lines:
            text.append(line + "\n", style="bold #00d7ff")  # Bright cyan
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
                placeholder='Ask anything... "Fix broken tests"',
                id="welcome-input",
            )


class ModelInfo(Static):
    """Display current model information."""

    DEFAULT_CSS = """
    ModelInfo {
        width: 100%;
        height: auto;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        """Set model info when mounted."""
        model_text = Text()
        model_text.append("Build", style="bold #7aa2f7")
        model_text.append("  Llama 3 2 3b ", style="#ffffff")
        model_text.append("Ollama (local)", style="dim #cccccc")

        self.update(Align.center(model_text))


class TipSection(Static):
    """Display helpful tips."""

    DEFAULT_CSS = """
    TipSection {
        width: 100%;
        height: auto;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        """Set tip when mounted."""
        tip_text = Text()
        tip_text.append("● ", style="bold #f2a65a")
        tip_text.append("Tip", style="bold #f2a65a")
        tip_text.append(" Use ", style="dim #cccccc")
        tip_text.append("irir run", style="bold #ffffff")
        tip_text.append(" for non-interactive scripting", style="dim #cccccc")

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
