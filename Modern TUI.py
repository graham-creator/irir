from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label, Markdown, Select
try:
    from textual.widgets import TextArea
except Exception:
    TextArea = None
try:
<<<<<<< HEAD
    from textual.widgets import Spinner  # type: ignore
=======
    from textual.widgets import Spinner
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
except Exception:
    Spinner = None
from textual import work
import ollama
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

<<<<<<< HEAD
=======
# Local package modules (now in modern_tui/ package)
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
from modern_tui.utils import extract_youtube_id, sanitize_id
import modern_tui.workers as workers
import modern_tui.compare as compare
import modern_tui.conversations as convs
import modern_tui.smoke as smoke
import time
from pathlib import Path
import json
import uuid
<<<<<<< HEAD

def main():
    try:
=======
# AIClient and all heavy UI code have been moved into `modern_tui.app` for better testability and packaging.
# See `modern_tui/app.py` for the implementation.

# Lightweight launcher shim. Implementation moved to `modern_tui.app` (AIClient)
# This file intentionally contains only a small `main()` that imports and runs the packaged TUI.

# Removed legacy inline implementation. See `modern_tui.app` for the current AIClient implementation.



def main():
    try:
        # delegate to the packaged implementation
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
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
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 244f663cf9ab4d014ded6891b188fdb0bd257b72
