"""
Welcome Screen — irir
======================

Custom animated welcome screen with:
- Plasma-pulse ASCII logo with colour cycling
- Rotating prompts that feel alive
- Glassmorphism input container
- Animated status dots
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align
import random


# ── Logo frames for pseudo-animation ──────────────────────────────────────────

LOGO_LINES = [
    "  ██╗██████╗ ██╗██████╗  ",
    "  ██║██╔══██╗██║██╔══██╗ ",
    "  ██║██████╔╝██║██████╔╝ ",
    "  ██║██╔══██╗██║██╔══██╗ ",
    "  ██║██║  ██║██║██║  ██║ ",
    "  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ",
]

# Plasma colour ramp — cycles through hot magenta → electric lime → cyan
PLASMA_FRAMES = [
    ["#ff2d78", "#ff5294", "#ff78b0", "#ffadd1", "#d475ff", "#a64dff"],
    ["#d475ff", "#a64dff", "#7b2fff", "#5b8fff", "#2dc4ff", "#00e5ff"],
    ["#00e5ff", "#00ffcc", "#00ff99", "#39ff6e", "#7fff3a", "#c8ff00"],
    ["#c8ff00", "#ffee00", "#ffbb00", "#ff8800", "#ff4400", "#ff2d78"],
]

PROMPTS = [
    "What models do you have pulled?",
    "Summarise this YouTube video for me…",
    "Compare llama3 vs mistral on this question…",
    "What's the best way to structure this project?",
    "Explain this error and how to fix it…",
    "Generate unit tests for my function…",
    "Rewrite this in a cleaner style…",
    "What are the trade-offs here?",
]


class LogoDisplay(Static):
    """Animated plasma logo — colour palette cycles every 1.5 s."""

    _frame: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(1.5, self._next_frame)
        self._render_logo()

    def _next_frame(self) -> None:
        self._frame = (self._frame + 1) % len(PLASMA_FRAMES)
        self._render_logo()

    def _render_logo(self) -> None:
        palette = PLASMA_FRAMES[self._frame]
        text = Text(justify="center")
        for i, line in enumerate(LOGO_LINES):
            colour = palette[i % len(palette)]
            text.append(line + "\n", style=f"bold {colour}")
        self.update(Align.center(text))


class StatusDots(Static):
    """Three pulsing dots that indicate readiness."""

    _tick: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(0.55, self._pulse)
        self._render()

    def _pulse(self) -> None:
        self._tick = (self._tick + 1) % 4
        self._render()

    def _render(self) -> None:
        t = self._tick
        dots = []
        colors = ["#ff2d78", "#a64dff", "#00e5ff"]
        for i, c in enumerate(colors):
            if i == t % 3:
                dots.append(f"[bold {c}]●[/]")
            else:
                dots.append("[dim #333355]●[/]")
        self.update(Align.center(Text.from_markup("  ".join(dots))))


class RotatingPrompt(Static):
    """Placeholder that cycles through example prompts every 4 s."""

    _idx: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(4.0, self._rotate)

    def _rotate(self) -> None:
        self._idx = (self._idx + 1) % len(PROMPTS)
        try:
            inp = self.app.query_one("#welcome-input", Input)
            inp.placeholder = PROMPTS[self._idx]
        except Exception:
            pass


class ModelBadge(Static):
    """Glowing model name badge."""

    def on_mount(self) -> None:
        try:
            from modern_tui import workers
            models = workers.list_models()
            if models:
                name = models[0].get("name", "llama3")
            else:
                name = "no model"
        except Exception:
            name = "ollama"

        text = Text(justify="center")
        text.append("  running  ", style="dim #445566")
        text.append(f" {name} ", style="bold #00e5ff on #001122")
        text.append("  via ollama  ", style="dim #445566")
        self.update(Align.center(text))


class WelcomeScreen(Container):
    """Full welcome screen — shown when chat is empty."""

    DEFAULT_CSS = """
    WelcomeScreen {
        width: 100%;
        height: 100%;
        background: #05050f;
        align: center middle;
    }

    #wc-shell {
        width: 72;
        height: auto;
        align: center middle;
    }

    #logo-wrap {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
    }

    #dots-wrap {
        width: 100%;
        height: 1;
        margin: 0 0 2 0;
    }

    #badge-wrap {
        width: 100%;
        height: auto;
        margin: 0 0 2 0;
    }

    #input-shell {
        width: 100%;
        height: auto;
        background: #0d0d1f;
        border: tall #2a1a4a;
        padding: 1 2;
        margin: 0 0 2 0;
    }

    #input-shell:focus-within {
        border: tall #a64dff;
    }

    #welcome-input {
        width: 100%;
        background: #0d0d1f;
        color: #e8e8ff;
        border: none;
    }

    #hint-row {
        width: 100%;
        height: auto;
    }

    #hint-left {
        width: 1fr;
        height: auto;
        color: #334455;
    }

    #hint-right {
        width: auto;
        height: auto;
        color: #334455;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="wc-shell"):
            with Container(id="logo-wrap"):
                yield LogoDisplay()
            with Container(id="dots-wrap"):
                yield StatusDots()
            with Container(id="badge-wrap"):
                yield ModelBadge()
            with Container(id="input-shell"):
                yield Input(
                    placeholder=PROMPTS[0],
                    id="welcome-input",
                )
                yield RotatingPrompt()
            with Horizontal(id="hint-row"):
                yield Static(
                    "  [dim]ctrl+p[/] commands   [dim]tab[/] agents   [dim]esc[/] interrupt",
                    id="hint-left",
                    markup=True,
                )
                yield Static(
                    "[dim]/ slash cmds[/]  ",
                    id="hint-right",
                    markup=True,
                )


__all__ = ["WelcomeScreen"]