"""Comprehensive tests for enhanced progress bar features.

Tests all Bubbles-inspired features:
- Spring physics
- Gradient modes
- Perceptual interpolation
- Frame tagging
- Equilibrium detection
- Themes
- Serialization
- Multi-bar groups
- And more!
"""

import tempfile
import time
from pathlib import Path

import pytest
from rich.text import Text

from modern_tui.progress_enhanced import (
    AnimatedProgressBar,
    ColorProfile,
    GRADIENT_PRESETS,
    ProgressGroup,
    ProgressMetrics,
    ProgressState,
    ProgressStyle,
    PROGRESS_STYLES,
    PureProgressBar,
    Spring,
    THEMES,
    clamp01,
    format_as_fraction,
    format_as_time_remaining,
    hex_to_rgb,
    interpolate_rgb,
    interpolate_rgb_perceptual,
    rgb_to_hex,
)


class TestColorUtilities:
    """Test color conversion and interpolation."""

    def test_hex_to_rgb(self):
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("#00ff00") == (0, 255, 0)
        assert hex_to_rgb("#0000ff") == (0, 0, 255)
        assert hex_to_rgb("#ffffff") == (255, 255, 255)
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_short_form(self):
        """Test 3-character hex colors."""
        assert hex_to_rgb("#f00") == (255, 0, 0)
        assert hex_to_rgb("#0f0") == (0, 255, 0)
        assert hex_to_rgb("#00f") == (0, 0, 255)

    def test_rgb_to_hex(self):
        assert rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert rgb_to_hex((0, 255, 0)) == "#00ff00"
        assert rgb_to_hex((0, 0, 255)) == "#0000ff"
        assert rgb_to_hex((255, 255, 255)) == "#ffffff"

    def test_roundtrip_conversion(self):
        """Test hex -> RGB -> hex roundtrip."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffffff", "#123456"]
        for color in colors:
            rgb = hex_to_rgb(color)
            back = rgb_to_hex(rgb)
            assert back == color

    def test_interpolate_rgb(self):
        """Test linear RGB interpolation."""
        black = (0, 0, 0)
        white = (255, 255, 255)

        assert interpolate_rgb(black, white, 0.0) == (0, 0, 0)
        assert interpolate_rgb(black, white, 1.0) == (255, 255, 255)
        assert interpolate_rgb(black, white, 0.5) == (127, 127, 127)

    def test_interpolate_rgb_perceptual(self):
        """Test perceptually uniform interpolation."""
        black = (0, 0, 0)
        white = (255, 255, 255)

        # Should produce different results than linear
        linear_mid = interpolate_rgb(black, white, 0.5)
        perceptual_mid = interpolate_rgb_perceptual(black, white, 0.5)

        # Perceptual should be brighter (gamma corrected)
        assert perceptual_mid > linear_mid

    def test_clamp01(self):
        assert clamp01(-1.0) == 0.0
        assert clamp01(2.0) == 1.0
        assert clamp01(0.5) == 0.5
        assert clamp01(0.0) == 0.0
        assert clamp01(1.0) == 1.0


class TestSpring:
    """Test spring physics simulation."""

    def test_spring_initialization(self):
        spring = Spring(fps=60, frequency=10.0, damping=1.0)
        assert spring.fps == 60
        assert spring.frequency == 10.0
        assert spring.damping == 1.0
        assert spring.dt == 1.0 / 60

    def test_spring_moves_toward_target(self):
        """Test spring moves position toward target."""
        spring = Spring(fps=60, frequency=10.0, damping=1.0)
        position = 0.0
        velocity = 0.0
        target = 1.0

        # Simulate several steps
        for _ in range(10):
            position, velocity = spring.update(position, velocity, target)

        # Should be moving toward target
        assert position > 0.0
        assert position < target

    def test_spring_eventually_reaches_target(self):
        """Test spring reaches equilibrium at target."""
        spring = Spring(fps=60, frequency=20.0, damping=2.0)
        position = 0.0
        velocity = 0.0
        target = 1.0

        # Simulate many steps
        for _ in range(400):
            position, velocity = spring.update(position, velocity, target)

        # Should be very close to target
        assert abs(position - target) < 0.02
        assert abs(velocity) < 0.05

    def test_spring_higher_frequency_is_faster(self):
        """Test that higher frequency reaches target faster."""
        slow_spring = Spring(fps=60, frequency=5.0, damping=1.0)
        fast_spring = Spring(fps=60, frequency=20.0, damping=1.0)

        slow_pos = 0.0
        slow_vel = 0.0
        fast_pos = 0.0
        fast_vel = 0.0
        target = 1.0

        # Same number of steps
        for _ in range(10):
            slow_pos, slow_vel = slow_spring.update(slow_pos, slow_vel, target)
            fast_pos, fast_vel = fast_spring.update(fast_pos, fast_vel, target)

        # Fast spring should be closer to target
        assert fast_pos > slow_pos


class TestProgressStyle:
    """Test ProgressStyle configuration."""

    def test_default_style(self):
        style = ProgressStyle()
        assert style.start_color == "#ff3333"
        assert style.end_color == "#ffffff"
        assert style.show_percentage is True
        assert style.use_gradient is False

    def test_style_serialization(self):
        """Test style can be serialized and deserialized."""
        style = ProgressStyle(
            start_color="#ff0000",
            end_color="#00ff00",
            use_gradient=True,
            scale_gradient=True,
        )

        # Serialize
        data = style.to_dict()

        # Deserialize
        restored = ProgressStyle.from_dict(data)

        assert restored.start_color == style.start_color
        assert restored.end_color == style.end_color
        assert restored.use_gradient == style.use_gradient
        assert restored.scale_gradient == style.scale_gradient


class TestPureProgressBar:
    """Test stateless progress bar rendering."""

    def test_render_returns_text(self):
        bar = PureProgressBar()
        result = bar.render(0.5)
        assert isinstance(result, Text)

    def test_render_with_percentage(self):
        style = ProgressStyle(show_percentage=True)
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)
        assert "50" in result.plain

    def test_render_without_percentage(self):
        style = ProgressStyle(show_percentage=False)
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)
        assert "50" not in result.plain

    def test_render_with_hint(self):
        style = ProgressStyle(hint="Loading...")
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)
        assert "Loading..." in result.plain

    def test_render_gradient_mode(self):
        """Test gradient rendering produces expected output."""
        style = ProgressStyle(
            use_gradient=True,
            start_color="#ff0000",
            end_color="#00ff00",
            show_percentage=False,
            max_width=50,
        )
        bar = PureProgressBar(style=style)
        result = bar.render(1.0)

        # Should contain full and empty characters
        assert style.full_char in result.plain or "[" in result.plain

    def test_render_scaled_gradient(self):
        """Test scaled gradient mode."""
        style = ProgressStyle(
            use_gradient=True,
            scale_gradient=True,
            show_percentage=False,
        )
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)
        assert isinstance(result, Text)

    def test_render_partial_blocks(self):
        """Test partial block rendering for sub-character precision."""
        style = ProgressStyle(
            use_partial_blocks=True,
            show_percentage=False,
        )
        bar = PureProgressBar(style=style)
        result = bar.render(0.55)
        assert isinstance(result, Text)

    def test_render_clamps_progress(self):
        """Test that progress values are clamped to [0, 1]."""
        bar = PureProgressBar()

        # Over 100%
        result1 = bar.render(1.5)
        assert isinstance(result1, Text)

        # Under 0%
        result2 = bar.render(-0.5)
        assert isinstance(result2, Text)

    def test_view_as_alias(self):
        bar = PureProgressBar()
        rendered = bar.view_as(0.2)
        assert isinstance(rendered, Text)


class TestAnimatedProgressBar:
    """Test stateful animated progress bar."""

    def test_initialization(self):
        bar = AnimatedProgressBar()
        assert bar.progress == 0.0
        assert bar.target == 0.0
        assert bar.state == ProgressState.IDLE

    def test_update_sets_target(self):
        bar = AnimatedProgressBar()
        bar.update(0.5)
        assert bar.target == 0.5
        assert bar.state == ProgressState.RUNNING

    def test_update_clamps_progress(self):
        bar = AnimatedProgressBar()
        bar.update(1.5)
        assert bar.target == 1.0

        bar.update(-0.5)
        assert bar.target == 0.0

    def test_incr_increments_by_step(self):
        bar = AnimatedProgressBar(step=0.25)
        bar.update(0.0)
        bar.incr()
        assert bar.target == 0.25

    def test_incr_with_custom_delta(self):
        bar = AnimatedProgressBar()
        bar.update(0.0)
        bar.incr(0.1)
        assert bar.target == 0.1

    def test_decr_decrements(self):
        bar = AnimatedProgressBar(step=0.25)
        bar.update(0.5)
        bar.decr()
        assert bar.target == 0.25

    def test_tick_advances_animation(self):
        """Test tick() moves display toward target."""
        bar = AnimatedProgressBar()
        bar.update(1.0)

        initial_progress = bar.progress

        # Tick several times
        for _ in range(10):
            bar.tick()

        # Progress should have advanced
        assert bar.progress > initial_progress

    def test_is_animating(self):
        bar = AnimatedProgressBar()
        bar.update(1.0)

        # Should be animating
        assert bar.is_animating()

        # Tick until complete
        for _ in range(400):
            bar.tick()

        # Should settle near equilibrium
        assert abs(bar.progress - bar.target) < 0.02
        assert not bar.is_animating() or abs(bar.progress - bar.target) < 0.01

    def test_is_complete(self):
        bar = AnimatedProgressBar()
        assert not bar.is_complete()

        bar.update(1.0)

        # Tick until animation completes
        for _ in range(200):
            bar.tick()

        assert bar.is_complete()

    def test_completion_callback(self):
        """Test completion callback is fired."""
        completed = {"called": False, "state": None}

        def on_complete(state: ProgressState):
            completed["called"] = True
            completed["state"] = state

        bar = AnimatedProgressBar(on_complete=on_complete)
        bar.update(1.0)

        # Should fire on first tick after reaching target
        bar.tick()

        assert completed["called"]
        assert completed["state"] == ProgressState.COMPLETED

    def test_completion_callback_fires_once(self):
        """Test callback only fires once."""
        call_count = {"count": 0}

        def on_complete(state: ProgressState):
            call_count["count"] += 1

        bar = AnimatedProgressBar(on_complete=on_complete)
        bar.update(1.0)

        # Tick multiple times
        for _ in range(10):
            bar.tick()

        # Should only fire once
        assert call_count["count"] == 1

    def test_cancel(self):
        bar = AnimatedProgressBar()
        bar.update(0.5)
        bar.cancel()
        assert bar.state == ProgressState.CANCELLED

    def test_reset(self):
        bar = AnimatedProgressBar()
        bar.update(0.8)
        bar.tick()

        bar.reset()

        assert bar.progress == 0.0
        assert bar.target == 0.0
        assert bar.state == ProgressState.IDLE

    def test_frame_tagging(self):
        """Test that tag increments prevent stale frame processing."""
        bar = AnimatedProgressBar()

        initial_tag = bar._tag
        bar.update(0.5)
        assert bar._tag == initial_tag + 1

        bar.update(0.8)
        assert bar._tag == initial_tag + 2

    def test_render(self):
        bar = AnimatedProgressBar()
        bar.update(0.5)
        result = bar.render()
        assert isinstance(result, Text)

    def test_metrics_tracking(self):
        """Test performance metrics can be enabled."""
        bar = AnimatedProgressBar()
        bar.enable_metrics()

        assert bar.metrics is not None

        bar.update(1.0)
        for _ in range(10):
            bar.tick()

        assert bar.metrics.frames_rendered > 0
        assert bar.metrics.total_time > 0
        assert bar.metrics.avg_frame_time > 0

    def test_metrics_disabled(self):
        bar = AnimatedProgressBar()
        bar.enable_metrics()
        bar.disable_metrics()
        assert bar.metrics is None


class TestFluentAPI:
    """Test fluent/builder API methods."""

    def test_with_gradient(self):
        bar = AnimatedProgressBar().with_gradient("#ff0000", "#00ff00", scaled=True)

        assert bar.style.start_color == "#ff0000"
        assert bar.style.end_color == "#00ff00"
        assert bar.style.use_gradient is True
        assert bar.style.scale_gradient is True

    def test_with_preset_gradient(self):
        bar = AnimatedProgressBar().with_preset_gradient("fire", scaled=True)

        start, end = GRADIENT_PRESETS["fire"]
        assert bar.style.start_color == start
        assert bar.style.end_color == end
        assert bar.style.scale_gradient is True

    def test_with_solid_fill(self):
        bar = AnimatedProgressBar().with_solid_fill("#0000ff")

        assert bar.style.start_color == "#0000ff"
        assert bar.style.use_gradient is False

    def test_with_width(self):
        bar = AnimatedProgressBar().with_width(100)
        assert bar.style.max_width == 100

    def test_with_hint(self):
        bar = AnimatedProgressBar().with_hint("Processing...")
        assert bar.style.hint == "Processing..."

    def test_without_percentage(self):
        bar = AnimatedProgressBar().without_percentage()
        assert bar.style.show_percentage is False

    def test_with_style_preset(self):
        bar = AnimatedProgressBar().with_style_preset("dots")

        assert bar.style.full_char == PROGRESS_STYLES["dots"]["full"]
        assert bar.style.empty_char == PROGRESS_STYLES["dots"]["empty"]

    def test_with_spring_options(self):
        bar = AnimatedProgressBar().with_spring_options(frequency=25.0, damping=1.5)

        assert bar.frequency == 25.0
        assert bar.damping == 1.5

    def test_method_chaining(self):
        """Test multiple fluent methods can be chained."""
        bar = (
            AnimatedProgressBar()
            .with_gradient("#ff0000", "#00ff00")
            .with_width(80)
            .with_hint("Loading...")
            .without_percentage()
        )

        assert bar.style.use_gradient is True
        assert bar.style.max_width == 80
        assert bar.style.hint == "Loading..."
        assert bar.style.show_percentage is False


class TestSerialization:
    """Test state serialization and deserialization."""

    def test_to_dict(self):
        bar = AnimatedProgressBar()
        bar.update(0.5)
        bar.tick()

        data = bar.to_dict()

        assert "progress" in data
        assert "target" in data
        assert "velocity" in data
        assert "state" in data
        assert data["target"] == 0.5

    def test_from_dict(self):
        bar = AnimatedProgressBar()
        bar.update(0.7)
        for _ in range(10):
            bar.tick()

        # Serialize
        data = bar.to_dict()

        # Deserialize
        restored = AnimatedProgressBar.from_dict(data)

        assert abs(restored.progress - bar.progress) < 0.01
        assert restored.target == bar.target
        assert restored.state == bar.state

    def test_save_and_load_file(self):
        """Test saving to and loading from file."""
        bar = AnimatedProgressBar()
        bar.update(0.8)
        bar.tick()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            # Save
            bar.save_to_file(filepath)

            # Load
            restored = AnimatedProgressBar.load_from_file(filepath)

            assert abs(restored.progress - bar.progress) < 0.01
            assert restored.target == bar.target
        finally:
            Path(filepath).unlink()


class TestThemes:
    """Test theme system."""

    def test_builtin_themes_exist(self):
        """Test all built-in themes are defined."""
        expected_themes = ["default", "matrix", "neon", "fire", "ocean", "minimal"]
        for theme_name in expected_themes:
            assert theme_name in THEMES

    def test_from_theme(self):
        """Test creating progress bar from theme."""
        bar = AnimatedProgressBar.from_theme("matrix")

        theme = THEMES["matrix"]
        assert bar.style.start_color == theme.style.start_color
        assert bar.style.end_color == theme.style.end_color

    def test_invalid_theme_raises(self):
        """Test invalid theme name raises error."""
        with pytest.raises(ValueError, match="Unknown theme"):
            AnimatedProgressBar.from_theme("nonexistent")


class TestProgressGroup:
    """Test multi-progress bar management."""

    def test_add_and_get(self):
        group = ProgressGroup()
        bar = AnimatedProgressBar()

        group.add("download", bar)

        retrieved = group.get("download")
        assert retrieved is bar

    def test_remove(self):
        group = ProgressGroup()
        bar = AnimatedProgressBar()

        group.add("task", bar)
        group.remove("task")

        assert group.get("task") is None

    def test_update_all(self):
        group = ProgressGroup()
        group.add("task1", AnimatedProgressBar())
        group.add("task2", AnimatedProgressBar())

        group.update_all(0.5)

        assert group.get("task1").target == 0.5
        assert group.get("task2").target == 0.5

    def test_tick_all(self):
        group = ProgressGroup()
        bar1 = AnimatedProgressBar()
        bar2 = AnimatedProgressBar()

        group.add("task1", bar1)
        group.add("task2", bar2)

        group.update_all(1.0)
        group.tick_all()

        # Both should have advanced
        assert bar1.progress > 0
        assert bar2.progress > 0

    def test_render_all(self):
        group = ProgressGroup()
        group.add("task1", AnimatedProgressBar())
        group.add("task2", AnimatedProgressBar())

        renders = group.render_all()

        assert len(renders) == 2
        assert all(isinstance(r, Text) for r in renders.values())

    def test_is_any_animating(self):
        group = ProgressGroup()
        bar1 = AnimatedProgressBar()
        bar2 = AnimatedProgressBar()

        group.add("task1", bar1)
        group.add("task2", bar2)

        bar1.update(0.5)

        assert group.is_any_animating()

    def test_is_all_complete(self):
        group = ProgressGroup()
        bar1 = AnimatedProgressBar()
        bar2 = AnimatedProgressBar()

        group.add("task1", bar1)
        group.add("task2", bar2)

        bar1.update(1.0)
        bar2.update(1.0)

        # Tick until both complete
        for _ in range(200):
            group.tick_all()

        assert group.is_all_complete()

    def test_reset_all(self):
        group = ProgressGroup()
        bar1 = AnimatedProgressBar()
        bar2 = AnimatedProgressBar()

        group.add("task1", bar1)
        group.add("task2", bar2)

        group.update_all(0.8)
        group.reset_all()

        assert bar1.target == 0.0
        assert bar2.target == 0.0

    def test_group_serialization(self):
        """Test serializing and deserializing groups."""
        group = ProgressGroup()
        group.add("task1", AnimatedProgressBar())
        group.add("task2", AnimatedProgressBar())

        group.update_all(0.5)

        # Serialize
        data = group.to_dict()

        # Deserialize
        restored = ProgressGroup.from_dict(data)

        assert len(restored.bars) == 2
        assert restored.get("task1").target == 0.5
        assert restored.get("task2").target == 0.5


class TestFormatters:
    """Test custom percentage formatters."""

    def test_format_as_fraction(self):
        formatter = format_as_fraction(total=100)

        assert formatter(0.0) == " 0/100"
        assert formatter(0.5) == " 50/100"
        assert formatter(1.0) == " 100/100"

    def test_format_as_time_remaining(self):
        formatter = format_as_time_remaining(elapsed_time=50.0)

        # At 50% with 50s elapsed, should estimate ~50s remaining
        result = formatter(0.5)
        assert "50" in result or "5" in result  # Could be "50s" or "50.0s"

    def test_custom_formatter(self):
        """Test custom formatter can be applied."""
        style = ProgressStyle(
            show_percentage=True,
            percent_formatter=lambda p: f" [{p * 100:.1f}%]",
        )

        bar = PureProgressBar(style=style)
        result = bar.render(0.555)

        assert "[55.5%]" in result.plain


class TestTimerMode:
    """Test timer-based auto-increment."""

    def test_timer_disabled_by_default(self):
        bar = AnimatedProgressBar()
        assert bar.timer_enabled is False

    def test_timer_increments_progress(self):
        """Test timer increments at intervals."""
        bar = AnimatedProgressBar(
            timer_enabled=True,
            interval_seconds=0.1,
            step=0.1,
        )

        bar.update(0.0)
        initial_target = bar.target

        # Wait for timer interval
        time.sleep(0.15)
        bar.tick()

        # Target should have incremented
        assert bar.target > initial_target


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_width_terminal(self):
        """Test graceful handling of very small terminal."""
        style = ProgressStyle(max_width=5)
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)

        # Should still produce valid output
        assert isinstance(result, Text)

    def test_very_long_hint(self):
        """Test long hint text doesn't break rendering."""
        style = ProgressStyle(hint="A" * 200)
        bar = PureProgressBar(style=style)
        result = bar.render(0.5)

        assert isinstance(result, Text)

    def test_rapid_updates(self):
        """Test rapid updates don't break state."""
        bar = AnimatedProgressBar()

        for i in range(100):
            bar.update(i / 100.0)
            bar.tick()

        assert 0.0 <= bar.progress <= 1.0
        assert 0.0 <= bar.target <= 1.0

    def test_negative_spring_parameters(self):
        """Test spring handles negative parameters gracefully."""
        # Should not crash, though behavior may be undefined
        bar = AnimatedProgressBar(frequency=-10.0, damping=-1.0)
        bar.update(0.5)
        bar.tick()

        # Should still be in valid range
        assert 0.0 <= bar.progress <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
