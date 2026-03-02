from rich.text import Text

from modern_tui.progress import (
    AnimatedProgressBar,
    ProgressStyle,
    PureProgressBar,
    clamp01,
    hex_to_rgb,
    rgb_to_hex,
)


def test_color_helpers_roundtrip():
    assert hex_to_rgb("#ff0000") == (255, 0, 0)
    assert rgb_to_hex((255, 255, 255)) == "#ffffff"


def test_clamp01():
    assert clamp01(-1) == 0.0
    assert clamp01(2) == 1.0
    assert clamp01(0.4) == 0.4


def test_pure_render_returns_text():
    bar = PureProgressBar(style=ProgressStyle(hint="Press any key to quit"))
    rendered = bar.render(0.5)
    assert isinstance(rendered, Text)
    assert "50%" in rendered.plain


def test_animated_progress_incr_and_complete_callback():
    hit = {"done": False}

    def done():
        hit["done"] = True

    bar = AnimatedProgressBar(step=0.25, on_complete=done)
    for _ in range(4):
        bar.incr()
    assert bar.target == 1.0
    assert hit["done"] is True


def test_animated_tick_moves_toward_target():
    bar = AnimatedProgressBar(animation_speed=10.0)
    bar.update(0.5)
    # multiple ticks should reach target quickly
    for _ in range(5):
        bar._last_tick -= 0.1
        bar.tick()
    assert 0.49 <= bar.progress <= 0.5
