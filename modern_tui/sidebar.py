"""
Sidebar — irir
===============

Neon-plasma sidebar with:
- Live pulse indicator (heartbeat dot)
- Animated context usage bar
- Model info badge
- Clean shortcut table
- Subtle scanline texture via Unicode
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

from .progress import PureProgressBar, ProgressStyle


# ── Heartbeat pulse ────────────────────────────────────────────────────────────

class PulseDot(Static):
    """Tiny beating dot that shows the app is alive."""

    _frame: reactive[int] = reactive(0)

    FRAMES = [
        ("◉", "#ff2d78"),
        ("◉", "#ff5294"),
        ("○", "#441122"),
        ("○", "#221111"),
    ]

    def on_mount(self) -> None:
        self.set_interval(0.45, self._beat)
        self._render()

    def _beat(self) -> None:
        self._frame = (self._frame + 1) % len(self.FRAMES)
        self._render()

    def _render(self) -> None:
        ch, col = self.FRAMES[self._frame]
        self.update(Text(ch, style=f"bold {col}"))


# ── Section header ─────────────────────────────────────────────────────────────

def _section(label: str) -> Static:
    text = Text()
    text.append("▸ ", style="bold #a64dff")
    text.append(label.upper(), style="bold #667799")
    return Static(text, classes="sb-section-head")


# ── Context metrics ────────────────────────────────────────────────────────────

class ContextMetrics(Static):
    """Token usage with animated neon bar."""

    tokens_used: reactive[int] = reactive(0)
    tokens_total: reactive[int] = reactive(100_000)
    cost_spent: reactive[float] = reactive(0.0)

    def on_mount(self) -> None:
        self._render()

    def watch_tokens_used(self, _: int) -> None:
        self._render()

    def watch_cost_spent(self, _: float) -> None:
        self._render()

    def _render(self) -> None:
        pct = self.tokens_used / max(1, self.tokens_total)

        # Pick bar colour based on usage
        if pct < 0.5:
            bar_start, bar_end = "#00e5ff", "#a64dff"
        elif pct < 0.8:
            bar_start, bar_end = "#ffbb00", "#ff8800"
        else:
            bar_start, bar_end = "#ff4400", "#ff2d78"

        style = ProgressStyle(
            start_color=bar_start,
            end_color=bar_end,
            background_color="#0d0d1f",
            show_percentage=False,
            horizontal_padding=0,
            max_width=28,
        )

        bar_text = PureProgressBar(style=style).render(pct)

        text = Text()
        text.append(f"{self.tokens_used:,}", style="bold #00e5ff")
        text.append(" / ", style="dim #445566")
        text.append(f"{self.tokens_total:,}", style="dim #667799")
        text.append(" tokens\n", style="dim #445566")
        text.append_text(bar_text)
        text.append("\n")
        text.append(f"${self.cost_spent:.4f}", style="bold #39ff6e")
        text.append(" spent", style="dim #445566")

        self.update(text)


# ── LSP status ─────────────────────────────────────────────────────────────────

class LSPStatus(Static):
    """LSP readiness indicator."""

    status: reactive[str] = reactive("waiting for files…")

    def on_mount(self) -> None:
        self._render()

    def watch_status(self, _: str) -> None:
        self._render()

    def _render(self) -> None:
        text = Text()
        if "active" in self.status.lower() or "●" in self.status:
            text.append("● ", style="bold #39ff6e")
        else:
            text.append("○ ", style="dim #334455")
        text.append(self.status, style="dim #667799")
        self.update(text)


# ── Model badge ────────────────────────────────────────────────────────────────

class ModelBadge(Static):
    """Currently active model name."""

    model_name: reactive[str] = reactive("llama3")

    def on_mount(self) -> None:
        self._render()

    def watch_model_name(self, _: str) -> None:
        self._render()

    def _render(self) -> None:
        text = Text()
        text.append("  ", style="")
        text.append(f" {self.model_name} ", style="bold #00e5ff on #001122")
        text.append("  ollama", style="dim #445566")
        self.update(text)


# ── Shortcuts ──────────────────────────────────────────────────────────────────

class ShortcutsTable(Static):
    """Keyboard shortcuts in a clean two-column layout."""

    SHORTCUTS = [
        ("ctrl+p", "command palette"),
        ("tab", "agents panel"),
        ("ctrl+n", "new chat"),
        ("ctrl+f", "search convs"),
        ("/", "slash commands"),
        ("esc", "interrupt"),
        ("ctrl+x e", "external editor"),
    ]

    def on_mount(self) -> None:
        text = Text()
        for key, action in self.SHORTCUTS:
            text.append(f"  {key:<12}", style="bold #a64dff")
            text.append(f"{action}\n", style="dim #667799")
        self.update(text)


# ── Sidebar header ─────────────────────────────────────────────────────────────

class SidebarHeader(Static):
    """irir wordmark + pulse dot."""

    def on_mount(self) -> None:
        text = Text(justify="center")
        text.append("i", style="bold #ff2d78")
        text.append("r", style="bold #a64dff")
        text.append("i", style="bold #00e5ff")
        text.append("r", style="bold #39ff6e")
        self.update(Align.center(text))


# ── Main sidebar ───────────────────────────────────────────────────────────────

class Sidebar(Container):
    """Full neon sidebar widget."""

    DEFAULT_CSS = """
    Sidebar {
        width: 28;
        height: 100%;
        background: #07071a;
        border-left: solid #1a0a2e;
        padding: 1 1;
    }

    Sidebar.hidden {
        display: none;
    }

    #sb-inner {
        width: 100%;
        height: 100%;
    }

    .sb-section-head {
        margin: 1 0 0 0;
        height: 1;
    }

    .sb-sep {
        height: 1;
        color: #1a0a2e;
    }

    #sb-title-row {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        align: center middle;
    }

    #sb-pulse {
        width: 1;
        height: 1;
        margin: 0 1 0 0;
    }

    #sb-wordmark {
        width: 1fr;
        height: 1;
    }

    ContextMetrics {
        margin: 1 0 0 1;
    }

    LSPStatus {
        margin: 1 0 0 1;
    }

    ModelBadge {
        margin: 1 0 0 0;
    }

    ShortcutsTable {
        margin: 1 0 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="sb-inner"):
            # Header row: pulse dot + wordmark
            with Container(id="sb-title-row"):
                yield PulseDot(id="sb-pulse")
                yield SidebarHeader(id="sb-wordmark")

            yield Static("─" * 26, classes="sb-sep")

            yield _section("model")
            yield ModelBadge()

            yield _section("context")
            yield ContextMetrics()

            yield _section("lsp")
            yield LSPStatus()

            yield _section("keys")
            yield ShortcutsTable()


# ── Detailed variant (same but wider) ─────────────────────────────────────────

class DetailedSidebar(Sidebar):
    DEFAULT_CSS = Sidebar.DEFAULT_CSS.replace("width: 28;", "width: 38;")


__all__ = [
    "Sidebar",
    "DetailedSidebar",
    "SidebarHeader",
    "ContextMetrics",
    "LSPStatus",
    "ModelBadge",
    "ShortcutsTable",
    "PulseDot",
]