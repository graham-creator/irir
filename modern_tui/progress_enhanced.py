"""Enhanced progress bar components with all Bubbles-inspired features.

This module provides highly customizable, physics-based progress bars with:
- Spring-based animation
- Gradient scaling modes
- Perceptual color interpolation
- Frame tagging for race condition prevention
- Equilibrium detection
- Theme system
- Multi-bar support
- State serialization
- And much more!

Based on charmbracelet/bubbles progress component with Python adaptations.
"""

from __future__ import annotations

import json
import shutil
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from itertools import count
from typing import Callable, Optional, Tuple, Dict, Any

from rich.text import Text

# Type aliases
RGB = Tuple[int, int, int]
ColorFormatter = Callable[[float], str]

# Thread-safe ID generation
_id_generator = count(1)
_id_lock = threading.Lock()


def next_id() -> int:
    """Thread-safe unique ID generation for progress bar instances."""
    with _id_lock:
        return next(_id_generator)


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


def interpolate_rgb(start: RGB, end: RGB, t: float) -> RGB:
    """Linear interpolation between two RGB colors."""
    t = clamp01(t)
    return (
        int(start[0] + (end[0] - start[0]) * t),
        int(start[1] + (end[1] - start[1]) * t),
        int(start[2] + (end[2] - start[2]) * t),
    )


def interpolate_rgb_perceptual(start: RGB, end: RGB, t: float) -> RGB:
    """Perceptually uniform interpolation using simple luminance-weighted RGB.

    For true perceptual uniformity, use Lab/Luv color space.
    This is a good approximation that doesn't require external dependencies.
    """
    t = clamp01(t)

    # Convert to linear RGB for perceptual interpolation
    def gamma_expand(c: int) -> float:
        c_norm = c / 255.0
        if c_norm <= 0.04045:
            return c_norm / 12.92
        return ((c_norm + 0.055) / 1.055) ** 2.4

    def gamma_compress(linear: float) -> int:
        if linear <= 0.0031308:
            return int(linear * 12.92 * 255)
        return int(((1.055 * (linear ** (1 / 2.4))) - 0.055) * 255)

    # Expand to linear space
    start_linear = tuple(gamma_expand(c) for c in start)
    end_linear = tuple(gamma_expand(c) for c in end)

    # Interpolate in linear space
    mid_linear = tuple(
        start_linear[i] + (end_linear[i] - start_linear[i]) * t
        for i in range(3)
    )

    # Compress back to sRGB
    return tuple(gamma_compress(c) for c in mid_linear)


class ProgressState(Enum):
    """Progress bar state machine."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class ColorProfile(Enum):
    """Terminal color capability levels."""

    ASCII = 0  # No colors
    ANSI = 1  # 16 colors
    ANSI256 = 2  # 256 colors
    TRUE_COLOR = 3  # 16M colors


class Spring:
    """Simple spring physics for smooth animations.

    Based on semi-implicit Euler integration.
    Frequency controls speed, damping controls bounciness.
    """

    def __init__(self, fps: int, frequency: float, damping: float):
        """Initialize spring with physics parameters.

        Args:
            fps: Target frames per second
            frequency: Spring stiffness (higher = faster)
            damping: Energy loss (higher = less bouncy)
        """
        self.fps = fps
        self.frequency = frequency
        self.damping = damping
        self.dt = 1.0 / fps

    def update(self, position: float, velocity: float, target: float) -> Tuple[float, float]:
        """Update spring physics simulation.

        Args:
            position: Current position
            velocity: Current velocity
            target: Target position

        Returns:
            Tuple of (new_position, new_velocity)
        """
        # Spring force (Hooke's law)
        force = (target - position) * self.frequency

        # Damping force
        damping_force = -velocity * self.damping

        # Total acceleration
        acceleration = force + damping_force

        # Semi-implicit Euler integration
        velocity += acceleration * self.dt
        position += velocity * self.dt

        return position, velocity


# Character sets for different visual styles
PROGRESS_STYLES = {
    "blocks": {"full": "█", "empty": "░"},
    "dots": {"full": "●", "empty": "○"},
    "arrows": {"full": "▶", "empty": "▷"},
    "lines": {"full": "━", "empty": "─"},
    "squares": {"full": "■", "empty": "□"},
    "circles": {"full": "◉", "empty": "◯"},
    "ascii": {"full": "#", "empty": "-"},
    "equals": {"full": "=", "empty": " "},
}

# Partial block characters for sub-character precision
PARTIAL_BLOCKS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

# Preset gradients
GRADIENT_PRESETS = {
    "purple_pink": ("#5A56E0", "#EE6FF8"),  # Default Bubbles
    "fire": ("#ff0000", "#ffff00"),
    "ocean": ("#0066cc", "#00cccc"),
    "forest": ("#228b22", "#90ee90"),
    "sunset": ("#ff4500", "#ffd700"),
    "monochrome": ("#000000", "#ffffff"),
    "matrix": ("#003300", "#00ff00"),
    "neon": ("#ff00ff", "#00ffff"),
    "ice": ("#00ffff", "#ffffff"),
    "lava": ("#8B0000", "#FF4500"),
}


@dataclass
class ProgressMetrics:
    """Performance metrics for progress bar rendering."""

    frames_rendered: int = 0
    total_time: float = 0.0
    avg_frame_time: float = 0.0
    peak_frame_time: float = 0.0
    last_frame_time: float = 0.0

    def record_frame(self, frame_time: float):
        """Record a frame render time."""
        self.frames_rendered += 1
        self.total_time += frame_time
        self.last_frame_time = frame_time
        self.avg_frame_time = self.total_time / self.frames_rendered
        self.peak_frame_time = max(self.peak_frame_time, frame_time)

    def to_dict(self) -> dict:
        """Serialize metrics to dict."""
        return asdict(self)

    def __str__(self) -> str:
        """Human-readable metrics."""
        return (
            f"Frames: {self.frames_rendered}, "
            f"Avg: {self.avg_frame_time * 1000:.2f}ms, "
            f"Peak: {self.peak_frame_time * 1000:.2f}ms"
        )


@dataclass
class ProgressStyle:
    """Visual configuration for progress bars."""

    # Colors
    start_color: str = "#ff3333"
    end_color: str = "#ffffff"
    background_color: str = "#1a1a1a"

    # Labels
    label_style: str = "bold white"
    muted_label_style: str = "dim white"
    show_percentage: bool = True
    percent_format: str = " {:3.0f}%"
    percent_formatter: Optional[ColorFormatter] = None

    # Hint text (e.g., "Processing...")
    hint: Optional[str] = None

    # Layout
    max_width: int = 80
    horizontal_padding: int = 2

    # Gradient settings
    use_gradient: bool = False
    scale_gradient: bool = False  # Scale to filled width vs full width
    perceptual_interpolation: bool = True

    # Character style
    full_char: str = "█"
    empty_char: str = "░"
    use_partial_blocks: bool = False

    # Color profile
    color_profile: ColorProfile = ColorProfile.TRUE_COLOR

    def to_dict(self) -> dict:
        """Serialize style to dict."""
        d = asdict(self)
        d["color_profile"] = self.color_profile.value
        # percent_formatter is not serializable
        d["percent_formatter"] = None
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ProgressStyle":
        """Deserialize style from dict."""
        data = data.copy()
        if "color_profile" in data:
            data["color_profile"] = ColorProfile(data["color_profile"])
        data.pop("percent_formatter", None)  # Skip non-serializable
        return cls(**data)


@dataclass
class ProgressTheme:
    """Named theme combining style and metadata."""

    style: ProgressStyle
    name: str
    description: str


# Built-in themes
THEMES = {
    "default": ProgressTheme(
        style=ProgressStyle(
            start_color="#ff3333",
            end_color="#ffffff",
            background_color="#1a1a1a",
            use_gradient=True,
        ),
        name="Default",
        description="Red to white gradient",
    ),
    "matrix": ProgressTheme(
        style=ProgressStyle(
            start_color="#003300",
            end_color="#00ff00",
            background_color="#000000",
            use_gradient=True,
            full_char="█",
            empty_char="░",
        ),
        name="Matrix",
        description="Green terminal aesthetic",
    ),
    "neon": ProgressTheme(
        style=ProgressStyle(
            start_color="#ff00ff",
            end_color="#00ffff",
            background_color="#0a0a0a",
            use_gradient=True,
            scale_gradient=True,
        ),
        name="Neon",
        description="Synthwave vibes",
    ),
    "fire": ProgressTheme(
        style=ProgressStyle(
            start_color="#8B0000",
            end_color="#FFD700",
            background_color="#1a0000",
            use_gradient=True,
            scale_gradient=True,
        ),
        name="Fire",
        description="Burning progress",
    ),
    "ocean": ProgressTheme(
        style=ProgressStyle(
            start_color="#0066cc",
            end_color="#00ffff",
            background_color="#001a33",
            use_gradient=True,
        ),
        name="Ocean",
        description="Deep blue sea",
    ),
    "minimal": ProgressTheme(
        style=ProgressStyle(
            start_color="#ffffff",
            end_color="#ffffff",
            background_color="#333333",
            use_gradient=False,
            show_percentage=False,
        ),
        name="Minimal",
        description="Clean and simple",
    ),
}


@dataclass
class PureProgressBar:
    """Stateless progress bar renderer.

    The containing app controls the progress value; this class only renders.
    """

    style: ProgressStyle = field(default_factory=ProgressStyle)

    def render(self, progress: float, override_style: Optional[ProgressStyle] = None) -> Text:
        """Render the bar from an external progress value (0.0 -> 1.0).

        Args:
            progress: Progress value between 0.0 and 1.0
            override_style: Optional style override for this render

        Returns:
            Rich Text object ready for display
        """
        style = override_style or self.style
        style = self._normalize_style(style)
        p = clamp01(progress)
        width = self._compute_bar_width(style)
        filled = int(round(p * width))

        # Handle partial blocks if enabled
        if style.use_partial_blocks and width > 0:
            precise_filled = p * width
            filled = int(precise_filled)
            fraction = precise_filled - filled
        else:
            fraction = 0.0

        # Build the bar
        bar = Text()

        if style.use_gradient:
            # Gradient fill
            start_rgb = hex_to_rgb(style.start_color)
            end_rgb = hex_to_rgb(style.end_color)

            for i in range(filled):
                if width == 1:
                    t = 0.5  # Middle color for single character
                elif style.scale_gradient:
                    # Scale gradient to filled portion
                    t = i / max(1, filled - 1) if filled > 1 else 0.0
                else:
                    # Scale gradient to full width
                    t = i / max(1, width - 1)

                if style.perceptual_interpolation:
                    color_rgb = interpolate_rgb_perceptual(start_rgb, end_rgb, t)
                else:
                    color_rgb = interpolate_rgb(start_rgb, end_rgb, t)

                color_hex = rgb_to_hex(color_rgb)
                bar.append(style.full_char, style=color_hex if style.color_profile != ColorProfile.ASCII else None)

            # Add partial block if needed
            if style.use_partial_blocks and fraction > 0.01:
                partial_idx = int(fraction * len(PARTIAL_BLOCKS))
                partial_char = PARTIAL_BLOCKS[min(partial_idx, len(PARTIAL_BLOCKS) - 1)]

                # Color the partial block
                if style.scale_gradient:
                    t = filled / max(1, filled) if filled > 0 else 0.0
                else:
                    t = filled / max(1, width - 1)

                if style.perceptual_interpolation:
                    color_rgb = interpolate_rgb_perceptual(start_rgb, end_rgb, t)
                else:
                    color_rgb = interpolate_rgb(start_rgb, end_rgb, t)

                color_hex = rgb_to_hex(color_rgb)
                bar.append(partial_char, style=color_hex if style.color_profile != ColorProfile.ASCII else None)
                filled += 1
        else:
            # Solid fill
            bar.append(style.full_char * filled, style=style.start_color if style.color_profile != ColorProfile.ASCII else None)

            # Partial block for solid fill
            if style.use_partial_blocks and fraction > 0.01:
                partial_idx = int(fraction * len(PARTIAL_BLOCKS))
                partial_char = PARTIAL_BLOCKS[min(partial_idx, len(PARTIAL_BLOCKS) - 1)]
                bar.append(partial_char, style=style.start_color if style.color_profile != ColorProfile.ASCII else None)
                filled += 1

        # Empty fill
        empty_count = max(0, width - filled)
        bar.append(style.empty_char * empty_count, style=style.background_color if style.color_profile != ColorProfile.ASCII else None)

        # Build final output
        left_pad = " " * style.horizontal_padding
        right_pad = " " * style.horizontal_padding
        out = Text(left_pad)
        out.append("[")
        out.append_text(bar)
        out.append("]")

        # Add percentage
        if style.show_percentage:
            if style.percent_formatter:
                pct_text = style.percent_formatter(p)
            else:
                pct_text = style.percent_format.format(p * 100)
            out.append(pct_text, style=style.label_style if style.color_profile != ColorProfile.ASCII else None)

        # Add hint
        if style.hint:
            out.append(f"  {style.hint}", style=style.muted_label_style if style.color_profile != ColorProfile.ASCII else None)

        out.append(right_pad)
        return out

    def _compute_bar_width(self, style: ProgressStyle) -> int:
        """Auto-calculate bar width based on terminal size."""
        terminal_cols, _ = shutil.get_terminal_size(fallback=(120, 24))
        terminal_cols = min(terminal_cols, style.max_width)

        # Account for decorations
        reserved = 2  # Brackets: []
        if style.show_percentage:
            reserved += 8  # Percentage: " 100%"
        if style.hint:
            reserved += len(style.hint) + 2

        reserved += 2 * style.horizontal_padding

        width = terminal_cols - reserved
        return max(10, width)

    def view_as(self, progress: float, override_style: Optional[ProgressStyle] = None) -> Text:
        """Alias for render(), useful for stateless, testing-friendly calls."""
        return self.render(progress, override_style=override_style)

    def _normalize_style(self, style: ProgressStyle) -> ProgressStyle:
        if style.color_profile == ColorProfile.ASCII:
            style = ProgressStyle.from_dict(style.to_dict())
            style.use_gradient = False
            style.full_char = PROGRESS_STYLES["ascii"]["full"]
            style.empty_char = PROGRESS_STYLES["ascii"]["empty"]
        return style


@dataclass
class AnimatedProgressBar:
    """Stateful progress bar with smooth spring-based animation.

    Progress flow:
    - `update()` sets a target value
    - `incr()` increments the target by a delta
    - `tick()` advances displayed progress smoothly toward the target

    Animation uses spring physics for natural motion.
    """

    style: ProgressStyle = field(default_factory=ProgressStyle)

    # Physics parameters
    fps: int = 60
    frequency: float = 18.0  # Spring stiffness
    damping: float = 1.0  # Bounciness (higher = less bounce)

    # Step for increment/decrement
    step: float = 0.25

    # Timer-based auto-increment
    interval_seconds: float = 1.0
    timer_enabled: bool = False

    # Completion callback
    on_complete: Optional[Callable[[ProgressState], None]] = None

    # State
    state: ProgressState = ProgressState.IDLE

    # Internal state (don't modify directly)
    _id: int = field(default_factory=next_id)
    _tag: int = 0  # Invalidates old frame messages
    _target_progress: float = 0.0
    _display_progress: float = 0.0
    _velocity: float = 0.0
    _spring: Spring = field(init=False)
    _last_tick: float = field(default_factory=time.monotonic)
    _last_timer_fire: float = field(default_factory=time.monotonic)
    _completed_notified: bool = False

    # Metrics
    metrics: Optional[ProgressMetrics] = None

    def __post_init__(self):
        """Initialize spring after dataclass initialization."""
        self._spring = Spring(self.fps, self.frequency, self.damping)

    @property
    def progress(self) -> float:
        """Current displayed/animated progress."""
        return self._display_progress

    @property
    def target(self) -> float:
        """Current target progress set by external updates."""
        return self._target_progress

    @property
    def id(self) -> int:
        """Unique identifier for this progress bar."""
        return self._id

    def update(self, progress: float) -> None:
        """Set absolute target progress (0.0 -> 1.0)."""
        self._target_progress = clamp01(progress)
        self._tag += 1  # Invalidate old frame messages

        if self.state == ProgressState.IDLE:
            self.state = ProgressState.RUNNING

        self._check_completion()

    def update_from_frame(self, progress: float, tag: int) -> bool:
        """Update from an external frame only if the tag matches.

        Returns True if the update is accepted, False if it is ignored.
        """
        if tag != self._tag:
            return False
        self.update(progress)
        return True

    def incr(self, delta: Optional[float] = None) -> None:
        """Increment target progress by delta (default: configured step)."""
        d = self.step if delta is None else float(delta)
        self.update(self._target_progress + d)

    def decr(self, delta: Optional[float] = None) -> None:
        """Decrement target progress by delta (default: configured step)."""
        d = self.step if delta is None else float(delta)
        self.update(self._target_progress - d)

    def tick(self) -> None:
        """Advance animation and optional timer-driven updates.

        Call this from your TUI refresh/update loop (e.g., every frame/timer).
        """
        start_time = time.perf_counter() if self.metrics else None

        now = time.monotonic()
        dt = max(0.0, now - self._last_tick)
        self._last_tick = now

        # Timer-based auto-increment
        if self.timer_enabled and now - self._last_timer_fire >= self.interval_seconds:
            self._last_timer_fire = now
            if self._target_progress < 1.0:
                self.incr(self.step)

        # Spring animation
        if self._display_progress < self._target_progress or abs(self._velocity) > 0.001:
            self._display_progress, self._velocity = self._spring.update(
                self._display_progress, self._velocity, self._target_progress
            )

            # Clamp to valid range
            self._display_progress = clamp01(self._display_progress)

        if self.is_equilibrium():
            self._display_progress = self._target_progress
            self._velocity = 0.0

        self._check_completion()

        # Record metrics
        if self.metrics and start_time is not None:
            elapsed = time.perf_counter() - start_time
            self.metrics.record_frame(elapsed)

    def render(self) -> Text:
        """Render using current animated/displayed progress."""
        return PureProgressBar(style=self.style).render(self._display_progress)

    def is_animating(self) -> bool:
        """Check if progress bar is currently animating."""
        return not self.is_equilibrium()

    def is_equilibrium(self) -> bool:
        """Check if the bar has settled (distance and velocity thresholds)."""
        distance = abs(self._display_progress - self._target_progress)
        velocity_low = abs(self._velocity) < 0.01
        distance_low = distance < 0.001
        return distance_low and velocity_low

    def is_complete(self) -> bool:
        """Check if progress has reached 100%."""
        return self._display_progress >= 1.0 and self._target_progress >= 1.0

    def cancel(self) -> None:
        """Cancel the progress operation."""
        self.state = ProgressState.CANCELLED
        if self.on_complete:
            self.on_complete(self.state)

    def reset(self) -> None:
        """Reset progress to 0."""
        self._target_progress = 0.0
        self._display_progress = 0.0
        self._velocity = 0.0
        self._tag += 1
        self._completed_notified = False
        self.state = ProgressState.IDLE

    def enable_metrics(self) -> None:
        """Enable performance metrics tracking."""
        self.metrics = ProgressMetrics()

    def disable_metrics(self) -> None:
        """Disable metrics tracking."""
        self.metrics = None

    def _check_completion(self) -> None:
        """Check if target has reached completion and fire callback."""
        if self._target_progress >= 1.0 and not self._completed_notified:
            self._completed_notified = True
            self.state = ProgressState.COMPLETED
            if self.on_complete:
                self.on_complete(self.state)

    # Fluent API methods
    def with_gradient(self, start: str, end: str, scaled: bool = False) -> "AnimatedProgressBar":
        """Set gradient colors (fluent API)."""
        self.style.start_color = start
        self.style.end_color = end
        self.style.use_gradient = True
        self.style.scale_gradient = scaled
        return self

    def with_preset_gradient(self, preset: str, scaled: bool = False) -> "AnimatedProgressBar":
        """Use a preset gradient (fluent API)."""
        if preset not in GRADIENT_PRESETS:
            raise ValueError(
                f"Unknown gradient preset: {preset}. "
                f"Available: {', '.join(GRADIENT_PRESETS.keys())}"
            )
        start, end = GRADIENT_PRESETS[preset]
        return self.with_gradient(start, end, scaled)

    def with_solid_fill(self, color: str) -> "AnimatedProgressBar":
        """Set solid fill color (fluent API)."""
        self.style.start_color = color
        self.style.use_gradient = False
        return self

    def with_width(self, width: int) -> "AnimatedProgressBar":
        """Set maximum width (fluent API)."""
        self.style.max_width = width
        return self

    def with_hint(self, hint: str) -> "AnimatedProgressBar":
        """Set hint text (fluent API)."""
        self.style.hint = hint
        return self

    def without_percentage(self) -> "AnimatedProgressBar":
        """Hide percentage display (fluent API)."""
        self.style.show_percentage = False
        return self

    def with_style_preset(self, name: str) -> "AnimatedProgressBar":
        """Apply character style preset (fluent API)."""
        if name not in PROGRESS_STYLES:
            raise ValueError(
                f"Unknown style preset: {name}. "
                f"Available: {', '.join(PROGRESS_STYLES.keys())}"
            )
        chars = PROGRESS_STYLES[name]
        self.style.full_char = chars["full"]
        self.style.empty_char = chars["empty"]
        return self

    def with_spring_options(self, frequency: float, damping: float) -> "AnimatedProgressBar":
        """Set spring physics parameters (fluent API)."""
        self.frequency = frequency
        self.damping = damping
        self._spring = Spring(self.fps, frequency, damping)
        return self

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for persistence/debugging."""
        return {
            "id": self._id,
            "tag": self._tag,
            "progress": self._display_progress,
            "target": self._target_progress,
            "velocity": self._velocity,
            "state": self.state.value,
            "style": self.style.to_dict(),
            "fps": self.fps,
            "frequency": self.frequency,
            "damping": self.damping,
            "step": self.step,
            "timer_enabled": self.timer_enabled,
            "interval_seconds": self.interval_seconds,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnimatedProgressBar":
        """Restore from serialized state."""
        style_data = data.get("style", {})
        style = ProgressStyle.from_dict(style_data)

        bar = cls(
            style=style,
            fps=data.get("fps", 60),
            frequency=data.get("frequency", 18.0),
            damping=data.get("damping", 1.0),
            step=data.get("step", 0.25),
            timer_enabled=data.get("timer_enabled", False),
            interval_seconds=data.get("interval_seconds", 1.0),
        )

        # Restore internal state
        bar._id = data.get("id", bar._id)
        bar._tag = data.get("tag", 0)
        bar._display_progress = data.get("progress", 0.0)
        bar._target_progress = data.get("target", 0.0)
        bar._velocity = data.get("velocity", 0.0)
        bar.state = ProgressState(data.get("state", "idle"))

        return bar

    @classmethod
    def from_theme(cls, theme_name: str) -> "AnimatedProgressBar":
        """Create progress bar from a named theme."""
        if theme_name not in THEMES:
            raise ValueError(
                f"Unknown theme: {theme_name}. "
                f"Available: {', '.join(THEMES.keys())}"
            )
        theme = THEMES[theme_name]
        return cls(style=theme.style)

    def save_to_file(self, filepath: str) -> None:
        """Save progress state to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "AnimatedProgressBar":
        """Load progress state from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


class ProgressGroup:
    """Manage multiple progress bars as a group."""

    def __init__(self):
        self.bars: Dict[str, AnimatedProgressBar] = {}

    def add(self, name: str, bar: AnimatedProgressBar) -> None:
        """Add a progress bar to the group."""
        self.bars[name] = bar

    def remove(self, name: str) -> None:
        """Remove a progress bar from the group."""
        self.bars.pop(name, None)

    def get(self, name: str) -> Optional[AnimatedProgressBar]:
        """Get a progress bar by name."""
        return self.bars.get(name)

    def update_all(self, progress: float) -> None:
        """Update all progress bars to the same value."""
        for bar in self.bars.values():
            bar.update(progress)

    def tick_all(self) -> None:
        """Tick all progress bars."""
        for bar in self.bars.values():
            bar.tick()

    def render_all(self) -> Dict[str, Text]:
        """Render all progress bars."""
        return {name: bar.render() for name, bar in self.bars.items()}

    def is_any_animating(self) -> bool:
        """Check if any progress bar is animating."""
        return any(bar.is_animating() for bar in self.bars.values())

    def is_all_complete(self) -> bool:
        """Check if all progress bars are complete."""
        return all(bar.is_complete() for bar in self.bars.values())

    def reset_all(self) -> None:
        """Reset all progress bars."""
        for bar in self.bars.values():
            bar.reset()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all progress bars."""
        return {name: bar.to_dict() for name, bar in self.bars.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressGroup":
        """Deserialize progress group."""
        group = cls()
        for name, bar_data in data.items():
            group.bars[name] = AnimatedProgressBar.from_dict(bar_data)
        return group


# Convenience functions
def format_as_fraction(total: int) -> ColorFormatter:
    """Create a formatter that shows progress as a fraction."""

    def formatter(p: float) -> str:
        return f" {int(p * total)}/{total}"

    return formatter


def format_as_time_remaining(elapsed_time: float) -> ColorFormatter:
    """Create a formatter that estimates time remaining."""

    def formatter(p: float) -> str:
        if p < 0.01:
            return " estimating..."
        total_time = elapsed_time / p
        remaining = total_time - elapsed_time
        if remaining < 60:
            return f" ~{remaining:.0f}s"
        if remaining < 3600:
            return f" ~{remaining / 60:.1f}m"
        return f" ~{remaining / 3600:.1f}h"

    return formatter


def format_engineering(p: float) -> str:
    """Format as engineering notation."""
    if p >= 0.999:
        return " 100%"
    return f" {p:.2e}"


__all__ = [
    # Core classes
    "AnimatedProgressBar",
    "PureProgressBar",
    "ProgressStyle",
    "ProgressGroup",
    "ProgressTheme",
    "ProgressState",
    "ProgressMetrics",
    # Physics
    "Spring",
    # Enums
    "ColorProfile",
    # Utilities
    "clamp01",
    "hex_to_rgb",
    "rgb_to_hex",
    "interpolate_rgb",
    "interpolate_rgb_perceptual",
    # Constants
    "GRADIENT_PRESETS",
    "PROGRESS_STYLES",
    "THEMES",
    # Formatters
    "format_as_fraction",
    "format_as_time_remaining",
    "format_engineering",
]
