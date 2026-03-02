from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label, Markdown, Select
try:
    from textual.widgets import TextArea
except Exception:
    TextArea = None
try:
    from textual.widgets import Spinner  # type: ignore
except Exception:
    Spinner = None
from textual import work
import ollama
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

from modern_tui.utils import extract_youtube_id, sanitize_id
import modern_tui.workers as workers
import modern_tui.compare as compare
import modern_tui.conversations as convs
import modern_tui.smoke as smoke
import time
from pathlib import Path
import json
import uuid

def main():
    try:
        from modern_tui.app import AIClient
        AIClient().run()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('modern_tui_error.log', 'w', encoding='utf-8') as f:
                f.write(tb)
        except Exception:
            pass
        print("An unexpected error occurred while running the TUI. Details were written to modern_tui_error.log")
        raise


if __name__ == "__main__":
    main()
