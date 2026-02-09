#!/usr/bin/env python3
"""
Enhanced Progress Bar - Interactive Demo
=========================================

Demonstrates all features from charmbracelet/bubbles integration:
- Spring physics animation
- Gradient modes (full-width and scaled)
- Perceptual color interpolation
- Multiple themes
- Custom formatters
- Multi-bar groups
- State serialization
- Performance metrics
- And more!

Run this script to see everything in action.
"""

import asyncio
import time
from pathlib import Path

from modern_tui.progress_enhanced import (
    AnimatedProgressBar,
    GRADIENT_PRESETS,
    ProgressGroup,
    ProgressState,
    PROGRESS_STYLES,
    PureProgressBar,
    THEMES,
    format_as_fraction,
    format_as_time_remaining,
)


def clear_screen():
    """Clear the terminal."""
    print("\033[2J\033[H", end="")


def demo_basic():
    """Demo 1: Basic usage."""
    print("=" * 60)
    print("DEMO 1: Basic Progress Bar")
    print("=" * 60)
    print()

    bar = AnimatedProgressBar()

    print("Simple progress from 0 to 100%:\n")

    for i in range(101):
        bar.update(i / 100)
        bar.tick()
        print(f"\r{bar.render().plain}", end="", flush=True)
        time.sleep(0.02)

    print("\n\n✓ Complete!\n")
    time.sleep(1)


def demo_spring_physics():
    """Demo 2: Spring physics comparison."""
    print("=" * 60)
    print("DEMO 2: Spring Physics Animation")
    print("=" * 60)
    print()

    print("Comparing different spring settings:\n")

    # Fast and bouncy
    fast = (
        AnimatedProgressBar()
        .with_spring_options(frequency=30.0, damping=0.5)
        .with_hint("Fast & bouncy")
    )

    # Smooth default
    smooth = (
        AnimatedProgressBar()
        .with_spring_options(frequency=18.0, damping=1.0)
        .with_hint("Smooth default")
    )

    # Slow and damped
    slow = (
        AnimatedProgressBar()
        .with_spring_options(frequency=8.0, damping=2.0)
        .with_hint("Slow & damped")
    )

    bars = [fast, smooth, slow]

    # Update all to 100%
    for b in bars:
        b.update(1.0)

    # Animate
    while any(b.is_animating() for b in bars):
        for b in bars:
            b.tick()

        print(f"\r{fast.render().plain}")
        print(f"\r{smooth.render().plain}")
        print(f"\r{slow.render().plain}")
        print("\033[3A", end="")  # Move cursor up 3 lines

        time.sleep(1 / 60)

    # Show final
    print(f"\r{fast.render().plain}")
    print(f"\r{smooth.render().plain}")
    print(f"\r{slow.render().plain}")
    print("\n✓ Notice the different animation styles!\n")
    time.sleep(2)


def demo_gradients():
    """Demo 3: Gradient modes."""
    print("=" * 60)
    print("DEMO 3: Gradient Modes")
    print("=" * 60)
    print()

    # Solid
    solid = AnimatedProgressBar().with_solid_fill("#00ff00").with_hint("Solid fill")

    # Full-width gradient
    full = (
        AnimatedProgressBar()
        .with_gradient("#ff0000", "#00ff00")
        .with_hint("Full-width gradient")
    )

    # Scaled gradient
    scaled = (
        AnimatedProgressBar()
        .with_gradient("#ff0000", "#00ff00", scaled=True)
        .with_hint("Scaled gradient")
    )

    bars = [solid, full, scaled]

    print("Watch how gradients behave differently:\n")

    for i in range(101):
        for b in bars:
            b.update(i / 100)
            b.tick()

        print(f"\r{solid.render().plain}")
        print(f"\r{full.render().plain}")
        print(f"\r{scaled.render().plain}")
        print("\033[3A", end="")

        time.sleep(0.02)

    print(f"\r{solid.render().plain}")
    print(f"\r{full.render().plain}")
    print(f"\r{scaled.render().plain}")
    print("\n✓ Notice the gradient scaling!\n")
    time.sleep(2)


def demo_themes():
    """Demo 4: Built-in themes."""
    print("=" * 60)
    print("DEMO 4: Built-in Themes")
    print("=" * 60)
    print()

    print("Showcasing all built-in themes:\n")

    theme_bars = {
        name: AnimatedProgressBar.from_theme(name).with_hint(theme.description)
        for name, theme in THEMES.items()
    }

    for i in range(101):
        for bar in theme_bars.values():
            bar.update(i / 100)
            bar.tick()

        for name, bar in theme_bars.items():
            print(f"\r{name:10s}: {bar.render().plain}")

        print(f"\033[{len(theme_bars)}A", end="")
        time.sleep(0.02)

    for name, bar in theme_bars.items():
        print(f"\r{name:10s}: {bar.render().plain}")

    print("\n✓ Themes complete!\n")
    time.sleep(2)


def demo_presets():
    """Demo 5: Gradient presets."""
    print("=" * 60)
    print("DEMO 5: Gradient Presets")
    print("=" * 60)
    print()

    print("All available gradient presets:\n")

    preset_bars = {
        name: (
            AnimatedProgressBar()
            .with_preset_gradient(name, scaled=True)
            .with_hint(f"{name} gradient")
        )
        for name in list(GRADIENT_PRESETS.keys())[:6]  # Show first 6
    }

    for i in range(101):
        for bar in preset_bars.values():
            bar.update(i / 100)
            bar.tick()

        for name, bar in preset_bars.items():
            print(f"\r{name:12s}: {bar.render().plain}")

        print(f"\033[{len(preset_bars)}A", end="")
        time.sleep(0.02)

    for name, bar in preset_bars.items():
        print(f"\r{name:12s}: {bar.render().plain}")

    print("\n✓ Gradient presets complete!\n")
    time.sleep(2)


def demo_styles():
    """Demo 6: Character styles."""
    print("=" * 60)
    print("DEMO 6: Character Styles")
    print("=" * 60)
    print()

    print("Different character sets for the progress bar:\n")

    style_bars = {
        name: (
            AnimatedProgressBar().with_style_preset(name).with_hint(f"{name} style")
        )
        for name in list(PROGRESS_STYLES.keys())[:6]
    }

    for i in range(101):
        for bar in style_bars.values():
            bar.update(i / 100)
            bar.tick()

        for name, bar in style_bars.items():
            print(f"\r{name:10s}: {bar.render().plain}")

        print(f"\033[{len(style_bars)}A", end="")
        time.sleep(0.02)

    for name, bar in style_bars.items():
        print(f"\r{name:10s}: {bar.render().plain}")

    print("\n✓ Character styles complete!\n")
    time.sleep(2)


def demo_formatters():
    """Demo 7: Custom formatters."""
    print("=" * 60)
    print("DEMO 7: Custom Formatters")
    print("=" * 60)
    print()

    print("Different ways to display progress:\n")

    from modern_tui.progress_enhanced import ProgressStyle

    # Default percentage
    default_style = ProgressStyle()
    default_bar = AnimatedProgressBar(style=default_style).with_hint("Default %")

    # Fraction
    fraction_style = ProgressStyle(percent_formatter=format_as_fraction(100))
    fraction_bar = AnimatedProgressBar(style=fraction_style).with_hint("Fraction")

    # Time remaining (simulate 10s elapsed)
    start_time = time.time()

    # Custom
    custom_style = ProgressStyle(percent_formatter=lambda p: f" [{p * 100:.1f}%]")
    custom_bar = AnimatedProgressBar(style=custom_style).with_hint("Custom format")

    bars = [default_bar, fraction_bar, custom_bar]

    for i in range(101):
        elapsed = time.time() - start_time

        # Update time formatter
        time_style = ProgressStyle(percent_formatter=format_as_time_remaining(elapsed))
        time_bar = AnimatedProgressBar(style=time_style).with_hint("Time remaining")

        for b in bars + [time_bar]:
            b.update(i / 100)
            b.tick()

        print(f"\r{default_bar.render().plain}")
        print(f"\r{fraction_bar.render().plain}")
        print(f"\r{time_bar.render().plain}")
        print(f"\r{custom_bar.render().plain}")
        print("\033[4A", end="")

        time.sleep(0.05)

    for b in bars + [time_bar]:
        print(f"\r{b.render().plain}")

    print("\n✓ Formatter demo complete!\n")
    time.sleep(2)


def demo_multibar():
    """Demo 8: Multi-bar group."""
    print("=" * 60)
    print("DEMO 8: Multi-Bar Progress")
    print("=" * 60)
    print()

    print("Simulating parallel downloads:\n")

    group = ProgressGroup()

    files = [
        ("video.mp4", "fire"),
        ("audio.mp3", "ocean"),
        ("document.pdf", "matrix"),
    ]

    for filename, theme in files:
        bar = AnimatedProgressBar.from_theme(theme).with_hint(filename)
        group.add(filename, bar)

    # Simulate different download speeds
    speeds = {
        "video.mp4": 0.5,
        "audio.mp3": 1.0,
        "document.pdf": 1.5,
    }

    max_steps = 100
    for i in range(max_steps + 1):
        for filename in speeds:
            # Each file progresses at its own speed
            progress = min(1.0, (i * speeds[filename]) / max_steps)
            group.get(filename).update(progress)

        group.tick_all()

        renders = group.render_all()
        for filename, _ in files:
            print(f"\r{renders[filename].plain}")

        print(f"\033[{len(files)}A", end="")
        time.sleep(0.02)

    renders = group.render_all()
    for filename, _ in files:
        print(f"\r{renders[filename].plain}")

    print("\n✓ All downloads complete!\n")
    time.sleep(2)


def demo_incremental():
    """Demo 9: Incremental updates."""
    print("=" * 60)
    print("DEMO 9: Incremental Updates")
    print("=" * 60)
    print()

    print("Using incr() and decr() methods:\n")

    bar = AnimatedProgressBar(step=0.1).with_hint("Step by 10%")

    bar.update(0.0)

    print("Incrementing by steps of 10%:")
    for _ in range(5):
        bar.incr()

        # Animate
        for _ in range(30):
            bar.tick()
            print(f"\r{bar.render().plain}", end="", flush=True)
            time.sleep(1 / 60)

    print("\n\nDecrementing:")
    for _ in range(3):
        bar.decr()

        for _ in range(30):
            bar.tick()
            print(f"\r{bar.render().plain}", end="", flush=True)
            time.sleep(1 / 60)

    print("\n\n✓ Incremental updates complete!\n")
    time.sleep(2)


def demo_callbacks():
    """Demo 10: Completion callbacks."""
    print("=" * 60)
    print("DEMO 10: Completion Callbacks")
    print("=" * 60)
    print()

    print("Progress bar with completion notification:\n")

    completed = {"done": False}

    def on_complete(state: ProgressState):
        completed["done"] = True
        print("\n\n🎉 Callback triggered!")
        print(f"State: {state.value}")

    bar = (
        AnimatedProgressBar(on_complete=on_complete)
        .with_preset_gradient("neon", scaled=True)
        .with_hint("Watch for completion...")
    )

    for i in range(101):
        bar.update(i / 100)
        bar.tick()
        print(f"\r{bar.render().plain}", end="", flush=True)
        time.sleep(0.02)

    print("\n\n✓ Callback demo complete!\n")
    time.sleep(2)


def demo_metrics():
    """Demo 11: Performance metrics."""
    print("=" * 60)
    print("DEMO 11: Performance Metrics")
    print("=" * 60)
    print()

    print("Tracking rendering performance:\n")

    bar = AnimatedProgressBar().with_hint("With metrics enabled")
    bar.enable_metrics()

    for i in range(101):
        bar.update(i / 100)
        bar.tick()
        print(f"\r{bar.render().plain}", end="", flush=True)
        time.sleep(0.01)

    print("\n")
    print(f"Frames rendered: {bar.metrics.frames_rendered}")
    print(f"Total time: {bar.metrics.total_time * 1000:.2f}ms")
    print(f"Average frame time: {bar.metrics.avg_frame_time * 1000:.2f}ms")
    print(f"Peak frame time: {bar.metrics.peak_frame_time * 1000:.2f}ms")
    print(f"\n{bar.metrics}")

    print("\n✓ Metrics demo complete!\n")
    time.sleep(2)


def demo_serialization():
    """Demo 12: State serialization."""
    print("=" * 60)
    print("DEMO 12: State Serialization")
    print("=" * 60)
    print()

    print("Saving and loading progress state:\n")

    # Create and update
    bar = (
        AnimatedProgressBar()
        .with_preset_gradient("fire", scaled=True)
        .with_hint("Original bar")
    )

    bar.update(0.6)
    for _ in range(50):
        bar.tick()

    print(f"Original: {bar.render().plain}")

    # Save
    filepath = "/tmp/progress_demo.json"
    bar.save_to_file(filepath)
    print(f"\n✓ Saved to {filepath}")

    # Load
    restored = AnimatedProgressBar.load_from_file(filepath)
    print(f"\nRestored: {restored.render().plain}")

    print(f"\nProgress matches: {abs(bar.progress - restored.progress) < 0.01}")
    print(f"Target matches: {bar.target == restored.target}")

    # Cleanup
    Path(filepath).unlink()

    print("\n✓ Serialization demo complete!\n")
    time.sleep(2)


def demo_fluent_api():
    """Demo 13: Fluent API."""
    print("=" * 60)
    print("DEMO 13: Fluent API (Method Chaining)")
    print("=" * 60)
    print()

    print("Building a progress bar with fluent API:\n")
    print("Code:")
    print("  bar = (AnimatedProgressBar()")
    print("         .with_preset_gradient('neon', scaled=True)")
    print("         .with_width(60)")
    print("         .with_hint('Fluent API demo')")
    print("         .with_style_preset('blocks')")
    print("         .with_spring_options(frequency=25.0, damping=1.2))")
    print()

    bar = (
        AnimatedProgressBar()
        .with_preset_gradient("neon", scaled=True)
        .with_width(60)
        .with_hint("Fluent API demo")
        .with_style_preset("blocks")
        .with_spring_options(frequency=25.0, damping=1.2)
    )

    print("Result:\n")

    for i in range(101):
        bar.update(i / 100)
        bar.tick()
        print(f"\r{bar.render().plain}", end="", flush=True)
        time.sleep(0.02)

    print("\n\n✓ Fluent API demo complete!\n")
    time.sleep(2)


def main():
    """Run all demos."""
    clear_screen()

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║     Enhanced Progress Bar - Complete Feature Demo       ║")
    print("║                                                          ║")
    print("║  Inspired by charmbracelet/bubbles                      ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    demos = [
        ("Basic Usage", demo_basic),
        ("Spring Physics", demo_spring_physics),
        ("Gradient Modes", demo_gradients),
        ("Themes", demo_themes),
        ("Gradient Presets", demo_presets),
        ("Character Styles", demo_styles),
        ("Custom Formatters", demo_formatters),
        ("Multi-Bar Groups", demo_multibar),
        ("Incremental Updates", demo_incremental),
        ("Completion Callbacks", demo_callbacks),
        ("Performance Metrics", demo_metrics),
        ("State Serialization", demo_serialization),
        ("Fluent API", demo_fluent_api),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n[{i}/{len(demos)}] Running: {name}")
        time.sleep(1)
        clear_screen()

        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n\n⚠ Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n\n❌ Error in demo: {e}")
            import traceback

            traceback.print_exc()
            time.sleep(3)

    clear_screen()
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║               All Demos Complete! 🎉                    ║")
    print("║                                                          ║")
    print("║  Check PROGRESS_GUIDE.md for detailed documentation     ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Demo suite interrupted")
