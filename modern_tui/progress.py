"""Reusable progress-bar components for terminal TUIs.

This module provides two drop-in progress bar modes:

1) AnimatedProgressBar (stateful):
   - Keeps internal state.
   - Supports fixed-step increments (default 25%).
   - Supports timer-driven increments (default 1s interval).
   - Smoothly animates displayed progress toward target progress.

2) PureProgressBar (stateless):
   - Rendering only; accepts an external progress float each call.
   - Deterministic and side-effect free.

Both modes support configurable color gradients (hex or RGB), dynamic terminal
width handling, and a maximum render width of 80 characters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from shutil import get_terminal_size
import time
from typing import Callable, Optional, Tuple

from rich.text import Text

RGB = Tuple[int, int, int]


def clamp01(value: float) -> float:
    """Clamp a float into [0.0, 1.0]."""
    return max(0.0, min(1.0, float(value)))


def rgb_to_hex(rgb: RGB) -> str:
    """Convert an (r, g, b) tuple to '#RRGGBB'."""
    r, g, b = rgb
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def hex_to_rgb(color: str) -> RGB:
    """Parse '#RGB' or '#RRGGBB' into an (r, g, b) tuple."""
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError(f"Invalid hex color: {color!r}")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _interpolate_rgb(start: RGB, end: RGB, t: float) -> RGB:
    """Linear interpolation between two RGB colors."""
    t = clamp01(t)
    return (
        int(start[0] + (end[0] - start[0]) * t),
        int(start[1] + (end[1] - start[1]) * t),
        int(start[2] + (end[2] - start[2]) * t),
    )


@dataclass
class ProgressStyle:
    """Visual configuration used by both progress bar modes."""

    start_color: str = "#ff3333"
    end_color: str = "#ffffff"
    background_color: str = "#1a1a1a"
    label_style: str = "bold white"
    muted_label_style: str = "dim white"
    show_percentage: bool = True
    hint: Optional[str] = None
    max_width: int = 80
    horizontal_padding: int = 2


@dataclass
class PureProgressBar:
    """Stateless progress-bar renderer.

    The containing app controls the progress value; this class only renders.
    """

    style: ProgressStyle = field(default_factory=ProgressStyle)

    def render(self, progress: float) -> Text:
        """Render the bar from an external progress value (0.0 -> 1.0)."""
        p = clamp01(progress)
        width = self._compute_bar_width()
        filled = int(round(p * width))

        start_rgb = hex_to_rgb(self.style.start_color)
        end_rgb = hex_to_rgb(self.style.end_color)

        # Build a gradient-colored filled segment and muted unfilled segment.
        bar = Text()
        for i in range(width):
            if i < filled:
                t = i / max(1, width - 1)
                color = rgb_to_hex(_interpolate_rgb(start_rgb, end_rgb, t))
                bar.append("█", style=f"{color}")
            else:
                bar.append("░", style=self.style.background_color)

        left_pad = " " * self.style.horizontal_padding
        right_pad = " " * self.style.horizontal_padding
        out = Text(left_pad)
        out.append("[")
        out.append_text(bar)
        out.append("]")

        if self.style.show_percentage:
            out.append(f" {int(round(p * 100)):3d}%", style=self.style.label_style)

        if self.style.hint:
            out.append(f"  {self.style.hint}", style=self.style.muted_label_style)

        out.append(right_pad)
        return out

    def _compute_bar_width(self) -> int:
        terminal_cols = min(get_terminal_size(fallback=(120, 24)).columns, self.style.max_width)
        reserved = 2 + (8 if self.style.show_percentage else 0) + (len(self.style.hint or "") + 2 if self.style.hint else 0)
        width = terminal_cols - reserved - (2 * self.style.horizontal_padding)
        return max(10, width)


@dataclass
class AnimatedProgressBar:
    """Stateful progress bar with smooth animation toward target progress.

    Progress flow:
    - `update()` sets a target value.
    - `incr()` increments the target by a delta.
    - `tick()` advances displayed progress smoothly toward the target.

    Animation logic:
    - Displayed value eases toward target at `animation_speed` per second.
    - Optional timer-driven updates (`timer_enabled`) can auto-increment target
      by `step` at every `interval_seconds`.

    Completion behavior:
    - When target reaches 1.0, completion is signaled once via callback.
    """

    style: ProgressStyle = field(default_factory=ProgressStyle)
    step: float = 0.25
    interval_seconds: float = 1.0
    animation_speed: float = 1.5
    timer_enabled: bool = False
    on_complete: Optional[Callable[[], None]] = None

    _target_progress: float = 0.0
    _display_progress: float = 0.0
    _last_tick: float = field(default_factory=time.monotonic)
    _last_timer_fire: float = field(default_factory=time.monotonic)
    _completed_notified: bool = False

    @property
    def progress(self) -> float:
        """Current displayed/animated progress."""
        return self._display_progress

    @property
    def target(self) -> float:
        """Current target progress set by external updates."""
        return self._target_progress

    def update(self, progress: float) -> None:
        """Set absolute target progress (0.0 -> 1.0)."""
        self._target_progress = clamp01(progress)
        self._check_completion_target()

    def incr(self, delta: Optional[float] = None) -> None:
        """Increment target progress by delta (default: configured step)."""
        d = self.step if delta is None else float(delta)
        self.update(self._target_progress + d)

    def tick(self) -> None:
        """Advance animation and optional timer-driven updates.

        Call this from your TUI refresh/update loop (e.g., every frame/timer).
        """
        now = time.monotonic()
        dt = max(0.0, now - self._last_tick)
        self._last_tick = now

        if self.timer_enabled and now - self._last_timer_fire >= self.interval_seconds:
            self._last_timer_fire = now
            if self._target_progress < 1.0:
                self.incr(self.step)

        if self._display_progress < self._target_progress:
            # Smoothly move displayed progress toward target.
            self._display_progress = min(
                self._target_progress,
                self._display_progress + (self.animation_speed * dt),
            )

        self._check_completion_displayed()

    def render(self) -> Text:
        """Render using current animated/displayed progress."""
        return PureProgressBar(style=self.style).render(self._display_progress)

    def is_complete(self) -> bool:
        return self._display_progress >= 1.0 and self._target_progress >= 1.0

    def _check_completion_target(self) -> None:
        if self._target_progress >= 1.0 and self.on_complete and not self._completed_notified:
            # We notify on *target* completion so parent TUIs can transition fast.
            self._completed_notified = True
            self.on_complete()

    def _check_completion_displayed(self) -> None:
        if self._display_progress >= 1.0:
            self._display_progress = 1.0


__all__ = [
    "AnimatedProgressBar",
    "PureProgressBar",
    "ProgressStyle",
    "clamp01",
    "hex_to_rgb",
    "rgb_to_hex",
]
