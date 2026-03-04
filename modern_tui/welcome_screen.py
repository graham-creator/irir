"""
Welcome Screen — irir
======================
opencode-inspired dark terminal home tab:
  - Minimal full-bleed dark canvas
  - Large animated ASCII wordmark with plasma colour sweep
  - Input that glows on focus
  - Rotating ghost prompts
  - No header, no footer — pure terminal
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align


LOGO = [
    " ██╗██████╗ ██╗██████╗ ",
    " ██║██╔══██╗██║██╔══██╗",
    " ██║██████╔╝██║██████╔╝",
    " ██║██╔══██╗██║██╔══██╗",
    " ██║██║  ██║██║██║  ██║",
    " ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝",
]

PALETTES = [
    ["#ff2d78", "#d964a8", "#b04dd8", "#7b2fff", "#5465ff", "#00e5ff"],
    ["#00e5ff", "#00d4cc", "#00c299", "#39ff6e", "#8fff3a", "#c8ff00"],
    ["#c8ff00", "#ffdd00", "#ffaa00", "#ff6600", "#ff3300", "#ff2d78"],
    ["#a64dff", "#7b2fff", "#4466ff", "#00aaff", "#00e5ff", "#39ff6e"],
]

PROMPTS = [
    "What models do you have pulled?",
    "Summarise this codebase for me…",
    "Compare llama3 vs mistral on this task…",
    "Best architecture for this feature?",
    "Explain this error and fix it…",
    "Generate tests for my module…",
    "Refactor this into cleaner style…",
    "What are the trade-offs here?",
    "Help me debug this async issue…",
    "Write a git commit message for these changes…",
]


class LogoDisplay(Static):
    """Plasma-animated wordmark."""

    _frame: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(1.8, self._next_frame)
        self._draw()

    def _next_frame(self) -> None:
        self._frame = (self._frame + 1) % len(PALETTES)
        self._draw()

    def _draw(self) -> None:
        palette = PALETTES[self._frame]
        text = Text(justify="center")
        for i, line in enumerate(LOGO):
            col = palette[i % len(palette)]
            text.append(line + "\n", style=f"bold {col}")
        self.update(Align.center(text))


class PulseDots(Static):
    """Three dots that breathe in sequence."""

    _tick: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(0.5, self._beat)
        self._draw()

    def _beat(self) -> None:
        self._tick = (self._tick + 1) % 6
        self._draw()

    def _draw(self) -> None:
        colors = ["#ff2d78", "#a64dff", "#00e5ff"]
        t = self._tick
        parts = []
        for i, c in enumerate(colors):
            bright = (t % 3) == i
            parts.append(f"[bold {c}]●[/]" if bright else "[#1a1a33]●[/]")
        self.update(Align.center(Text.from_markup("   ".join(parts))))


class GhostPrompt(Static):
    """Cycles placeholder text on the input."""

    _idx: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(3.5, self._rotate)

    def _rotate(self) -> None:
        self._idx = (self._idx + 1) % len(PROMPTS)
        try:
            inp = self.app.query_one("#welcome-input", Input)
            inp.placeholder = PROMPTS[self._idx]
        except Exception:
            pass


class ModelTag(Static):
    """Inline model pill."""

    def on_mount(self) -> None:
        try:
            from modern_tui import workers
            models = workers.list_models()
            name = models[0].get("name", "llama3") if models else "no model"
        except Exception:
            name = "ollama"

        t = Text(justify="center")
        t.append("◆ ", style="#a64dff")
        t.append(f"{name}", style="bold #c8d0e8")
        t.append("  via ollama", style="dim #334455")
        self.update(Align.center(t))


class WelcomeScreen(Container):
    """Full-bleed opencode-style home tab."""

    DEFAULT_CSS = """
    WelcomeScreen {
        width: 100%;
        height: 100%;
        background: #060610;
        align: center middle;
        overflow: hidden;
    }

    #wc-col {
        width: 66;
        height: auto;
        align: center middle;
    }

    #wc-logo {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
    }

    #wc-divider {
        width: 100%;
        height: 1;
        margin: 0 0 1 0;
    }

    #wc-dots {
        width: 100%;
        height: 1;
        margin: 0 0 2 0;
    }

    #wc-model {
        width: 100%;
        height: 1;
        margin: 0 0 3 0;
    }

    #wc-input-wrap {
        width: 100%;
        height: auto;
        background: #0c0c20;
        border: tall #1c1c38;
        padding: 0 2;
        margin: 0 0 2 0;
    }

    #wc-input-wrap:focus-within {
        border: tall #a64dff;
        background: #0f0f26;
    }

    #welcome-input {
        width: 100%;
        background: transparent;
        color: #d0d8f0;
        border: none;
    }

    #wc-hints {
        width: 100%;
        height: 1;
    }

    #wc-hint-l {
        width: 1fr;
        color: #1e1e3a;
    }

    #wc-hint-r {
        width: auto;
        color: #1e1e3a;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="wc-col"):
            with Container(id="wc-logo"):
                yield LogoDisplay()
            yield Static(
                Align.center(Text.from_markup(
                    "[#171730]" + "─" * 50 + "[/]"
                )),
                id="wc-divider",
            )
            with Container(id="wc-dots"):
                yield PulseDots()
            with Container(id="wc-model"):
                yield ModelTag()
            with Container(id="wc-input-wrap"):
                yield Input(
                    placeholder=PROMPTS[0],
                    id="welcome-input",
                )
                yield GhostPrompt()
            with Horizontal(id="wc-hints"):
                yield Static(
                    "  [#2a2a50]ctrl+p[/] palette"
                    "   [#2a2a50]tab[/] agents"
                    "   [#2a2a50]ctrl+n[/] new chat",
                    id="wc-hint-l",
                    markup=True,
                )
                yield Static(
                    "/ slash cmds   [#2a2a50]esc[/] stop  ",
                    id="wc-hint-r",
                    markup=True,
                )


__all__ = ["WelcomeScreen"]